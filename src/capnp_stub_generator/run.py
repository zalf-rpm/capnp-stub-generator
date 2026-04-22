"""Top-level module for stub generation."""

from __future__ import annotations

import asyncio
import logging
import os.path
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import capnp

from capnp_stub_generator.writer import Writer

if TYPE_CHECKING:
    import argparse
    from collections.abc import Iterator

    from capnp.lib.capnp import _Schema

if hasattr(capnp, "remove_import_hook"):
    capnp.remove_import_hook()


logger = logging.getLogger(__name__)

type InterfaceModuleMap = dict[str, tuple[str, list[str]]]
type DynamicObjectReaderTypes = tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]

PYI_SUFFIX = ".pyi"
PY_SUFFIX = ".py"
MIN_PRESERVED_PATH_DEPTH = 2
CAPNP_STDLIB_MODULES = {
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


@dataclass(frozen=True)
class RunFromSchemasOptions:
    """Configuration for generating stubs from pre-loaded schemas."""

    output_dir: str
    import_paths: list[str]
    skip_pyright: bool
    augment_capnp_stubs: bool
    ruff_config_path: str | None = None
    common_base: str | None = None
    preserve_path_structure: bool = False
    file_schemas_only: set[int] | None = None


@dataclass(frozen=True)
class SchemaWriterContext:
    """Shared state for writing stubs from a schema."""

    schema_loader: capnp.SchemaLoader
    file_id_to_path: dict[int, str]
    generated_module_names_by_schema_id: dict[int, str]
    inherited_interface_schema_ids: set[int]


@dataclass(frozen=True)
class SchemaWriteTarget:
    """Output target metadata for a generated schema."""

    file_path: str
    output_file_path: str
    module_path_prefix: str | None = None


@dataclass
class GeneratedSchemaState:
    """Collected generation outputs grouped by output directory."""

    output_directories_used: set[str] = field(default_factory=set)
    interfaces_by_dir: dict[str, dict[str, tuple[str, list[str]]]] = field(default_factory=dict)
    dynamic_object_types_by_dir: dict[str, dict[str, list[tuple[str, str]]]] = field(default_factory=dict)


def _resolve_executable(name: str) -> str:
    """Resolve an executable to an absolute path."""
    executable = shutil.which(name)
    if executable is not None:
        return executable

    msg = f"{name} command not found"
    raise FileNotFoundError(msg)


def _run_command(command: list[str], *, check: bool) -> subprocess.CompletedProcess[str]:
    """Run a trusted subprocess command and capture its output."""
    completed = asyncio.run(_run_command_async(command))
    if check and completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return completed


async def _run_command_async(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a trusted subprocess command asynchronously and capture its output."""
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return subprocess.CompletedProcess(
        command,
        process.returncode or 0,
        stdout.decode(),
        stderr.decode(),
    )


def _ruff_command_args(ruff_config_path: str | None) -> list[str]:
    """Return Ruff config arguments when a project config file is available."""
    if ruff_config_path is None:
        return []

    config_path = Path(ruff_config_path)
    if config_path.is_file():
        return ["--config", str(config_path)]

    return []


def find_capnp_stubs_package() -> str | None:
    """Find the bundled capnp-stubs package directory.

    Uses the bundled stubs from the resources directory.

    Returns:
        Path to the capnp-stubs directory, or None if not found.

    """
    # Get the bundled capnp-stubs from capnp-stubs directory
    bundled_stubs_path = Path(__file__).resolve().parent.parent / "pycapnp_base_stubs"

    if bundled_stubs_path.is_dir():
        logger.info("Using bundled capnp-stubs from: %s", bundled_stubs_path)
        return str(bundled_stubs_path)

    logger.warning("Bundled capnp-stubs not found at: %s", bundled_stubs_path)
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


def _replace_tree(source_path: Path, dest_path: Path) -> None:
    """Replace a destination directory with a fresh copy of the source tree."""
    if dest_path.exists():
        shutil.rmtree(dest_path)
    shutil.copytree(source_path, dest_path)


def _fix_schema_capnp_imports(capnp_pyi_path: Path) -> None:
    """Replace relative schema_capnp imports in the bundled capnp stubs."""
    if not capnp_pyi_path.exists():
        return

    with capnp_pyi_path.open(encoding="utf8") as file:
        content = file.read()

    content = content.replace("from ...schema_capnp import", "from schema_capnp import")

    with capnp_pyi_path.open("w", encoding="utf8") as file:
        file.write(content)

    logger.info("Fixed schema_capnp imports to be absolute")


def _copy_augmented_stub_packages(source_stubs_path: str, augmented_stubs_dir: str) -> tuple[Path, Path | None]:
    """Copy bundled stub packages into the augmentation directory."""
    source_stubs_dir = Path(source_stubs_path)
    dest_stubs_path = Path(augmented_stubs_dir) / "capnp-stubs"
    _replace_tree(source_stubs_dir, dest_stubs_path)
    logger.info("Copied capnp-stubs to: %s", dest_stubs_path)

    _fix_schema_capnp_imports(dest_stubs_path / "lib" / "capnp.pyi")

    source_schema_path = source_stubs_dir.parent / "schema_capnp"
    if not source_schema_path.is_dir():
        logger.warning("Schema stubs not found at: %s", source_schema_path)
        return dest_stubs_path, None

    dest_schema_path = Path(augmented_stubs_dir) / "schema_capnp"
    _replace_tree(source_schema_path, dest_schema_path)
    logger.info("Copied schema stubs to: %s", dest_schema_path)
    return dest_stubs_path, dest_schema_path


def _has_dynamic_object_overloads(dynamic_object_types: dict[str, list[tuple[str, str]]]) -> bool:
    """Return whether any dynamic reader overloads need to be generated."""
    return any(dynamic_object_types.get(type_name) for type_name in ("structs", "lists", "interfaces"))


def _read_stub_lines(capnp_pyi_path: Path) -> list[str]:
    """Read a stub file and return it as a mutable list of lines."""
    with capnp_pyi_path.open(encoding="utf8") as file:
        return file.read().split("\n")


def _write_stub_lines(capnp_pyi_path: Path, lines: list[str]) -> None:
    """Write a mutable list of lines back to a stub file."""
    with capnp_pyi_path.open("w", encoding="utf8") as file:
        file.write("\n".join(lines))


def _find_typing_import_idx(lines: list[str]) -> int | None:
    """Return the index of the `from typing import ...` line if present."""
    return next((idx for idx, line in enumerate(lines) if line.startswith("from typing import")), None)


def _ensure_overload_import(lines: list[str], typing_import_idx: int) -> None:
    """Ensure the typing import line includes `overload`."""
    if "overload" in lines[typing_import_idx]:
        return

    lines[typing_import_idx] = lines[typing_import_idx].replace("from typing import ", "from typing import overload, ")


def _find_import_end_idx(lines: list[str], typing_import_idx: int) -> int:
    """Find the first line after the import block starting at the typing import."""
    import_end_idx = typing_import_idx + 1
    in_multiline_import = False

    for idx, line in enumerate(lines[typing_import_idx + 1 :], start=typing_import_idx + 1):
        stripped = line.strip()

        if "from " in stripped and "import (" in stripped and ")" not in stripped:
            in_multiline_import = True
            continue

        if in_multiline_import:
            if ")" in stripped:
                in_multiline_import = False
            continue

        if not stripped or stripped.startswith(("import ", "from ", "#")):
            continue

        import_end_idx = idx
        break

    return import_end_idx


def _collect_qualified_names(
    interfaces: dict[str, tuple[str, list[str]]],
    dynamic_object_types: dict[str, list[tuple[str, str]]],
) -> set[str]:
    """Collect all qualified type names that need additional imports."""
    qualified_names = set(interfaces)
    qualified_names.update(protocol_name for protocol_name, _ in dynamic_object_types.get("structs", []))
    qualified_names.update(list_name for list_name, _ in dynamic_object_types.get("lists", []))
    qualified_names.update(protocol_name for protocol_name, _ in dynamic_object_types.get("interfaces", []))
    return qualified_names


def _find_capnp_module_idx(parts: list[str]) -> int | None:
    """Find the first `_capnp` module segment in a qualified name."""
    return next((idx for idx, part in enumerate(parts) if part.endswith("_capnp")), None)


def _extract_module_import(qualified_name: str) -> tuple[str, str] | None:
    """Return the module name and import path for a qualified generated type."""
    parts = qualified_name.split(".")
    capnp_module_idx = _find_capnp_module_idx(parts)
    if capnp_module_idx is None:
        return None

    capnp_module_name = parts[capnp_module_idx]
    if capnp_module_idx + 1 < len(parts) and parts[capnp_module_idx + 1] == capnp_module_name:
        from_path = capnp_module_name if capnp_module_idx == 0 else ".".join(parts[: capnp_module_idx + 1])
        return capnp_module_name, from_path

    from_path = "" if capnp_module_idx == 0 else ".".join(parts[:capnp_module_idx])
    return capnp_module_name, from_path


def _store_preferred_module_import(module_imports: dict[str, str], module_name: str, from_path: str) -> None:
    """Prefer a non-empty module import path over an empty direct import."""
    existing = module_imports.get(module_name)
    if existing is None or (from_path and not existing):
        module_imports[module_name] = from_path


def _render_module_import_lines(module_imports: dict[str, str]) -> list[str]:
    """Render import statements for generated project-specific types."""
    import_lines = ["", "# Generated imports for project-specific types"]

    for module_name in sorted(module_imports):
        from_path = module_imports[module_name]
        if not from_path and module_name in CAPNP_STDLIB_MODULES:
            import_lines.append(f"import capnp.{module_name} as {module_name}")
        elif from_path:
            import_lines.append(f"from {from_path} import {module_name}")
        else:
            import_lines.append(f"import {module_name}")

    return import_lines


def _find_class_bounds(lines: list[str], class_name: str) -> tuple[int, int] | None:
    """Return the start and end indices of a top-level class definition."""
    class_start_idx = next(
        (idx for idx, line in enumerate(lines) if line.strip().startswith(f"class {class_name}")),
        None,
    )
    if class_start_idx is None:
        return None

    class_end_idx = len(lines)
    for idx in range(class_start_idx + 1, len(lines)):
        if lines[idx].strip().startswith("class "):
            class_end_idx = idx
            break

    return class_start_idx, class_end_idx


def _adjust_insert_idx(lines: list[str], method_idx: int, class_start_idx: int) -> int:
    """Move an insertion index above decorators and blank separator lines."""
    insert_idx = method_idx
    for idx in range(method_idx - 1, class_start_idx, -1):
        previous_line = lines[idx].strip()
        if previous_line.startswith("@") or previous_line == "":
            insert_idx = idx
            continue
        break

    return insert_idx


def _find_method_insert_idx(lines: list[str], class_name: str, method_name: str) -> tuple[int | None, int | None]:
    """Find where overloads should be inserted for a schema-accepting class method."""
    class_bounds = _find_class_bounds(lines, class_name)
    if class_bounds is None:
        return None, None

    class_start_idx, class_end_idx = class_bounds
    for method_idx in range(class_start_idx + 1, class_end_idx):
        line = lines[method_idx]
        if line.strip().startswith("@overload"):
            continue
        if f"def {method_name}" in line and "schema:" in line:
            return class_start_idx, _adjust_insert_idx(lines, method_idx, class_start_idx)

    return class_start_idx, None


def _capnp_qualified_suffix(qualified_name: str) -> tuple[str, str] | None:
    """Return the `_capnp` module name and suffix for a qualified generated type."""
    parts = qualified_name.split(".")
    capnp_module_idx = _find_capnp_module_idx(parts)
    if capnp_module_idx is None:
        return None
    return parts[capnp_module_idx], ".".join(parts[capnp_module_idx:])


def _build_cast_as_overloads(
    interfaces: dict[str, tuple[str, list[str]]],
    module_imports: dict[str, str],
) -> list[str]:
    """Build overloads for `_CapabilityClient.cast_as`."""
    overload_lines: list[str] = []

    for interface_name, client_name in _sort_interfaces_by_inheritance(interfaces):
        interface_details = _capnp_qualified_suffix(interface_name)
        client_details = _capnp_qualified_suffix(client_name)
        if interface_details is None or client_details is None:
            logger.warning("Could not find capnp module in interface name: %s", interface_name)
            continue

        capnp_module_name, qualified_interface = interface_details
        _, qualified_client = client_details
        if capnp_module_name not in module_imports:
            logger.warning("Could not find import path for module %s", capnp_module_name)
            continue

        overload_lines.extend(
            [
                "    @overload",
                f"    def cast_as(self, schema: {qualified_interface}) -> {qualified_client}: ...",
            ],
        )

    if overload_lines:
        overload_lines.extend(
            [
                "    @overload",
                "    def cast_as(self, schema: _InterfaceSchema | _InterfaceModule) -> _DynamicCapabilityClient: ...",
            ],
        )
    return overload_lines


def _trim_to_capnp_module(qualified_name: str) -> str:
    """Drop any non-module prefix before the first `_capnp` segment."""
    qualified_details = _capnp_qualified_suffix(qualified_name)
    return qualified_details[1] if qualified_details is not None else qualified_name


def _sort_types_by_specificity(types: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Sort qualified generated types by nesting depth, deepest first."""
    return sorted(types, key=lambda item: (-item[0].count("."), item[0]))


def _build_dynamic_reader_overloads(
    method_name: str,
    types: list[tuple[str, str]],
    *,
    wrap_schema_in_type: bool = False,
    catchall_signature: str | None = None,
) -> list[str]:
    """Build overload blocks for `_DynamicObjectReader` methods."""
    overload_lines: list[str] = []

    for schema_name, return_name in types:
        clean_schema = _trim_to_capnp_module(schema_name)
        clean_return = _trim_to_capnp_module(return_name)
        schema_expression = f"type[{clean_schema}]" if wrap_schema_in_type else clean_schema
        overload_lines.extend(
            [
                "    @overload",
                f"    def {method_name}(self, schema: {schema_expression}) -> {clean_return}: ...",
            ],
        )

    if catchall_signature is not None and overload_lines:
        overload_lines.extend(["    @overload", catchall_signature])

    return overload_lines


def _sort_interface_reader_types(
    interface_types: list[tuple[str, str]],
    interfaces: dict[str, tuple[str, list[str]]],
) -> list[tuple[str, str]]:
    """Sort interface reader overloads by inheritance, then preserve any leftovers."""
    if not interfaces:
        return _sort_types_by_specificity(interface_types)

    interface_type_map = dict(interface_types)
    sorted_interface_types = [
        (interface_name, interface_type_map[interface_name])
        for interface_name, _ in _sort_interfaces_by_inheritance(interfaces)
        if interface_name in interface_type_map
    ]
    seen = {interface_name for interface_name, _ in sorted_interface_types}
    sorted_interface_types.extend(
        (interface_name, client_name) for interface_name, client_name in interface_types if interface_name not in seen
    )
    return sorted_interface_types


def _insert_overload_blocks(lines: list[str], overload_blocks: list[tuple[int, list[str]]]) -> None:
    """Insert overload blocks from bottom to top so earlier indices stay stable."""
    for insert_idx, overload_lines in sorted(overload_blocks, key=lambda item: item[0], reverse=True):
        lines[insert_idx:insert_idx] = overload_lines


def augment_capnp_stubs_with_overloads(
    source_stubs_path: str,
    augmented_stubs_dir: str,
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
        interfaces: Dictionary mapping interface names to (client_name, base_client_names) tuples.
        dynamic_object_types: Dictionary with "structs" and "interfaces" keys containing type tuples.

    Returns:
        Tuple of (capnp-stubs path, schema_capnp path or None) that were copied/augmented,
        or None if lib/capnp.pyi could not be found.

    """
    dest_stubs_path, dest_schema_path = _copy_augmented_stub_packages(source_stubs_path, augmented_stubs_dir)

    if not interfaces and not _has_dynamic_object_overloads(dynamic_object_types):
        logger.info("No interfaces or _DynamicObjectReader types found, skipping capnp-stubs augmentation.")
        return str(dest_stubs_path), str(dest_schema_path) if dest_schema_path else None

    capnp_pyi_path = dest_stubs_path / "lib" / "capnp.pyi"
    if not capnp_pyi_path.exists():
        logger.warning("Could not find lib/capnp.pyi at %s, skipping augmentation.", capnp_pyi_path)
        return None

    lines = _read_stub_lines(capnp_pyi_path)
    typing_import_idx = _find_typing_import_idx(lines)
    if typing_import_idx is None:
        logger.warning("Could not find 'from typing import' in lib/capnp.pyi, skipping augmentation.")
        return str(dest_stubs_path), str(dest_schema_path) if dest_schema_path else None

    _ensure_overload_import(lines, typing_import_idx)
    module_imports = _build_module_imports(interfaces, dynamic_object_types, lines, typing_import_idx)
    _write_stub_lines(capnp_pyi_path, lines)

    if interfaces:
        _augment_capnp_pyi(capnp_pyi_path, interfaces, module_imports)

    if _has_dynamic_object_overloads(dynamic_object_types):
        _augment_dynamic_object_reader(capnp_pyi_path, dynamic_object_types, interfaces)

    return str(dest_stubs_path), str(dest_schema_path) if dest_schema_path else None


def _build_module_imports(
    interfaces: dict[str, tuple[str, list[str]]],
    dynamic_object_types: dict[str, list[tuple[str, str]]],
    lines: list[str],
    typing_import_idx: int,
) -> dict[str, str]:
    """Build module imports section for augmented capnp.pyi.

    Args:
        interfaces: Dictionary of interfaces for cast_as overloads.
        dynamic_object_types: Dictionary with struct/interface types for _DynamicObjectReader.
        lines: Current lines of capnp.pyi (will be modified in place).
        typing_import_idx: Index of the typing import line.

    Returns:
        Dictionary mapping module names to import paths.

    """
    module_imports: dict[str, str] = {}
    for qualified_name in _collect_qualified_names(interfaces, dynamic_object_types):
        module_import = _extract_module_import(qualified_name)
        if module_import is None:
            continue
        module_name, from_path = module_import
        _store_preferred_module_import(module_imports, module_name, from_path)

    import_end_idx = _find_import_end_idx(lines, typing_import_idx)
    lines[import_end_idx:import_end_idx] = _render_module_import_lines(module_imports)
    return module_imports


def _augment_capnp_pyi(
    capnp_pyi_path: str | Path,
    interfaces: dict[str, tuple[str, list[str]]],
    module_imports: dict[str, str],
) -> None:
    """Augment _CapabilityClient.cast_as method with interface-specific overloads.

    Args:
        capnp_pyi_path: Path to the lib/capnp.pyi file.
        interfaces: Dictionary mapping interface names to (client_name, base_client_names).
        module_imports: Dictionary mapping module names to import paths.

    """
    capnp_pyi_path = Path(capnp_pyi_path)
    lines = _read_stub_lines(capnp_pyi_path)
    _, cast_as_line_idx = _find_method_insert_idx(lines, "_CapabilityClient", "cast_as")
    if cast_as_line_idx is None:
        logger.warning("Could not find cast_as method in _CapabilityClient class, skipping augmentation.")
        return

    lines[cast_as_line_idx:cast_as_line_idx] = _build_cast_as_overloads(interfaces, module_imports)
    _write_stub_lines(capnp_pyi_path, lines)
    logger.info("Augmented %s with %s cast_as overload(s).", capnp_pyi_path, len(interfaces))


def _augment_dynamic_object_reader(
    capnp_pyi_path: str | Path,
    dynamic_object_types: dict[str, list[tuple[str, str]]],
    interfaces: dict[str, tuple[str, list[str]]],
) -> None:
    """Augment _DynamicObjectReader class in lib/capnp.pyi with as_struct/as_list/as_interface overloads.

    Args:
        capnp_pyi_path: Path to the lib/capnp.pyi file to augment.
        dynamic_object_types: Dictionary of generated struct, list, and interface types.
        interfaces: Full interfaces dict for inheritance-based sorting.

    """
    capnp_pyi_path = Path(capnp_pyi_path)
    struct_types = dynamic_object_types.get("structs", [])
    list_types = dynamic_object_types.get("lists", [])
    interface_types = dynamic_object_types.get("interfaces", [])

    logger.info(
        "Augmenting _DynamicObjectReader with %s structs, %s lists, %s interfaces",
        len(struct_types),
        len(list_types),
        len(interface_types),
    )

    if not struct_types and not list_types and not interface_types:
        logger.info("No _DynamicObjectReader types to augment.")
        return

    lines = _read_stub_lines(capnp_pyi_path)
    dynamic_reader_idx, as_struct_insert_idx = _find_method_insert_idx(lines, "_DynamicObjectReader", "as_struct")
    _, as_list_insert_idx = _find_method_insert_idx(lines, "_DynamicObjectReader", "as_list")
    _, as_interface_insert_idx = _find_method_insert_idx(lines, "_DynamicObjectReader", "as_interface")

    if dynamic_reader_idx is None:
        logger.warning("Could not find _DynamicObjectReader class in lib/capnp.pyi, skipping augmentation.")
        return

    if as_struct_insert_idx is None or as_interface_insert_idx is None:
        logger.warning(
            "Could not find as_struct/as_interface methods in _DynamicObjectReader (as_struct=%s, as_interface=%s), skipping augmentation.",
            as_struct_insert_idx,
            as_interface_insert_idx,
        )
        return

    struct_overloads = _build_dynamic_reader_overloads(
        "as_struct",
        _sort_types_by_specificity(struct_types),
        catchall_signature="    def as_struct(self, schema: _StructSchema | _StructModule) -> _DynamicStructReader: ...",
    )
    list_overloads = _build_dynamic_reader_overloads(
        "as_list",
        _sort_types_by_specificity(list_types),
        wrap_schema_in_type=True,
    )
    interface_overloads = _build_dynamic_reader_overloads(
        "as_interface",
        _sort_interface_reader_types(interface_types, interfaces),
        catchall_signature="    def as_interface(self, schema: _InterfaceSchema | _InterfaceModule) -> _DynamicCapabilityClient: ...",
    )

    overload_blocks: list[tuple[int, list[str]]] = [(as_struct_insert_idx, struct_overloads)]
    if as_list_insert_idx is not None and list_overloads:
        overload_blocks.append((as_list_insert_idx, list_overloads))
    overload_blocks.append((as_interface_insert_idx, interface_overloads))
    _insert_overload_blocks(lines, overload_blocks)
    _write_stub_lines(capnp_pyi_path, lines)

    total_overloads = sum(len(overload_lines) // 2 for _, overload_lines in overload_blocks)
    logger.info("Augmented _DynamicObjectReader in %s with %s overload(s).", capnp_pyi_path, total_overloads)


def format_all_outputs(output_directories: set[str], *, ruff_config_path: str | None = None) -> None:
    """Format all generated stub files using ruff.

    Runs multiple passes to catch everything:
    1. ruff format (default settings)
    2. ruff check --fix --select ALL
    3. ruff format again

    Args:
        output_directories: Set of directories containing generated stubs.
        ruff_config_path: Optional path to a Ruff config file.

    """
    ruff_targets = sorted(str(path) for path in map(Path, output_directories) if path.exists())
    if not ruff_targets:
        logger.warning("No output directories found to format")
        return

    logger.info("Formatting generated outputs in %s directorie(s) with ruff...", len(ruff_targets))

    try:
        ruff = _resolve_executable("ruff")
        config_args = _ruff_command_args(ruff_config_path)

        # Pass 1: ruff format (default settings)
        logger.info("Pass 1: Running ruff format...")
        _run_command([ruff, "format", *config_args, *ruff_targets], check=True)

        # Pass 2: ruff check --fix --select ALL
        logger.info("Pass 2: Running ruff check --fix --select ALL...")
        _run_command([ruff, "check", *config_args, "--fix", "--select", "ALL", *ruff_targets], check=False)

        # Pass 3: ruff format again
        logger.info("Pass 3: Running ruff format again...")
        _run_command([ruff, "format", *config_args, *ruff_targets], check=True)

        logger.info("✓ Ruff formatting completed successfully")

    except FileNotFoundError:
        logger.exception("ruff not found. Please install ruff: pip install ruff")
    except subprocess.CalledProcessError as e:
        logger.exception("Ruff formatting failed. Stdout: %s\nStderr: %s", e.stdout, e.stderr)
    except OSError:
        logger.exception("Ruff formatting failed due to an OS error")


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
            stub_files.extend(str(Path(root, file)) for file in files if file.endswith(".pyi"))

    if not stub_files:
        logger.warning("No stub files found to validate")
        return

    logger.info("Validating %s generated stub file(s) with pyright...", len(stub_files))

    try:
        pyright = _resolve_executable("pyright")

        # Run pyright on all stub files
        result = _run_command([pyright, *stub_files], check=False)

        # Check for errors in output
        error_count = result.stdout.count(" error:")

        if error_count > 0 or result.returncode != 0:
            error_msg = f"Pyright validation failed with {error_count} error(s):\n\n{result.stdout}"
            logger.error(error_msg)
            raise PyrightValidationError(error_msg)

        logger.info("✓ Pyright validation passed - no type errors found")

    except FileNotFoundError as error:
        logger.exception("pyright not found. Please install pyright: npm install -g pyright")
        msg = "pyright command not found. Please install pyright."
        raise PyrightValidationError(msg) from error
    except subprocess.SubprocessError as error:
        logger.exception("Error running pyright")
        error_msg = f"Error running pyright: {error}"
        raise PyrightValidationError(error_msg) from error


def format_outputs(raw_input: str) -> str:
    """Return raw input without formatting.

    Args:
        raw_input (str): The unformatted input.

    Returns:
        str: The unformatted outputs.

    """
    return raw_input


def _generate_stubs_from_schema(
    schema: _Schema,
    context: SchemaWriterContext,
    target: SchemaWriteTarget,
) -> tuple[
    InterfaceModuleMap,
    DynamicObjectReaderTypes,
]:
    """Generate stub files from schema information.

    Args:
        schema: The root schema to parse and write stubs for.
        context: Shared schema loader and file-path mapping for generation.
        target: Output path metadata for the generated module.

    Returns:
        Dictionary mapping interface names to (client_name, base_client_names) tuples.

    """
    writer = Writer(
        schema=schema,
        file_path=target.file_path,
        schema_loader=context.schema_loader,
        file_id_to_path=context.file_id_to_path,
        generated_module_names_by_schema_id=context.generated_module_names_by_schema_id,
        inherited_interface_schema_ids=context.inherited_interface_schema_ids,
    )
    writer.generate_all_nested()

    output_directory = Path(target.output_file_path).parent
    generated_outputs = {
        Path(target.output_file_path + PYI_SUFFIX): writer.dumps_pyi(),
        Path(target.output_file_path + PY_SUFFIX): writer.dumps_py(),
    }

    generated_outputs.update(
        {
            output_directory / relative_path: content
            for relative_path, content in writer.dumps_types_pyi_files().items()
        },
    )
    generated_outputs.update(
        {output_directory / relative_path: content for relative_path, content in writer.dumps_types_py_files().items()},
    )

    for output_path, outputs in generated_outputs.items():
        formatted_output = format_outputs(outputs)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf8") as output_file:
            output_file.write(formatted_output)

    logger.info("Wrote stubs to '%s(%s/%s)'.", target.output_file_path, PYI_SUFFIX, PY_SUFFIX)

    # Return interfaces found in this module (with module prefix)
    # If output_file_path ends with __init__, use the directory name as the module name
    output_path = Path(target.output_file_path)
    output_basename = output_path.name
    output_dir_path = output_path.parent

    if output_basename == "__init__":
        # For __init__.pyi files, the module name is the directory containing it
        # And module_path_prefix already includes this directory name if it was nested
        # So we use module_path_prefix directly as full_module_name
        full_module_name = target.module_path_prefix or output_dir_path.name
    else:
        # For non-__init__ files, check if we're inside a package (has __init__.py)
        module_name = output_basename
        package_has_init = (output_dir_path / "__init__.py").exists()

        # If inside a package and module name matches directory name, we need package.module syntax
        if package_has_init and module_name == output_dir_path.name:
            # This is a module inside a package of the same name (e.g., schema_capnp/schema_capnp.pyi)
            # Full name should be schema_capnp.schema_capnp
            if target.module_path_prefix:
                full_module_name = f"{target.module_path_prefix}.{module_name}.{module_name}"
            else:
                full_module_name = f"{module_name}.{module_name}"
        # Normal case
        elif target.module_path_prefix:
            full_module_name = f"{target.module_path_prefix}.{module_name}"
        else:
            full_module_name = module_name

    interfaces_with_module: InterfaceModuleMap = {}
    for interface_name, (client_name, base_client_names) in writer._all_interfaces.items():
        # Add module prefix to make fully qualified names
        qualified_interface = f"{full_module_name}.types.modules.{interface_name}"
        qualified_client = f"{full_module_name}.types.clients.{client_name}"

        # Also qualify the base client names
        qualified_base_clients = [f"{full_module_name}.types.clients.{base}" for base in base_client_names]

        interfaces_with_module[qualified_interface] = (qualified_client, qualified_base_clients)

    # Get _DynamicObjectReader types for augmentation tracking
    struct_types, list_types, interface_types = writer.get_dynamic_object_reader_types()

    logger.debug(
        "Writer returned %s structs, %s lists, %s interfaces for %s",
        len(struct_types),
        len(list_types),
        len(interface_types),
        full_module_name,
    )

    # Qualify the types with module prefix
    qualified_struct_types: list[tuple[str, str]] = [
        (f"{full_module_name}.types.modules.{proto}", f"{full_module_name}.types.readers.{reader}")
        for proto, reader in struct_types
    ]
    qualified_list_types: list[tuple[str, str]] = [
        (f"{full_module_name}.types.lists.{list_class}", f"{full_module_name}.types.readers.{reader}")
        for list_class, reader in list_types
    ]
    qualified_interface_types: list[tuple[str, str]] = [
        (f"{full_module_name}.types.modules.{proto}", f"{full_module_name}.types.clients.{client}")
        for proto, client in interface_types
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
    pattern_path = Path(pattern)
    base_parts: list[str] = []
    found_wildcard = False

    for part in pattern_path.parts:
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

    base = Path(*base_parts)

    # If no wildcard was found and the pattern is a specific file, use its parent directory
    if not found_wildcard and pattern_path.suffix == ".capnp":
        base = base.parent

    return str(base)


def _expand_path_pattern(root_directory: Path, pattern: str) -> set[Path]:
    """Expand a user-provided file or glob pattern relative to the root directory."""
    pattern_path = Path(pattern)

    if pattern_path.is_absolute():
        base_dir = Path(pattern_path.anchor)
        relative_pattern = str(pattern_path.relative_to(base_dir))
        return set(base_dir.glob(relative_pattern))

    return set(root_directory.glob(pattern))


def _collect_cleanup_paths(root_path: Path, patterns: list[str]) -> set[Path]:
    """Expand cleanup patterns into concrete file paths."""
    cleanup_paths: set[Path] = set()
    for pattern in patterns:
        cleanup_paths |= _expand_path_pattern(root_path, pattern)
    return cleanup_paths


def _collect_excluded_paths(root_path: Path, excludes: list[str]) -> set[Path]:
    """Resolve excluded files and glob patterns."""
    excluded_paths: set[Path] = set()
    for exclude in excludes:
        exclude_path = root_path / exclude
        if exclude_path.is_file():
            excluded_paths.add(exclude_path)
            continue
        excluded_paths |= _expand_path_pattern(root_path, exclude)
    return excluded_paths


def _iter_capnp_files(search_path: Path, *, recursive: bool) -> set[Path]:
    """Return schema files from a directory."""
    if recursive:
        return {
            Path(root, file) for root, _, files in os.walk(search_path) for file in files if file.endswith(".capnp")
        }

    return {file_path for file_path in search_path.iterdir() if file_path.is_file() and file_path.suffix == ".capnp"}


def _collect_search_paths(root_path: Path, paths: list[str], *, recursive: bool) -> set[Path]:
    """Resolve input paths into the set of schema files that should be processed."""
    search_paths: set[Path] = set()
    for path in paths:
        search_path = root_path / path
        if search_path.is_dir():
            search_paths |= _iter_capnp_files(search_path, recursive=recursive)
            continue
        search_paths |= _expand_path_pattern(root_path, path)
    return search_paths


def _create_capnpc_wrapper() -> Path:
    """Create a temporary wrapper that invokes the bundled capnpc plugin."""
    with tempfile.NamedTemporaryFile(mode="w", suffix="_capnpc", delete=False) as wrapper:
        wrapper.write(f"""#!/usr/bin/env {sys.executable}
import sys
sys.path.insert(0, {str(Path(__file__).parent.parent)!r})
from capnp_stub_generator.capnpc_plugin import main
main()
""")
        wrapper_path = Path(wrapper.name)

    wrapper_path.chmod(0o700)
    return wrapper_path


def _determine_src_prefix(output_dir: str, paths: list[str], valid_paths: set[str], root_directory: str) -> str:
    """Determine the capnp compile source prefix."""
    if output_dir:
        common_base = _determine_output_directory_structure(output_dir, paths, valid_paths, root_directory)
        return common_base or root_directory
    return str(Path(next(iter(valid_paths))).parent)


def _build_capnp_compile_command(
    wrapper_path: Path,
    output_dir: str,
    src_prefix: str,
    absolute_import_paths: list[str],
    valid_paths: set[str],
) -> list[str]:
    """Build the `capnp compile` command line."""
    command = [_resolve_executable("capnp"), "compile"]
    if src_prefix:
        command.append(f"--src-prefix={src_prefix}")

    command.append(f"-o{wrapper_path}:{output_dir or '.'}")
    for import_path in absolute_import_paths:
        command.extend(["-I", import_path])
    command.extend(sorted(valid_paths))
    return command


def _validation_output_directories(output_dir: str, valid_paths: set[str]) -> set[str]:
    """Return directories that should be checked with pyright after generation."""
    return {output_dir} if output_dir else {str(Path(path).parent) for path in valid_paths}


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
    root_path = Path(root_directory)
    output_dir_path = Path(output_dir) if output_dir else None

    for cleanup_path in _collect_cleanup_paths(root_path, clean):
        cleanup_path.unlink()

    excluded_paths = _collect_excluded_paths(root_path, excludes)
    search_paths = _collect_search_paths(root_path, paths, recursive=args.recursive)
    valid_paths = {str(path) for path in (search_paths - excluded_paths)}

    if not valid_paths:
        logger.warning("No schema files found to process")
        return

    absolute_import_paths = [str((root_path / p).resolve()) for p in import_paths]

    logger.info("Compiling %s schema(s) using capnpc plugin", len(valid_paths))

    if output_dir_path:
        output_dir_path.mkdir(parents=True, exist_ok=True)

    wrapper_path = _create_capnpc_wrapper()

    try:
        src_prefix = _determine_src_prefix(output_dir, paths, valid_paths, root_directory)
        cmd = _build_capnp_compile_command(wrapper_path, output_dir, src_prefix, absolute_import_paths, valid_paths)
        logger.debug("Running: %s", " ".join(cmd))

        result = _run_command(cmd, check=False)
        if result.returncode != 0:
            logger.error("capnp compile failed:\n%s", result.stderr)
            sys.exit(1)

        logger.info("✓ Generated stubs for %s schema(s)", len(valid_paths))

        if not skip_pyright:
            try:
                validate_with_pyright(_validation_output_directories(output_dir, valid_paths))
            except PyrightValidationError:
                logger.exception("Pyright validation failed")
                sys.exit(1)

    finally:
        wrapper_path.unlink(missing_ok=True)


def _iter_loaded_schemas(
    schema_loader: capnp.SchemaLoader,
    file_id_to_path: dict[int, str],
    file_schemas_only: set[int] | None,
) -> Iterator[tuple[_Schema, str]]:
    """Yield loadable file schemas and skip missing ones with a warning."""
    for schema_id, path in file_id_to_path.items():
        if file_schemas_only is not None and schema_id not in file_schemas_only:
            continue
        try:
            yield schema_loader.get(schema_id), path
        except capnp.KjException as error:
            logger.warning("Could not load schema %s from %s: %s", hex(schema_id), path, error)


def _collect_inherited_interface_schema_ids(
    schema_loader: capnp.SchemaLoader,
    file_id_to_path: dict[int, str],
) -> set[int]:
    """Collect interface schema IDs that appear as superclasses anywhere in the loaded file graph."""
    inherited_interface_schema_ids: set[int] = set()
    visited_schema_ids: set[int] = set()

    def visit_schema(schema: _Schema) -> None:
        if schema.node.id in visited_schema_ids:
            return
        visited_schema_ids.add(schema.node.id)

        if schema.node.which() == "interface":
            inherited_interface_schema_ids.update(superclass.id for superclass in schema.node.interface.superclasses)

        for nested_node in schema.node.nestedNodes:
            try:
                visit_schema(schema_loader.get(nested_node.id))
            except capnp.KjException:
                continue

    for schema, _ in _iter_loaded_schemas(schema_loader, file_id_to_path, None):
        visit_schema(schema)

    return inherited_interface_schema_ids


def _schema_module_name(path_obj: Path) -> str:
    """Return the generated Python module name for a schema file."""
    return f"{path_obj.stem.replace('-', '_')}_capnp"


def _python_module_path_for_schema(
    schema: _Schema,
    path: str,
    schema_loader: capnp.SchemaLoader,
    file_id_to_path: dict[int, str],
) -> str | None:
    """Return the Python module annotation for a schema if present."""
    temp_writer = Writer(
        schema=schema,
        file_path=path,
        schema_loader=schema_loader,
        file_id_to_path=file_id_to_path,
    )
    return temp_writer._python_module_path


def _relative_output_directory_without_annotation(
    path: str,
    path_obj: Path,
    common_base: str | None,
    *,
    preserve_path_structure: bool,
) -> Path:
    """Build the relative output directory for a schema without module annotations."""
    module_name = _schema_module_name(path_obj)
    if preserve_path_structure:
        relative_dir = _preserved_relative_dir(path, path_obj)
    elif common_base:
        relative_dir = Path(os.path.relpath(path_obj.resolve(), common_base)).parent
    else:
        relative_dir = Path()

    return relative_dir / module_name


def _preserved_relative_dir(path: str, path_obj: Path) -> Path:
    """Return the schema directory while stripping any absolute-root prefix."""
    if not path_obj.is_absolute():
        return path_obj.parent

    relative_path = path.lstrip(os.sep)
    if ":" in relative_path:
        relative_path = relative_path.split(":", 1)[1].lstrip(os.sep)
    return Path(relative_path).parent


def _output_directory_from_annotation(output_dir: str, path_obj: Path, python_module_path: str) -> Path:
    """Build the output directory from a schema's Python module annotation."""
    output_directory_path = Path(output_dir, *python_module_path.split("."), _schema_module_name(path_obj))
    output_directory_path.mkdir(parents=True, exist_ok=True)
    logger.info("Using Python module annotation: %s -> %s", python_module_path, output_directory_path)
    return output_directory_path


def _output_directory_without_annotation(
    output_dir: str,
    path: str,
    path_obj: Path,
    common_base: str | None,
    *,
    preserve_path_structure: bool,
) -> Path:
    """Build the fallback output directory for a schema without module annotations."""
    output_directory_path = Path(
        output_dir,
        _relative_output_directory_without_annotation(
            path,
            path_obj,
            common_base,
            preserve_path_structure=preserve_path_structure,
        ),
    )
    output_directory_path.mkdir(parents=True, exist_ok=True)
    return output_directory_path


def _resolve_generated_module_name(
    path: str,
    python_module_path: str | None,
    options: RunFromSchemasOptions,
) -> str | None:
    """Resolve the importable module name that will be generated for a schema."""
    path_obj = Path(path)
    if python_module_path:
        return f"{python_module_path}.{_schema_module_name(path_obj)}"
    if not options.output_dir:
        return None

    relative_output_directory = _relative_output_directory_without_annotation(
        path,
        path_obj,
        options.common_base,
        preserve_path_structure=options.preserve_path_structure,
    )
    return ".".join(relative_output_directory.parts)


def _resolve_output_directory(path: str, python_module_path: str | None, options: RunFromSchemasOptions) -> Path:
    """Resolve the output directory for a generated schema module."""
    path_obj = Path(path)
    if options.output_dir and python_module_path:
        return _output_directory_from_annotation(options.output_dir, path_obj, python_module_path)
    if options.output_dir:
        return _output_directory_without_annotation(
            options.output_dir,
            path,
            path_obj,
            options.common_base,
            preserve_path_structure=options.preserve_path_structure,
        )
    return path_obj.parent


def _resolve_module_path_prefix(output_dir: str, output_directory: str) -> str | None:
    """Return the Python package prefix for a generated schema output directory."""
    if not output_dir or output_directory == output_dir:
        return None

    relative_module_path = os.path.relpath(output_directory, output_dir)
    if relative_module_path == ".":
        return None
    return relative_module_path.replace(os.sep, ".")


def _new_dynamic_object_types_bucket() -> dict[str, list[tuple[str, str]]]:
    """Return an empty aggregation bucket for dynamic reader overload types."""
    return {"structs": [], "lists": [], "interfaces": []}


def _record_generated_module(
    state: GeneratedSchemaState,
    output_directory: str,
    module_interfaces: dict[str, tuple[str, list[str]]],
    dynamic_object_types: tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]],
    path_obj: Path,
) -> None:
    """Record generated interfaces and dynamic object types for one output module."""
    if module_interfaces:
        state.interfaces_by_dir.setdefault(output_directory, {}).update(module_interfaces)

    struct_types, list_types, interface_types = dynamic_object_types
    logger.debug(
        "Schema %s returned %s structs, %s lists, %s interfaces",
        path_obj.name,
        len(struct_types),
        len(list_types),
        len(interface_types),
    )
    if not struct_types and not list_types and not interface_types:
        return

    bucket = state.dynamic_object_types_by_dir.setdefault(output_directory, _new_dynamic_object_types_bucket())
    bucket["structs"].extend(struct_types)
    bucket["lists"].extend(list_types)
    bucket["interfaces"].extend(interface_types)


def _process_loaded_schema(
    schema: _Schema,
    path: str,
    options: RunFromSchemasOptions,
    context: SchemaWriterContext,
    state: GeneratedSchemaState,
) -> None:
    """Generate stubs for a loaded schema and record the resulting metadata."""
    path_obj = Path(path)
    logger.debug("Processing schema %s from %s", schema.node.displayName, path)
    logger.debug("  Schema ID: %s", hex(schema.node.id))
    logger.debug("  Nested nodes in schema: %s", len(schema.node.nestedNodes))

    output_directory_path = _resolve_output_directory(
        path,
        _python_module_path_for_schema(schema, path, context.schema_loader, context.file_id_to_path),
        options,
    )
    output_directory = str(output_directory_path)
    state.output_directories_used.add(output_directory)

    module_interfaces, dynamic_object_types = _generate_stubs_from_schema(
        schema=schema,
        context=context,
        target=SchemaWriteTarget(
            file_path=path,
            output_file_path=str(output_directory_path / "__init__"),
            module_path_prefix=_resolve_module_path_prefix(options.output_dir, output_directory),
        ),
    )
    _record_generated_module(state, output_directory, module_interfaces, dynamic_object_types, path_obj)


def _ensure_package_init_files(directory: Path) -> None:
    """Create package marker files for a generated directory if needed."""
    init_py_path = directory / "__init__.py"
    init_pyi_path = directory / "__init__.pyi"

    if not init_py_path.exists():
        init_py_path.write_text("# Auto-generated package initialization\n", encoding="utf8")
        logger.debug("Created __init__.py at %s", directory)

    if not init_pyi_path.exists():
        init_pyi_path.write_text("# Auto-generated package initialization\n", encoding="utf8")
        logger.debug("Created __init__.pyi at %s", directory)


def _ensure_parent_package_init_files(output_directory_path: Path, output_dir_path: Path) -> None:
    """Create package marker files on parent directories within the output root."""
    current_dir = output_directory_path.parent
    output_dir_abs = output_dir_path.resolve()

    while True:
        current_dir_abs = current_dir.resolve()
        if current_dir_abs == output_dir_abs:
            return

        if not current_dir_abs.is_relative_to(output_dir_abs):
            return

        _ensure_package_init_files(current_dir)
        parent_dir = current_dir.parent
        if parent_dir == current_dir:
            return
        current_dir = parent_dir


def _ensure_output_packages(output_directories_used: set[str], output_dir_path: Path | None) -> None:
    """Create package marker files for generated output directories and their parents."""
    for output_directory in output_directories_used:
        output_directory_path = Path(output_directory)
        _ensure_package_init_files(output_directory_path)
        if output_dir_path is not None:
            _ensure_parent_package_init_files(output_directory_path, output_dir_path)


def _build_generated_module_name_map(
    schema_loader: capnp.SchemaLoader,
    file_id_to_path: dict[int, str],
    options: RunFromSchemasOptions,
) -> dict[int, str]:
    """Build a map from generated file schema IDs to their importable module names."""
    if not options.output_dir:
        return {}

    generated_module_names_by_schema_id: dict[int, str] = {}
    for schema, path in _iter_loaded_schemas(schema_loader, file_id_to_path, options.file_schemas_only):
        python_module_path = _python_module_path_for_schema(schema, path, schema_loader, file_id_to_path)
        generated_module_name = _resolve_generated_module_name(path, python_module_path, options)
        if generated_module_name is not None:
            generated_module_names_by_schema_id[schema.node.id] = generated_module_name

    return generated_module_names_by_schema_id


def _combine_interfaces_by_dir(
    interfaces_by_dir: dict[str, dict[str, tuple[str, list[str]]]],
) -> dict[str, tuple[str, list[str]]]:
    """Flatten per-directory interface metadata into one mapping."""
    all_interfaces: dict[str, tuple[str, list[str]]] = {}
    for interfaces in interfaces_by_dir.values():
        all_interfaces.update(interfaces)
    return all_interfaces


def _combine_dynamic_object_types(
    dynamic_object_types_by_dir: dict[str, dict[str, list[tuple[str, str]]]],
) -> dict[str, list[tuple[str, str]]]:
    """Flatten per-directory dynamic object metadata into one mapping."""
    all_dynamic_object_types = _new_dynamic_object_types_bucket()
    for types_by_name in dynamic_object_types_by_dir.values():
        all_dynamic_object_types["structs"].extend(types_by_name["structs"])
        all_dynamic_object_types["lists"].extend(types_by_name["lists"])
        all_dynamic_object_types["interfaces"].extend(types_by_name["interfaces"])
    return all_dynamic_object_types


def _resolve_augmented_stubs_dir(
    output_dir: str,
    output_dir_path: Path | None,
    output_directories_used: set[str],
) -> str:
    """Determine where augmented bundled stubs should be written."""
    if output_dir:
        assert output_dir_path is not None
        return str(output_dir_path.resolve())

    output_dirs_list = list(output_directories_used)
    if len(output_dirs_list) == 1:
        return output_dirs_list[0]
    return os.path.commonpath([str(Path(directory).resolve()) for directory in output_dirs_list])


def _augment_bundled_stubs(
    state: GeneratedSchemaState,
    output_dir: str,
    output_dir_path: Path | None,
    *,
    augment_capnp_stubs: bool,
) -> set[str]:
    """Copy and augment bundled capnp stubs when requested."""
    if not augment_capnp_stubs:
        return set()

    source_stubs_path = find_capnp_stubs_package()
    if not source_stubs_path:
        logger.warning("--augment-capnp-stubs specified but capnp-stubs package not found")
        return set()

    all_interfaces = _combine_interfaces_by_dir(state.interfaces_by_dir)
    all_dynamic_object_types = _combine_dynamic_object_types(state.dynamic_object_types_by_dir)
    logger.info(
        "Augmenting capnp-stubs with %s interfaces, %s structs, %s lists, %s interface types",
        len(all_interfaces),
        len(all_dynamic_object_types["structs"]),
        len(all_dynamic_object_types["lists"]),
        len(all_dynamic_object_types["interfaces"]),
    )

    result = augment_capnp_stubs_with_overloads(
        source_stubs_path,
        _resolve_augmented_stubs_dir(output_dir, output_dir_path, state.output_directories_used),
        all_interfaces,
        all_dynamic_object_types,
    )
    if result is None:
        return set()

    capnp_stubs_path, schema_capnp_path = result
    return {path for path in (capnp_stubs_path, schema_capnp_path) if path}


def run_from_schemas(
    schema_loader: capnp.SchemaLoader,
    file_id_to_path: dict[int, str],
    options: RunFromSchemasOptions,
) -> None:
    """Run stub generation from pre-loaded schemas.

    Args:
        schema_loader: SchemaLoader instance with all nodes loaded.
        file_id_to_path: Mapping of schema IDs to file paths.
        options: Output and validation options for generation.

    """
    output_dir_path = Path(options.output_dir) if options.output_dir else None
    writer_context = SchemaWriterContext(
        schema_loader=schema_loader,
        file_id_to_path=file_id_to_path,
        generated_module_names_by_schema_id=_build_generated_module_name_map(schema_loader, file_id_to_path, options),
        inherited_interface_schema_ids=_collect_inherited_interface_schema_ids(schema_loader, file_id_to_path),
    )
    state = GeneratedSchemaState()

    for schema, path in _iter_loaded_schemas(schema_loader, file_id_to_path, options.file_schemas_only):
        _process_loaded_schema(schema, path, options, writer_context, state)

    _ensure_output_packages(state.output_directories_used, output_dir_path)
    bundled_stub_dirs = _augment_bundled_stubs(
        state,
        options.output_dir,
        output_dir_path,
        augment_capnp_stubs=options.augment_capnp_stubs,
    )
    all_output_dirs = state.output_directories_used | bundled_stub_dirs
    format_all_outputs(all_output_dirs, ruff_config_path=options.ruff_config_path)

    if not options.skip_pyright:
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
        file_dir = str(Path(path).resolve().parent)
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

    if depth < MIN_PRESERVED_PATH_DEPTH:
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

    abs_paths = [str(Path(p).resolve()) for p in valid_paths]
    if len(abs_paths) == 1:
        return str(Path(abs_paths[0]).parent)

    common = os.path.commonpath(abs_paths)
    common_path = Path(common)
    return str(common_path.parent) if common_path.is_file() else common


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

    if depth < MIN_PRESERVED_PATH_DEPTH:
        return base

    # Verify files are actually in this directory
    if _all_files_in_directory(valid_paths, base):
        return str(Path(base).parent)

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
        return str(Path(common_base).parent)

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
    absolute_bases: list[str] = []
    relative_bases: list[str] = []

    for pattern in paths:
        # Extract base from pattern (the directory before wildcards)
        base = extract_base_from_pattern(pattern)
        if not base:
            continue

        # Convert to absolute path
        abs_pattern = str(Path(root_directory, pattern)) if not Path(pattern).is_absolute() else pattern

        abs_base = extract_base_from_pattern(abs_pattern)
        if not Path(abs_base).is_absolute():
            abs_base = str(Path(root_directory, abs_base))
        absolute_bases.append(abs_base)

        # Track relative version for depth calculation
        pattern_path = Path(pattern)
        root_path = Path(root_directory)
        if pattern_path.is_absolute():
            if pattern_path.drive and root_path.drive and pattern_path.drive != root_path.drive:
                continue
            rel_pattern = os.path.relpath(pattern, root_directory)
            if not rel_pattern.startswith(".."):
                rel_base = extract_base_from_pattern(rel_pattern)
                if rel_base:
                    relative_bases.append(rel_base)
        else:
            relative_bases.append(base)

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
