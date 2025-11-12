"""Top-level module for stub generation."""

from __future__ import annotations

import argparse
import glob
import logging
import os.path
import shutil
import subprocess
import sys
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


class PyrightValidationError(Exception):
    """Raised when pyright validation finds type errors in generated stubs."""

    pass


def find_capnp_stubs_package() -> str | None:
    """Find the installed capnp-stubs package directory.

    Checks both standard site-packages and .pth files for the package location.

    Returns:
        Path to the capnp-stubs directory, or None if not found.
    """
    # First check for direct capnp-stubs directory
    for path in sys.path:
        capnp_stubs_path = os.path.join(path, "capnp-stubs")
        if os.path.isdir(capnp_stubs_path):
            logger.info(f"Found capnp-stubs package at: {capnp_stubs_path}")
            return capnp_stubs_path

    # Check for .pth files that might point to capnp-stubs
    for path in sys.path:
        if os.path.isdir(path):
            pth_file = os.path.join(path, "capnp_stubs.pth")
            if os.path.exists(pth_file):
                with open(pth_file) as f:
                    pth_path = f.read().strip()
                    capnp_stubs_path = os.path.join(pth_path, "capnp-stubs")
                    if os.path.isdir(capnp_stubs_path):
                        logger.info(f"Found capnp-stubs package via .pth file at: {capnp_stubs_path}")
                        return capnp_stubs_path

    return None


def _sort_interfaces_by_inheritance(interfaces: dict[str, tuple[str, list[str]]]) -> list[tuple[str, str]]:
    """Sort interfaces by inheritance depth - most derived first.

    This ensures overloads are ordered correctly with specific types before general types.

    Args:
        interfaces: Dict mapping interface_name -> (client_name, base_client_names)

    Returns:
        Sorted list of (interface_name, client_name) tuples, most derived first
    """
    # Build a mapping of client_name -> interface_name for reverse lookup
    client_to_interface = {}
    for iface_name, (client_name, _) in interfaces.items():
        client_to_interface[client_name] = iface_name

    # Compute depth for each interface (number of ancestors)
    def compute_depth(interface_name: str, visited: set[str] | None = None) -> int:
        if visited is None:
            visited = set()

        if interface_name in visited:
            # Circular dependency - shouldn't happen but handle gracefully
            return 0

        visited.add(interface_name)

        if interface_name not in interfaces:
            # Base interface not in our set
            return 0

        _, base_client_names = interfaces[interface_name]
        if not base_client_names:
            # No bases - this is a root
            return 0

        # Depth is 1 + max depth of any base
        max_base_depth = 0
        for base_client_name in base_client_names:
            # Convert client name back to interface name
            base_interface_name = client_to_interface.get(base_client_name)
            if base_interface_name:
                base_depth = compute_depth(base_interface_name, visited.copy())
                max_base_depth = max(max_base_depth, base_depth)

        return 1 + max_base_depth

    # Compute depths for all interfaces
    interface_depths = []
    for interface_name, (client_name, _) in interfaces.items():
        depth = compute_depth(interface_name)
        interface_depths.append((depth, interface_name, client_name))

    # Sort by depth (descending) then by name (ascending for stability)
    interface_depths.sort(key=lambda x: (-x[0], x[1]))

    # Return just the (interface_name, client_name) tuples
    return [(iface_name, client_name) for _, iface_name, client_name in interface_depths]


