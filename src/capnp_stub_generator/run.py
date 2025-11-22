"""Top-level module for stub generation."""

from __future__ import annotations

import argparse
import glob
import logging
import os.path
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

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


@dataclass
class InterfaceNode:
    """Represents an interface in the inheritance hierarchy."""

    name: str
    client_name: str
    base_client_names: list[str]

    def compute_depth(
        self,
        registry: dict[str, InterfaceNode],
        client_to_interface: dict[str, str],
        visited: set[str] | None = None,
    ) -> int:
        """Compute inheritance depth for this interface.

        Returns:
            Depth value where 0 = root interface (no bases),
            1+ = derived interfaces
        """
        if visited is None:
            visited = set()

        if self.name in visited:
            # Circular dependency - shouldn't happen but handle gracefully
            return 0

        visited.add(self.name)

        if not self.base_client_names:
            # No bases - this is a root
            return 0

        # Depth is 1 + max depth of any base
        max_base_depth = 0
        for base_client_name in self.base_client_names:
            # Convert client name back to interface name
            base_interface_name = client_to_interface.get(base_client_name)
            if base_interface_name and base_interface_name in registry:
                base_node = registry[base_interface_name]
                base_depth = base_node.compute_depth(registry, client_to_interface, visited.copy())
                max_base_depth = max(max_base_depth, base_depth)

        return 1 + max_base_depth


def find_capnp_stubs_package() -> str | None:
    """Find the bundled capnp-stubs package directory.

    Uses the bundled stubs from the resources directory.

    Returns:
        Path to the capnp-stubs directory, or None if not found.
    """
    # Get the bundled capnp-stubs from capnp-stubs directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bundled_stubs_path = os.path.join(current_dir, "..", "pycapnp-base-stubs")

    if os.path.isdir(bundled_stubs_path):
        logger.info(f"Using bundled capnp-stubs from: {bundled_stubs_path}")
        return bundled_stubs_path

    logger.warning(f"Bundled capnp-stubs not found at: {bundled_stubs_path}")
    return None


def _sort_interfaces_by_inheritance(interfaces: dict[str, tuple[str, list[str]]]) -> list[tuple[str, str]]:
    """Sort interfaces by inheritance depth - most derived first.

    This ensures overloads are ordered correctly with specific types before general types.

    Args:
        interfaces: Dict mapping interface_name -> (client_name, base_client_names)

    Returns:
        Sorted list of (interface_name, client_name) tuples, most derived first
    """
    if not interfaces:
        return []

    # Build registry of InterfaceNode objects
    nodes = {name: InterfaceNode(name, client, bases) for name, (client, bases) in interfaces.items()}

    # Build reverse lookup: client_name -> interface_name
    client_to_interface = {client: name for name, (client, _) in interfaces.items()}

    # Compute depths for all interfaces
    depths = [
        (node.compute_depth(nodes, client_to_interface), len(node.base_client_names), name, node.client_name)
        for name, node in nodes.items()
    ]

    # Sort by depth (descending), then by number of bases (descending), then by name (ascending for stability)
    # This ensures most derived/specific interfaces come first
    depths.sort(key=lambda x: (-x[0], -x[1], x[2]))

    # Return just the (interface_name, client_name) tuples
    return [(iface_name, client_name) for _, _, iface_name, client_name in depths]


