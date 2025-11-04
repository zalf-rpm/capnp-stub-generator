"""Top-level module for stub generation."""

from __future__ import annotations

import argparse
import glob
import logging
import os.path
from types import ModuleType

import black
import capnp
import isort

from capnp_stub_generator.capnp_types import ModuleRegistryType
from capnp_stub_generator.helper import replace_capnp_suffix
from capnp_stub_generator.writer import Writer

capnp.remove_import_hook()


logger = logging.getLogger(__name__)

PYI_SUFFIX = ".pyi"
PY_SUFFIX = ".py"
LINE_LENGTH = 120


def format_outputs(raw_input: str, is_pyi: bool, line_length: int = LINE_LENGTH) -> str:
    """Formats raw input by means of `black` and `isort`.

    Args:
        raw_input (str): The unformatted input.
        is_pyi (bool): Whether or not the output is a `pyi` file.

    Returns:
        str: The formatted outputs.
    """
    # FIXME: Extract config from dev_policies
    sorted_imports = isort.code(
        raw_input, config=isort.Config(profile="black", line_length=line_length)
    )
    try:
        return black.format_str(
            sorted_imports, mode=black.Mode(is_pyi=is_pyi, line_length=line_length)
        )
    except black.parsing.InvalidInput as e:
        # Save unformatted output for debugging
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".pyi.unformatted", delete=False) as f:
            f.write(sorted_imports)
            logger.error(f"Black formatting failed. Unformatted output saved to: {f.name}")

        # Print context around the error for debugging
        error_msg = str(e)
        if ":" in error_msg:
            try:
                # Extract line number from error message like "234:21: ..."
                line_num = int(error_msg.split(":")[0].strip().split()[-1])
                lines = sorted_imports.split("\n")
                context_start = max(0, line_num - 3)
                context_end = min(len(lines), line_num + 3)
                logger.error(f"Black formatting error at line {line_num}:")
                for i in range(context_start, context_end):
                    marker = ">>>" if i == line_num - 1 else "   "
                    logger.error(f"{marker} {i + 1:4}: {lines[i]}")
            except (ValueError, IndexError):
                pass
        raise


def generate_stubs(module: ModuleType, module_registry: ModuleRegistryType, output_file_path: str):
    """Entry-point for generating *.pyi stubs from a module definition.

    Args:
        module (ModuleType): The module to generate stubs for.
        module_registry (ModuleRegistryType): A registry of all detected modules.
        output_file_path (str): The name of the output stub files, without file extension.
    """
    writer = Writer(module, module_registry)
    writer.generate_all_nested()

    for outputs, suffix, is_pyi in zip(
        (writer.dumps_pyi(), writer.dumps_py()), (PYI_SUFFIX, PY_SUFFIX), (True, False)
    ):
        formatted_output = format_outputs(outputs, is_pyi)

        with open(output_file_path + suffix, "w", encoding="utf8") as output_file:
            output_file.write(formatted_output)

    logger.info("Wrote stubs to '%s(%s/%s)'.", output_file_path, PYI_SUFFIX, PY_SUFFIX)


def extract_base_from_pattern(pattern: str) -> str:
    """Extract the base directory from a glob pattern.

    The base is the directory that should be used as the root for preserving directory structure.
    - For patterns with **, returns the directory before the **
    - For patterns with *, returns the directory containing the *
    - For specific file paths, returns the parent directory

    Args:
        pattern: A file path or glob pattern.

    Returns:
        The base directory path, or empty string if pattern starts with wildcard.
    """
    # Handle absolute vs relative paths
    is_absolute = os.path.isabs(pattern)

    # Split pattern into parts and find the longest directory path before any wildcard
    parts = pattern.split(os.sep)
    base_parts = []
    found_wildcard = False

    for i, part in enumerate(parts):
        if "**" in part:
            # For **, use the directory before it
            found_wildcard = True
            break
        elif "*" in part or "?" in part or "[" in part:
            # For other wildcards, use the directory containing them
            found_wildcard = True
            break
        base_parts.append(part)

    if not base_parts:
        return ""

    # Reconstruct the path
    if is_absolute:
        # For absolute paths, join from root
        base = os.sep + os.path.join(*base_parts[1:]) if len(base_parts) > 1 else os.sep
    else:
        base = os.path.join(*base_parts) if len(base_parts) > 1 else base_parts[0]

    # If no wildcard was found and the pattern is a specific file, use its parent directory
    if not found_wildcard and os.path.splitext(pattern)[1] == ".capnp":
        base = os.path.dirname(base)

    return base