def augment_capnp_stubs_with_overloads(
    source_stubs_path: str,
    augmented_stubs_dir: str,
    output_dir: str,
    interfaces: dict[str, tuple[str, list[str]]],
) -> None:
    """Copy capnp-stubs package and augment with cast_as overloads.

    This copies the entire capnp-stubs package to a separate directory
    and augments lib/capnp.pyi with overloaded cast_as methods for generated interfaces.

    Args:
        source_stubs_path: Path to the source capnp-stubs package.
        augmented_stubs_dir: Directory where the augmented capnp-stubs should be placed (beside output).
        output_dir: The output directory where generated stubs are located (for relative import calculation).
        interfaces: Dictionary mapping interface names to (client_name, base_client_names) tuples.
    """
    if not interfaces:
        logger.info("No interfaces found, skipping capnp-stubs augmentation.")
        return

    # Create destination path for augmented stubs
    dest_stubs_path = os.path.join(augmented_stubs_dir, "capnp-stubs")

    # Copy the entire capnp-stubs directory
    if os.path.exists(dest_stubs_path):
        shutil.rmtree(dest_stubs_path)
    shutil.copytree(source_stubs_path, dest_stubs_path)
    logger.info(f"Copied capnp-stubs to: {dest_stubs_path}")

    # Path to lib/capnp.pyi
    capnp_pyi_path = os.path.join(dest_stubs_path, "lib", "capnp.pyi")

    if not os.path.exists(capnp_pyi_path):
        logger.warning(f"Could not find lib/capnp.pyi at {capnp_pyi_path}, skipping augmentation.")
        return

    # Read the original file
    with open(capnp_pyi_path, encoding="utf8") as f:
        original_content = f.read()

    lines = original_content.split("\n")

    # Find where to add overload import
    typing_import_idx = None
    for i, line in enumerate(lines):
        if line.startswith("from typing import"):
            typing_import_idx = i
            break

    if typing_import_idx is None:
        logger.warning("Could not find 'from typing import' in lib/capnp.pyi, skipping augmentation.")
        return

    # Add overload to the typing import if not already present
    typing_line = lines[typing_import_idx]
    if "overload" not in typing_line:
        # Add overload to the import
        typing_line = typing_line.replace("from typing import ", "from typing import overload, ")
        lines[typing_import_idx] = typing_line

    # Find the end of ALL imports (including multi-line imports)
    # We need to skip past all import statements and multi-line parenthesized imports
    import_end_idx = typing_import_idx + 1
    in_multiline_import = False

    for i in range(typing_import_idx + 1, len(lines)):
        line = lines[i]
        stripped = line.strip()

        # Check if we're in a multi-line import
        if "from " in stripped and "import (" in stripped and ")" not in stripped:
            in_multiline_import = True
            continue

        if in_multiline_import:
            if ")" in stripped:
                in_multiline_import = False
            continue

        # Check if this is a single-line import
        if stripped.startswith("import ") or stripped.startswith("from "):
            continue

        # Empty lines or comments between imports - continue
        if not stripped or stripped.startswith("#"):
            continue

        # We've found the first non-import line
        import_end_idx = i
        break

    # Build the module imports section
    # Extract unique modules from interface names and build import paths relative to output
    # Map: module_capnp_name -> (from_path, module_name)
    module_imports = {}

    for interface_name in interfaces.keys():
        # interface_name is like "calculator.calculator_capnp.Calculator" or
        # "models.monica.monica_management_capnp.MonicaManagement"
        # We need to extract the module path (ends with _capnp)
        parts = interface_name.split(".")

        # Find the part that ends with _capnp
        capnp_module_idx = None
        for i, part in enumerate(parts):
            if part.endswith("_capnp"):
                capnp_module_idx = i
                break

        if capnp_module_idx is None:
            # Couldn't find a capnp module, skip
            continue

        # Get the capnp module name
        capnp_module_name = parts[capnp_module_idx]

        # Get the base name of the output directory to use as the root module
        output_base_name = os.path.basename(os.path.abspath(output_dir))

        # Build the from path
        if capnp_module_idx == 0:
            # Top-level module: from <output_base> import calculator_capnp
            from_path = output_base_name
        else:
            # Nested module: from <output_base>.models.monica import monica_management_capnp
            subpath = ".".join(parts[:capnp_module_idx])
            from_path = f"{output_base_name}.{subpath}"

        # Store unique import (from_path, module_name)
        module_imports[capnp_module_name] = from_path

    # Build import lines
    import_lines = [
        "",
        "# Generated imports for project-specific interfaces",
    ]
    for capnp_module_name in sorted(module_imports.keys()):
        from_path = module_imports[capnp_module_name]
        import_lines.append(f"from {from_path} import {capnp_module_name}  # type: ignore[import-not-found]")

    # Insert the imports after the existing imports
    lines[import_end_idx:import_end_idx] = import_lines

    # Now find _CastableBootstrap class and its cast_as method
    cast_as_line_idx = None
    in_castable_bootstrap = False

    for i, line in enumerate(lines):
        if "class _CastableBootstrap" in line:
            in_castable_bootstrap = True
        elif in_castable_bootstrap and "def cast_as(self, interface:" in line:
            cast_as_line_idx = i
            break
        elif in_castable_bootstrap and line.strip().startswith("class ") and "_CastableBootstrap" not in line:
            # Found another class, stop looking
            break

    if cast_as_line_idx is None:
        logger.warning("Could not find cast_as method in _CastableBootstrap class, skipping augmentation.")
        return

    # Sort interfaces by inheritance depth (most derived first)
    sorted_interfaces = _sort_interfaces_by_inheritance(interfaces)

    # Build the overloads (insert before the existing cast_as method)
    overload_lines = []

    for interface_name, client_name in sorted_interfaces:
        # interface_name is like "calculator.calculator_capnp.Calculator" or
        # "models.monica.monica_management_capnp.MonicaManagement"
        parts = interface_name.split(".")

        # Find the part that ends with _capnp
        capnp_module_idx = None
        capnp_module_name = None
        for j, part in enumerate(parts):
            if part.endswith("_capnp"):
                capnp_module_idx = j
                capnp_module_name = part
                break

        if capnp_module_idx is None or capnp_module_name is None:
            logger.warning(f"Could not find capnp module in interface name: {interface_name}")
            continue

        # Get the from path from module_imports
        from_path = module_imports.get(capnp_module_name)
        if not from_path:
            logger.warning(f"Could not find import path for module {capnp_module_name}")
            continue

        # Build qualified names: capnp_module_name.RestOfPath
        # For "calculator.calculator_capnp.Calculator" -> "calculator_capnp.Calculator"
        # For "models.monica.monica_management_capnp.MonicaManagement" -> "monica_management_capnp.MonicaManagement"
        interface_suffix = ".".join(parts[capnp_module_idx:])
        client_suffix = ".".join(client_name.split(".")[capnp_module_idx:])

        qualified_interface = interface_suffix
        qualified_client = client_suffix

        overload_lines.append("    @overload")
        overload_lines.append(
            f"    def cast_as(self, interface: type[{qualified_interface}]) -> {qualified_client}: ..."
        )

    # Add a catchall overload that matches the original function definition
    overload_lines.append("    @overload")
    overload_lines.append("    def cast_as(self, interface: Any) -> _DynamicCapabilityClient: ...")

    # Insert overloads before the original cast_as method
    lines[cast_as_line_idx:cast_as_line_idx] = overload_lines

    # Write back
    augmented_content = "\n".join(lines)
    with open(capnp_pyi_path, "w", encoding="utf8") as f:
        f.write(augmented_content)

    logger.info(f"Augmented {capnp_pyi_path} with {len(interfaces)} cast_as overload(s).")

    # Format the augmented file with ruff
    try:
        subprocess.run(
            ["ruff", "format", capnp_pyi_path],
            capture_output=True,
            check=True,
        )
        logger.info(f"Formatted augmented file: {capnp_pyi_path}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to format augmented file: {e}")
    except FileNotFoundError:
        logger.warning("ruff not found, skipping formatting of augmented file")