def augment_capnp_stubs_with_overloads(
    source_stubs_path: str,
    augmented_stubs_dir: str,
    output_dir: str,
    interfaces: dict[str, tuple[str, list[str]]],
    dynamic_object_types: dict[str, list[tuple[str, str]]],
) -> None:
    """Copy capnp-stubs package and augment with cast_as and _DynamicObjectReader overloads.

    This copies the entire capnp-stubs package to a separate directory
    and augments lib/capnp.pyi with overloaded cast_as methods for generated interfaces
    and overloaded as_struct/as_interface methods for _DynamicObjectReader.

    Args:
        source_stubs_path: Path to the source capnp-stubs package.
        augmented_stubs_dir: Directory where the augmented capnp-stubs should be placed (beside output).
        output_dir: The output directory where generated stubs are located (for relative import calculation).
        interfaces: Dictionary mapping interface names to (client_name, base_client_names) tuples.
        dynamic_object_types: Dictionary with "structs" and "interfaces" keys containing type tuples.
    """
    if not interfaces and not dynamic_object_types.get("structs") and not dynamic_object_types.get("interfaces"):
        logger.info("No interfaces or _DynamicObjectReader types found, skipping capnp-stubs augmentation.")
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

    # Build module imports for both cast_as and _DynamicObjectReader augmentation
    module_imports = _build_module_imports(interfaces, dynamic_object_types, output_dir, lines, typing_import_idx)

    # Write back the lines with imports added
    with open(capnp_pyi_path, "w", encoding="utf8") as f:
        f.write("\n".join(lines))

    # Augment cast_as if we have interfaces
    if interfaces:
        _augment_capnp_pyi(capnp_pyi_path, output_dir, interfaces, module_imports)

    # Augment _DynamicObjectReader if we have types
    struct_types = dynamic_object_types.get("structs", [])
    interface_types = dynamic_object_types.get("interfaces", [])
    if struct_types or interface_types:
        _augment_dynamic_object_reader(
            capnp_pyi_path, output_dir, struct_types, interface_types, module_imports, interfaces
        )


def _build_module_imports(
    interfaces: dict[str, tuple[str, list[str]]],
    dynamic_object_types: dict[str, list[tuple[str, str]]],
    output_dir: str,
    lines: list[str],
    typing_import_idx: int,
) -> dict[str, str]:
    """Build module imports section for augmented capnp.pyi.

    Args:
        interfaces: Dictionary of interfaces for cast_as overloads.
        dynamic_object_types: Dictionary with struct/interface types for _DynamicObjectReader.
        output_dir: Output directory for calculating relative imports.
        lines: Current lines of capnp.pyi (will be modified in place).
        typing_import_idx: Index of the typing import line.

    Returns:
        Dictionary mapping module names to import paths.
    """
    # Find the end of ALL imports (including multi-line imports)
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

    # Collect all module names from interfaces and dynamic object types
    all_qualified_names = set()

    # From interfaces
    for interface_name in interfaces.keys():
        all_qualified_names.add(interface_name)

    # From struct types
    for protocol_name, _ in dynamic_object_types.get("structs", []):
        all_qualified_names.add(protocol_name)

    # From interface types
    for protocol_name, _ in dynamic_object_types.get("interfaces", []):
        all_qualified_names.add(protocol_name)

    # Build module imports
    module_imports = {}
    for qualified_name in all_qualified_names:
        parts = qualified_name.split(".")

        # Find the part that ends with _capnp
        capnp_module_idx = None
        for i, part in enumerate(parts):
            if part.endswith("_capnp"):
                capnp_module_idx = i
                break

        if capnp_module_idx is None:
            continue

        capnp_module_name = parts[capnp_module_idx]
        output_base_name = os.path.basename(os.path.abspath(output_dir))

        # Build the from path
        if capnp_module_idx == 0:
            from_path = output_base_name
        else:
            subpath = ".".join(parts[:capnp_module_idx])
            from_path = f"{output_base_name}.{subpath}"

        module_imports[capnp_module_name] = from_path

    # Build import lines
    import_lines = [
        "",
        "# Generated imports for project-specific types",
    ]
    for capnp_module_name in sorted(module_imports.keys()):
        from_path = module_imports[capnp_module_name]
        import_lines.append(f"from {from_path} import {capnp_module_name}  # type: ignore[import-not-found]")

    # Insert the imports after the existing imports
    lines[import_end_idx:import_end_idx] = import_lines

    return module_imports


