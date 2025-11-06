"""Top-level module for stub generation."""

from __future__ import annotations

import argparse
import glob
import logging
import os.path
import subprocess
import tempfile
from pathlib import Path
from types import ModuleType

import capnp

from capnp_stub_generator.capnp_types import ModuleRegistryType
from capnp_stub_generator.helper import replace_capnp_suffix
from capnp_stub_generator.writer import Writer

if hasattr(capnp, "remove_import_hook"):
    capnp.remove_import_hook()


logger = logging.getLogger(__name__)

PYI_SUFFIX = ".pyi"
PY_SUFFIX = ".py"
LINE_LENGTH = 120


def format_outputs(raw_input: str, is_pyi: bool, line_length: int = LINE_LENGTH) -> str:
    """Formats raw input using ruff.

    Args:
        raw_input (str): The unformatted input.
        is_pyi (bool): Whether or not the output is a `pyi` file.
        line_length (int): Line length for formatting (not used, taken from pyproject.toml).

    Returns:
        str: The formatted outputs.
    """
    try:
        # Write to temporary file for ruff to process
        suffix = ".pyi" if is_pyi else ".py"
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
            temp_path = Path(f.name)
            f.write(raw_input)

        try:
            # Run ruff check --fix to fix import ordering and other issues
            subprocess.run(
                ["ruff", "check", "--fix", "--select", "I", str(temp_path)],
                capture_output=True,
                check=False,  # Don't raise on non-zero exit
            )

            # Run ruff format to format the code
            subprocess.run(
                ["ruff", "format", str(temp_path)],
                capture_output=True,
                check=True,
            )

            # Read the formatted output
            return temp_path.read_text(encoding="utf-8")

        finally:
            # Clean up temporary file
            temp_path.unlink(missing_ok=True)

    except subprocess.CalledProcessError as e:
        logger.error(f"Ruff formatting failed: {e}")
        logger.error(f"Stdout: {e.stdout.decode('utf-8', errors='replace')}")
        logger.error(f"Stderr: {e.stderr.decode('utf-8', errors='replace')}")
        # Return unformatted output on error
        return raw_input
    except Exception as e:
        logger.error(f"Unexpected error during formatting: {e}")
        return raw_input


def generate_stubs(
    module: ModuleType,
    module_registry: ModuleRegistryType,
    output_file_path: str,
    output_directory: str | None = None,
    import_paths: list[str] | None = None,
):
    """Entry-point for generating *.pyi stubs from a module definition.

    Args:
        module (ModuleType): The module to generate stubs for.
        module_registry (ModuleRegistryType): A registry of all detected modules.
        output_file_path (str): The name of the output stub files, without file extension.
        output_directory (str | None): The directory where output files are written, if different from schema location.
        import_paths (list[str] | None): Additional import paths for resolving absolute imports.
    """
    writer = Writer(module, module_registry, output_directory=output_directory, import_paths=import_paths)
    writer.generate_all_nested()

    for outputs, suffix, is_pyi in zip((writer.dumps_pyi(), writer.dumps_py()), (PYI_SUFFIX, PY_SUFFIX), (True, False)):
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
        exclude_path = os.path.join(root_directory, exclude)
        # Handle both specific files and glob patterns
        if os.path.isfile(exclude_path):
            excluded_paths.add(exclude_path)
        else:
            excluded_paths = excluded_paths.union(glob.glob(exclude_path, recursive=args.recursive))

    search_paths: set[str] = set()
    for path in paths:
        search_path = os.path.join(root_directory, path)

        # If recursive flag is set and path is a directory, find all .capnp files recursively
        if args.recursive and os.path.isdir(search_path):
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith(".capnp"):
                        search_paths.add(os.path.join(root, file))
        # If path is a directory without recursive flag, find only direct children
        elif os.path.isdir(search_path):
            for file in os.listdir(search_path):
                file_path = os.path.join(search_path, file)
                if os.path.isfile(file_path) and file.endswith(".capnp"):
                    search_paths.add(file_path)
        # Otherwise use glob for patterns or specific files
        else:
            search_paths = search_paths.union(glob.glob(search_path, recursive=args.recursive))

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

    # Track output directories for py.typed marker
    output_directories_used = set()

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

        output_directories_used.add(output_directory)

        output_file_name = replace_capnp_suffix(os.path.basename(path))

        # Pass output_directory to generate_stubs so it can calculate relative paths
        # Only pass it if it's different from the schema's directory
        schema_directory = os.path.dirname(path)
        output_dir_to_pass = output_directory if output_directory != schema_directory else None

        generate_stubs(
            module,
            module_registry,
            os.path.join(output_directory, output_file_name),
            output_dir_to_pass,
            absolute_import_paths,
        )

    # Create py.typed marker in each output directory to mark the package as typed (PEP 561)
    for output_directory in output_directories_used:
        py_typed_path = os.path.join(output_directory, "py.typed")
        # Create an empty py.typed file if it doesn't exist
        if not os.path.exists(py_typed_path):
            with open(py_typed_path, "w", encoding="utf8") as f:
                f.write("")  # Empty file as per PEP 561
