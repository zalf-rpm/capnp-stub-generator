"""Top-level module for stub generation."""

from __future__ import annotations

import contextlib
import glob
import logging
import os.path
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import TYPE_CHECKING

import capnp

from capnp_stub_generator.writer import Writer

if TYPE_CHECKING:
    import argparse
    from collections.abc import Set as AbstractSet

    from capnp.lib.capnp import _Schema

if hasattr(capnp, "remove_import_hook"):
    capnp.remove_import_hook()


logger = logging.getLogger(__name__)

PYI_SUFFIX = ".pyi"
PY_SUFFIX = ".py"


class PyrightValidationError(Exception):
    """Raised when pyright validation finds type errors in generated stubs."""


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
) -> tuple[str, str | None] | None:
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

    Returns:
        Tuple of (capnp-stubs path, schema_capnp path or None) that were copied/augmented,
        or None if lib/capnp.pyi could not be found.

    """
    # Create destination path for augmented stubs
    dest_stubs_path = os.path.join(augmented_stubs_dir, "capnp-stubs")

    # Copy the entire capnp-stubs directory
    if os.path.exists(dest_stubs_path):
        shutil.rmtree(dest_stubs_path)
    shutil.copytree(source_stubs_path, dest_stubs_path)
    logger.info(f"Copied capnp-stubs to: {dest_stubs_path}")

    # Fix schema_capnp imports to be absolute instead of relative
    capnp_pyi_path = os.path.join(dest_stubs_path, "lib", "capnp.pyi")
    if os.path.exists(capnp_pyi_path):
        with open(capnp_pyi_path, encoding="utf8") as f:
            content = f.read()

        # Replace relative imports with absolute imports
        # from ...schema_capnp.schema_capnp -> from schema_capnp.schema_capnp
        content = content.replace("from ...schema_capnp import", "from schema_capnp import")

        with open(capnp_pyi_path, "w", encoding="utf8") as f:
            f.write(content)

        logger.info("Fixed schema_capnp imports to be absolute")

    # Copy the schema_capnp directory if it exists (sibling to source_stubs_path)
    source_schema_path = os.path.join(os.path.dirname(source_stubs_path), "schema_capnp")
    dest_schema_path = os.path.join(augmented_stubs_dir, "schema_capnp")

    if os.path.isdir(source_schema_path):
        if os.path.exists(dest_schema_path):
            shutil.rmtree(dest_schema_path)
        shutil.copytree(source_schema_path, dest_schema_path)
        logger.info(f"Copied schema stubs to: {dest_schema_path}")
    else:
        logger.warning(f"Schema stubs not found at: {source_schema_path}")
        dest_schema_path = None

    if not interfaces and not dynamic_object_types.get("structs") and not dynamic_object_types.get("interfaces"):
        logger.info("No interfaces or _DynamicObjectReader types found, skipping capnp-stubs augmentation.")
        return dest_stubs_path, dest_schema_path

    # Path to lib/capnp.pyi
    capnp_pyi_path = os.path.join(dest_stubs_path, "lib", "capnp.pyi")

    if not os.path.exists(capnp_pyi_path):
        logger.warning(f"Could not find lib/capnp.pyi at {capnp_pyi_path}, skipping augmentation.")
        return None

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
        return dest_stubs_path, dest_schema_path

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
    list_types = dynamic_object_types.get("lists", [])
    interface_types = dynamic_object_types.get("interfaces", [])
    if struct_types or list_types or interface_types:
        _augment_dynamic_object_reader(
            capnp_pyi_path,
            output_dir,
            struct_types,
            list_types,
            interface_types,
            module_imports,
            interfaces,
        )

    # Return the paths to the bundled stubs that were copied
    return dest_stubs_path, dest_schema_path


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
        if stripped.startswith(("import ", "from ")):
            continue

        # Empty lines or comments between imports - continue
        if not stripped or stripped.startswith("#"):
            continue

        # We've found the first non-import line
        import_end_idx = i
        break

    # Collect all module names from interfaces and dynamic object types
    all_qualified_names: AbstractSet[str] = set()

    # From interfaces
    for interface_name in interfaces:
        all_qualified_names.add(interface_name)

    # From struct types
    for protocol_name, _ in dynamic_object_types.get("structs", []):
        all_qualified_names.add(protocol_name)

    # From interface types
    for protocol_name, _ in dynamic_object_types.get("interfaces", []):
        all_qualified_names.add(protocol_name)

    # Build module imports
    module_imports: dict[str, str] = {}
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

        # Check if next part is the same name (package.module pattern like schema_capnp.schema_capnp)
        # In this case, we need to import from the package
        if capnp_module_idx + 1 < len(parts) and parts[capnp_module_idx + 1] == capnp_module_name:
            # This is a package with a submodule of same name (e.g., schema_capnp.schema_capnp)
            # Import as: from schema_capnp import schema_capnp
            from_path = capnp_module_name if capnp_module_idx == 0 else ".".join(parts[: capnp_module_idx + 1])
        # Normal module
        # Build the from path - use the module annotation if present (parts before _capnp)
        # For "mas.schema.climate.climate_capnp._ClimateSensorInterfaceModule"
        # -> from_path = "mas.schema.climate"
        # For "basic.advanced_features_capnp._TestIfaceInterfaceModule"
        # -> from_path = "basic"
        # For "climate_capnp._ClimateSensorInterfaceModule" (no annotation)
        # -> from_path = "" (direct import)
        elif capnp_module_idx == 0:
            from_path = ""  # No prefix, direct import
        else:
            from_path = ".".join(parts[:capnp_module_idx])

        # Only update if we don't have an entry yet, or if new from_path is more specific (non-empty)
        if capnp_module_name not in module_imports or (from_path and not module_imports[capnp_module_name]):
            module_imports[capnp_module_name] = from_path

    # Build import lines
    import_lines = [
        "",
        "# Generated imports for project-specific types",
    ]

    # Standard library capnp modules that should be imported from capnp package
    capnp_stdlib_modules = {
        "persistent_capnp",
        "schema_capnp",
        "c++_capnp",
        "c_capnp",
        "java_capnp",
        "go_capnp",
        "python_capnp",
        "json_capnp",
        "compat_capnp",
    }

    for capnp_module_name in sorted(module_imports.keys()):
        from_path = module_imports[capnp_module_name]

        # Check if this is a standard library module (no path prefix)
        if not from_path and capnp_module_name in capnp_stdlib_modules:
            # Import from capnp package using import...as syntax for pyright compatibility
            import_lines.append(f"import capnp.{capnp_module_name} as {capnp_module_name}")
        # Use "from X import Y" style when we have a module path
        # e.g., "from mas.schema.climate import climate_capnp"
        # Or direct import when no path: "import climate_capnp"
        elif from_path:
            import_lines.append(f"from {from_path} import {capnp_module_name}")
        else:
            import_lines.append(f"import {capnp_module_name}")

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
    overload_lines: list[str] = []

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
            f"    def cast_as(self, schema: {qualified_interface}) -> {qualified_client}: ...  # type: ignore[reportOverlappingOverload]",
        )

    # Add a catchall overload that matches the original function definition
    overload_lines.append("    @overload")
    overload_lines.append(
        "    def cast_as(self, schema: _InterfaceSchema | _InterfaceModule) -> _DynamicCapabilityClient: ...  # type: ignore[reportOverlappingOverload]",
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
    list_types: list[tuple[str, str]],
    interface_types: list[tuple[str, str]],
    module_imports: dict[str, str],
    interfaces: dict[str, tuple[str, list[str]]],
) -> None:
    """Augment _DynamicObjectReader class in lib/capnp.pyi with as_struct/as_list/as_interface overloads.

    Args:
        capnp_pyi_path: Path to the lib/capnp.pyi file to augment.
        output_dir: Output directory for calculating relative imports.
        struct_types: List of (protocol_name, reader_type) tuples for structs.
        list_types: List of (list_class, reader_type) tuples for lists.
        interface_types: List of (protocol_name, client_type) tuples for interfaces.
        module_imports: Dictionary mapping module names to import paths.
        interfaces: Full interfaces dict for inheritance-based sorting.

    """
    logger.info(
        f"Augmenting _DynamicObjectReader with {len(struct_types)} structs, {len(list_types)} lists, {len(interface_types)} interfaces",
    )

    if not struct_types and not list_types and not interface_types:
        logger.info("No _DynamicObjectReader types to augment.")
        return

    # Read the file
    with open(capnp_pyi_path, encoding="utf8") as f:
        original_content = f.read()

    lines = original_content.split("\n")

    # Find the _DynamicObjectReader class and its methods
    dynamic_reader_idx = None
    as_struct_insert_idx = None
    as_list_insert_idx = None
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
                insert_at = i
                if dynamic_reader_idx is not None:
                    for j in range(i - 1, dynamic_reader_idx, -1):
                        prev_line = lines[j].strip()
                        if prev_line.startswith("@") or prev_line == "":
                            insert_at = j
                        else:
                            break
                as_interface_insert_idx = insert_at
            elif "def as_struct" in line and as_struct_insert_idx is None and "schema:" in line:
                insert_at = i
                if dynamic_reader_idx is not None:
                    for j in range(i - 1, dynamic_reader_idx, -1):
                        prev_line = lines[j].strip()
                        if prev_line.startswith("@") or prev_line == "":
                            insert_at = j
                        else:
                            break
                as_struct_insert_idx = insert_at
            elif "def as_list" in line and as_list_insert_idx is None and "schema:" in line:
                insert_at = i
                if dynamic_reader_idx is not None:
                    for j in range(i - 1, dynamic_reader_idx, -1):
                        prev_line = lines[j].strip()
                        if prev_line.startswith("@") or prev_line == "":
                            insert_at = j
                        else:
                            break
                as_list_insert_idx = insert_at
            elif line.strip().startswith("class ") and "_DynamicObjectReader" not in line:
                # Found another class, stop looking
                break

    if dynamic_reader_idx is None:
        logger.warning("Could not find _DynamicObjectReader class in lib/capnp.pyi, skipping augmentation.")
        return

    # We need at least as_struct and as_interface (as_list might not exist in older stubs)
    if as_struct_insert_idx is None or as_interface_insert_idx is None:
        logger.warning(
            f"Could not find as_struct/as_interface methods in _DynamicObjectReader (as_struct={as_struct_insert_idx}, as_interface={as_interface_insert_idx}), skipping augmentation.",
        )
        return

    # Build overloads for as_struct (insert before the existing as_struct method)
    # Sort struct types: more specific (nested) first
    # Protocol path with more dots = more nested = more specific
    sorted_struct_types = sorted(
        struct_types,
        key=lambda x: (-x[0].count("."), x[0]),  # Most nested first, then alphabetical
    )

    struct_overloads: list[str] = []
    for protocol_name, type_alias in sorted_struct_types:
        # protocol_name is like "examples.restorer.restorer_capnp._RestorerStructModule"
        # type_alias is like "examples.restorer.restorer_capnp.RestorerReader"

        # Extract just the _capnp module part and after (remove path prefixes)
        protocol_parts = protocol_name.split(".")
        alias_parts = type_alias.split(".")

        # Find _capnp module in both
        protocol_capnp_idx = None
        alias_capnp_idx = None

        for i, part in enumerate(protocol_parts):
            if part.endswith("_capnp"):
                protocol_capnp_idx = i
                break
        for i, part in enumerate(alias_parts):
            if part.endswith("_capnp"):
                alias_capnp_idx = i
                break

        # Build the clean names starting from _capnp module
        # But if the next part is the same (package.module pattern), include both
        if protocol_capnp_idx is not None:
            # Check for package.module pattern (e.g., schema_capnp.schema_capnp)
            if (
                protocol_capnp_idx + 1 < len(protocol_parts)
                and protocol_parts[protocol_capnp_idx] == protocol_parts[protocol_capnp_idx + 1]
            ):
                # Keep both parts for package.module pattern
                clean_protocol = ".".join(protocol_parts[protocol_capnp_idx:])
            else:
                clean_protocol = ".".join(protocol_parts[protocol_capnp_idx:])
        else:
            clean_protocol = protocol_name

        if alias_capnp_idx is not None:
            # Check for package.module pattern in alias too
            if (
                alias_capnp_idx + 1 < len(alias_parts)
                and alias_parts[alias_capnp_idx] == alias_parts[alias_capnp_idx + 1]
            ):
                clean_alias = ".".join(alias_parts[alias_capnp_idx:])
            else:
                clean_alias = ".".join(alias_parts[alias_capnp_idx:])
        else:
            clean_alias = type_alias

        struct_overloads.append("    @overload")
        struct_overloads.append(
            f"    def as_struct(self, schema: {clean_protocol}) -> {clean_alias}: ...  # type: ignore[reportOverlappingOverload]",
        )

    # Add catchall overload for as_struct
    struct_overloads.append("    @overload")
    struct_overloads.append(
        "    def as_struct(self, schema: _StructSchema | _StructModule) -> _DynamicStructReader: ...  # type: ignore[reportOverlappingOverload]",
    )

    # Build overloads for as_list
    # Sort: more nested (specific) first
    sorted_list_types = sorted(
        list_types,
        key=lambda x: (-x[0].count("."), x[0]),  # Most nested first
    )

    list_overloads: list[str] = []
    for list_class, type_alias in sorted_list_types:
        # list_class: "examples.dummy.dummy_capnp._BoolList"
        # type_alias: "examples.dummy.dummy_capnp.BoolListReader"

        # Extract just the _capnp module part and after
        list_parts = list_class.split(".")
        alias_parts = type_alias.split(".")

        list_capnp_idx = None
        alias_capnp_idx = None

        for i, part in enumerate(list_parts):
            if part.endswith("_capnp"):
                list_capnp_idx = i
                break
        for i, part in enumerate(alias_parts):
            if part.endswith("_capnp"):
                alias_capnp_idx = i
                break

        clean_list = ".".join(list_parts[list_capnp_idx:]) if list_capnp_idx is not None else list_class

        clean_alias = ".".join(alias_parts[alias_capnp_idx:]) if alias_capnp_idx is not None else type_alias

        list_overloads.append("    @overload")
        list_overloads.append(
            f"    def as_list(self, schema: type[{clean_list}]) -> {clean_alias}: ...  # type: ignore[reportOverlappingOverload]",
        )

    # Add catchall overload for as_list
    if list_overloads:  # Only add if we have list overloads
        list_overloads.append("    @overload")
        list_overloads.append(
            "    def as_list(self, schema: type) -> _DynamicListReader: ...  # type: ignore[reportOverlappingOverload]",
        )

    # Build overloads for as_interface
    # Sort by actual inheritance: most derived (specific) first
    # Use the same sorting as cast_as which has inheritance info

    if interfaces:
        # Build a map of interface types we have
        interface_type_map = dict(interface_types)

        # Use inheritance-based sorting from _sort_interfaces_by_inheritance
        # This returns (interface_name, client_name) sorted by inheritance depth
        sorted_by_inheritance = _sort_interfaces_by_inheritance(interfaces)

        # Build the sorted list, only including types we actually have overloads for
        sorted_interface_types: list[tuple[str, str]] = []
        for iface_name, _ in sorted_by_inheritance:
            if iface_name in interface_type_map:
                sorted_interface_types.append((iface_name, interface_type_map[iface_name]))

        # Add any remaining types that weren't in the interfaces dict (shouldn't happen but safety check)
        seen = {proto for proto, _ in sorted_interface_types}
        for proto, client in interface_types:
            if proto not in seen:
                sorted_interface_types.append((proto, client))
    else:
        # Fallback: sort by nesting depth
        sorted_interface_types = sorted(
            interface_types,
            key=lambda x: (-x[0].count("."), x[0]),
        )

    interface_overloads: list[str] = []
    for protocol_name, type_alias in sorted_interface_types:
        # protocol_name: "examples.calculator.calculator_capnp._CalculatorInterfaceModule"
        # type_alias: "examples.calculator.calculator_capnp.CalculatorClient"

        # Extract just the _capnp module part and after
        protocol_parts = protocol_name.split(".")
        alias_parts = type_alias.split(".")

        protocol_capnp_idx = None
        alias_capnp_idx = None

        for i, part in enumerate(protocol_parts):
            if part.endswith("_capnp"):
                protocol_capnp_idx = i
                break
        for i, part in enumerate(alias_parts):
            if part.endswith("_capnp"):
                alias_capnp_idx = i
                break

        if protocol_capnp_idx is not None:
            clean_protocol = ".".join(protocol_parts[protocol_capnp_idx:])
        else:
            clean_protocol = protocol_name

        clean_alias = ".".join(alias_parts[alias_capnp_idx:]) if alias_capnp_idx is not None else type_alias

        interface_overloads.append("    @overload")
        interface_overloads.append(
            f"    def as_interface(self, schema: {clean_protocol}) -> {clean_alias}: ...  # type: ignore[reportOverlappingOverload]",
        )

    # Add catchall overload for as_interface
    interface_overloads.append("    @overload")
    interface_overloads.append(
        "    def as_interface(self, schema: _InterfaceSchema | _InterfaceModule) -> _DynamicCapabilityClient: ...  # type: ignore[reportOverlappingOverload]",
    )

    # Insert overloads - ensure proper ordering
    # Order in file: as_interface, as_list, as_struct (typically)
    # Insert from last to first so indices don't shift

    # Insert struct overloads BEFORE the def as_struct line
    if struct_overloads and as_struct_insert_idx is not None:
        lines[as_struct_insert_idx:as_struct_insert_idx] = struct_overloads

    # Insert list overloads BEFORE the def as_list line (if it exists)
    if list_overloads and as_list_insert_idx is not None:
        # Adjust index if struct was inserted before list
        if as_struct_insert_idx is not None and as_struct_insert_idx < as_list_insert_idx:
            as_list_insert_idx += len(struct_overloads)
        lines[as_list_insert_idx:as_list_insert_idx] = list_overloads

    # Insert interface overloads BEFORE the def as_interface line
    if interface_overloads and as_interface_insert_idx is not None:
        # Adjust index if struct/list were inserted before interface
        if as_struct_insert_idx is not None and as_struct_insert_idx < as_interface_insert_idx:
            as_interface_insert_idx += len(struct_overloads)
        if as_list_insert_idx is not None and as_list_insert_idx < as_interface_insert_idx:
            as_interface_insert_idx += len(list_overloads)
        lines[as_interface_insert_idx:as_interface_insert_idx] = interface_overloads

    # Write back
    augmented_content = "\n".join(lines)
    with open(capnp_pyi_path, "w", encoding="utf8") as f:
        f.write(augmented_content)

    total_overloads = len(struct_overloads) + len(interface_overloads)
    logger.info(f"Augmented _DynamicObjectReader in {capnp_pyi_path} with {total_overloads // 2} overload(s).")


def format_all_outputs(output_directories: set[str]) -> None:
    """Format all generated stub files using ruff.

    Runs multiple passes to catch everything:
    1. ruff format (default settings)
    2. ruff check --fix --select ALL
    3. ruff format again

    Args:
        output_directories: Set of directories containing generated stubs.

    """
    # Collect all .py and .pyi files from output directories
    stub_files: list[str] = []
    for output_dir in output_directories:
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.endswith((".pyi", ".py")):
                    stub_files.append(os.path.join(root, file))

    if not stub_files:
        logger.warning("No files found to format")
        return

    logger.info(f"Formatting {len(stub_files)} generated file(s) with ruff...")

    try:
        # Pass 1: ruff format (default settings)
        logger.info("Pass 1: Running ruff format...")
        subprocess.run(
            ["ruff", "format", *stub_files],
            capture_output=True,
            text=True,
            check=True,
        )

        # Pass 2: ruff check --fix --select ALL
        logger.info("Pass 2: Running ruff check --fix --select ALL...")
        subprocess.run(
            ["ruff", "check", "--fix", "--select", "ALL", *stub_files],
            capture_output=True,
            text=True,
            check=False,  # Don't fail on unfixable issues
        )

        # Pass 3: ruff format again
        logger.info("Pass 3: Running ruff format again...")
        subprocess.run(
            ["ruff", "format", *stub_files],
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info("✓ Ruff formatting completed successfully")

    except FileNotFoundError:
        logger.exception("ruff not found. Please install ruff: pip install ruff")
    except subprocess.CalledProcessError as e:
        logger.exception(f"Ruff formatting failed: {e}")
        logger.exception(f"Stdout: {e.stdout}")
        logger.exception(f"Stderr: {e.stderr}")
    except Exception as e:
        logger.exception(f"Unexpected error during formatting: {e}")


def validate_with_pyright(output_directories: set[str]) -> None:
    """Validate generated stub files using pyright.

    Args:
        output_directories: Set of directories containing generated stubs.

    Raises:
        PyrightValidationError: If pyright finds any type errors.

    """
    # Collect all .pyi files from output directories
    stub_files: list[str] = []
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
            ["pyright", *stub_files],
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
        logger.exception("pyright not found. Please install pyright: npm install -g pyright")
        msg = "pyright command not found. Please install pyright."
        raise PyrightValidationError(msg)
    except subprocess.SubprocessError as e:
        error_msg = f"Error running pyright: {e}"
        logger.exception(error_msg)
        raise PyrightValidationError(error_msg)


def format_outputs(raw_input: str, is_pyi: bool) -> str:
    """Returns raw input without formatting (formatting is done at the end).

    Args:
        raw_input (str): The unformatted input.
        is_pyi (bool): Whether or not the output is a `pyi` file.

    Returns:
        str: The unformatted outputs.

    """
    return raw_input


def _generate_stubs_from_schema(
    schema: _Schema,
    file_path: str,
    schema_loader: capnp.SchemaLoader,
    file_id_to_path: dict[int, str],
    output_file_path: str,
    output_directory: str | None = None,
    import_paths: list[str] | None = None,
    module_path_prefix: str | None = None,
    schema_base_directory: str | None = None,
) -> tuple[
    dict[str, tuple[str, list[str]]],
    tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]],
]:
    """Internal function for generating *.pyi stubs from schema information.

    Args:
        schema: The root schema to parse and write stubs for.
        file_path: Path to the schema file.
        schema_loader: SchemaLoader instance with all nodes loaded.
        file_id_to_path: Mapping of schema IDs to file paths.
        output_file_path: The name of the output stub files, without file extension.
        output_directory: The directory where output files are written, if different from schema location.
        import_paths: Additional import paths for resolving absolute imports.
        module_path_prefix: Prefix for module path (e.g., "calculator" for subdirectory structure).
        schema_base_directory: The base directory where schema module is located (for relative imports).

    Returns:
        Dictionary mapping interface names to (client_name, base_client_names) tuples.

    """
    writer = Writer(
        schema=schema,
        file_path=file_path,
        schema_loader=schema_loader,
        file_id_to_path=file_id_to_path,
    )
    writer.generate_all_nested()

    for outputs, suffix, is_pyi in zip(
        (writer.dumps_pyi(), writer.dumps_py()), (PYI_SUFFIX, PY_SUFFIX), (True, False), strict=False
    ):
        formatted_output = format_outputs(outputs, is_pyi)

        with open(output_file_path + suffix, "w", encoding="utf8") as output_file:
            output_file.write(formatted_output)

    logger.info("Wrote stubs to '%s(%s/%s)'.", output_file_path, PYI_SUFFIX, PY_SUFFIX)

    # Return interfaces found in this module (with module prefix)
    # If output_file_path ends with __init__, use the directory name as the module name
    output_basename = os.path.basename(output_file_path)
    output_dir_path = os.path.dirname(output_file_path)

    if output_basename == "__init__":
        # For __init__.pyi files, the module name is the directory containing it
        # And module_path_prefix already includes this directory name if it was nested
        # So we use module_path_prefix directly as full_module_name
        full_module_name = module_path_prefix or os.path.basename(output_dir_path)
    else:
        # For non-__init__ files, check if we're inside a package (has __init__.py)
        module_name = output_basename
        package_has_init = os.path.exists(os.path.join(output_dir_path, "__init__.py"))

        # If inside a package and module name matches directory name, we need package.module syntax
        if package_has_init and module_name == os.path.basename(output_dir_path):
            # This is a module inside a package of the same name (e.g., schema_capnp/schema_capnp.pyi)
            # Full name should be schema_capnp.schema_capnp
            if module_path_prefix:
                full_module_name = f"{module_path_prefix}.{module_name}.{module_name}"
            else:
                full_module_name = f"{module_name}.{module_name}"
        # Normal case
        elif module_path_prefix:
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
    struct_types, list_types, interface_types = writer.get_dynamic_object_reader_types()

    logger.debug(
        f"Writer returned {len(struct_types)} structs, {len(list_types)} lists, {len(interface_types)} interfaces for {full_module_name}",
    )

    # Qualify the types with module prefix
    qualified_struct_types = [
        (f"{full_module_name}.{proto}", f"{full_module_name}.{reader}") for proto, reader in struct_types
    ]
    qualified_list_types = [
        (f"{full_module_name}.{list_class}", f"{full_module_name}.{reader}") for list_class, reader in list_types
    ]
    qualified_interface_types = [
        (f"{full_module_name}.{proto}", f"{full_module_name}.{client}") for proto, client in interface_types
    ]

    return interfaces_with_module, (qualified_struct_types, qualified_list_types, qualified_interface_types)


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

    for _i, part in enumerate(parts):
        if "**" in part:
            # For **, use the directory before it
            found_wildcard = True
            break
        if "*" in part or "?" in part or "[" in part:
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


def run(args: argparse.Namespace, root_directory: str) -> None:
    """Run the stub generator on a set of paths that point to *.capnp schemas.

    Now uses capnp compile with the plugin to ensure all schemas including
    groups in unions are properly handled.

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

    if not valid_paths:
        logger.warning("No schema files found to process")
        return

    # Convert import paths to absolute paths relative to root_directory
    absolute_import_paths = [os.path.join(root_directory, p) for p in import_paths]

    # Use capnp compile with our plugin to generate stubs
    # This ensures all schemas including groups in unions are properly embedded
    logger.info(f"Compiling {len(valid_paths)} schema(s) using capnpc plugin")

    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Create a wrapper script to invoke our plugin
    with tempfile.NamedTemporaryFile(mode="w", suffix="_capnpc", delete=False) as wrapper:
        wrapper.write(f"""#!/usr/bin/env {sys.executable}
import sys
sys.path.insert(0, {os.path.dirname(os.path.dirname(__file__))!r})
from capnp_stub_generator.capnpc_plugin import main
main()
""")
        wrapper_path = wrapper.name

    # Make wrapper executable
    os.chmod(wrapper_path, 0o755)

    try:
        # Determine source prefix for output structure
        if output_dir:
            # Calculate common base for preserving directory structure
            common_base = _determine_output_directory_structure(
                output_dir,
                paths,
                valid_paths,
                root_directory,
            )
            src_prefix = common_base or root_directory
        else:
            # Generate stubs next to source files - use parent of first schema
            src_prefix = os.path.dirname(next(iter(valid_paths)))

        # Build capnp compile command
        cmd = ["capnp", "compile"]

        if src_prefix:
            cmd.append(f"--src-prefix={src_prefix}")

        # Add output specification
        output_spec = output_dir or "."
        cmd.append(f"-o{wrapper_path}:{output_spec}")

        # Add import paths
        for import_path in absolute_import_paths:
            cmd.extend(["-I", import_path])

        # Add schema files
        cmd.extend(list(valid_paths))

        logger.debug(f"Running: {' '.join(cmd)}")

        # Run capnp compile
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"capnp compile failed:\n{result.stderr}")
            sys.exit(1)

        logger.info(f"✓ Generated stubs for {len(valid_paths)} schema(s)")

        # Run pyright validation if requested
        if not skip_pyright:
            output_directories = {output_dir} if output_dir else {os.path.dirname(p) for p in valid_paths}
            try:
                validate_with_pyright(output_directories)
            except PyrightValidationError as e:
                logger.exception(str(e))
                sys.exit(1)

    finally:
        # Clean up wrapper script
        with contextlib.suppress(Exception):
            os.unlink(wrapper_path)