def _augment_capnp_pyi(
    capnp_pyi_path: str,
    output_dir: str,
    interfaces: dict[str, tuple[str, list[str]]],
    module_imports: dict[str, str],
) -> None:
    """Augment _CapabilityClient.cast_as method with interface-specific overloads.

    Args:
        capnp_pyi_path: Path to the lib/capnp.pyi file.
        output_dir: Output directory for calculating relative imports.
        interfaces: Dictionary mapping interface names to (client_name, base_client_names).
        module_imports: Dictionary mapping module names to import paths.
    """
    # Read the file again (after imports were added)
    with open(capnp_pyi_path, encoding="utf8") as f:
        original_content = f.read()

    lines = original_content.split("\n")

    # Now find _CapabilityClient class and its cast_as method
    cast_as_line_idx = None
    in_castable_bootstrap = False

    for i, line in enumerate(lines):
        if "class _CapabilityClient" in line:
            in_castable_bootstrap = True
        elif in_castable_bootstrap and "def cast_as(self, schema:" in line:
            cast_as_line_idx = i
            break
        elif in_castable_bootstrap and line.strip().startswith("class ") and "_CapabilityClient" not in line:
            # Found another class, stop looking
            break

    if cast_as_line_idx is None:
        logger.warning("Could not find cast_as method in _CapabilityClient class, skipping augmentation.")
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
        overload_lines.append(f"    def cast_as(self, schema: {qualified_interface}) -> {qualified_client}: ...")

    # Add a catchall overload that matches the original function definition
    overload_lines.append("    @overload")
    overload_lines.append(
        "    def cast_as(self, schema: _InterfaceSchema | _InterfaceModule) -> _DynamicCapabilityClient: ..."
    )

    # Insert overloads before the original cast_as method
    lines[cast_as_line_idx:cast_as_line_idx] = overload_lines

    # Write back
    augmented_content = "\n".join(lines)
    with open(capnp_pyi_path, "w", encoding="utf8") as f:
        f.write(augmented_content)

    logger.info(f"Augmented {capnp_pyi_path} with {len(interfaces)} cast_as overload(s).")