def validate_with_pyright(output_directories: set[str]) -> None:
    """Validate generated stub files using pyright.

    Args:
        output_directories: Set of directories containing generated stubs.

    Raises:
        PyrightValidationError: If pyright finds any type errors.
    """
    # Collect all .pyi files from output directories
    stub_files = []
    for output_dir in output_directories:
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.endswith(".pyi"):
                    stub_files.append(os.path.join(root, file))

    if not stub_files:
        logger.warning("No stub files found to validate")
        return

    logger.info(f"Validating {len(stub_files)} generated stub file(s) with pyright...")

    try:
        # Run pyright on all stub files
        result = subprocess.run(
            ["pyright"] + stub_files,
            capture_output=True,
            text=True,
            check=False,
        )

        # Check for errors in output
        error_count = result.stdout.count(" error:")

        if error_count > 0 or result.returncode != 0:
            error_msg = f"Pyright validation failed with {error_count} error(s):\n\n{result.stdout}"
            logger.error(error_msg)
            raise PyrightValidationError(error_msg)

        logger.info("✓ Pyright validation passed - no type errors found")

    except FileNotFoundError:
        logger.error("pyright not found. Please install pyright: npm install -g pyright")
        raise PyrightValidationError("pyright command not found. Please install pyright.")
    except subprocess.SubprocessError as e:
        error_msg = f"Error running pyright: {e}"
        logger.error(error_msg)
        raise PyrightValidationError(error_msg)


