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
        return black.format_str(sorted_imports, mode=black.Mode(is_pyi=is_pyi, line_length=line_length))
    except black.parsing.InvalidInput as e:
        # Save unformatted output for debugging
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pyi.unformatted', delete=False) as f:
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
                    logger.error(f"{marker} {i+1:4}: {lines[i]}")
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

    # If output_dir is specified, determine the common base path of all input files
    # to preserve directory structure
    common_base = None
    if output_dir and len(valid_paths) > 1:
        # Find common base path for all input files
        abs_paths = [os.path.abspath(p) for p in valid_paths]
        common_base = os.path.commonpath(abs_paths)
        # If common base is just a file (not a directory), use its parent
        if os.path.isfile(common_base):
            common_base = os.path.dirname(common_base)
    elif output_dir and len(valid_paths) == 1:
        # Single file: use its directory as base
        common_base = os.path.dirname(os.path.abspath(list(valid_paths)[0]))
    
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