def _augment_dynamic_object_reader(
    capnp_pyi_path: str,
    output_dir: str,
    struct_types: list[tuple[str, str]],
    interface_types: list[tuple[str, str]],
    module_imports: dict[str, str],
    interfaces: dict[str, tuple[str, list[str]]],
) -> None:
    """Augment _DynamicObjectReader class in lib/capnp.pyi with as_struct/as_interface overloads.

    Args:
        capnp_pyi_path: Path to the lib/capnp.pyi file to augment.
        output_dir: Output directory for calculating relative imports.
        struct_types: List of (protocol_name, reader_type) tuples.
        interface_types: List of (protocol_name, client_type) tuples.
        module_imports: Dictionary mapping module names to import paths.
        interfaces: Full interfaces dict for inheritance-based sorting.
    """
    if not struct_types and not interface_types:
        logger.info("No _DynamicObjectReader types to augment.")
        return

    # Read the file
    with open(capnp_pyi_path, encoding="utf8") as f:
        original_content = f.read()

    lines = original_content.split("\n")

    # Find the _DynamicObjectReader class and its as_struct/as_interface methods
    # We need to find the ORIGINAL method definitions (not any existing overloads)
    # And we need to insert BEFORE the method definition, accounting for decorators
    dynamic_reader_idx = None
    as_struct_insert_idx = None
    as_interface_insert_idx = None

    in_dynamic_reader = False
    for i, line in enumerate(lines):
        if "class _DynamicObjectReader" in line:
            dynamic_reader_idx = i
            in_dynamic_reader = True
        elif in_dynamic_reader:
            # Skip @overload decorators - we want the actual implementation
            if line.strip().startswith("@overload"):
                continue
            # Look for the actual method definitions (not overloads)
            if "def as_interface" in line and as_interface_insert_idx is None and "schema:" in line:
                # This is the original implementation (has schema parameter)
                # Find the start of this method definition (skip back over any decorators/empty lines)
                insert_at = i
                # Look backwards to find where to insert (before any decorators)
                if dynamic_reader_idx is not None:
                    for j in range(i - 1, dynamic_reader_idx, -1):
                        prev_line = lines[j].strip()
                        if prev_line.startswith("@") or prev_line == "":
                            insert_at = j
                        else:
                            break
                as_interface_insert_idx = insert_at
            elif "def as_struct" in line and as_struct_insert_idx is None and "schema:" in line:
                # This is the original implementation (has schema parameter)
                insert_at = i
                # Look backwards to find where to insert (before any decorators)
                if dynamic_reader_idx is not None:
                    for j in range(i - 1, dynamic_reader_idx, -1):
                        prev_line = lines[j].strip()
                        if prev_line.startswith("@") or prev_line == "":
                            insert_at = j
                        else:
                            break
                as_struct_insert_idx = insert_at
            elif line.strip().startswith("class ") and "_DynamicObjectReader" not in line:
                # Found another class, stop looking
                break

    if dynamic_reader_idx is None:
        logger.warning("Could not find _DynamicObjectReader class in lib/capnp.pyi, skipping augmentation.")
        return

    if as_struct_insert_idx is None or as_interface_insert_idx is None:
        logger.warning(
            f"Could not find as_struct/as_interface methods in _DynamicObjectReader (as_struct={as_struct_insert_idx}, as_interface={as_interface_insert_idx}), skipping augmentation."
        )
        return

    # Build overloads for as_struct (insert before the existing as_struct method)
    # Sort struct types by inheritance/specificity (same heuristic as interfaces)
    # Build a pseudo-inheritance structure based on nesting
    # More dots = more nested = more specific = higher "depth"
    struct_overloads = []

    # Sort structs: prioritize by depth (more nested first), then alphabetically
    # This matches the interface sorting pattern where more specific types come first
    sorted_struct_types = sorted(
        struct_types,
        key=lambda x: (-x[0].count("."), x[0]),  # Most dots first, then alphabetical
    )

    for protocol_name, reader_type in sorted_struct_types:
        # Extract module-relative names (remove extra path prefixes)
        # From "test_augment.generic_interface_capnp._MyStructModule"
        # Get "generic_interface_capnp._MyStructModule"
        param_parts = protocol_name.split(".")
        # Find the _capnp module
        capnp_idx = None
        for i, part in enumerate(param_parts):
            if part.endswith("_capnp"):
                capnp_idx = i
                break
        if capnp_idx is not None:
            clean_param = ".".join(param_parts[capnp_idx:])
        else:
            clean_param = protocol_name

        # For return type, use the flat type alias pattern
        # Top-level type aliases are generated as flat names at module level
        # From "generic_interface_capnp._MyStructModule.Reader" build "generic_interface_capnp.MyStructReader"
        # From "management_capnp._ParamsModule._AutomaticSowingModule._AvgSoilTempModule.Reader"
        # build "management_capnp.AvgSoilTempReader" (just the innermost struct)
        return_parts = reader_type.split(".")
        capnp_idx = None
        for i, part in enumerate(return_parts):
            if part.endswith("_capnp"):
                capnp_idx = i
                break
        if capnp_idx is not None and len(return_parts) >= capnp_idx + 3:
            # return_parts might be ["management_capnp", "_ParamsModule", "_AutomaticSowingModule", "_AvgSoilTempModule", "Reader"]
            module_name = return_parts[capnp_idx]  # "management_capnp"
            reader_builder = return_parts[-1]  # "Reader" or "Builder"

            # Get the last module part (the actual struct we're returning)
            last_module = return_parts[-2]  # "_AvgSoilTempModule"

            # Convert _XxxModule to Xxx
            if last_module.startswith("_") and last_module.endswith("Module"):
                struct_name = last_module[1:-6]  # "AvgSoilTemp"
                alias_name = f"{struct_name}{reader_builder}"  # "AvgSoilTempReader"
                clean_return = f"{module_name}.{alias_name}"
            else:
                # Fallback to full path
                clean_return = ".".join(return_parts[capnp_idx:])
        else:
            clean_return = reader_type

        struct_overloads.append("    @overload")
        struct_overloads.append(f"    def as_struct(self, schema: {clean_param}) -> {clean_return}: ...")

    # Add catchall overload for as_struct
    struct_overloads.append("    @overload")
    struct_overloads.append(
        "    def as_struct(self, schema: _StructSchema | _StructModule) -> _DynamicStructReader: ..."
    )

    # Build overloads for as_interface (insert before the existing as_interface method)
    # Sort interface types by inheritance depth (most derived first) - same as cast_as
    # Build a mapping from protocol_name to full interface data
    interface_map = {}
    for protocol_name, client_type in interface_types:
        # Find matching entry in interfaces dict
        # protocol_name might be like "persistent_capnp._PersistentModule"
        # interfaces keys are like "persistent_capnp._PersistentModule"
        if protocol_name in interfaces:
            interface_map[protocol_name] = interfaces[protocol_name]

    # Sort using the same function as cast_as
    if interface_map:
        sorted_interface_names = _sort_interfaces_by_inheritance(interface_map)
        # Build the sorted list
        sorted_interface_types = []
        for iface_name, _ in sorted_interface_names:
            # Find the corresponding entry in interface_types
            for proto, client in interface_types:
                if proto == iface_name:
                    sorted_interface_types.append((proto, client))
                    break
    else:
        # Fallback to path depth sorting if no inheritance info
        sorted_interface_types = sorted(interface_types, key=lambda x: (-x[0].count("."), x[0]))

    interface_overloads = []
    for protocol_name, client_type in sorted_interface_types:
        # Extract module-relative names
        param_parts = protocol_name.split(".")
        capnp_idx = None
        for i, part in enumerate(param_parts):
            if part.endswith("_capnp"):
                capnp_idx = i
                break
        if capnp_idx is not None:
            clean_param = ".".join(param_parts[capnp_idx:])
        else:
            clean_param = protocol_name

        # For return type, use the type alias pattern
        # From "_GenericGetterModule.GenericGetterClient" build "GenericGetterClient"
        # From "generic_interface_capnp._GenericGetterModule.GenericGetterClient" build "generic_interface_capnp.GenericGetterClient"
        return_parts = client_type.split(".")
        capnp_idx = None
        for i, part in enumerate(return_parts):
            if part.endswith("_capnp"):
                capnp_idx = i
                break
        if capnp_idx is not None and len(return_parts) >= capnp_idx + 2:
            module_name = return_parts[capnp_idx]  # "generic_interface_capnp"
            client_name = return_parts[-1]  # "GenericGetterClient"
            # The type alias is just the client name at module level
            clean_return = f"{module_name}.{client_name}"
        else:
            clean_return = client_type

        interface_overloads.append("    @overload")
        interface_overloads.append(f"    def as_interface(self, schema: {clean_param}) -> {clean_return}: ...")

    # Add catchall overload for as_interface
    interface_overloads.append("    @overload")
    interface_overloads.append(
        "    def as_interface(self, schema: _InterfaceSchema | _InterfaceModule) -> _DynamicCapabilityClient: ..."
    )

    # Insert overloads - ensure proper ordering
    # We want: interface overloads before as_interface, struct overloads before as_struct
    # Since as_interface comes before as_struct in the file, insert as_interface first

    # Insert interface overloads BEFORE the def as_interface line
    if interface_overloads and as_interface_insert_idx is not None:
        lines[as_interface_insert_idx:as_interface_insert_idx] = interface_overloads
        # Adjust as_struct_insert_idx since we inserted lines before it
        if as_struct_insert_idx is not None and as_struct_insert_idx > as_interface_insert_idx:
            as_struct_insert_idx += len(interface_overloads)

    # Insert struct overloads BEFORE the def as_struct line
    if struct_overloads and as_struct_insert_idx is not None:
        lines[as_struct_insert_idx:as_struct_insert_idx] = struct_overloads

    # Write back
    augmented_content = "\n".join(lines)
    with open(capnp_pyi_path, "w", encoding="utf8") as f:
        f.write(augmented_content)

    total_overloads = len(struct_overloads) + len(interface_overloads)
    logger.info(f"Augmented _DynamicObjectReader in {capnp_pyi_path} with {total_overloads // 2} overload(s).")


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

            # Run ruff format with very large line length (320 is max) to prevent wrapping
            # This keeps pyright ignore comments on the correct lines
            subprocess.run(
                ["ruff", "format", "--line-length", "320", str(temp_path)],
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
    module: capnp.lib.capnp._CapnpModuleType,
    module_registry: ModuleRegistryType,
    output_file_path: str,
    output_directory: str | None = None,
    import_paths: list[str] | None = None,
    module_path_prefix: str | None = None,
) -> tuple[dict[str, tuple[str, list[str]]], tuple[list[tuple[str, str]], list[tuple[str, str]]]]:
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

    # Get _DynamicObjectReader types for augmentation tracking
    struct_types, interface_types = writer.get_dynamic_object_reader_types()

    # Qualify the types with module prefix
    qualified_struct_types = [
        (f"{full_module_name}.{proto}", f"{full_module_name}.{reader}") for proto, reader in struct_types
    ]
    qualified_interface_types = [
        (f"{full_module_name}.{proto}", f"{full_module_name}.{client}") for proto, client in interface_types
    ]

    return interfaces_with_module, (qualified_struct_types, qualified_interface_types)


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

    # Determine the common base path for preserving directory structure
    common_base = _determine_output_directory_structure(
        output_dir,
        paths,
        valid_paths,
        root_directory,
    )

    # Track output directories for py.typed marker
    output_directories_used = set()

    # Collect all interfaces from all modules for cast_as overloads
    # Map of output_dir -> {interface_name: (client_name, base_client_names)}
    all_interfaces_by_dir: dict[str, dict[str, tuple[str, list[str]]]] = {}

    # Track all _DynamicObjectReader types by output directory
    all_dynamic_object_types_by_dir: dict[str, dict[str, list[tuple[str, str]]]] = {}

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

        module_interfaces, dynamic_object_types = generate_stubs(
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

        # Collect _DynamicObjectReader types for this output directory
        struct_types, interface_types = dynamic_object_types
        if struct_types or interface_types:
            if output_directory not in all_dynamic_object_types_by_dir:
                all_dynamic_object_types_by_dir[output_directory] = {"structs": [], "interfaces": []}
            all_dynamic_object_types_by_dir[output_directory]["structs"].extend(struct_types)
            all_dynamic_object_types_by_dir[output_directory]["interfaces"].extend(interface_types)

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

            # Combine all _DynamicObjectReader types from all directories
            all_dynamic_object_types = {"structs": [], "interfaces": []}
            for types_dict in all_dynamic_object_types_by_dir.values():
                all_dynamic_object_types["structs"].extend(types_dict["structs"])
                all_dynamic_object_types["interfaces"].extend(types_dict["interfaces"])

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
                source_stubs_path, augmented_stubs_dir, actual_output_dir, all_interfaces, all_dynamic_object_types
            )
        else:
            logger.warning("--augment-capnp-stubs specified but capnp-stubs package not found in sys.path")

    # Validate generated stubs with pyright (unless disabled)
    if not skip_pyright:
        validate_with_pyright(output_directories_used)