def format_outputs(raw_input: str, is_pyi: bool) -> str:
    """Formats raw input using ruff.

    Args:
        raw_input (str): The unformatted input.
        is_pyi (bool): Whether or not the output is a `pyi` file.

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
    module_path_prefix: str | None = None,
) -> dict[str, tuple[str, list[str]]]:
    """Entry-point for generating *.pyi stubs from a module definition.

    Args:
        module (ModuleType): The module to generate stubs for.
        module_registry (ModuleRegistryType): A registry of all detected modules.
        output_file_path (str): The name of the output stub files, without file extension.
        output_directory (str | None): The directory where output files are written, if different from schema location.
        import_paths (list[str] | None): Additional import paths for resolving absolute imports.
        module_path_prefix (str | None): Prefix for module path (e.g., "calculator" for subdirectory structure).

    Returns:
        dict[str, tuple[str, list[str]]]: Dictionary mapping interface names to (client_name, base_client_names) tuples.
    """
    writer = Writer(module, module_registry, output_directory=output_directory, import_paths=import_paths)
    writer.generate_all_nested()

    for outputs, suffix, is_pyi in zip((writer.dumps_pyi(), writer.dumps_py()), (PYI_SUFFIX, PY_SUFFIX), (True, False)):
        formatted_output = format_outputs(outputs, is_pyi)

        with open(output_file_path + suffix, "w", encoding="utf8") as output_file:
            output_file.write(formatted_output)

    logger.info("Wrote stubs to '%s(%s/%s)'.", output_file_path, PYI_SUFFIX, PY_SUFFIX)

    # Return interfaces found in this module (with module prefix)
    module_name = os.path.basename(output_file_path)

    # If module_path_prefix is provided, prepend it
    if module_path_prefix:
        full_module_name = f"{module_path_prefix}.{module_name}"
    else:
        full_module_name = module_name

    interfaces_with_module = {}
    for interface_name, (client_name, base_client_names) in writer._all_interfaces.items():
        # Add module prefix to make fully qualified names
        qualified_interface = f"{full_module_name}.{interface_name}"
        qualified_client = f"{full_module_name}.{client_name}"

        # Also qualify the base client names
        qualified_base_clients = [f"{full_module_name}.{base}" for base in base_client_names]

        interfaces_with_module[qualified_interface] = (qualified_client, qualified_base_clients)

    return interfaces_with_module


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
    skip_pyright: bool = getattr(args, "skip_pyright", False)

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
            for root, _, files in os.walk(search_path):
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

    # Collect all interfaces from all modules for cast_as overloads
    # Map of output_dir -> {interface_name: (client_name, base_client_names)}
    all_interfaces_by_dir: dict[str, dict[str, tuple[str, list[str]]]] = {}

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

        # Calculate module path prefix for subdirectory structure
        # This is used for fully qualified module names in cast_as overloads
        module_path_prefix = None
        if output_dir and output_directory != output_dir:
            # Calculate the relative path from output_dir to output_directory
            rel_module_path = os.path.relpath(output_directory, output_dir)
            # Convert path separators to dots for Python module path
            # Skip if it's just "." (current directory)
            if rel_module_path != ".":
                module_path_prefix = rel_module_path.replace(os.sep, ".")

        # Pass output_directory to generate_stubs so it can calculate relative paths
        # Only pass it if it's different from the schema's directory
        schema_directory = os.path.dirname(path)
        output_dir_to_pass = output_directory if output_directory != schema_directory else None

        module_interfaces = generate_stubs(
            module,
            module_registry,
            os.path.join(output_directory, output_file_name),
            output_dir_to_pass,
            absolute_import_paths,
            module_path_prefix,
        )

        # Collect interfaces for this output directory
        if module_interfaces:
            if output_directory not in all_interfaces_by_dir:
                all_interfaces_by_dir[output_directory] = {}
            all_interfaces_by_dir[output_directory].update(module_interfaces)

    # Create py.typed marker in each output directory to mark the package as typed (PEP 561)
    for output_directory in output_directories_used:
        py_typed_path = os.path.join(output_directory, "py.typed")
        # Create an empty py.typed file if it doesn't exist
        if not os.path.exists(py_typed_path):
            with open(py_typed_path, "w", encoding="utf8") as f:
                f.write("")  # Empty file as per PEP 561

    # Augment capnp-stubs with cast_as overloads if requested
    if args.augment_capnp_stubs:
        source_stubs_path = find_capnp_stubs_package()
        if source_stubs_path:
            # Combine all interfaces from all directories
            all_interfaces = {}
            for interfaces in all_interfaces_by_dir.values():
                all_interfaces.update(interfaces)

            # Determine where to place augmented stubs (beside output directories, not inside)
            # If output_dir is specified, place augmented stubs beside it
            # Otherwise, pick a common parent directory of all output directories
            if output_dir:
                # Place augmented stubs in the parent directory of output_dir
                augmented_stubs_dir = os.path.dirname(os.path.abspath(output_dir))
            else:
                # Find common parent of all output directories
                output_dirs_list = list(output_directories_used)
                if len(output_dirs_list) == 1:
                    augmented_stubs_dir = output_dirs_list[0]
                else:
                    augmented_stubs_dir = os.path.commonpath([os.path.abspath(d) for d in output_dirs_list])

            # Use the absolute path to output_dir for import path calculation
            actual_output_dir = os.path.abspath(output_dir) if output_dir else list(output_directories_used)[0]
            augment_capnp_stubs_with_overloads(
                source_stubs_path, augmented_stubs_dir, actual_output_dir, all_interfaces
            )
        else:
            logger.warning("--augment-capnp-stubs specified but capnp-stubs package not found in sys.path")

    # Validate generated stubs with pyright (unless disabled)
    if not skip_pyright:
        validate_with_pyright(output_directories_used)