def run(args: argparse.Namespace, root_directory: str):
    """Run the stub generator on a set of paths that point to *.capnp schemas.

    Uses `generate_stubs` on each input file.

    Args:
        args (argparse.Namespace): The arguments that were passed when calling the stub generator.
        root_directory (str): The directory, from which the generator is executed.
    """
    paths: list[str] = args.paths
    excludes: list[str] = args.excludes
    clean: list[str] = args.clean
    output_dir: str = getattr(args, "output_dir", "")
    import_paths: list[str] = getattr(args, "import_paths", [])

    cleanup_paths: set[str] = set()
    for c in clean:
        cleanup_directory = os.path.join(root_directory, c)
        cleanup_paths = cleanup_paths.union(glob.glob(cleanup_directory, recursive=args.recursive))

    for cleanup_path in cleanup_paths:
        os.remove(cleanup_path)

    excluded_paths: set[str] = set()
    for exclude in excludes:
        exclude_directory = os.path.join(root_directory, exclude)
        excluded_paths = excluded_paths.union(
            glob.glob(exclude_directory, recursive=args.recursive)
        )

    search_paths: set[str] = set()
    for path in paths:
        search_directory = os.path.join(root_directory, path)
        search_paths = search_paths.union(glob.glob(search_directory, recursive=args.recursive))

    # The `valid_paths` contain the automatically detected search paths, except for specifically excluded paths.
    valid_paths = search_paths - excluded_paths

    # Convert import paths to absolute paths relative to root_directory
    absolute_import_paths = [os.path.join(root_directory, p) for p in import_paths]

    parser = capnp.SchemaParser()
    module_registry: ModuleRegistryType = {}

    for path in valid_paths:
        module = parser.load(path, imports=absolute_import_paths)
        module_registry[module.schema.node.id] = (path, module)

    # If output_dir is specified, determine the common base path from the search patterns
    # to preserve directory structure
    common_base = None
    if output_dir and len(paths) > 0:
        # Extract base directories from all search patterns
        # Use relative paths if possible to accurately measure depth
        original_pattern_bases = []
        relative_pattern_bases = []
        for path in paths:
            # Get base from the path as-is
            base = extract_base_from_pattern(path)
            if base:
                original_pattern_bases.append(base)
                # Also track relative version for depth calculation
                if os.path.isabs(path):
                    # Convert to relative if possible
                    try:
                        rel_path = os.path.relpath(path, root_directory)
                        # Only use relative path if it doesn't go outside root_directory
                        # (i.e., doesn't start with '..')
                        if not rel_path.startswith(".."):
                            rel_base = extract_base_from_pattern(rel_path)
                            if rel_base:
                                relative_pattern_bases.append(rel_base)
                        # else: path is outside root_directory, don't add to relative_pattern_bases
                    except ValueError:
                        # Paths on different drives on Windows
                        pass  # Don't add to relative_pattern_bases
                else:
                    relative_pattern_bases.append(base)

        # Now get absolute pattern bases
        pattern_bases = []
        for path in paths:
            # Convert to absolute path relative to root_directory
            if not os.path.isabs(path):
                path = os.path.join(root_directory, path)
            base = extract_base_from_pattern(path)
            if base:
                # Convert to absolute path
                if not os.path.isabs(base):
                    base = os.path.join(root_directory, base)
                pattern_bases.append(base)

        # Find common base from all pattern bases
        if len(pattern_bases) == 1:
            common_base = pattern_bases[0]
            # For single pattern: only preserve subdirectory structure if it's a recursive glob
            # or if the pattern explicitly shows subdirectory structure with wildcards
            if relative_pattern_bases and len(paths) > 0:
                original_pattern = paths[0]
                # Check if pattern has ** (recursive glob) - these should preserve structure
                if "**" in original_pattern:
                    sample_relative = relative_pattern_bases[0]
                    depth = sample_relative.count(os.sep)
                    if depth >= 2:
                        # Verify all files are in this directory
                        all_files_direct = True
                        for path in list(valid_paths)[:10]:
                            abs_path = os.path.abspath(path)
                            file_dir = os.path.dirname(abs_path)
                            if file_dir != common_base:
                                all_files_direct = False
                                break
                        if all_files_direct:
                            common_base = os.path.dirname(common_base)
        elif len(pattern_bases) > 1:
            common_base = os.path.commonpath(pattern_bases)

            # If all pattern bases are identical (files from same directory),
            # check if we should go up to preserve the subdirectory name.
            # Only do this if the bases are actually different paths (multiple subdirs involved)
            if all(base == pattern_bases[0] for base in pattern_bases):
                # Check if files are directly in common_base
                all_files_direct = True
                for path in list(valid_paths)[:10]:
                    abs_path = os.path.abspath(path)
                    file_dir = os.path.dirname(abs_path)
                    if file_dir != common_base:
                        all_files_direct = False
                        break

                # Go up if all files are direct AND depth >= 2 (subdirectory to preserve)
                if all_files_direct and relative_pattern_bases:
                    sample_relative = relative_pattern_bases[0]
                    depth = sample_relative.count(os.sep)
                    if depth >= 2:
                        common_base = os.path.dirname(common_base)
            # If bases are different, the commonpath already gives us the right level

        # If no pattern bases were found, use the common path of all found files
        if not common_base and len(valid_paths) > 0:
            abs_paths = [os.path.abspath(p) for p in valid_paths]
            if len(abs_paths) == 1:
                common_base = os.path.dirname(abs_paths[0])
            else:
                common_base = os.path.commonpath(abs_paths)
                if os.path.isfile(common_base):
                    common_base = os.path.dirname(common_base)

    for path, module in module_registry.values():
        if output_dir:
            abs_path = os.path.abspath(path)

            if common_base:
                # Calculate relative path from common base
                rel_path = os.path.relpath(abs_path, common_base)
                rel_dir = os.path.dirname(rel_path)

                # Create output directory preserving structure
                output_directory = os.path.join(output_dir, rel_dir)
            else:
                output_directory = output_dir

            os.makedirs(output_directory, exist_ok=True)
        else:
            # No output_dir specified: place stubs next to source files
            output_directory = os.path.dirname(path)

        output_file_name = replace_capnp_suffix(os.path.basename(path))

        generate_stubs(module, module_registry, os.path.join(output_directory, output_file_name))