# ===== Directory Structure Helper Functions =====


def _all_files_in_directory(valid_paths: set[str], directory: str) -> bool:
    """Check if all files are directly in the given directory.

    Args:
        valid_paths: Set of file paths to check
        directory: Directory to check against

    Returns:
        True if all files (sampled) are in the directory, False otherwise
    """
    # Sample check (avoid checking thousands of files)
    for path in list(valid_paths)[:10]:
        abs_path = os.path.abspath(path)
        file_dir = os.path.dirname(abs_path)
        if file_dir != directory:
            return False
    return True


def _should_preserve_parent_directory(
    common_base: str,
    relative_bases: list[str],
    valid_paths: set[str],
) -> bool:
    """Determine if parent directory name should be preserved in output.

    Args:
        common_base: The common base directory
        relative_bases: Relative path bases for depth calculation
        valid_paths: Set of valid file paths

    Returns:
        True if parent directory should be preserved
    """
    if not relative_bases:
        return False

    # Check depth - only preserve if depth >= 2
    sample_relative = relative_bases[0]
    depth = sample_relative.count(os.sep)

    if depth < 2:
        return False

    # Verify files are in the base directory
    return _all_files_in_directory(valid_paths, common_base)


def _fallback_common_base(valid_paths: set[str]) -> str | None:
    """Calculate common base from file paths when no pattern bases found.

    Args:
        valid_paths: Set of valid file paths

    Returns:
        Common base directory or None
    """
    if not valid_paths:
        return None

    abs_paths = [os.path.abspath(p) for p in valid_paths]
    if len(abs_paths) == 1:
        return os.path.dirname(abs_paths[0])

    common = os.path.commonpath(abs_paths)
    return os.path.dirname(common) if os.path.isfile(common) else common