def run_from_schemas(
    schema_loader: capnp.SchemaLoader,
    file_id_to_path: dict[int, str],
    output_dir: str,
    import_paths: list[str],
    skip_pyright: bool,
    augment_capnp_stubs: bool,
    common_base: str | None = None,
    preserve_path_structure: bool = False,
    file_schemas_only: set[int] | None = None,
) -> None:
    """Run stub generation from pre-loaded schemas.

    Args:
        schema_loader: SchemaLoader instance with all nodes loaded.
        file_id_to_path: Mapping of schema IDs to file paths.
        output_dir: Output directory for stubs.
        import_paths: Import paths for resolving absolute imports.
        skip_pyright: Whether to skip pyright validation.
        augment_capnp_stubs: Whether to augment capnp-stubs package.
        common_base: Common base directory for preserving structure.
        preserve_path_structure: Whether to preserve the full path structure of input files.
        file_schemas_only: Optional set of schema IDs to generate stubs for (file-level only).
            If None, generates stubs for all schemas in file_id_to_path.

    """
    # Track output directories for py.typed marker
    output_directories_used = set()

    # Collect all interfaces from all modules for cast_as overloads
    # Map of output_dir -> {interface_name: (client_name, base_client_names)}
    all_interfaces_by_dir: dict[str, dict[str, tuple[str, list[str]]]] = {}

    # Track all _DynamicObjectReader types by output directory
    all_dynamic_object_types_by_dir: dict[str, dict[str, list[tuple[str, str]]]] = {}

    for schema_id, path in file_id_to_path.items():
        # Skip nested schemas if file_schemas_only is specified
        if file_schemas_only is not None and schema_id not in file_schemas_only:
            continue

        # Get schema from loader
        try:
            schema = schema_loader.get(schema_id)
        except Exception as e:
            logger.warning(f"Could not load schema {hex(schema_id)} from {path}: {e}")
            continue

        file_path = path

        # Debug: log what we're processing
        logger.debug(f"Processing schema {schema.node.displayName} from {path}")
        logger.debug(f"  Schema ID: {hex(schema.node.id)}")
        logger.debug(f"  Nested nodes in schema: {len(schema.node.nestedNodes)}")

        # Create a temporary writer just to extract Python module annotation
        from capnp_stub_generator.writer import Writer

        temp_writer = Writer(
            schema=schema,
            file_path=path,
            schema_loader=schema_loader,
            file_id_to_path=file_id_to_path,
        )

        # Check if schema has Python module annotation
        python_module_path = temp_writer._python_module_path

        if output_dir and python_module_path:
            # Use module annotation to determine output structure
            # Convert "mas.schema.climate" -> "mas/schema/climate/climate_capnp/__init__.pyi"
            # The module annotation should include the full module path, we add _capnp suffix
            module_parts = python_module_path.split(".")

            # Get base name from path (e.g., "climate" from "climate.capnp")
            base_name = os.path.splitext(os.path.basename(path))[0]
            # Replace hyphens with underscores to make valid Python identifiers
            base_name = base_name.replace("-", "_")
            module_name = f"{base_name}_capnp"

            # Build directory structure: mas/schema/climate/climate_capnp/
            module_dir = os.path.join(*module_parts, module_name)
            output_directory = os.path.join(output_dir, module_dir)
            os.makedirs(output_directory, exist_ok=True)

            logger.info(f"Using Python module annotation: {python_module_path} -> {output_directory}")
        elif output_dir:
            # No Python module annotation - use flat structure but with module folder
            # For pycapnp 2.0+, all schemas need module folders: schema_name_capnp/__init__.py
            base_name = os.path.splitext(os.path.basename(path))[0]
            # Replace hyphens with underscores
            base_name = base_name.replace("-", "_")
            module_name = f"{base_name}_capnp"

            if preserve_path_structure:
                # Use the path as provided, treating it as relative to output_dir
                # If absolute, strip root to avoid writing outside output_dir
                rel_path = path
                if os.path.isabs(rel_path):
                    rel_path = rel_path.lstrip(os.sep)
                    # Handle Windows drive letters if needed (simple check)
                    if ":" in rel_path:
                        rel_path = rel_path.split(":", 1)[1].lstrip(os.sep)

                rel_dir = os.path.dirname(rel_path)
                # Add module folder
                output_directory = os.path.join(output_dir, rel_dir, module_name)
            elif common_base:
                abs_path = os.path.abspath(path)
                # Calculate relative path from common base
                rel_path = os.path.relpath(abs_path, common_base)
                rel_dir = os.path.dirname(rel_path)

                # Create output directory preserving structure with module folder
                output_directory = os.path.join(output_dir, rel_dir, module_name)
            else:
                # Flat structure with module folder
                output_directory = os.path.join(output_dir, module_name)

            os.makedirs(output_directory, exist_ok=True)
        else:
            # No output_dir specified: place stubs next to source files
            output_directory = os.path.dirname(path)

        output_directories_used.add(output_directory)

        # For pycapnp 2.0+, all schemas use module folders with __init__.py/__init__.pyi
        # Whether or not they have Python annotations
        output_file_name = "__init__"  # No suffix - will be added by _generate_stubs_from_schema

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

        module_interfaces, dynamic_object_types = _generate_stubs_from_schema(
            schema=schema,
            file_path=file_path,
            schema_loader=schema_loader,
            file_id_to_path=file_id_to_path,
            output_file_path=os.path.join(output_directory, output_file_name),
            output_directory=output_dir_to_pass,
            import_paths=import_paths,
            module_path_prefix=module_path_prefix,
            schema_base_directory=output_dir or output_directory,
        )

        # Collect interfaces for this output directory
        if module_interfaces:
            if output_directory not in all_interfaces_by_dir:
                all_interfaces_by_dir[output_directory] = {}
            all_interfaces_by_dir[output_directory].update(module_interfaces)

        # Collect _DynamicObjectReader types for this output directory
        struct_types, list_types, interface_types = dynamic_object_types
        logger.debug(
            f"Schema {os.path.basename(path)} returned {len(struct_types)} structs, {len(list_types)} lists, {len(interface_types)} interfaces",
        )
        if struct_types or list_types or interface_types:
            if output_directory not in all_dynamic_object_types_by_dir:
                all_dynamic_object_types_by_dir[output_directory] = {"structs": [], "lists": [], "interfaces": []}
            all_dynamic_object_types_by_dir[output_directory]["structs"].extend(struct_types)
            all_dynamic_object_types_by_dir[output_directory]["lists"].extend(list_types)
            all_dynamic_object_types_by_dir[output_directory]["interfaces"].extend(interface_types)

    # Create py.typed marker and __init__.py/__init__.pyi in each output directory to make them packages
    # Also create __init__.py/__init__.pyi files for all parent directories
    for output_directory in output_directories_used:
        # Create __init__.py and __init__.pyi to make it a package (needed for imports)
        init_py_path = os.path.join(output_directory, "__init__.py")
        init_pyi_path = os.path.join(output_directory, "__init__.pyi")

        if not os.path.exists(init_py_path):
            with open(init_py_path, "w", encoding="utf8") as f:
                f.write("# Auto-generated package initialization\n")

        if not os.path.exists(init_pyi_path):
            with open(init_pyi_path, "w", encoding="utf8") as f:
                f.write("# Auto-generated package initialization\n")

        # Create __init__.py and __init__.pyi files for all parent directories up to output_dir
        if output_dir:
            current_dir = os.path.dirname(output_directory)
            output_dir_abs = os.path.abspath(output_dir)

            # Walk up the directory tree
            while current_dir:
                current_dir_abs = os.path.abspath(current_dir)

                # Stop if we've reached or passed the output_dir
                if current_dir_abs == output_dir_abs:
                    break
                if not current_dir_abs.startswith(output_dir_abs):
                    break

                parent_init_py = os.path.join(current_dir, "__init__.py")
                parent_init_pyi = os.path.join(current_dir, "__init__.pyi")

                if not os.path.exists(parent_init_py):
                    with open(parent_init_py, "w", encoding="utf8") as f:
                        f.write("# Auto-generated package initialization\n")
                    logger.debug(f"Created __init__.py at {current_dir}")

                if not os.path.exists(parent_init_pyi):
                    with open(parent_init_pyi, "w", encoding="utf8") as f:
                        f.write("# Auto-generated package initialization\n")
                    logger.debug(f"Created __init__.pyi at {current_dir}")

                # Move up one level
                parent_dir = os.path.dirname(current_dir)
                if parent_dir == current_dir:  # Reached root
                    break
                current_dir = parent_dir

    # Track bundled stub directories for formatting
    bundled_stub_dirs = set()

    # Copy bundled schema module once at the top level (common parent or output_dir)
    # This avoids duplicating the schema module in each subdirectory
    source_stubs_path = find_capnp_stubs_package()
    if source_stubs_path:
        source_schema_path = os.path.join(os.path.dirname(source_stubs_path), "schema_capnp")

        # Determine top-level directory for schema
        if output_dir:
            # Use the output_dir as top level
            schema_dest_dir = os.path.abspath(output_dir)
        else:
            # Find common parent of all output directories
            output_dirs_list = list(output_directories_used)
            if len(output_dirs_list) == 1:
                schema_dest_dir = output_dirs_list[0]
            else:
                schema_dest_dir = os.path.commonpath([os.path.abspath(d) for d in output_dirs_list])

        # Copy to 'schema_capnp' directory at top level
        dest_schema_path = os.path.join(schema_dest_dir, "schema_capnp")

        if os.path.isdir(source_schema_path):
            if os.path.exists(dest_schema_path):
                shutil.rmtree(dest_schema_path)
            shutil.copytree(source_schema_path, dest_schema_path)
            logger.info(f"Copied schema module to top level: {dest_schema_path}")
            bundled_stub_dirs.add(dest_schema_path)
        else:
            logger.warning(f"Schema module not found at: {source_schema_path}")

    # Augment capnp-stubs with cast_as overloads (now default behavior)
    source_stubs_path = find_capnp_stubs_package()
    if source_stubs_path and augment_capnp_stubs:
        # Combine all interfaces from all directories
        all_interfaces = {}
        for interfaces in all_interfaces_by_dir.values():
            all_interfaces.update(interfaces)

        # Combine all _DynamicObjectReader types from all directories
        all_dynamic_object_types = {"structs": [], "interfaces": []}
        for types_dict in all_dynamic_object_types_by_dir.values():
            all_dynamic_object_types["structs"].extend(types_dict["structs"])
            all_dynamic_object_types["interfaces"].extend(types_dict["interfaces"])

        # Determine where to place augmented stubs (inside output directory)
        # If output_dir is specified, place augmented stubs inside it
        # Otherwise, pick a common parent directory of all output directories
        if output_dir:
            # Place augmented stubs in the output_dir itself
            augmented_stubs_dir = os.path.abspath(output_dir)
        else:
            # Find common parent of all output directories
            output_dirs_list = list(output_directories_used)
            if len(output_dirs_list) == 1:
                augmented_stubs_dir = output_dirs_list[0]
            else:
                augmented_stubs_dir = os.path.commonpath([os.path.abspath(d) for d in output_dirs_list])

        # Use the absolute path to output_dir for import path calculation
        actual_output_dir = os.path.abspath(output_dir) if output_dir else next(iter(output_directories_used))

        logger.info(
            f"Augmenting capnp-stubs with {len(all_interfaces)} interfaces, {len(all_dynamic_object_types.get('structs', []))} structs, {len(all_dynamic_object_types.get('lists', []))} lists, {len(all_dynamic_object_types.get('interfaces', []))} interface types",
        )

        result = augment_capnp_stubs_with_overloads(
            source_stubs_path,
            augmented_stubs_dir,
            actual_output_dir,
            all_interfaces,
            all_dynamic_object_types,
        )

        # Add augmented stubs to bundled dirs for formatting
        if result:
            capnp_stubs_path, schema_capnp_path = result
            if capnp_stubs_path:
                bundled_stub_dirs.add(capnp_stubs_path)
            if schema_capnp_path:
                bundled_stub_dirs.add(schema_capnp_path)
    elif augment_capnp_stubs:
        logger.warning("--augment-capnp-stubs specified but capnp-stubs package not found")

    # Combine all directories (generated stubs + bundled stubs) for formatting
    all_output_dirs = output_directories_used | bundled_stub_dirs

    # Format all generated files with ruff (includes bundled stubs)
    format_all_outputs(all_output_dirs)

    # Validate generated stubs with pyright (unless disabled)
    if not skip_pyright:
        validate_with_pyright(all_output_dirs)


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
    if all(base == absolute_bases[0] for base in absolute_bases) and _should_preserve_parent_directory(
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
        abs_pattern = os.path.join(root_directory, pattern) if not os.path.isabs(pattern) else pattern

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
    return _calculate_common_base(
        absolute_bases,
        relative_bases,
        paths,
        valid_paths,
    )