def _handle_single_pattern_base(
    base: str,
    relative_bases: list[str],
    paths: list[str],
    valid_paths: set[str],
) -> str:
    """Handle case where there's only one pattern base directory.

    Args:
        base: The single pattern base directory
        relative_bases: Relative path bases
        paths: Original search patterns
        valid_paths: Set of valid file paths

    Returns:
        The base directory to use
    """
    # Check if we should preserve subdirectory structure
    if not relative_bases or not paths:
        return base

    original_pattern = paths[0]

    # Only preserve structure for recursive globs (**) with depth >= 2
    if "**" not in original_pattern:
        return base

    sample_relative = relative_bases[0]
    depth = sample_relative.count(os.sep)

    if depth < 2:
        return base

    # Verify files are actually in this directory
    if _all_files_in_directory(valid_paths, base):
        return os.path.dirname(base)

    return base


def _handle_multiple_pattern_bases(
    absolute_bases: list[str],
    relative_bases: list[str],
    valid_paths: set[str],
) -> str:
    """Handle case where there are multiple pattern base directories.

    Args:
        absolute_bases: Absolute pattern base directories
        relative_bases: Relative path bases
        valid_paths: Set of valid file paths

    Returns:
        The common base directory to use
    """
    common_base = os.path.commonpath(absolute_bases)

    # If all bases are identical, check if we should go up one level
    if all(base == absolute_bases[0] for base in absolute_bases):
        if _should_preserve_parent_directory(
            common_base,
            relative_bases,
            valid_paths,
        ):
            return os.path.dirname(common_base)

    return common_base


def _calculate_common_base(
    absolute_bases: list[str],
    relative_bases: list[str],
    paths: list[str],
    valid_paths: set[str],
) -> str | None:
    """Calculate common base directory from pattern bases.

    Args:
        absolute_bases: Absolute paths to pattern base directories
        relative_bases: Relative paths (for depth calculation)
        paths: Original search patterns
        valid_paths: Set of valid file paths found

    Returns:
        Common base directory path, or None if not applicable
    """
    if not absolute_bases:
        return _fallback_common_base(valid_paths)

    if len(absolute_bases) == 1:
        return _handle_single_pattern_base(
            absolute_bases[0],
            relative_bases,
            paths,
            valid_paths,
        )

    return _handle_multiple_pattern_bases(
        absolute_bases,
        relative_bases,
        valid_paths,
    )


def _extract_pattern_bases(
    paths: list[str],
    root_directory: str,
) -> tuple[list[str], list[str]]:
    """Extract base directories from search patterns.

    Args:
        paths: List of search patterns (may be absolute or relative)
        root_directory: The root directory for resolving relative paths

    Returns:
        Tuple of (absolute_bases, relative_bases)
        - absolute_bases: Absolute path to each pattern's base directory
        - relative_bases: Relative path (for depth calculation)
    """
    absolute_bases = []
    relative_bases = []

    for pattern in paths:
        # Extract base from pattern (the directory before wildcards)
        base = extract_base_from_pattern(pattern)
        if not base:
            continue

        # Convert to absolute path
        if not os.path.isabs(pattern):
            abs_pattern = os.path.join(root_directory, pattern)
        else:
            abs_pattern = pattern

        abs_base = extract_base_from_pattern(abs_pattern)
        if not os.path.isabs(abs_base):
            abs_base = os.path.join(root_directory, abs_base)
        absolute_bases.append(abs_base)

        # Track relative version for depth calculation
        try:
            if os.path.isabs(pattern):
                rel_pattern = os.path.relpath(pattern, root_directory)
                if not rel_pattern.startswith(".."):
                    rel_base = extract_base_from_pattern(rel_pattern)
                    if rel_base:
                        relative_bases.append(rel_base)
            else:
                relative_bases.append(base)
        except ValueError:
            # Paths on different drives (Windows)
            pass

    return absolute_bases, relative_bases


def _determine_output_directory_structure(
    output_dir: str,
    paths: list[str],
    valid_paths: set[str],
    root_directory: str,
) -> str | None:
    """Determine the base path for preserving directory structure in output.

    This function analyzes the input patterns and found files to decide
    how to preserve directory structure when writing to output_dir.

    Args:
        output_dir: The output directory specified by user
        paths: List of search patterns
        valid_paths: Set of valid .capnp files found
        root_directory: The root directory for resolving relative paths

    Returns:
        Common base directory to use for calculating relative paths,
        or None if directory structure should not be preserved.

    Examples:
        # Single pattern: tests/schemas/basic/*.capnp
        # Output: tests/schemas/basic/ (preserve "basic" in output)

        # Multiple patterns from different subdirs
        # Output: tests/schemas/ (common parent)

        # Recursive glob: tests/schemas/**/*.capnp
        # Output: tests/schemas/ (preserve full structure)
    """
    if not output_dir or not paths:
        return None

    # Step 1: Extract base directories from patterns
    absolute_bases, relative_bases = _extract_pattern_bases(paths, root_directory)

    # Step 2: Calculate common base directory
    common_base = _calculate_common_base(
        absolute_bases,
        relative_bases,
        paths,
        valid_paths,
    )

    return common_base
