"""Generate type hints for *.capnp schemas.

Note: This generator requires pycapnp >= 2.0.0.
"""

from __future__ import annotations

import base64
import contextlib
import logging
import os.path
import pathlib
import re
from copy import copy
from typing import TYPE_CHECKING, Literal

import capnp
from capnp.lib.capnp import (
    _EnumSchema,
    _InterfaceSchema,
    _Schema,
    _StructSchema,
)

from capnp_stub_generator import capnp_types, helper
from capnp_stub_generator.scope import INDENT_SPACES, CapnpType, NoParentError, Scope
from capnp_stub_generator.writer_dto import (
    EnumGenerationContext,
    InterfaceGenerationContext,
    InterfaceMethodTypeNames,
    MethodInfo,
    MethodSignatureCollection,
    ParameterInfo,
    ServerMethodsCollection,
    StructFieldsCollection,
    StructGenerationContext,
)

if TYPE_CHECKING:
    from capnp.lib.capnp import _StructSchemaField

    from schema_capnp import FieldReader, NestedNodeReader, NodeReader, TypeReader

capnp.remove_import_hook()

logger = logging.getLogger(__name__)

InitChoice = tuple[str, str]
GeneratedFieldSchema = _StructSchema | _EnumSchema | _InterfaceSchema
GeneratedTypeAliasInfo = tuple[str, str] | tuple[str, str, list[str]]

# Constants
DISCRIMINANT_NONE = 65535  # Value indicating no discriminant (not part of a union)
MIN_ALIAS_DATA_PARTS = 2
MODULE_PATH_PARTS = 2
ENUM_ALIAS_DATA_PARTS = 3

# Type alias for AnyPointer fields - accepts all pointer types
ANYPOINTER_TYPE = "str | bytes | _DynamicStructBuilder | _DynamicStructReader | _DynamicCapabilityClient | _DynamicCapabilityServer | _DynamicListBuilder | _DynamicListReader | _DynamicObjectReader | _DynamicObjectBuilder"
CAPABILITY_TYPE = "_DynamicCapabilityClient | _DynamicCapabilityServer | _DynamicObjectReader | _DynamicObjectBuilder"
ANYSTRUCT_TYPE = "_DynamicStructBuilder | _DynamicStructReader | _DynamicObjectReader | _DynamicObjectBuilder"
ANYLIST_TYPE = "_DynamicListBuilder | _DynamicListReader | _DynamicObjectReader | _DynamicObjectBuilder"

# Expected best-effort failures while traversing partially loaded pycapnp schemas.
SCHEMA_LOOKUP_EXCEPTIONS = (capnp.KjException,)
ANNOTATION_ACCESS_EXCEPTIONS = (*SCHEMA_LOOKUP_EXCEPTIONS, AttributeError)
TYPE_GENERATION_EXCEPTIONS = (*SCHEMA_LOOKUP_EXCEPTIONS, KeyError, NoParentError)
TYPE_RESOLUTION_EXCEPTIONS = (*TYPE_GENERATION_EXCEPTIONS, TypeError)
SCHEMA_SERIALIZATION_EXCEPTIONS = (*SCHEMA_LOOKUP_EXCEPTIONS, AttributeError)


class Writer:
    """A class that handles writing the stub file, based on a provided module definition."""

    type VALID_TYPING_IMPORTS = Literal[
        "Iterator",
        "Generic",
        "TypeVar",
        "Sequence",
        "Literal",
        "Union",
        "overload",
        "Protocol",
        "Any",
        "BinaryIO",
        "Awaitable",
        "NamedTuple",
        "Self",
        "TypeAlias",
        "override",
        "MutableSequence",
        "IO",
        "Callable",
    ]

    def __init__(  # noqa: PLR0913
        self,
        schema: _Schema,
        file_path: str,
        schema_loader: capnp.SchemaLoader,
        file_id_to_path: dict[int, str],
        generated_module_names_by_schema_id: dict[int, str] | None = None,
        inherited_interface_schema_ids: set[int] | None = None,
    ) -> None:
        """Initialize the stub writer with schema information.

        Args:
            schema: The root schema to parse and write stubs for.
            file_path: Path to the schema file (e.g., "path/to/schema.capnp").
            schema_loader: SchemaLoader instance with all nodes loaded.
            file_id_to_path: Mapping of schema IDs to file paths for resolving imports.
            generated_module_names_by_schema_id: Generated module names keyed by file schema ID.
            inherited_interface_schema_ids: Interface schema IDs that appear as superclasses anywhere in the loaded graph.

        """
        self.scope: Scope = Scope(name="", id=schema.node.id, parent=None, return_scope=None)
        self.scopes_by_id: dict[int, Scope] = {self.scope.id: self.scope}

        self._schema: _Schema = schema
        self._schema_loader: capnp.SchemaLoader = schema_loader
        self._file_id_to_path: dict[int, str] = file_id_to_path
        self._generated_module_names_by_schema_id: dict[int, str] = generated_module_names_by_schema_id or {}

        self._module_path: pathlib.Path = pathlib.Path(file_path)

        # Python module annotation ID (from python.capnp: annotation module(file): Text)
        self._python_module_annotation_id: int = 0x8C5EA3FEE3B0F96C
        self._python_module_path: str | None = self._get_python_module_annotation()

        # Build a flat mapping of all schemas by ID for nested type resolution
        self._schemas_by_id: dict[int, capnp_types.SchemaType] = {}
        self._build_schema_id_mapping()
        discovered_inherited_interface_schema_ids = {
            superclass.id
            for loaded_schema in self._schemas_by_id.values()
            if loaded_schema.node.which() == capnp_types.CapnpElementType.INTERFACE
            for superclass in loaded_schema.node.interface.superclasses
        }
        self._inherited_interface_schema_ids: set[int] = (
            discovered_inherited_interface_schema_ids
            if inherited_interface_schema_ids is None
            else discovered_inherited_interface_schema_ids | inherited_interface_schema_ids
        )

        self._imports: list[str] = []
        self._add_import("from __future__ import annotations")
        self._add_import(
            "from capnp.lib.capnp import _DynamicCapabilityClient, _DynamicCapabilityServer, _DynamicStructBuilder, _DynamicStructReader, _DynamicListBuilder, _DynamicListReader, _DynamicObjectBuilder, _DynamicObjectReader, _InterfaceModule, _Request, _StructModule",
        )

        self._typing_imports: set[Writer.VALID_TYPING_IMPORTS] = set()

        self.type_vars: set[str] = set()
        self.type_map: dict[int, CapnpType] = {}

        # Track imported module paths for capnp.load imports parameter
        self._imported_module_paths: set[pathlib.Path] = set()
        self._imported_aliases: set[str] = set()

        # Track all server NamedTuples globally (scope_name -> {method_name: (namedtuple_name, fields)})
        self._all_server_namedtuples: dict[str, dict[str, tuple[str, list[tuple[str, str]]]]] = {}

        # Track all interfaces for cast_as overloads (interface_name -> (client_name, base_client_names))
        self._all_interfaces: dict[str, tuple[str, list[str]]] = {}

        # Track all generated types for top-level TypeAliases
        # Format: {flat_name: (protocol_path, type_kind, [enum_values])} where type_kind is "Reader", "Builder", "Client", or "Enum"
        self._all_type_aliases: dict[str, GeneratedTypeAliasInfo] = {}
        self._runtime_server_aliases: dict[str, str] = {}
        self._root_module_class_names: set[str] = set()
        self._schema_helper_export_targets: dict[str, str] = {}

        # Track if we need _DynamicObjectReader augmentation (for AnyPointer in interface returns)
        # Always enable this to generate as_struct/as_interface overloads for all types
        self._needs_dynamic_object_reader_augmentation: bool = True

        # Track if we need AnyPointer type alias (for generic parameter fields)
        self._needs_anypointer_alias: bool = False
        self._needs_capability_alias: bool = False
        self._needs_anystruct_alias: bool = False
        self._needs_anylist_alias: bool = False

        # Track generated list types to avoid duplicates
        self._generated_list_types: set[str] = set()
        self._generated_client_classes: set[str] = set()
        self._generated_interface_helper_types: set[str] = set()

        self.docstring: str = f'"""This is an automatically generated stub for `{self._module_path.name}`."""'

    def _get_python_module_annotation(self) -> str | None:
        """Extract Python module path from $Python.module() annotation.

        Returns:
            The Python module path (e.g., "mas.schema.climate") or None if not present.

        """
        try:
            for annotation in self._schema.node.annotations:
                if annotation.id == self._python_module_annotation_id and annotation.value.which() == "text":
                    module_path = annotation.value.text
                    logger.info("Found Python module annotation: %s", module_path)
                    return module_path
        except ANNOTATION_ACCESS_EXCEPTIONS as error:
            logger.debug("Error reading Python module annotation: %s", error)
        return None

    def get_python_module_for_schema(self, schema_id: int) -> str | None:
        """Get the Python module path for a schema by ID.

        Looks up the schema in the loader and extracts its Python module annotation.

        Args:
            schema_id: The schema ID to look up.

        Returns:
            The Python module path (e.g., "mas.schema.common") or None if not found.

        """
        try:
            schema = self._schema_loader.get(schema_id)
            for annotation in schema.node.annotations:
                if annotation.id == self._python_module_annotation_id and annotation.value.which() == "text":
                    return annotation.value.text
        except ANNOTATION_ACCESS_EXCEPTIONS as error:
            logger.debug("Error reading Python module annotation from schema %s: %s", hex(schema_id), error)

        return None

    def _build_schema_id_mapping(self) -> None:
        """Build a flat mapping of all schemas by their ID.

        This walks through ALL schemas available in the loader, including:
        - The root schema
        - All nested nodes recursively
        - Schemas from other files (for cross-file references)
        """
        self._add_schema_and_nested(self._schema)

        logger.debug("Built schema ID mapping with %s schemas", len(self._schemas_by_id))
        if len(self._schemas_by_id) == 0:
            logger.warning("Schema ID mapping is empty! This will result in empty stubs.")
            logger.warning("Root schema ID: %s", hex(self._schema.node.id))

    def _add_schema_and_nested(self, schema: capnp_types.SchemaType) -> None:
        """Recursively add a schema and its nested or referenced schemas to the mapping."""
        schema_id = schema.node.id
        if schema_id in self._schemas_by_id:
            return

        self._schemas_by_id[schema_id] = schema
        self._add_nested_node_schemas(schema)
        self._add_struct_field_schemas(schema)
        self._add_interface_method_schemas(schema)

    def _add_nested_node_schemas(self, schema: capnp_types.SchemaType) -> None:
        """Add schemas reachable from nested nodes."""
        for nested_node in schema.node.nestedNodes:
            nested_id = nested_node.id
            if nested_id in self._schemas_by_id:
                continue
            try:
                nested_schema = self._schema_loader.get(nested_id)
            except SCHEMA_LOOKUP_EXCEPTIONS as error:
                logger.debug(
                    "Could not resolve nested schema %s (id=%s) for %s: %s",
                    nested_node.name,
                    hex(nested_id),
                    schema.node.displayName,
                    error,
                )
                continue
            self._add_schema_and_nested(nested_schema)

    def _collect_referenced_type_ids(self, type_obj: TypeReader) -> list[int]:
        """Extract all schema IDs referenced by a field type."""
        type_which = type_obj.which()
        if type_which == "list":
            return self._collect_referenced_type_ids(type_obj.list.elementType)
        if type_which in {"struct", "interface", "enum"}:
            return [getattr(type_obj, type_which).typeId]
        return []

    def _add_struct_field_schemas(self, schema: capnp_types.SchemaType) -> None:
        """Add schemas referenced by struct fields."""
        if schema.node.which() != capnp_types.CapnpElementType.STRUCT:
            return

        for field in schema.node.struct.fields:
            if field.which() == "group":
                self._add_group_field_schema(field)
                continue
            if field.which() == "slot":
                self._add_slot_field_schemas(field)

    def _add_group_field_schema(self, field: FieldReader) -> None:
        """Add the schema referenced by a group field."""
        group_id = field.group.typeId
        if group_id in self._schemas_by_id:
            return
        try:
            group_schema = self._schema_loader.get(group_id)
        except SCHEMA_LOOKUP_EXCEPTIONS as error:
            logger.warning("Group field %s references schema %s not in loader: %s", field.name, hex(group_id), error)
            return
        self._add_schema_and_nested(group_schema)

    def _add_slot_field_schemas(self, field: FieldReader) -> None:
        """Add schemas referenced by a slot field."""
        for ref_id in self._collect_referenced_type_ids(field.slot.type):
            if ref_id in self._schemas_by_id:
                continue
            try:
                referenced_schema = self._schema_loader.get(ref_id)
            except SCHEMA_LOOKUP_EXCEPTIONS as error:
                logger.debug("Could not load referenced type %s for field %s: %s", hex(ref_id), field.name, error)
                continue
            self._add_schema_and_nested(referenced_schema)

    def _add_interface_method_schemas(self, schema: capnp_types.SchemaType) -> None:
        """Add implicit param/result struct schemas for interface methods."""
        if schema.node.which() != capnp_types.CapnpElementType.INTERFACE:
            return

        for superclass in schema.node.interface.superclasses:
            self._add_interface_superclass_schema(superclass.id)

        for method in schema.node.interface.methods:
            self._add_method_struct_schema(method.paramStructType, method.name, "param")
            self._add_method_struct_schema(method.resultStructType, method.name, "result")

    def _add_interface_superclass_schema(self, schema_id: int) -> None:
        """Add the schema referenced by an interface superclass."""
        if schema_id in self._schemas_by_id:
            return
        try:
            superclass_schema = self._schema_loader.get(schema_id)
        except SCHEMA_LOOKUP_EXCEPTIONS as error:
            logger.debug("Could not load superclass schema %s: %s", hex(schema_id), error)
            return
        self._add_schema_and_nested(superclass_schema)

    def _add_method_struct_schema(self, schema_id: int, method_name: str, schema_kind: str) -> None:
        """Add a method parameter or result struct schema."""
        if schema_id in self._schemas_by_id:
            return
        try:
            method_schema = self._schema_loader.get(schema_id)
        except SCHEMA_LOOKUP_EXCEPTIONS as error:
            logger.debug(
                "Could not load %s struct for method %s (id=%s): %s", schema_kind, method_name, hex(schema_id), error
            )
            return
        self._add_schema_and_nested(method_schema)

    def _extract_name_from_protocol(self, protocol_name: str) -> str:
        """Extract user-facing name from Protocol name.

        Handles:
        - _{Name}StructModule -> {Name}
        - _{Name}InterfaceModule -> {Name}
        - _{Name}EnumModule -> {Name}
        - _{Name}Module -> {Name} (legacy/base)
        """
        if not protocol_name.startswith("_"):
            return protocol_name

        if protocol_name.endswith("StructModule"):
            return protocol_name[1:-12]
        if protocol_name.endswith("InterfaceModule"):
            return protocol_name[1:-15]
        if protocol_name.endswith("EnumModule"):
            return protocol_name[1:-10]
        if protocol_name.endswith("Module"):
            return protocol_name[1:-6]

        return protocol_name

    def _build_nested_builder_type(self, base_type: str) -> str:
        """Convert a type name to its Builder form using nested class syntax.

        Args:
            base_type: The base type name (e.g., "Outer.Inner")

        Returns:
            The Builder type name (e.g., "Outer.Inner.Builder")

        """
        return f"{base_type}.Builder"

    def _build_nested_reader_type(self, base_type: str) -> str:
        """Convert a type name to its Reader form using nested class syntax.

        Args:
            base_type: The base type name (e.g., "Outer.Inner")

        Returns:
            The Reader type name (e.g., "Outer.Inner.Reader")

        """
        return f"{base_type}.Reader"

    def _get_flat_builder_alias(self, module_type: str) -> str | None:
        """Convert a module type path to its flat Builder alias name if defined in this module.

        Args:
            module_type: The module type path (e.g., "_CalculatorModule._ExpressionModule")

        Returns:
            The flat Builder alias name if the type is defined in this module (e.g., "ExpressionBuilder"),
            or None if the type is imported from another module

        """
        # Extract the last component (e.g., "_ExpressionStructModule")
        last_part = module_type.rsplit(".", maxsplit=1)[-1]
        # Remove "_" prefix and "Module" suffix to get the base name
        if last_part.startswith("_"):
            base_name = self._extract_name_from_protocol(last_part)
            alias_name = helper.new_builder_flat(base_name)
            # Check if this alias is defined in the current module
            if alias_name in self._all_type_aliases:
                return alias_name
            # Also check if it's an imported alias
            if alias_name in self._imported_aliases:
                return alias_name
        return None

    def _get_flat_reader_alias(self, module_type: str) -> str | None:
        """Convert a module type path to its flat Reader alias name if defined in this module.

        Args:
            module_type: The module type path (e.g., "_CalculatorModule._ExpressionModule")

        Returns:
            The flat Reader alias name if the type is defined in this module (e.g., "ExpressionReader"),
            or None if the type is imported from another module

        """
        # Extract the last component (e.g., "_ExpressionStructModule")
        last_part = module_type.rsplit(".", maxsplit=1)[-1]
        # Remove "_" prefix and "Module" suffix to get the base name
        if last_part.startswith("_"):
            base_name = self._extract_name_from_protocol(last_part)
            alias_name = helper.new_reader_flat(base_name)
            # Check if this alias is defined in the current module
            if alias_name in self._all_type_aliases:
                return alias_name
            # Also check if it's an imported alias
            if alias_name in self._imported_aliases:
                return alias_name
        return None

    def _get_flat_client_alias(self, module_type: str) -> str | None:
        """Convert an interface module type path to its flat Client alias name if defined in this module.

        Args:
            module_type: The interface module type path (e.g., "_CalculatorModule._ValueModule")

        Returns:
            The flat Client alias name if the type is defined in this module (e.g., "ValueClient"),
            or None if the type is imported from another module

        """
        interface_info = self._all_interfaces.get(module_type)
        if interface_info is not None:
            return interface_info[0]

        # Extract the last component (e.g., "_ValueInterfaceModule")
        last_part = module_type.rsplit(".", maxsplit=1)[-1]
        # Remove "_" prefix and "Module" suffix to get the base name
        if last_part.startswith("_"):
            base_name = self._extract_name_from_protocol(last_part)
            alias_name = f"{base_name}Client"
            # Check if this alias is defined in the current module
            if alias_name in self._all_type_aliases:
                return alias_name
            # Also check if it's an imported alias
            if alias_name in self._imported_aliases:
                return alias_name
        return None

    def _protocol_path_to_runtime_path(self, path: str) -> str:
        """Convert Protocol module path to runtime-accessible path.

        This handles nested interfaces where the scoped name uses Protocol module names
        but the runtime uses user-facing names.

        Args:
            path: Protocol-based path (e.g., "_HostPortResolverModule.Registrar")

        Returns:
            Runtime-accessible path (e.g., "HostPortResolver.Registrar")

        Examples:
            "_HostPortResolverModule.Registrar" -> "HostPortResolver.Registrar"
            "_PersistentModule.ReleaseSturdyRef" -> "Persistent.ReleaseSturdyRef"
            "Gateway" -> "Gateway"

        """
        parts = path.split(".")
        runtime_parts: list[str] = []
        for part in parts:
            if part.startswith("_"):
                # Strip "_" prefix and "Module" suffix to get user-facing name
                runtime_parts.append(self._extract_name_from_protocol(part))
            else:
                runtime_parts.append(part)
        return ".".join(runtime_parts)

    def _add_typing_import(self, module_name: Writer.VALID_TYPING_IMPORTS) -> None:
        """Add an import for a module from the 'typing' package.

        E.g., when using
        add_typing_import("Sequence")
        add_typing_import("Union")

        this generates an import line `from typing import Sequence, Union`.

        Args:
            module_name (Writer.VALID_TYPING_IMPORTS): The module to import from `typing`.

        """
        self._typing_imports.add(module_name)

    def _add_import(self, import_line: str) -> None:
        """Add a full import line.

        E.g. 'import numpy as np'.

        Args:
            import_line (str): The import line to add.

        """
        # Preserve insertion order while avoiding duplicates
        if import_line not in self._imports:
            self._imports.append(import_line)

    def _add_enum_import(self) -> None:
        """Retain the deprecated `Enum` import helper for compatibility."""
        # Note: _EnumModule is already imported in __init__, so this method is now a no-op
        # We keep it for compatibility with existing code structure

    @property
    def full_display_name(self) -> str:
        """The base name of this writer's target module."""
        return self._schema.node.displayName

    @property
    def display_name(self) -> str:
        """The base name of this writer's target module."""
        return pathlib.Path(self._schema.node.displayName).name

    @property
    def imports(self) -> list[str]:
        """Get the full list of import strings that were added to the writer, including typing imports.

        Returns:
            list[str]: The list of imports that were previously added.

        """
        import_lines = self._imports.copy()

        if self._typing_imports:
            # Consolidate typing imports deterministically.
            # Iterator and Sequence should be imported from collections.abc.
            order = [
                "Iterator",
                "Literal",
                "Sequence",
                "overload",
                "override",
                "Generic",
                "TypeVar",
                "Union",
                "Protocol",
                "Any",
            ]
            names = [n for n in order if n in self._typing_imports]
            extra = sorted(self._typing_imports.difference(set(names)))
            names.extend(extra)

            # Split names into collections.abc vs typing
            collections_abc_names = [
                n for n in names if n in ("Iterator", "Sequence", "Awaitable", "MutableSequence", "Callable")
            ]
            typing_names = [
                n for n in names if n not in ("Iterator", "Sequence", "Awaitable", "MutableSequence", "Callable")
            ]

            if collections_abc_names:
                import_lines.append("from collections.abc import " + ", ".join(collections_abc_names))

            if typing_names:
                import_lines.append("from typing import " + ", ".join(typing_names))

        return import_lines

    # ===== Helper Methods for Type Name Manipulation =====

    def _build_scoped_builder_type(self, field_type: str) -> str:
        """Build Builder type name using nested class syntax.

        Args:
            field_type (str): The base field type (e.g., "MyStruct", "Outer.Inner", or "Env[T]").

        Returns:
            str: The Builder type name (e.g., "MyStruct.Builder", "Outer.Inner.Builder", or "Env.Builder[T]").

        """
        return helper.new_builder(field_type)

    def _get_scope_path(self, scope: Scope | None = None) -> str:
        """Get the scope path as a dotted string.

        Args:
            scope (Scope | None): The scope to get path for (defaults to current scope).

        Returns:
            str: The scope path (e.g., "OuterStruct.InnerStruct").

        """
        if scope is None:
            scope = self.scope
        return ".".join(s.name for s in scope.trace if not s.is_root)

    def _create_capnp_limit_params(self) -> list[helper.TypeHintedVariable]:
        """Create standard Cap'n Proto traversal and nesting limit parameters.

        These parameters are used in all deserialization methods (from_bytes,
        from_bytes_packed, read, read_packed) to control security limits.

        Returns:
            List containing traversal_limit_in_words and nesting_limit parameters.

        """
        return [
            helper.TypeHintedVariable(
                "traversal_limit_in_words",
                [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                default="None",
            ),
            helper.TypeHintedVariable(
                "nesting_limit",
                [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                default="None",
            ),
        ]

    def _add_from_bytes_methods(self, scoped_reader_type: str, scoped_builder_type: str) -> None:
        """Add from_bytes and from_bytes_packed instance methods to current scope.

        These are instance methods on the module that override base class methods.

        Args:
            scoped_reader_type (str): The Reader type name (can be flat alias or scoped).
            scoped_builder_type (str): The Builder type name (can be flat alias or scoped).

        """
        self._add_import("from contextlib import AbstractContextManager")
        self._add_typing_import("Literal")
        self._add_typing_import("overload")
        self._add_typing_import("override")

        buf_param = helper.TypeHintedVariable("buf", [helper.TypeHint("bytes", primary=True)])

        # from_bytes overload 1: no builder parameter (returns Reader)
        self.scope.add("@override")
        self.scope.add(helper.new_decorator("overload"))
        self.scope.add(
            helper.new_function(
                "from_bytes",
                parameters=["self", buf_param, *self._create_capnp_limit_params()],
                return_type=helper.new_type_group("AbstractContextManager", [scoped_reader_type]),
            ),
        )

        # from_bytes overload 2: builder=False (returns Reader)
        builder_kwarg = helper.TypeHintedVariable("builder", [helper.TypeHint("Literal[False]", primary=True)])
        self.scope.add(helper.new_decorator("overload"))
        self.scope.add(
            helper.new_function(
                "from_bytes",
                parameters=["self", buf_param, *self._create_capnp_limit_params(), "*", builder_kwarg],
                return_type=helper.new_type_group("AbstractContextManager", [scoped_reader_type]),
            ),
        )

        # from_bytes overload 3: builder=True (returns Builder)
        builder_kwarg_true = helper.TypeHintedVariable("builder", [helper.TypeHint("Literal[True]", primary=True)])
        self.scope.add(helper.new_decorator("overload"))
        self.scope.add(
            helper.new_function(
                "from_bytes",
                parameters=["self", buf_param, *self._create_capnp_limit_params(), "*", builder_kwarg_true],
                return_type=helper.new_type_group("AbstractContextManager", [scoped_builder_type]),
            ),
        )

        # from_bytes_packed method - returns bare _DynamicStructReader, not override
        self.scope.add("@override")
        self.scope.add(
            helper.new_function(
                "from_bytes_packed",
                parameters=["self", buf_param, *self._create_capnp_limit_params()],
                return_type="_DynamicStructReader",
            ),
        )

    def _add_read_methods(self, scoped_reader_type: str) -> None:
        """Add read and read_packed instance methods to current scope.

        These are instance methods on the module that override base class methods.

        Args:
            scoped_reader_type (str): The Reader type name (can be flat alias or scoped).

        """
        self._add_typing_import("IO")

        file_param = helper.TypeHintedVariable("file", [helper.TypeHint("IO[str] | IO[bytes]", primary=True)])

        # read method
        self.scope.add(helper.new_decorator("override"))
        self.scope.add(
            helper.new_function(
                "read",
                parameters=["self", file_param, *self._create_capnp_limit_params()],
                return_type=scoped_reader_type,
            ),
        )

        # read_packed method
        self.scope.add(helper.new_decorator("override"))
        self.scope.add(
            helper.new_function(
                "read_packed",
                parameters=["self", file_param, *self._create_capnp_limit_params()],
                return_type=scoped_reader_type,
            ),
        )

    def _get_reader_property_type(self, field: helper.TypeHintedVariable) -> str:
        """Determine the property type for Reader class fields.

        Args:
            field: The field to get the type for

        Returns:
            Type string appropriate for Reader property getter

        """
        if field.has_type_hint_with_reader_affix:
            # Get the narrowed Reader-only type for this field
            return field.get_type_with_affixes([helper.READER_NAME])
        # Primitive and other fields with their primary type
        return field.primary_type_nested

    def _to_mutable_sequence_type(self, type_name: str) -> str:
        """Convert Sequence[T] to MutableSequence[T] for builder-facing getters."""
        if "Sequence[" not in type_name:
            return type_name

        self._add_typing_import("MutableSequence")
        return type_name.replace("Sequence[", "MutableSequence[")

    def _get_special_builder_property_types(
        self,
        field: helper.TypeHintedVariable,
    ) -> tuple[str, str] | None:
        """Handle special builder property cases that need alias types."""
        if field.is_generic_param:
            self._needs_anypointer_alias = True
            return field.primary_type_nested, "AnyPointer"

        if field.is_any_pointer:
            self._needs_anypointer_alias = True
            return field.get_type_with_affixes([helper.BUILDER_NAME]), "AnyPointer"

        if field.is_any_struct:
            self._needs_anystruct_alias = True
            self._add_typing_import("Any")
            return field.get_type_with_affixes([helper.BUILDER_NAME]), "AnyStruct | dict[str, Any]"

        if field.is_any_list:
            self._needs_anylist_alias = True
            self._add_typing_import("Sequence")
            self._add_typing_import("Any")
            return field.get_type_with_affixes([helper.BUILDER_NAME]), "AnyList | Sequence[Any]"

        if field.is_capability:
            self._needs_capability_alias = True
            return field.primary_type_nested, "Capability"

        return None

    def _get_affixed_builder_property_types(self, field: helper.TypeHintedVariable) -> tuple[str, str]:
        """Build getter and setter types for struct and list fields on Builder."""
        getter_type = self._to_mutable_sequence_type(field.get_type_with_affixes([helper.BUILDER_NAME]))
        setter_types = field.get_type_with_affixes([helper.BUILDER_NAME, helper.READER_NAME])

        if field.nesting_depth == 1:
            self._add_typing_import("Sequence")
            self._add_typing_import("Any")
            return getter_type, f"{setter_types} | Sequence[dict[str, Any]]"

        self._add_typing_import("Any")
        return getter_type, f"{setter_types} | dict[str, Any]"

    @staticmethod
    def _has_interface_server_hint(field: helper.TypeHintedVariable) -> bool:
        """Return whether a field includes an interface Server setter variant."""
        return len(field.type_hints) > 1 and any(".Server" in str(type_hint) for type_hint in field.type_hints)

    def _get_builder_property_types(self, field: helper.TypeHintedVariable) -> tuple[str, str | None]:
        """Determine getter and setter types for Builder class fields.

        Args:
            field: The field to get the types for

        Returns:
            Tuple of (getter_type, setter_type). setter_type is None if same as getter.

        """
        special_types = self._get_special_builder_property_types(field)
        if special_types is not None:
            return special_types

        if field.has_type_hint_with_builder_affix:
            return self._get_affixed_builder_property_types(field)

        getter_type = self._to_mutable_sequence_type(field.primary_type_nested)
        if self._has_interface_server_hint(field):
            return getter_type, field.full_type_nested

        setter_type = field.full_type_nested if field.full_type_nested != getter_type else None
        return getter_type, setter_type

    def _add_properties(
        self, slot_fields: list[helper.TypeHintedVariable], mode: Literal["base", "reader", "builder"]
    ) -> None:
        """Add properties to current scope based on mode.

        Args:
            slot_fields: Fields to add as properties
            mode: "base" (none), "reader" (read-only), or "builder" (with setters)

        """
        if mode == "base":
            # Base class (StructModule) does not have field properties
            # Properties are only on Reader and Builder classes
            return

        for slot_field in slot_fields:
            field_copy = copy(slot_field)

            if mode == "reader":
                field_type = self._get_reader_property_type(field_copy)
                should_override = slot_field.name == "schema"
                for line in helper.new_property(slot_field.name, field_type, add_override=should_override):
                    self.scope.add(line)

            elif mode == "builder":
                getter_type, setter_type = self._get_builder_property_types(field_copy)
                should_override = slot_field.name == "schema"
                for line in helper.new_property(
                    slot_field.name,
                    getter_type,
                    with_setter=True,
                    setter_type=setter_type,
                    add_override=should_override,
                ):
                    self.scope.add(line)

    def _add_reader_properties(self, slot_fields: list[helper.TypeHintedVariable]) -> None:
        """Add read-only properties to Reader class.

        Args:
            slot_fields (list[helper.TypeHintedVariable]): The fields to add as properties.

        """
        self._add_properties(slot_fields, "reader")

    def _add_builder_properties(self, slot_fields: list[helper.TypeHintedVariable]) -> None:
        """Add mutable properties with setters to Builder class.

        Args:
            slot_fields (list[helper.TypeHintedVariable]): The fields to add as properties.

        """
        self._add_properties(slot_fields, "builder")

    def _add_builder_init_overloads(
        self,
        init_choices: list[InitChoice],
        list_init_choices: list[tuple[str, str]],
    ) -> None:
        """Add init method overloads to Builder class.

        Args:
            init_choices (list[InitChoice]): List of (field_name, field_type) tuples for struct/group fields.
            list_init_choices (list[tuple[str, str]]): List of (field_name, builder_type) for list fields.

        """
        resolved_init_choices = [
            (field_name, self._get_flat_builder_alias(field_type) or self._build_scoped_builder_type(field_type))
            for field_name, field_type in init_choices
        ]
        total_init_overloads = len(resolved_init_choices) + len(list_init_choices)
        use_overload = total_init_overloads > 1

        if use_overload:
            self._add_typing_import("overload")
        if resolved_init_choices or list_init_choices:
            self._add_typing_import("Literal")

        # Note: The init() method parameter is now LiteralString in pycapnp stubs
        # This allows our Literal["fieldname"] overloads to be compatible

        if resolved_init_choices or list_init_choices:
            self.scope.add("@override")

        for field_name, builder_type in [*resolved_init_choices, *list_init_choices]:
            if use_overload:
                self.scope.add(helper.new_decorator("overload"))
            self.scope.add(
                helper.new_function(
                    "init",
                    parameters=[
                        "self",
                        helper.TypeHintedVariable("field", [helper.TypeHint(f'Literal["{field_name}"]', primary=True)]),
                        helper.TypeHintedVariable(
                            "size",
                            [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                            default="None",
                        ),
                    ],
                    return_type=builder_type,
                ),
            )

        # Add catchall overload if we added any specific overloads
        if use_overload:
            self.scope.add(helper.new_decorator("overload"))
            catchall_params = [
                "self",
                helper.TypeHintedVariable("field", [helper.TypeHint("str", primary=True)]),
                helper.TypeHintedVariable(
                    "size",
                    [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                    default="None",
                ),
            ]
            self.scope.add(
                helper.new_function(
                    "init",
                    parameters=catchall_params,
                    return_type="Any",
                ),
            )

    def _add_which_method(self, schema: _StructSchema) -> None:
        """Add which() method override for unions with specific Literal return type.

        Args:
            schema: The struct schema containing potential union fields.

        """
        if schema.node.struct.discriminantCount:
            self._add_typing_import("Literal")
            self._add_typing_import("override")
            field_names = [
                f'"{field.name}"' for field in schema.node.struct.fields if field.discriminantValue != DISCRIMINANT_NONE
            ]
            return_type = helper.new_type_group("Literal", field_names)
            self.scope.add("@override")
            self.scope.add(helper.new_function("which", parameters=["self"], return_type=return_type))

    # ===== Struct Generation Helper Methods =====

    def _add_new_message_method(
        self,
        slot_fields: list[helper.TypeHintedVariable],
        builder_type_name: str,
    ) -> None:
        """Add new_message instance method override with field parameters as kwargs.

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields to add as parameters.
            builder_type_name (str): The Builder type name to return (flat alias).

        """
        self._add_typing_import("Callable")
        new_message_params: list[helper.TypeHintedVariable | str] = [
            "self",
            helper.TypeHintedVariable(
                "num_first_segment_words",
                [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                default="None",
            ),
            helper.TypeHintedVariable(
                "allocate_seg_callable",
                [helper.TypeHint("Callable[[int], bytearray]", primary=True), helper.TypeHint("None")],
                default="None",
            ),
        ]

        # Add each field as an optional kwarg parameter
        for slot_field in slot_fields:
            # Handle generic parameters specially
            if slot_field.is_generic_param:
                # Generic parameters accept only pointer types (structs, lists, blobs, interfaces)
                # Primitives (int, float, bool) are NOT allowed per Cap'n Proto spec
                field_type = "AnyPointer"
                self._needs_anypointer_alias = True
                type_hints = [helper.TypeHint(field_type, primary=True), helper.TypeHint("None")]
            # Handle AnyPointer fields specially
            elif slot_field.is_any_pointer:
                field_type = "AnyPointer"
                self._needs_anypointer_alias = True
                type_hints = [helper.TypeHint(field_type, primary=True), helper.TypeHint("None")]
            # Handle AnyStruct fields specially
            elif slot_field.is_any_struct:
                field_type = "AnyStruct"
                self._needs_anystruct_alias = True
                type_hints = [helper.TypeHint(field_type, primary=True)]
                type_hints.append(helper.TypeHint("dict[str, Any]"))
                self._add_typing_import("Any")
                type_hints.append(helper.TypeHint("None"))
            # Handle AnyList fields specially
            elif slot_field.is_any_list:
                field_type = "AnyList"
                self._needs_anylist_alias = True
                type_hints = [helper.TypeHint(field_type, primary=True)]
                type_hints.append(helper.TypeHint("Sequence[Any]"))
                self._add_typing_import("Sequence")
                self._add_typing_import("Any")
                type_hints.append(helper.TypeHint("None"))
            # Handle Capability fields specially
            elif slot_field.is_capability:
                field_type = "Capability"
                self._needs_capability_alias = True
                type_hints = [helper.TypeHint(field_type, primary=True), helper.TypeHint("None")]
            else:
                # Get the type suitable for initialization (Builder types for struct fields)
                field_type = (
                    slot_field.get_type_with_affixes(["Builder"])
                    if slot_field.has_type_hint_with_builder_affix
                    else slot_field.full_type_nested
                )
                # For struct fields, also accept dict for initialization
                type_hints = [helper.TypeHint(field_type, primary=True)]
                if slot_field.has_type_hint_with_builder_affix:
                    if slot_field.nesting_depth == 0:
                        # Non-list struct fields accept dict directly
                        type_hints.append(helper.TypeHint("dict[str, Any]"))
                        self._add_typing_import("Any")
                    elif slot_field.nesting_depth == 1:
                        # List of struct fields accept Sequence[dict]
                        type_hints.append(helper.TypeHint("Sequence[dict[str, Any]]"))
                        self._add_typing_import("Sequence")
                        self._add_typing_import("Any")
                type_hints.append(helper.TypeHint("None"))

            # Make field optional since not all fields need to be set
            field_param = helper.TypeHintedVariable(
                slot_field.name,
                type_hints,
                default="None",
            )
            new_message_params.append(field_param)

        # Add **kwargs: object as a safe catch-all for runtime-accepted keyword forwarding.
        new_message_params.append("**kwargs: object")

        # Add as instance method with @override decorator
        self.scope.add("@override")
        self.scope.add(helper.new_function("new_message", new_message_params, builder_type_name))

    def _gen_struct_base_class(
        self,
        slot_fields: list[helper.TypeHintedVariable],
        reader_type_name: str,
        builder_type_name: str,
    ) -> None:
        """Generate the base struct class with minimal overrides.

        Now inherits from _StructModule, so we only need to add:
        - new_message with field parameters (overriding base)
        - read methods (from_bytes, from_bytes_packed, read, read_packed) with correct Reader return type

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields.
            init_choices (list[InitChoice]): Init method overload choices.
            schema (_StructSchema): The struct schema.
            reader_type_name (str): Reader type name (flat alias).
            builder_type_name (str): Builder type name (flat alias).

        """
        # Add new_message method override with field parameters
        self._add_typing_import("override")
        self._add_new_message_method(slot_fields, builder_type_name)

        # Add read method overrides with correct Reader and Builder return types (flat aliases)
        self._add_from_bytes_methods(reader_type_name, builder_type_name)
        self._add_read_methods(reader_type_name)

    def _ensure_schema_helper_support(self) -> None:
        """Ensure imports required by generated schema helper types are present."""
        self._add_import(
            "from capnp.lib.capnp import _EnumSchema, _InterfaceMethod, _InterfaceSchema, _ListSchema, _StructSchema, _StructSchemaField",
        )
        self._add_typing_import("Literal")
        self._add_typing_import("overload")
        self._add_typing_import("override")

    @staticmethod
    def _indent_relative_lines(lines: list[str], levels: int = 1) -> list[str]:
        """Indent helper lines relative to their containing generated scope."""
        prefix = " " * (INDENT_SPACES * levels)
        return [f"{prefix}{line}" if line else "" for line in lines]

    @staticmethod
    def _schema_helper_token(name: str) -> str:
        """Build a stable private helper token without lower-casing camelCase names."""
        parts = [part for part in re.split(r"[^0-9A-Za-z]+", helper.sanitize_name(name)) if part]
        token = "".join(f"{part[:1].upper()}{part[1:]}" for part in parts) or "Value"
        return f"N{token}" if token[0].isdigit() else token

    def _module_schema_helper_name(self, protocol_name: str) -> str:
        """Return the private schema-helper class name for one generated module class."""
        return f"_{self._schema_helper_token(self._extract_name_from_protocol(protocol_name))}Schema"

    def _schema_export_name(self, protocol_path: str) -> str:
        """Return the public schema-helper alias name for one generated module path."""
        path_tokens = [
            self._schema_helper_token(self._extract_name_from_protocol(path_part))
            for path_part in protocol_path.split(".")
        ]
        return f"_{''.join(path_tokens)}Schema"

    def _should_emit_precise_interface_schema_helper(self, schema: capnp_types.SchemaType) -> bool:
        """Return whether this interface schema can safely receive a generated precise helper."""
        return schema.node.id not in self._inherited_interface_schema_ids

    def _resolve_schema_reference(self, schema_id: int) -> capnp_types.SchemaType | None:
        """Resolve a schema by ID and cache it in the local mapping."""
        schema = self._schemas_by_id.get(schema_id)
        if schema is not None:
            return schema

        with contextlib.suppress(*SCHEMA_LOOKUP_EXCEPTIONS):
            schema = self._schema_loader.get(schema_id)
            self._schemas_by_id[schema_id] = schema
            return schema

        return None

    def _schema_type_annotation_for_schema(self, schema: capnp_types.SchemaType) -> str:
        """Return the precise annotation used for a known schema object."""
        node_kind = schema.node.which()
        annotation = "_ListSchema"
        if node_kind == capnp_types.CapnpElementType.ENUM:
            annotation = "_EnumSchema"
        elif node_kind == capnp_types.CapnpElementType.INTERFACE:
            annotation = "_InterfaceSchema"
            if self._is_schema_in_current_module(schema) and self._should_emit_precise_interface_schema_helper(schema):
                resolved_type = self.get_type_by_id(schema.node.id)
                annotation = self._schema_export_name(resolved_type.scoped_name)
        elif node_kind == capnp_types.CapnpElementType.STRUCT:
            annotation = "_StructSchema"
            if self._is_schema_in_current_module(schema):
                resolved_type = self.get_type_by_id(schema.node.id)
                annotation = self._schema_export_name(resolved_type.scoped_name)

        return annotation

    def _render_list_schema_helper_lines(
        self,
        element_type: TypeReader,
        helper_name: str,
        helper_path: str,
    ) -> tuple[str, list[str]]:
        """Render a precise helper for a list schema when its element type is known."""
        element_kind = element_type.which()
        if element_kind not in {"list", "struct", "interface", "enum"}:
            return "_ListSchema", []

        if element_kind == "list":
            element_annotation, nested_element_lines = self._render_list_schema_helper_lines(
                element_type.list.elementType,
                "_ElementSchema",
                f"{helper_path}._ElementSchema",
            )
        else:
            nested_element_lines = []
            referenced_schema = self._resolve_schema_reference(getattr(element_type, element_kind).typeId)
            if referenced_schema is None:
                return "_ListSchema", []
            element_annotation = self._schema_type_annotation_for_schema(referenced_schema)

        body_lines: list[str] = []
        body_lines.extend(nested_element_lines)
        if body_lines:
            body_lines.append("")
        body_lines.extend(helper.new_property("elementType", element_annotation, add_override=True))
        return (
            f'"{helper_path}"',
            [f"class {helper_name}(_ListSchema):", *self._indent_relative_lines(body_lines or ["pass"])],
        )

    def _render_field_schema_helper_lines(
        self,
        field: FieldReader,
        helper_name: str,
        helper_path: str,
    ) -> tuple[str, list[str]] | None:
        """Render a precise `_StructSchemaField` subclass for one slot or group field."""
        body_lines: list[str] = []
        schema_annotation: str

        if field.which() == "group":
            group_schema = self._resolve_schema_reference(field.group.typeId)
            if group_schema is None:
                return None
            schema_annotation = self._schema_type_annotation_for_schema(group_schema)
        elif field.which() == "slot":
            field_kind = field.slot.type.which()
            if field_kind == "list":
                schema_annotation, list_helper_lines = self._render_list_schema_helper_lines(
                    field.slot.type.list.elementType,
                    "_Schema",
                    f"{helper_path}._Schema",
                )
                body_lines.extend(list_helper_lines)
                if body_lines:
                    body_lines.append("")
            elif field_kind in {"struct", "interface", "enum"}:
                referenced_schema = self._resolve_schema_reference(getattr(field.slot.type, field_kind).typeId)
                if referenced_schema is None:
                    return None
                schema_annotation = self._schema_type_annotation_for_schema(referenced_schema)
            else:
                return None
        else:
            return None

        body_lines.extend(helper.new_property("schema", schema_annotation, add_override=True))
        return (
            helper_name,
            [f"class {helper_name}(_StructSchemaField):", *self._indent_relative_lines(body_lines or ["pass"])],
        )

    def _render_struct_schema_helper_lines(
        self,
        schema: capnp_types.SchemaType,
        helper_name: str,
        helper_path: str,
    ) -> list[str]:
        """Render a precise `_StructSchema` helper for one generated module or method struct."""
        self._ensure_schema_helper_support()
        body_lines: list[str] = []
        field_overloads: list[str] = []

        for field in schema.node.struct.fields:
            field_class_name = f"_{self._schema_helper_token(field.name)}Field"
            field_helper = self._render_field_schema_helper_lines(
                field,
                field_class_name,
                f"{helper_path}.{field_class_name}",
            )
            field_return_type = (
                f'"{helper_path}.{field_class_name}"' if field_helper is not None else "_StructSchemaField"
            )
            if field_helper is not None:
                _, field_helper_lines = field_helper
                body_lines.extend(field_helper_lines)
                body_lines.append("")

            field_overloads.extend(
                [
                    "@overload",
                    f"def __getitem__(self, key: Literal[{field.name!r}]) -> {field_return_type}: ...",
                ],
            )

        if field_overloads:
            field_overloads.extend(
                [
                    "@overload",
                    "def __getitem__(self, key: str) -> _StructSchemaField: ...",
                ],
            )
        else:
            field_overloads.append("...")

        body_lines.extend(
            [
                "class _Fields(dict[str, _StructSchemaField]):",
                *self._indent_relative_lines(field_overloads),
                "",
                *helper.new_property("fields", f'"{helper_path}._Fields"', add_override=True),
            ],
        )

        return [f"class {helper_name}(_StructSchema):", *self._indent_relative_lines(body_lines or ["pass"])]

    def _collect_interface_method_specs(
        self,
        schema: capnp_types.SchemaType,
    ) -> list[tuple[str, str, int, int]]:
        """Collect visible interface methods, flattening inherited methods into one ordered mapping."""
        method_specs: dict[str, tuple[str, int, int]] = {}

        for superclass in schema.node.interface.superclasses:
            superclass_schema = self._resolve_schema_reference(superclass.id)
            if superclass_schema is None or superclass_schema.node.which() != capnp_types.CapnpElementType.INTERFACE:
                continue

            for method_name, owner_token, param_struct_type, result_struct_type in self._collect_interface_method_specs(
                superclass_schema
            ):
                method_specs[method_name] = (owner_token, param_struct_type, result_struct_type)

        owner_token = self._schema_helper_token(self.get_type_by_id(schema.node.id).name)
        for method in schema.node.interface.methods:
            method_specs[method.name] = (owner_token, method.paramStructType, method.resultStructType)

        return [
            (method_name, owner_token, param_struct_type, result_struct_type)
            for method_name, (owner_token, param_struct_type, result_struct_type) in method_specs.items()
        ]

    def _render_interface_schema_helper_lines(
        self,
        schema: capnp_types.SchemaType,
        helper_name: str,
        helper_path: str,
    ) -> list[str]:
        """Render a precise `_InterfaceSchema` helper for one generated interface module."""
        self._ensure_schema_helper_support()
        body_lines: list[str] = []
        method_overloads: list[str] = []
        for method_name, owner_token, param_struct_type, result_struct_type in self._collect_interface_method_specs(
            schema
        ):
            method_token = self._schema_helper_token(method_name)
            helper_token_prefix = f"{owner_token}{method_token}"
            param_helper_name = f"_{helper_token_prefix}ParamSchema"
            result_helper_name = f"_{helper_token_prefix}ResultSchema"

            param_schema = self._resolve_schema_reference(param_struct_type)
            result_schema = self._resolve_schema_reference(result_struct_type)

            if param_schema is not None:
                body_lines.extend(
                    self._render_struct_schema_helper_lines(
                        param_schema,
                        param_helper_name,
                        f"{helper_path}.{param_helper_name}",
                    ),
                )
                body_lines.append("")
            if result_schema is not None:
                body_lines.extend(
                    self._render_struct_schema_helper_lines(
                        result_schema,
                        result_helper_name,
                        f"{helper_path}.{result_helper_name}",
                    ),
                )
                body_lines.append("")

            param_annotation = f'"{helper_path}.{param_helper_name}"' if param_schema is not None else "_StructSchema"
            result_annotation = (
                f'"{helper_path}.{result_helper_name}"' if result_schema is not None else "_StructSchema"
            )
            method_type = f"_InterfaceMethod[{param_annotation}, {result_annotation}]"

            method_overloads.extend(
                [
                    "@overload",
                    f"def __getitem__(self, key: Literal[{method_name!r}]) -> {method_type}: ...",
                ],
            )

        if method_overloads:
            method_overloads.extend(
                [
                    "@overload",
                    "def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...",
                ],
            )
        else:
            method_overloads.append("...")

        body_lines.extend(
            [
                helper.new_class_declaration(
                    "_Methods",
                    ["dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]"],
                ),
                *self._indent_relative_lines(method_overloads),
                "",
                *helper.new_property("methods", f'"{helper_path}._Methods"', add_override=True),
            ],
        )

        return [
            helper.new_class_declaration(helper_name, ["_InterfaceSchema"]),
            *self._indent_relative_lines(body_lines or ["pass"]),
        ]

    def _add_module_schema_helpers(self, schema: capnp_types.SchemaType) -> None:
        """Add precise `.schema` helper types to the currently open module class."""
        helper_lines: list[str]
        helper_name = self._module_schema_helper_name(self.scope.name)
        schema_export_name = self._schema_export_name(self.scope.scoped_name)
        helper_path = f"{self.scope.scoped_name}.{helper_name}"
        node_kind = schema.node.which()
        if node_kind == capnp_types.CapnpElementType.INTERFACE:
            if not self._should_emit_precise_interface_schema_helper(schema):
                return
            helper_lines = self._render_interface_schema_helper_lines(schema, helper_name, helper_path)
        elif node_kind == capnp_types.CapnpElementType.STRUCT:
            helper_lines = self._render_struct_schema_helper_lines(schema, helper_name, helper_path)
        else:
            return

        if self.scope.lines and self.scope.lines[-1].strip():
            self.scope.add("")
        for line in helper_lines:
            self.scope.add(line)
        self.scope.add("")
        recorded_target = self._schema_helper_export_targets.setdefault(schema_export_name, helper_path)
        if recorded_target != helper_path:
            msg = f"Schema export name collision for {schema_export_name}: {recorded_target} != {helper_path}"
            raise ValueError(msg)

        for line in helper.new_property("schema", f'"{schema_export_name}"', add_override=True):
            self.scope.add(line)

    def _gen_struct_reader_class(
        self,
        slot_fields: list[helper.TypeHintedVariable],
        builder_type_name: str,
        schema: _StructSchema,
    ) -> None:
        """Generate the Reader class for a struct.

        Now inherits from _DynamicStructReader, so we only need to add:
        - Field properties (read-only getters)
        - as_builder method override (with proper signature)
        - which() method override for unions (with specific Literal return type)

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields.
            builder_type_name (str): Builder type name (flat alias).
            schema (_StructSchema): The struct schema.

        """
        # Add the reader slot fields as properties
        self._add_reader_properties(slot_fields)

        # Add which() method override for unions with specific Literal return type
        self._add_which_method(schema)

        # Add as_builder method with override decorator and proper signature
        self._add_typing_import("override")
        self._add_typing_import("Any")
        self._add_typing_import("Callable")
        self.scope.add("@override")
        self.scope.add(
            helper.new_function(
                "as_builder",
                parameters=[
                    "self",
                    helper.TypeHintedVariable(
                        "num_first_segment_words",
                        [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                        default="None",
                    ),
                    helper.TypeHintedVariable(
                        "allocate_seg_callable",
                        [helper.TypeHint("Callable[[int], bytearray]", primary=True), helper.TypeHint("None")],
                        default="None",
                    ),
                ],
                return_type=builder_type_name,
            ),
        )

    def _gen_struct_builder_class(
        self,
        slot_fields: list[helper.TypeHintedVariable],
        init_choices: list[InitChoice],
        list_init_choices: list[tuple[str, str]],
        reader_type_name: str,
        schema: _StructSchema,
    ) -> None:
        """Generate the Builder class for a struct.

        Now inherits from _DynamicStructBuilder, so we only need to add:
        - Field properties (getters and setters)
        - as_reader method override
        - which() method override for unions (with specific Literal return type)

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields.
            init_choices (list[InitChoice]): Init method overload choices for structs.
            list_init_choices (list[tuple[str, str]]): Init method overload choices for lists.
            builder_type_name (str): Builder type name (flat alias).
            reader_type_name (str): Reader type name (flat alias).
            schema (_StructSchema): The struct schema.

        """
        # Add all builder slot fields with setters
        self._add_builder_properties(slot_fields)

        # Add which() method override for unions with specific Literal return type
        self._add_which_method(schema)

        # Add init method overloads for struct and list fields
        # These are needed to properly initialize list fields with the right size
        self._add_builder_init_overloads(init_choices, list_init_choices)

        # Add as_reader method with override decorator
        self._add_typing_import("override")
        self.scope.add("@override")
        self.scope.add(
            helper.new_function(
                "as_reader",
                parameters=["self"],
                return_type=reader_type_name,
            ),
        )

    # ===== Interface Generation Helper Methods =====

    def _collect_interface_base_classes(self, schema: _InterfaceSchema) -> list[str]:
        """Collect base classes for an interface (superclasses only).

        Args:
            schema (_InterfaceSchema): The interface schema.

        Returns:
            list[str]: List of base interface module class names (e.g., ["_IdentifiableModule"]).

        """
        base_classes: list[str] = []

        # Process interface inheritance (extends)
        if schema.node.which() == "interface":
            interface_node = schema.node.interface
            for superclass in interface_node.superclasses:
                superclass_type = self._maybe_get_type_by_id(superclass.id)
                if superclass_type is None:
                    logger.debug("Could not resolve superclass %s", superclass.id)
                    continue
                protocol_name = superclass_type.name
                if superclass_type.scope and not superclass_type.scope.is_root:
                    base_protocol = f"{superclass_type.scope.scoped_name}.{protocol_name}"
                else:
                    base_protocol = protocol_name
                base_classes.append(base_protocol)

        # No longer add Protocol - interface modules inherit from _InterfaceModule
        return base_classes

    def _generate_nested_types_for_interface(self, schema: _InterfaceSchema) -> None:
        """Generate all nested types for an interface.

        Args:
            schema (_InterfaceSchema): The interface schema.

        """
        # Save current interface scope before generating nested types
        interface_scope = self.scope

        for nested_node in schema.node.nestedNodes:
            try:
                # Get the nested schema from our ID mapping
                nested_schema = self._schemas_by_id.get(nested_node.id)
                if nested_schema:
                    self.generate_nested(nested_schema)
                else:
                    # Try to load it from the schema loader
                    try:
                        nested_schema = self._schema_loader.get(nested_node.id)
                        # Add it to our mapping for future reference
                        self._schemas_by_id[nested_node.id] = nested_schema
                        self.generate_nested(nested_schema)
                    except SCHEMA_LOOKUP_EXCEPTIONS as load_error:
                        logger.debug(
                            "Could not find or load nested type %s (id=%s) in interface %s: %s",
                            nested_node.name,
                            hex(nested_node.id),
                            schema.node.displayName,
                            load_error,
                        )
            except TYPE_GENERATION_EXCEPTIONS as error:  # pragma: no cover
                logger.debug(
                    "Could not generate nested type %s in interface %s: %s",
                    nested_node.name,
                    schema.node.displayName,
                    error,
                )

        # Restore interface scope after generating nested types
        self.scope = interface_scope

    def _add_new_client_method(self, name: str, client_return_type: str | None = None) -> None:
        """Add _new_client() class method to create capability client from Server.

        Args:
            name (str): The interface name.
            schema (_InterfaceSchema): The interface schema.
            client_return_type (str | None): Optional client class name to return (default: interface name).

        """
        scope_path = self._get_scope_path()
        fully_qualified_interface = scope_path or name

        # Use base type _DynamicCapabilityServer for parameter to match base class signature
        # This accepts any server implementation (including subclasses of this interface's Server)
        server_param_type = "_DynamicCapabilityServer"

        # Determine return type (narrow, specific client type)
        return_type = client_return_type or fully_qualified_interface

        self._add_typing_import("override")
        self.scope.add("@override")
        self.scope.add(
            helper.new_function(
                "_new_client",
                parameters=["self", f"server: {server_param_type}"],
                return_type=return_type,
            ),
        )

    # ===== Slot Generation Methods =====

    @staticmethod
    def _list_builder_init_args() -> list[str]:
        """Return the standard Builder.init signature for list items."""
        return ["self", "index: int", "size: int | None = None"]

    def _build_struct_list_class_info(self, element_type: TypeReader) -> tuple[str, str, str, str, bool, list[str]]:
        """Build list-class typing info for struct elements."""
        struct_name = self.get_type_name(element_type)
        builder_alias = self._get_flat_builder_alias(struct_name)
        reader_alias = self._get_flat_reader_alias(struct_name)
        reader_type = reader_alias or self._build_nested_reader_type(struct_name)
        builder_type = builder_alias or self._build_scoped_builder_type(struct_name)
        self._add_typing_import("Any")

        last_component = struct_name.split(".")[-1]
        base_name = (
            self._extract_name_from_protocol(last_component) if last_component.startswith("_") else last_component
        )
        setter_type = f"{reader_type} | {builder_type} | dict[str, Any]"
        return reader_type, builder_type, setter_type, base_name, True, self._list_builder_init_args()

    def _build_nested_list_class_info(self, element_type: TypeReader) -> tuple[str, str, str, str, bool, list[str]]:
        """Build list-class typing info for nested list elements."""
        inner_list_class, inner_reader_alias, inner_builder_alias = self._generate_list_class(element_type)
        self._add_typing_import("Sequence")
        self._add_typing_import("Any")
        return (
            inner_reader_alias,
            inner_builder_alias,
            f"{inner_reader_alias} | {inner_builder_alias} | Sequence[Any]",
            inner_list_class.removeprefix("_"),
            True,
            self._list_builder_init_args(),
        )

    def _build_interface_list_class_info(self, interface_name: str) -> tuple[str, str, str, str, bool, list[str]]:
        """Build list-class typing info for interface elements."""
        client_alias = self._get_flat_client_alias(interface_name)
        if not client_alias:
            client_alias = self._get_client_type_name_from_interface_path(interface_name)
        return (
            client_alias,
            client_alias,
            f"{client_alias} | {interface_name}.Server",
            client_alias,
            False,
            [],
        )

    def _build_list_class_info(self, element_type: TypeReader) -> tuple[str, str, str, str, bool, list[str]]:
        """Build the list-class typing information for one list element type."""
        element_which = element_type.which()

        if element_which == capnp_types.CapnpElementType.STRUCT:
            return self._build_struct_list_class_info(element_type)
        if element_which == capnp_types.CapnpElementType.LIST:
            return self._build_nested_list_class_info(element_type)
        if element_which == capnp_types.CapnpElementType.ENUM:
            enum_name = self.get_type_name(element_type)
            return enum_name, enum_name, enum_name, enum_name.replace(".", "_"), False, []
        if element_which == capnp_types.CapnpElementType.INTERFACE:
            return self._build_interface_list_class_info(self.get_type_name(element_type))
        if element_which == capnp_types.CapnpElementType.ANY_POINTER:
            self._needs_anypointer_alias = True
            return "_DynamicObjectReader", "_DynamicObjectBuilder", "AnyPointer", "AnyPointer", False, []

        python_type = capnp_types.CAPNP_TYPE_TO_PYTHON[element_which]
        return python_type, python_type, python_type, element_which.title(), False, []

    def _add_generated_list_class(
        self,
        list_class_name: str,
        aliases: tuple[str, str],
        class_info: tuple[str, str, str, bool, list[str]],
    ) -> None:
        """Emit the generated list Reader/Builder classes into the root scope."""
        reader_alias, builder_alias = aliases
        reader_type, builder_type, setter_type, has_init, init_args = class_info
        self._generated_list_types.add(list_class_name)
        self._all_type_aliases[reader_alias] = (f"{list_class_name}.Reader", "Reader")
        self._all_type_aliases[builder_alias] = (f"{list_class_name}.Builder", "Builder")

        self._add_typing_import("Iterator")
        self._add_typing_import("overload")
        self._add_typing_import("override")

        root_scope = self.scope.root
        root_scope.add(f"class {list_class_name}:")
        root_scope.add("    class Reader(_DynamicListReader):")
        root_scope.add("        @override")
        root_scope.add("        def __len__(self) -> int: ...")
        root_scope.add("        @override")
        root_scope.add(f"        def __getitem__(self, key: int) -> {reader_type}: ...")
        root_scope.add("        @override")
        root_scope.add(f"        def __iter__(self) -> Iterator[{reader_type}]: ...")

        root_scope.add("    class Builder(_DynamicListBuilder):")
        root_scope.add("        @override")
        root_scope.add("        def __len__(self) -> int: ...")
        root_scope.add("        @override")
        root_scope.add(f"        def __getitem__(self, key: int) -> {builder_type}: ...")
        root_scope.add("        @override")
        root_scope.add(f"        def __setitem__(self, key: int, value: {setter_type}) -> None: ...")
        root_scope.add("        @override")
        root_scope.add(f"        def __iter__(self) -> Iterator[{builder_type}]: ...")

        if has_init:
            root_scope.add("        @override")
            root_scope.add(f"        def init({', '.join(init_args)}) -> {builder_type}: ...")

        root_scope.add("")

    def _generate_list_class(self, type_reader: TypeReader) -> tuple[str, str, str]:
        """Generate a specific List class for the given list type reader.

        Args:
            type_reader: The TypeReader for the list (must be of type LIST).

        Returns:
            Tuple of (list_class_name, reader_alias, builder_alias).

        """
        assert type_reader.which() == capnp_types.CapnpElementType.LIST
        reader_type, builder_type, setter_type, base_name, has_init, init_args = self._build_list_class_info(
            type_reader.list.elementType,
        )

        # Construct list class name
        list_class_name = f"_{base_name}List"

        # Register aliases
        reader_alias = f"{base_name}ListReader"
        builder_alias = f"{base_name}ListBuilder"

        # Check if already generated
        if list_class_name in self._generated_list_types:
            return list_class_name, reader_alias, builder_alias

        self._add_generated_list_class(
            list_class_name,
            (reader_alias, builder_alias),
            (reader_type, builder_type, setter_type, has_init, init_args),
        )

        return list_class_name, reader_alias, builder_alias

    @staticmethod
    def _add_struct_slot_type_hints(
        hinted_variable: helper.TypeHintedVariable, builder_alias: str | None, reader_alias: str | None
    ) -> None:
        """Add Builder/Reader variants to a struct slot variable."""
        if builder_alias and reader_alias:
            hinted_variable.add_type_hint(helper.TypeHint(builder_alias, affix="Builder", flat_alias=True))
            hinted_variable.add_type_hint(helper.TypeHint(reader_alias, affix="Reader", flat_alias=True))
            return

        hinted_variable.add_builder_from_primary_type()
        hinted_variable.add_reader_from_primary_type()

    @staticmethod
    def _track_list_init_choice(
        hinted_variable: helper.TypeHintedVariable | None,
        field_name: str,
        list_init_choices: list[tuple[str, str]] | None,
    ) -> None:
        """Track list field init overload information when requested."""
        if list_init_choices is None or hinted_variable is None:
            return

        builder_type = hinted_variable.get_type_with_affixes(["Builder"])
        list_init_choices.append((helper.sanitize_name(field_name), builder_type))

    @staticmethod
    def _require_struct_schema(raw_field: _StructSchemaField) -> _StructSchema:
        """Extract a struct schema from a pycapnp field wrapper."""
        schema = raw_field.schema
        if isinstance(schema, _StructSchema):
            return schema
        if isinstance(schema, _Schema):
            return schema.as_struct()
        msg = f"Expected struct schema, got {type(schema).__name__}"
        raise TypeError(msg)

    @staticmethod
    def _require_enum_schema(raw_field: _StructSchemaField) -> _EnumSchema:
        """Extract an enum schema from a pycapnp field wrapper."""
        schema = raw_field.schema
        if isinstance(schema, _EnumSchema):
            return schema
        if isinstance(schema, _Schema):
            return schema.as_enum()
        msg = f"Expected enum schema, got {type(schema).__name__}"
        raise TypeError(msg)

    @staticmethod
    def _require_interface_schema(raw_field: _StructSchemaField) -> _InterfaceSchema:
        """Extract an interface schema from a pycapnp field wrapper."""
        schema = raw_field.schema
        if isinstance(schema, _InterfaceSchema):
            return schema
        if isinstance(schema, _Schema):
            return schema.as_interface()
        msg = f"Expected interface schema, got {type(schema).__name__}"
        raise TypeError(msg)

    def _generate_interface_slot(
        self,
        field: FieldReader,
        schema: _InterfaceSchema,
    ) -> helper.TypeHintedVariable:
        """Generate a slot for an interface field."""
        with contextlib.suppress(
            *TYPE_GENERATION_EXCEPTIONS
        ):  # pragma: no cover - best effort for incomplete imported schemas
            self.generate_nested(schema)
        try:
            protocol_type_name = self.get_type_name(field.slot.type)
        except TYPE_RESOLUTION_EXCEPTIONS:
            protocol_type_name = "Any"
            self._add_typing_import("Union")

        client_type = protocol_type_name
        server_type = f"{protocol_type_name}.Server"
        if protocol_type_name != "Any":
            client_type, server_type = self._get_interface_client_server_types(protocol_type_name)

        return helper.TypeHintedVariable(
            helper.sanitize_name(field.name),
            [helper.TypeHint(client_type, primary=True), helper.TypeHint(server_type)],
        )

    def gen_slot(
        self,
        raw_field: _StructSchemaField,
        field: FieldReader,
        init_choices: list[InitChoice],
        list_init_choices: list[tuple[str, str]] | None = None,
    ) -> helper.TypeHintedVariable | None:
        """Generate a type-hinted variable from a slot field.

        Args:
            raw_field: The pycapnp field schema wrapper (provides .schema property).
            field: The field descriptor from schema.capnp.
            init_choices (list[InitChoice]): A list of possible (overload) `init` functions that are populated
                by this method.
            list_init_choices: Optional list of list field init choices.

        Returns:
            helper.TypeHintedVariable | None: The type hinted variable that was created, or None otherwise.

        """
        field_slot_type = field.slot.type.which()
        if field_slot_type in capnp_types.CAPNP_TYPE_TO_PYTHON:
            return self.gen_python_type_slot(field, field_slot_type)

        if field_slot_type == capnp_types.CapnpElementType.INTERFACE:
            return self._generate_interface_slot(field, self._require_interface_schema(raw_field))

        if field_slot_type == capnp_types.CapnpElementType.LIST:
            hinted_variable = self.gen_list_slot(field)
            self._track_list_init_choice(hinted_variable, field.name, list_init_choices)
            return hinted_variable

        if field_slot_type == capnp_types.CapnpElementType.ENUM:
            return self.gen_enum_slot(field, self._require_enum_schema(raw_field))

        if field_slot_type == capnp_types.CapnpElementType.ANY_POINTER:
            return self.gen_any_pointer_slot(field)

        if field_slot_type != capnp_types.CapnpElementType.STRUCT:
            msg = f"Unknown field slot type {field_slot_type}."
            raise TypeError(msg)

        hinted_variable = self.gen_struct_slot(field, self._require_struct_schema(raw_field), init_choices)
        type_name = hinted_variable.primary_type_hint.name
        self._add_struct_slot_type_hints(
            hinted_variable,
            self._get_flat_builder_alias(type_name),
            self._get_flat_reader_alias(type_name),
        )

        return hinted_variable

    def gen_list_slot(
        self,
        field: FieldReader,
    ) -> helper.TypeHintedVariable:
        """Generate a slot, which contains a `list`.

        Args:
            field (_DynamicStructReader): The field reader.
            schema (_ListSchema): The schema of the list.

        Returns:
            helper.TypeHintedVariable: The extracted hinted variable object.

        """
        # Generate the specific list class
        _, reader_alias, builder_alias = self._generate_list_class(field.slot.type)

        # Create TypeHintedVariable
        # Primary type is Reader (for read-only access)
        hinted_variable = helper.TypeHintedVariable(
            helper.sanitize_name(field.name),
            [helper.TypeHint(reader_alias, primary=True, flat_alias=True)],
            nesting_depth=0,  # We handle nesting in the class itself
        )

        # Add Builder variant
        hinted_variable.add_type_hint(helper.TypeHint(builder_alias, affix="Builder", flat_alias=True))

        # Add Reader variant explicitly
        hinted_variable.add_type_hint(helper.TypeHint(reader_alias, affix="Reader", flat_alias=True))

        return hinted_variable

    def gen_python_type_slot(self, field: FieldReader, field_type: str) -> helper.TypeHintedVariable:
        """Generate a slot, which contains a regular Python type.

        Args:
            field (FieldReader): The field reader.
            field_type (str): The (primitive) type of the slot.

        Returns:
            helper.HintedVariable: The extracted hinted variable object.

        """
        python_type_name: str = capnp_types.CAPNP_TYPE_TO_PYTHON[field_type]
        return helper.TypeHintedVariable(
            helper.sanitize_name(field.name),
            [helper.TypeHint(python_type_name, primary=True)],
        )

    def gen_enum_slot(self, field: FieldReader, schema: _EnumSchema) -> helper.TypeHintedVariable:
        """Generate a slot, which contains a `enum`.

        Args:
            field (FieldReader): The field reader.
            schema: The schema of the field (expected to be an enum schema).

        Returns:
            str: The type-hinted slot.

        """
        if not self.is_type_id_known(field.slot.type.enum.typeId):
            with contextlib.suppress(NoParentError):
                self.generate_nested(schema)

        # Enum values are integers at runtime, but also accept string literals
        type_name = self.get_type_name(field.slot.type)
        return helper.TypeHintedVariable(
            helper.sanitize_name(field.name),
            [helper.TypeHint(type_name, primary=True)],
        )

    def gen_struct_slot(
        self,
        field: FieldReader,
        schema: _StructSchema,
        init_choices: list[InitChoice],
    ) -> helper.TypeHintedVariable:
        """Generate a slot, which contains a `struct`.

        Args:
            field (_DynamicStructReader): The field reader.
            schema (_StructSchema): The schema of the field.
            init_choices (list[InitChoice]): A list of overloaded `init` function choices, to be filled by this function.

        Returns:
            helper.HintedVariable: The extracted hinted variable object.

        """
        if not self.is_type_id_known(schema.node.id):
            # Try to register as an import first, then generate if needed
            imported = self.register_import(schema)
            if imported is None:
                _ = self.gen_struct(schema)

        type_name = self.get_type_name(field.slot.type)
        init_choices.append((helper.sanitize_name(field.name), type_name))
        hints = [helper.TypeHint(type_name, primary=True)]
        # If this is an interface type, also allow passing its Server implementation
        if field.slot.type.which() == capnp_types.CapnpElementType.INTERFACE:
            # type_name is already the Protocol module name (e.g., "_GreeterModule")
            hints.append(helper.TypeHint(f"{type_name}.Server"))
        return helper.TypeHintedVariable(helper.sanitize_name(field.name), hints)

    def gen_any_pointer_slot(self, field: FieldReader) -> helper.TypeHintedVariable | None:
        """Generate a slot, which contains an `any_pointer` object.

        Args:
            field (FieldReader): The field reader.
            new_type (CapnpType): The new type that was registered previously.

        Returns:
            helper.HintedVariable | None: The extracted hinted variable object, or None in case of error.

        """
        try:
            # Check if this is a generic parameter
            if field.slot.type.anyPointer.which() == "parameter":
                # Generic parameters at runtime:
                # - Reader properties return _DynamicObjectReader
                # - Builder properties return _DynamicObjectReader (getter)
                # - Builder properties accept only pointer types (setter)
                self._needs_dynamic_object_reader_augmentation = True

                # Create TypeHintedVariable with primary type for getter and Any for setter
                hinted_var = helper.TypeHintedVariable(
                    helper.sanitize_name(field.name),
                    [helper.TypeHint("_DynamicObjectReader", primary=True)],
                )
                # Mark that this field needs special setter handling in Builder
                hinted_var.is_generic_param = True
                return hinted_var

            # Check for unconstrained types (AnyStruct, AnyList, Capability, AnyPointer)
            if field.slot.type.anyPointer.which() == "unconstrained":
                kind = field.slot.type.anyPointer.unconstrained.which()

                if kind == "struct":
                    # Primary type is Reader
                    # At runtime, AnyStruct fields return _DynamicObjectReader
                    hints = [helper.TypeHint("_DynamicObjectReader", primary=True)]
                    hinted_var = helper.TypeHintedVariable(helper.sanitize_name(field.name), hints)
                    # Add Builder variant
                    hinted_var.add_type_hint(helper.TypeHint("_DynamicStructBuilder", affix="Builder", flat_alias=True))
                    # Add Reader variant explicitly for setter type lookup
                    hinted_var.add_type_hint(helper.TypeHint("_DynamicObjectReader", affix="Reader", flat_alias=True))
                    # Mark as AnyStruct for special setter handling
                    hinted_var.is_any_struct = True
                    return hinted_var

                if kind == "list":
                    # Primary type is Reader
                    # At runtime, AnyList fields return _DynamicObjectReader
                    hints = [helper.TypeHint("_DynamicObjectReader", primary=True)]
                    hinted_var = helper.TypeHintedVariable(helper.sanitize_name(field.name), hints)
                    # Add Builder variant
                    hinted_var.add_type_hint(helper.TypeHint("_DynamicListBuilder", affix="Builder", flat_alias=True))
                    # Add Reader variant explicitly for setter type lookup
                    hinted_var.add_type_hint(helper.TypeHint("_DynamicObjectReader", affix="Reader", flat_alias=True))
                    # Mark as AnyList for special setter handling
                    hinted_var.is_any_list = True
                    return hinted_var

                if kind == "capability":
                    # Capability is like interface
                    # When reading a struct field of type Capability, we get a _DynamicObjectReader (generic pointer)
                    # The user must call .as_interface(Interface) to get a client
                    hints = [helper.TypeHint("_DynamicObjectReader", primary=True)]
                    hints.append(helper.TypeHint("_DynamicCapabilityServer"))
                    hints.append(helper.TypeHint("_DynamicCapabilityClient"))
                    # Add Reader/Builder variants explicitly
                    hints.append(helper.TypeHint("_DynamicObjectReader", affix="Reader", flat_alias=True))
                    # When building, we can set it to Client or Server (handled by primary/secondary hints usually, but explicit Builder helps)
                    hints.append(helper.TypeHint("_DynamicCapabilityClient", affix="Builder", flat_alias=True))
                    hinted_var = helper.TypeHintedVariable(helper.sanitize_name(field.name), hints)
                    # Mark as Capability for special setter handling
                    hinted_var.is_capability = True
                    return hinted_var

                if kind == "anyKind":
                    # AnyPointer
                    # Primary type is Reader
                    hints = [helper.TypeHint("_DynamicObjectReader", primary=True)]
                    hinted_var = helper.TypeHintedVariable(helper.sanitize_name(field.name), hints)
                    # Add Builder variant
                    hinted_var.add_type_hint(helper.TypeHint("_DynamicObjectBuilder", affix="Builder", flat_alias=True))
                    # Add Reader variant explicitly for setter type lookup
                    hinted_var.add_type_hint(helper.TypeHint("_DynamicObjectReader", affix="Reader", flat_alias=True))
                    # Mark as AnyPointer for special setter handling (accepts all Cap'n Proto types)
                    hinted_var.is_any_pointer = True
                    return hinted_var

        except (capnp.KjException, AttributeError, IndexError):
            pass

        # Fallback
        self._add_typing_import("Any")
        return helper.TypeHintedVariable(helper.sanitize_name(field.name), [helper.TypeHint("Any", primary=True)])

    def gen_const(self, schema: _Schema) -> None:
        """Generate a `const` object.

        Args:
            schema (_Schema): The schema to generate the `const` object out of.

        """
        assert schema.node.which() == capnp_types.CapnpElementType.CONST

        const_type = schema.node.const.type.which()
        name = helper.get_display_name(schema)

        if const_type in capnp_types.CAPNP_TYPE_TO_PYTHON:
            python_type = capnp_types.CAPNP_TYPE_TO_PYTHON[schema.node.const.type.which()]
            self.scope.add(helper.TypeHintedVariable(name, [helper.TypeHint(python_type, primary=True)]))

        elif const_type == "struct":
            pass

    def gen_enum(self, schema: _EnumSchema) -> CapnpType | None:
        """Generate an `enum` object as a class with int attributes.

        At runtime, enums are _EnumModule instances with integer attributes.
        We generate a simple class with int type annotations to represent this,
        then create an instance annotation.

        Args:
            schema (_EnumSchema): The schema to generate the `enum` object out of.

        """
        assert schema.node.which() == capnp_types.CapnpElementType.ENUM

        imported = self.register_import(schema)

        if imported is not None:
            return imported

        # Get the user-facing enum name
        name = helper.get_display_name(schema)

        # Create Enum class name (e.g., _TestEnumEnumModule)
        enum_class_name = f"_{name}EnumModule"

        # No special imports needed - just a plain class
        self._add_enum_import()

        # Generate a plain class declaration (no inheritance)
        enum_declaration = helper.new_class_declaration(enum_class_name, [])

        # Find the parent scope for the enum (where it should be declared)
        enum_parent_scope = self.scopes_by_id.get(schema.node.scopeId, self.scope.root)

        # Create new scope for the Enum
        _ = self.new_scope(
            enum_class_name,
            schema.node,
            scope_heading=enum_declaration,
            parent_scope=enum_parent_scope,
        )

        # Construct flat alias name for nested enums to avoid "Variable not allowed" errors
        # e.g. CalculatorOperatorEnum
        flat_name = name
        s = enum_parent_scope
        while s and not s.is_root:
            # s.name is like _CalculatorStructModule
            # Extract Calculator
            part = self._extract_name_from_protocol(s.name) if s.name.startswith("_") else s.name
            flat_name = f"{part}{flat_name}"
            s = s.parent

        alias_name = f"{flat_name}Enum"

        # Register type with the alias name so get_type_name() returns the alias
        # Always register at root scope so it's a top-level alias
        new_type = self.register_type(schema.node.id, schema, name=alias_name, scope=self.scope.root)

        # Create context
        context = EnumGenerationContext.create(
            schema=schema,
            type_name=name,
            new_type=new_type,
        )

        # Generate enum values as type annotations (not assignments)
        # At runtime these are integer attributes set by pycapnp
        enum_values: list[str] = []
        for enumerant in schema.node.enum.enumerants:
            self.scope.add(f"{enumerant.name}: int")
            enum_values.append(enumerant.name)

        # Return to parent scope
        self.return_from_scope()

        # Ensure Literal is imported for type alias generation
        self._add_typing_import("Literal")

        # For nested enums, add instance annotation so enum.value works at runtime
        is_nested = enum_parent_scope and not enum_parent_scope.is_root
        if is_nested:
            # Instance annotation: allows Calculator.Operator.add to return int at runtime
            enum_parent_scope.add(f"{context.type_name}: {enum_class_name}")

        # Track for top-level annotations
        # For enums, we store the enum values to generate the type alias
        # Suffix with Enum to make it clear it's a type alias
        self._all_type_aliases[alias_name] = (new_type.scoped_name, "Enum", enum_values)

        return new_type

    # ===== Struct Generation Helper Methods (Phase 2 Refactoring) =====

    def _setup_struct_generation(
        self,
        schema: _StructSchema,
        type_name: str,
    ) -> tuple[StructGenerationContext | None, str]:
        """Set up struct generation and create its context.

        This method handles the initial setup phase of struct generation including:
        - Checking if the struct is already imported
        - Determining the type name
        - Creating the _StructModule class declaration
        - Setting up the scope
        - Registering the type

        Args:
            schema: The Cap'n Proto struct schema
            type_name: Optional type name override (empty string to auto-generate)

        Returns:
            A tuple of (context, protocol_declaration) where:
            - context is None if the struct should be skipped (already imported or no parent)
            - protocol_declaration is the string for the Protocol class declaration

        """
        # Check if already imported
        imported = self.register_import(schema)
        if imported is not None:
            return None, ""

        # Determine type name
        if not type_name:
            type_name = helper.get_display_name(schema)

        # Create _StructModule class declaration
        protocol_class_name = f"_{type_name}StructModule"
        protocol_declaration = helper.new_class_declaration(protocol_class_name, parameters=["_StructModule"])

        # Create scope using the Protocol class name
        try:
            _ = self.new_scope(protocol_class_name, schema.node)
        except NoParentError:
            logger.warning("Skipping generation of %s - parent scope not available", type_name)
            return None, ""

        # Register type with the Protocol class name for correct scoped_name generation
        # The type's scoped_name will be used for all internal type references
        new_type = self.register_type(schema.node.id, schema, name=protocol_class_name)

        # Create context with auto-generated names
        context = StructGenerationContext.create_with_protocol(schema, type_name, protocol_class_name, new_type, [])
        flat_base_name = self._resolve_flat_struct_base_name(type_name, new_type.scope)
        context.reader_type_name = helper.new_reader_flat(flat_base_name)
        context.builder_type_name = helper.new_builder_flat(flat_base_name)

        return context, protocol_declaration

    def _count_local_struct_name_occurrences(self, type_name: str) -> int:
        """Count local struct definitions that share the same display name."""
        return sum(
            1
            for local_schema in self._schemas_by_id.values()
            if local_schema.node.which() == capnp_types.CapnpElementType.STRUCT
            and self._is_schema_in_current_module(local_schema)
            and helper.get_display_name(local_schema) == type_name
        )

    def _count_local_interface_name_occurrences(self, type_name: str) -> int:
        """Count local interface definitions that share the same display name."""
        return sum(
            1
            for local_schema in self._schemas_by_id.values()
            if local_schema.node.which() == capnp_types.CapnpElementType.INTERFACE
            and self._is_schema_in_current_module(local_schema)
            and helper.get_display_name(local_schema) == type_name
        )

    def _build_flat_name_from_scope(self, base_name: str, scope: Scope) -> str:
        """Prefix a flat name with its containing scope names to make it unique."""
        flat_name = base_name
        current_scope: Scope | None = scope
        while current_scope and not current_scope.is_root:
            scope_name = (
                self._extract_name_from_protocol(current_scope.name)
                if current_scope.name.startswith("_")
                else current_scope.name
            )
            flat_name = f"{scope_name}{flat_name}"
            current_scope = current_scope.parent
        return flat_name

    def _resolve_flat_struct_base_name(self, type_name: str, scope: Scope) -> str:
        """Resolve the flattened base name used for top-level Builder/Reader typing classes."""
        candidate_reader = helper.new_reader_flat(type_name)
        candidate_builder = helper.new_builder_flat(type_name)
        has_local_collision = self._count_local_struct_name_occurrences(type_name) > 1
        has_existing_collision = (
            candidate_reader in self._all_type_aliases
            or candidate_builder in self._all_type_aliases
            or candidate_reader in self._imported_aliases
            or candidate_builder in self._imported_aliases
        )
        if has_local_collision or has_existing_collision:
            return self._build_flat_name_from_scope(type_name, scope)
        return type_name

    def _resolve_flat_interface_client_name(self, type_name: str, scope: Scope) -> str:
        """Resolve the flattened top-level Client class name for an interface."""
        candidate_name = f"{type_name}Client"
        has_local_collision = self._count_local_interface_name_occurrences(type_name) > 1
        has_existing_collision = candidate_name in self._all_type_aliases or candidate_name in self._imported_aliases
        if has_local_collision or has_existing_collision:
            return f"{self._build_flat_name_from_scope(type_name, scope)}Client"
        return candidate_name

    def _resolve_nested_schema(
        self,
        nested_node: NestedNodeReader,
    ) -> capnp_types.SchemaType | None:
        """Resolve a nested schema from a nested node.

        Args:
            nested_node: The nested node to resolve
            parent_schema: The parent struct schema

        Returns:
            The nested schema or None if it cannot be resolved

        """
        # Look up the nested schema by ID in our schema mapping
        return self._schemas_by_id.get(nested_node.id)

    def _generate_nested_types(self, schema: _StructSchema) -> None:
        """Generate all nested types (structs, enums, interfaces) within this struct.

        Nested types must be generated before processing fields so they're available
        for reference in field types.

        Args:
            schema: The struct schema containing nested nodes
            type_name: The name of the parent type (for error messages and fallback)

        """
        for nested_node in schema.node.nestedNodes:
            nested_schema = self._resolve_nested_schema(nested_node)
            if nested_schema:
                # Don't catch exceptions - let them propagate for debugging
                self.generate_nested(nested_schema)

    def _process_slot_field(
        self,
        field: FieldReader,
        raw_field: _StructSchemaField,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Process a SLOT field and add to collection.

        Args:
            field: The field descriptor from schema.capnp
            raw_field: The pycapnp field schema wrapper
            context: The struct generation context
            fields_collection: The collection to add the field to

        """
        slot_field = self.gen_slot(
            raw_field,
            field,
            fields_collection.init_choices,
            fields_collection.list_init_choices,
        )

        if slot_field is not None:
            fields_collection.add_slot_field(slot_field)

    def _process_group_field(
        self,
        field: FieldReader,
        raw_field: _StructSchemaField,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Process a GROUP field and add to collection.

        GROUP fields are essentially nested structs that are generated recursively.

        Args:
            field: The field descriptor from schema.capnp
            raw_field: The pycapnp field schema wrapper
            fields_collection: The collection to add the field to

        """
        # Capitalize first letter for group type name
        # Always scope group type name to parent to avoid collisions
        # e.g. Node.struct -> NodeStruct, Type.struct -> TypeStruct
        # e.g. Person.address -> PersonAddress, Company.address -> CompanyAddress
        parent_protocol = self.scope.name
        parent_name = self._extract_name_from_protocol(parent_protocol)
        group_name = f"{parent_name}{field.name[0].upper() + field.name[1:]}"

        assert group_name != field.name

        # Generate the group struct recursively
        group_type = self.gen_struct(self._require_struct_schema(raw_field), type_name=group_name)
        group_scoped_name = group_type.scoped_name

        # Create hinted variable for the group field
        hinted_variable = helper.TypeHintedVariable(
            helper.sanitize_name(field.name),
            [helper.TypeHint(group_scoped_name, primary=True)],
        )

        # Try to use flat TypeAliases for Builder/Reader if available
        builder_alias = self._get_flat_builder_alias(group_scoped_name)
        reader_alias = self._get_flat_reader_alias(group_scoped_name)

        if builder_alias and reader_alias:
            # Use flat aliases with affix only for lookup (flat_alias=True prevents appending affix)
            hinted_variable.add_type_hint(helper.TypeHint(builder_alias, affix="Builder", flat_alias=True))
            hinted_variable.add_type_hint(helper.TypeHint(reader_alias, affix="Reader", flat_alias=True))
        else:
            # Fall back to scoped names with affixes (old behavior)
            hinted_variable.add_builder_from_primary_type()
            hinted_variable.add_reader_from_primary_type()

        # Add to collections
        fields_collection.add_slot_field(hinted_variable)
        fields_collection.add_init_choice(helper.sanitize_name(field.name), group_scoped_name)

    def _process_struct_fields(
        self,
        schema: _StructSchema,
        _context: StructGenerationContext,
    ) -> StructFieldsCollection:
        """Process all fields in a struct and collect field metadata.

        Args:
            schema: The struct schema
            _context: The generation context

        Returns:
            Collection of processed fields and metadata

        """
        fields_collection = StructFieldsCollection()

        for field, raw_field in zip(schema.node.struct.fields, schema.as_struct().fields_list, strict=False):
            field_type = field.which()

            if field_type == capnp_types.CapnpFieldType.SLOT:
                self._process_slot_field(field, raw_field, fields_collection)
            elif field_type == capnp_types.CapnpFieldType.GROUP:
                self._process_group_field(field, raw_field, fields_collection)
            else:
                msg = f"{schema.node.displayName}: {field.name}: {field.which()}"
                raise AssertionError(msg)

        return fields_collection

    def _generate_nested_reader_class(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Generate the runtime Reader marker nested inside the struct module.

        Args:
            context: The generation context
            fields_collection: The processed fields collection

        """
        _ = context
        _ = fields_collection
        self.scope.add("class Reader(_DynamicStructReader): ...")

    def _generate_nested_builder_class(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Generate the runtime Builder marker nested inside the struct module.

        Args:
            context: The generation context
            fields_collection: The processed fields collection

        """
        _ = context
        _ = fields_collection
        self.scope.add("class Builder(_DynamicStructBuilder): ...")

    def _generate_flat_reader_class(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Generate the precise flattened top-level Reader typing class.

        This models the dynamic object returned at runtime more closely than the
        runtime-only ``Struct.Reader`` marker class.
        """
        root_scope = self.scope.root
        reader_class_declaration = helper.new_class_declaration(
            context.reader_type_name,
            parameters=["_DynamicStructReader"],
        )
        root_scope.add(reader_class_declaration)
        _ = self.new_scope(context.reader_type_name, context.schema.node, register=False, parent_scope=root_scope)
        self._gen_struct_reader_class(
            fields_collection.slot_fields,
            context.builder_type_name,
            context.schema,
        )
        self.return_from_scope()

    def _generate_flat_builder_class(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Generate the precise flattened top-level Builder typing class.

        This models the dynamic object returned at runtime more closely than the
        runtime-only ``Struct.Builder`` marker class.
        """
        root_scope = self.scope.root
        builder_class_declaration = helper.new_class_declaration(
            context.builder_type_name,
            parameters=["_DynamicStructBuilder"],
        )
        root_scope.add(builder_class_declaration)
        _ = self.new_scope(context.builder_type_name, context.schema.node, register=False, parent_scope=root_scope)
        self._gen_struct_builder_class(
            fields_collection.slot_fields,
            fields_collection.init_choices,
            fields_collection.list_init_choices,
            context.reader_type_name,
            context.schema,
        )
        self.return_from_scope()

    def _generate_struct_classes(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
        protocol_declaration: str,
    ) -> None:
        """Generate one struct module plus flattened top-level Builder/Reader typing classes.

        This generates:
        1. The runtime-facing _<Name>StructModule with separate nested Reader and Builder markers
        2. Flattened top-level <Name>Reader and <Name>Builder typing classes
        3. The runtime module annotation linking the public struct name to _<Name>StructModule

        Args:
            context: Generation context with names and metadata
            fields_collection: Processed fields and init choices
            protocol_declaration: The Module class declaration string

        """
        protocol_class_name = f"_{context.type_name}StructModule"

        # Add Protocol class declaration to parent scope
        if self.scope.parent:
            if self.scope.parent.is_root:
                self._root_module_class_names.add(protocol_class_name)
            self.scope.parent.add(protocol_declaration)

        # Generate the runtime Reader/Builder markers nested inside the struct module.
        self._generate_nested_reader_class(context, fields_collection)
        self._generate_nested_builder_class(context, fields_collection)
        self._add_module_schema_helpers(context.schema)

        # Generate struct-module methods that return the precise flattened Builder/Reader types.
        self._gen_struct_base_class(
            fields_collection.slot_fields,
            context.reader_type_name,
            context.builder_type_name,
        )

        # Emit the precise typing-only Builder/Reader classes at module top level.
        self._generate_flat_reader_class(context, fields_collection)
        self._generate_flat_builder_class(context, fields_collection)

        self.return_from_scope()

        # Track the flattened Builder/Reader classes so local references resolve, but don't re-emit them as aliases.
        self._all_type_aliases[context.reader_type_name] = (context.scoped_reader_type_name, "ReaderClass")
        self._all_type_aliases[context.builder_type_name] = (context.scoped_builder_type_name, "BuilderClass")

        # Add annotation for the module type at the correct parent scope
        # Use the registered type's scope to ensure it goes to the right place
        # For top-level types, this is root scope; for nested types, this is the parent's scope
        target_scope = context.new_type.scope or self.scope
        target_scope.add(f"{context.type_name}: {protocol_class_name}")

    def gen_struct(self, schema: _StructSchema | _EnumSchema | _InterfaceSchema, type_name: str = "") -> CapnpType:
        """Generate a `struct` object.

        This orchestrator delegates to specialized methods for clarity and testability.

        Args:
            schema: The schema to generate the `struct` object out of (must be a struct schema).
            type_name (str, optional): A type name to override the display name of the struct. Defaults to "".

        Returns:
            Type: The `struct`-type module that was generated.

        """
        assert isinstance(schema, _StructSchema), f"Expected _StructSchema, got {type(schema).__name__}"
        assert schema.node.which() == capnp_types.CapnpElementType.STRUCT

        # Phase 1: Setup and initialization
        context, protocol_declaration = self._setup_struct_generation(schema, type_name)
        if context is None:
            # Already imported or skipped due to missing parent scope
            # Try to return the already registered type if available
            registered_type = self._maybe_get_type_by_id(schema.node.id)
            if registered_type is not None:
                return registered_type
            if not type_name:
                type_name = helper.get_display_name(schema)
            return self.register_type(schema.node.id, schema, name=type_name, scope=self.scope.root)

        # Register TypeAliases early so they're available during field processing
        # This handles self-referential fields and forward references
        self._all_type_aliases[context.reader_type_name] = (context.scoped_reader_type_name, "ReaderClass")
        self._all_type_aliases[context.builder_type_name] = (context.scoped_builder_type_name, "BuilderClass")

        # Phase 2: Generate nested types (must be done before field processing)
        self._generate_nested_types(schema)

        # Phase 3: Process all struct fields
        fields_collection = self._process_struct_fields(schema, context)

        # Phase 4: Generate the Protocol with nested Protocols and TypeAliases
        self._generate_struct_classes(context, fields_collection, protocol_declaration)

        return context.new_type

    # ===== Interface Generation Helper Methods (Phase 2 Extraction) =====

    def _setup_interface_generation(self, schema: _InterfaceSchema) -> InterfaceGenerationContext | None:
        """Set up interface generation and create its context.

        Args:
            schema: The Cap'n Proto interface schema

        Returns:
            InterfaceGenerationContext or None if already imported

        """
        assert schema.node.which() == capnp_types.CapnpElementType.INTERFACE

        # Check if already imported
        imported = self.register_import(schema)
        if imported is not None:
            return None
        if self.is_type_id_known(schema.node.id):
            return None

        # IMPORTANT: Ensure parent scope exists before registering this interface
        # For nested interfaces, the parent interface must be generated first
        parent_scope = self.scopes_by_id.get(schema.node.scopeId)
        if parent_scope is None:
            # Parent scope doesn't exist yet - need to generate the parent first
            # Find the parent schema and generate it
            parent_schema = self._schemas_by_id.get(schema.node.scopeId)
            if parent_schema and parent_schema.node.which() == capnp_types.CapnpElementType.INTERFACE:
                logger.debug(
                    "Generating parent interface %s before nested %s",
                    parent_schema.node.displayName,
                    schema.node.displayName,
                )
                # Recursively generate the parent interface first
                # Try to get it as an interface schema from the loader
                try:
                    interface_schema = self._schema_loader.get(parent_schema.node.id)
                    if hasattr(interface_schema, "as_interface"):
                        _ = self.gen_interface(interface_schema.as_interface())
                    elif isinstance(interface_schema, _InterfaceSchema):
                        _ = self.gen_interface(interface_schema)
                except TYPE_GENERATION_EXCEPTIONS as error:
                    logger.debug("Could not generate parent interface: %s", error)
                # Now the parent scope should exist
                parent_scope = self.scopes_by_id.get(schema.node.scopeId)

            # If still no parent scope, fall back to root
            if parent_scope is None:
                parent_scope = self.scope.root

        # Get display name
        name = helper.get_display_name(schema)

        # Register type with Protocol name (_<Name>InterfaceModule) for correct internal references
        # This ensures get_type_name() returns the Protocol name, not the user-facing name
        protocol_name = f"_{name}InterfaceModule"
        registered_type = self.register_type(schema.node.id, schema, name=protocol_name, scope=parent_scope)

        # Add typing imports
        self._add_typing_import("Protocol")
        self._add_typing_import("Iterator")
        self._add_typing_import("Any")

        # Collect base classes
        base_classes = self._collect_interface_base_classes(schema)

        # Create and return context
        context = InterfaceGenerationContext.create(
            schema=schema,
            type_name=name,
            registered_type=registered_type,
            base_classes=base_classes,
            parent_scope=parent_scope,
        )
        context.client_type_name = self._resolve_flat_interface_client_name(name, registered_type.scope)
        self._all_interfaces[registered_type.scoped_name] = (context.client_type_name, [])
        return context

    def _enumerate_interface_methods(self, context: InterfaceGenerationContext) -> list[MethodInfo]:
        """Enumerate methods from runtime interface.

        Args:
            context: The interface generation context

        Returns:
            List of MethodInfo objects

        """
        # Use the schema directly from context instead of traversing runtime objects
        iface_schema = context.schema
        method_items = iface_schema.methods.items()

        return [MethodInfo.from_runtime_method(method_name, method) for method_name, method in method_items]

    @staticmethod
    def _find_struct_field(param_schema: _StructSchema, field_name: str) -> FieldReader:
        """Find a field by name inside a struct schema."""
        return next(field for field in param_schema.node.struct.fields if field.name == field_name)

    @staticmethod
    def _get_anypointer_kind(type_reader: TypeReader) -> str:
        """Return the unconstrained AnyPointer kind, or `anyKind` when unavailable."""
        try:
            if type_reader.anyPointer.which() == "unconstrained":
                return type_reader.anyPointer.unconstrained.which()
        except (AttributeError, IndexError):
            pass
        return "anyKind"

    def _get_struct_builder_reader_types(self, type_name: str) -> tuple[str, str, str | None, str | None]:
        """Return Builder/Reader type names plus any local flat aliases for a struct."""
        return (
            self._build_nested_builder_type(type_name),
            self._build_nested_reader_type(type_name),
            self._get_flat_builder_alias(type_name),
            self._get_flat_reader_alias(type_name),
        )

    def _get_interface_client_server_types(self, interface_type: str) -> tuple[str, str]:
        """Return nested Client and Server type names for an interface Protocol path."""
        client_alias = self._get_flat_client_alias(interface_type)
        if client_alias:
            return client_alias, f"{interface_type}.Server"

        last_part = interface_type.rsplit(".", maxsplit=1)[-1]
        if last_part.startswith("_"):
            client_type = f"{self._extract_name_from_protocol(last_part)}Client"
        else:
            client_type = f"{interface_type}Client"
        return client_type, f"{interface_type}.Server"

    def _resolve_method_parameter_types(self, field_obj: FieldReader, base_type: str) -> tuple[str, str, str]:
        """Resolve client/server/request types for one method parameter field."""
        field_type = field_obj.slot.type.which()
        result = (base_type, base_type, base_type)

        if field_type == capnp_types.CapnpElementType.ANY_POINTER:
            self._needs_anypointer_alias = True
            result = ("AnyPointer", "AnyPointer", "AnyPointer")
        elif field_type == capnp_types.CapnpElementType.ENUM:
            enum_type = self.get_type_name(field_obj.slot.type)
            result = (enum_type, enum_type, enum_type)
        elif field_type == capnp_types.CapnpElementType.STRUCT:
            builder_type, reader_type, builder_alias, reader_alias = self._get_struct_builder_reader_types(base_type)
            if builder_alias and reader_alias:
                result = (
                    f"{builder_alias} | {reader_alias} | dict[str, Any]",
                    reader_alias,
                    builder_alias,
                )
            else:
                result = (f"{base_type} | dict[str, Any]", reader_type, builder_type)
        elif field_type == capnp_types.CapnpElementType.LIST:
            _, reader_alias, builder_alias = self._generate_list_class(field_obj.slot.type)
            self._add_typing_import("Sequence")
            self._add_typing_import("Any")
            sequence_type = f"{builder_alias} | {reader_alias} | Sequence[Any]"
            result = (sequence_type, reader_alias, sequence_type)
        elif field_type == capnp_types.CapnpElementType.INTERFACE:
            last_part = base_type.rsplit(".", maxsplit=1)[-1]
            if last_part.startswith("_"):
                client_type, server_type = self._get_interface_client_server_types(base_type)
                union_type = f"{client_type} | {server_type}"
                result = (union_type, client_type, union_type)
            else:
                union_type = f"{base_type} | {base_type}.Server"
                result = (union_type, base_type, union_type)

        return result

    def _process_method_parameter(
        self,
        param_name: str,
        param_schema: _StructSchema,
    ) -> ParameterInfo:
        """Process a single method parameter and determine its types.

        Args:
            param_name: Name of the parameter
            param_schema: Schema containing the parameter

        Returns:
            ParameterInfo with client/server/request types

        """
        field_obj = self._find_struct_field(param_schema, param_name)

        base_type = self.get_type_name(field_obj.slot.type)
        client_type, server_type, request_type = self._resolve_method_parameter_types(field_obj, base_type)

        return ParameterInfo(
            name=param_name,
            client_type=client_type,
            server_type=server_type,
            request_type=request_type,
        )

    def _process_method_results(
        self,
        method_info: MethodInfo,
    ) -> tuple[str, bool]:
        """Process method results to determine return type.

        Args:
            method_info: Information about the method

        Returns:
            Tuple of (return_type, is_direct_struct_return)

        """
        # Always generate a Result class name (even for void methods)
        # For void methods, the Result Protocol will be awaitable but have no fields
        result_class_name = f"{helper.sanitize_name(method_info.method_name).title()}Result"

        if not method_info.result_fields:
            # Void method: still return Result class name for promise pipelining
            return result_class_name, False

        # Check if result schema is a direct struct return (not a synthetic $Results struct)
        # When you write `method() -> Struct`, pycapnp gives you the Struct schema directly
        # When you write `method() -> (field: Type)`, pycapnp creates a synthetic "method$Results" schema
        is_direct_struct = False
        if method_info.result_schema is not None:
            display_name = method_info.result_schema.node.displayName
            is_direct_struct = not display_name.endswith("$Results")

        if is_direct_struct:
            # Direct struct return: use Result Protocol with struct's fields expanded
            return result_class_name, True

        # Named field return (single or multiple): use Result Protocol
        return result_class_name, False

    @staticmethod
    def _is_direct_struct_parameter(method_info: MethodInfo) -> bool:
        """Return whether a method uses direct-struct parameter shorthand."""
        if method_info.param_schema is None:
            return False
        return not method_info.param_schema.node.displayName.endswith("$Params")

    def _get_direct_struct_param_context_type(self, method_info: MethodInfo) -> str | None:
        """Return the reader type exposed by CallContext.params for direct-struct params."""
        if not self._is_direct_struct_parameter(method_info) or method_info.param_schema is None:
            return None

        struct_type = self.get_type_by_id(method_info.param_schema.node.id)
        return self._get_flat_reader_alias(struct_type.scoped_name) or self._build_nested_reader_type(
            struct_type.scoped_name,
        )

    def _supports_regular_server_method_signature(self, method_info: MethodInfo) -> bool:
        """Return whether the flattened server method signature is safe to advertise."""
        if not self._is_direct_struct_parameter(method_info) or method_info.param_schema is None:
            return True

        return method_info.param_schema.node.struct.discriminantCount == 0

    def _get_client_type_name_from_interface_path(self, interface_path: str) -> str:
        """Extract client type name from interface path.

        E.g., "_HolderInterfaceModule" -> "HolderClient"
              "_CalculatorInterfaceModule._FunctionInterfaceModule" -> "FunctionClient"

        Args:
            interface_path: The full interface path

        Returns:
            The client type name

        """
        interface_info = self._all_interfaces.get(interface_path)
        if interface_info is not None:
            return interface_info[0]

        # Get the last component: "_HolderInterfaceModule" -> "_HolderInterfaceModule"
        last_component = interface_path.rsplit(".", maxsplit=1)[-1]
        # Remove "_" prefix and "Module" suffix: "_HolderInterfaceModule" -> "Holder"
        name = self._extract_name_from_protocol(last_component)
        # Add "Client" suffix: "Holder" -> "HolderClient"
        return f"{name}Client"

    def _count_local_interface_helper_name_occurrences(self, helper_name: str) -> int:
        """Count helper class names shared by local interface methods in this module."""
        count = 0
        for local_schema in self._schemas_by_id.values():
            if (
                local_schema.node.which() != capnp_types.CapnpElementType.INTERFACE
                or not self._is_schema_in_current_module(local_schema)
            ):
                continue

            for method in local_schema.node.interface.methods:
                method_base = helper.sanitize_name(method.name).title()
                generated_names = {
                    f"{method_base}Request",
                    f"{method_base}Result",
                    f"{method_base}ServerResult",
                    f"{method_base}Params",
                    f"{method_base}CallContext",
                    f"{method_base}ResultTuple",
                }
                if helper_name in generated_names:
                    count += 1
        return count

    def _build_interface_method_type_names(
        self,
        context: InterfaceGenerationContext,
        method_info: MethodInfo,
    ) -> InterfaceMethodTypeNames:
        """Build flattened helper type names for one interface method."""
        method_base = helper.sanitize_name(method_info.method_name).title()
        interface_prefix = context.client_type_name.removesuffix("Client")

        def resolve(candidate: str) -> str:
            reserved_names = (
                set(self._all_type_aliases) | self._imported_aliases | self._generated_interface_helper_types
            )
            if self._count_local_interface_helper_name_occurrences(candidate) > 1 or candidate in reserved_names:
                return f"{interface_prefix}{candidate}"
            return candidate

        return InterfaceMethodTypeNames(
            request_type_name=resolve(f"{method_base}Request"),
            client_result_type_name=resolve(f"{method_base}Result"),
            server_result_type_name=resolve(f"{method_base}ServerResult"),
            params_type_name=resolve(f"{method_base}Params"),
            call_context_type_name=resolve(f"{method_base}CallContext"),
            result_tuple_type_name=resolve(f"{method_base}ResultTuple"),
        )

    def _emit_top_level_helper_class(self, class_name: str, lines: list[str]) -> None:
        """Emit a typing-only helper class at module top level once."""
        if not lines or class_name in self._generated_interface_helper_types:
            return

        self._generated_interface_helper_types.add(class_name)
        root_scope = self.scope.root
        if root_scope.lines and root_scope.lines[-1] != "":
            root_scope.add("")
        for line in lines:
            root_scope.add(line)

    def _emit_top_level_namedtuple_class(
        self,
        class_name: str,
        fields: list[tuple[str, str]],
    ) -> None:
        """Emit a server result NamedTuple at module top level once."""
        if class_name in self._generated_interface_helper_types:
            return

        self._add_typing_import("NamedTuple")
        lines = [f"class {class_name}(NamedTuple):"]
        if fields:
            for field_name, field_type in fields:
                lines.append(f"    {field_name}: {field_type}")
        else:
            lines.append("    pass")
        self._emit_top_level_helper_class(class_name, lines)

    def _get_list_parameters(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
    ) -> list[tuple[str, str]]:
        """Extract list parameters that need init() overloads.

        Args:
            method_info: Information about the method
            parameters: List of processed parameters

        Returns:
            List of (field_name, list_builder_type) tuples

        """
        list_params: list[tuple[str, str]] = []

        if method_info.param_schema is None:
            return list_params

        for param in parameters:
            field_obj = self._find_struct_field(method_info.param_schema, param.name)

            if field_obj.slot.type.which() == capnp_types.CapnpElementType.LIST:
                # Generate list class and get aliases
                _, _, builder_alias = self._generate_list_class(field_obj.slot.type)
                list_params.append((param.name, builder_alias))

        return list_params

    def _get_struct_parameters(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
    ) -> list[tuple[str, str]]:
        """Extract struct parameters that need init() overloads.

        Args:
            method_info: Information about the method
            parameters: List of processed parameters

        Returns:
            List of (field_name, struct_builder_type) tuples

        """
        struct_params: list[tuple[str, str]] = []

        if method_info.param_schema is None:
            return struct_params

        for param in parameters:
            field_obj = self._find_struct_field(method_info.param_schema, param.name)

            if field_obj.slot.type.which() == capnp_types.CapnpElementType.STRUCT:
                struct_type_name = self.get_type_name(field_obj.slot.type)
                # Get the Builder type for the struct - try flat alias first
                builder_alias = self._get_flat_builder_alias(struct_type_name)
                builder_type = builder_alias or self._build_scoped_builder_type(struct_type_name)
                struct_params.append((param.name, builder_type))

        return struct_params

    def _generate_client_method(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
        result_type: str,
    ) -> list[str]:
        """Generate client method signature.

        Args:
            method_info: Information about the method
            parameters: List of processed parameters
            result_type: The return type

        Returns:
            List of lines for the client method

        """
        method_name = helper.sanitize_name(method_info.method_name)

        # For promise pipelining: return the Result directly (not wrapped in Awaitable)
        # The Result Protocol has fields for pipelining AND can be awaited
        wrapped_result_type = result_type

        # Build parameter list
        param_list = ["self"] + [p.to_client_param() for p in parameters]
        param_str = ", ".join(param_list)

        # Generate method signature
        return [f"def {method_name}({param_str}) -> {wrapped_result_type}: ..."]

    def _generate_request_protocol(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
        request_class_name: str,
        result_type: str,
    ) -> list[str]:
        """Generate Request Protocol class for a method.

        Args:
            method_info: Information about the method
            parameters: List of processed parameters
            request_class_name: Name of the request helper class to generate
            result_type: The return type for send()

        Returns:
            List of lines for the Request Protocol class

        """
        lines: list[str] = []

        # Class declaration
        lines.append(f"class {request_class_name}(Protocol):")

        # Add parameter fields
        for param in parameters:
            # Sanitize field name to avoid Python keywords
            sanitized_name = helper.sanitize_name(param.name)
            lines.append(f"    {sanitized_name}: {param.request_type}")

        # Collect parameters that need init() overloads
        list_params = self._get_list_parameters(method_info, parameters)
        struct_params = self._get_struct_parameters(method_info, parameters)

        # Add init() overloads if there are list or struct parameters
        if list_params or struct_params:
            self._add_typing_import("overload")
            self._add_typing_import("Literal")

            # Add list init overloads
            if list_params:
                for field_name, list_builder_type in list_params:
                    lines.append("    @overload")
                    lines.append(
                        f'    def init(self, name: Literal["{field_name}"], size: int = ...) -> {list_builder_type}: ...'
                    )

            # Add struct init overloads
            for field_name, builder_type in struct_params:
                lines.append("    @overload")
                lines.append(f'    def init(self, name: Literal["{field_name}"]) -> {builder_type}: ...')

            # Add a catchall overload for pyright
            lines.append("    @overload")
            lines.append("    def init(self, name: str, size: int = ...) -> Any: ...")

        # Add send() method - returns the Result directly for pipelining
        send_return = result_type
        lines.append(f"    def send(self) -> {send_return}: ...")

        return lines

    def _server_anypointer_alias_type(self, any_pointer_kind: str) -> str:
        """Return the server-side alias type for an AnyPointer result field."""
        alias_by_kind = {
            "capability": ("Capability", "_needs_capability_alias"),
            "struct": ("AnyStruct", "_needs_anystruct_alias"),
            "list": ("AnyList", "_needs_anylist_alias"),
        }
        alias_name, flag_name = alias_by_kind.get(any_pointer_kind, ("AnyPointer", "_needs_anypointer_alias"))
        setattr(self, flag_name, True)
        return alias_name

    def _resolve_named_result_field_type(
        self,
        field_obj: FieldReader,
        *,
        for_server: bool,
    ) -> tuple[str, str | None, str | None]:
        """Resolve the field type used by named result protocols and NamedTuples."""
        field_type = self.get_type_name(field_obj.slot.type)
        field_type_enum = field_obj.slot.type.which()

        if field_type_enum == capnp_types.CapnpElementType.ANY_POINTER:
            return (
                (self._server_anypointer_alias_type(self._get_anypointer_kind(field_obj.slot.type)), None, None)
                if for_server
                else ("_DynamicObjectReader", None, None)
            )

        if field_type_enum == capnp_types.CapnpElementType.STRUCT:
            builder_type, reader_type, builder_alias, reader_alias = self._get_struct_builder_reader_types(field_type)
            builder_hint = builder_alias or builder_type
            reader_hint = reader_alias or reader_type
            return (f"{builder_hint} | {reader_hint}" if for_server else reader_hint, builder_hint, reader_hint)

        if field_type_enum == capnp_types.CapnpElementType.INTERFACE:
            client_type, server_type = self._get_interface_client_server_types(field_type)
            return (f"{server_type} | {client_type}" if for_server else client_type, None, None)

        if field_type_enum == capnp_types.CapnpElementType.LIST:
            _, reader_alias, builder_alias = self._generate_list_class(field_obj.slot.type)
            return (f"{builder_alias} | {reader_alias}" if for_server else reader_alias, builder_alias, reader_alias)

        return (field_type, None, None)

    def _resolve_direct_result_field_type(self, field_obj: FieldReader, *, for_server: bool) -> str:
        """Resolve a field type for direct-struct result protocols."""
        if field_obj.slot.type.which() != capnp_types.CapnpElementType.ANY_POINTER:
            return self._resolve_named_result_field_type(field_obj, for_server=for_server)[0]

        any_pointer_kind = self._get_anypointer_kind(field_obj.slot.type)
        field_type = "_DynamicObjectReader"
        if for_server:
            if any_pointer_kind == "capability":
                field_type = "_DynamicCapabilityClient | _DynamicCapabilityServer"
            else:
                self._needs_anypointer_alias = True
                field_type = "AnyPointer"
        elif any_pointer_kind == "capability":
            field_type = "_DynamicCapabilityClient"
        elif any_pointer_kind == "struct":
            field_type = "_DynamicStructReader"
        elif any_pointer_kind == "list":
            field_type = "_DynamicListReader"
        return field_type

    @staticmethod
    def _collect_union_field_names(result_schema: _StructSchema) -> list[str]:
        """Collect union field names for a result struct."""
        return [
            field.name for field in result_schema.node.struct.fields if field.discriminantValue != DISCRIMINANT_NONE
        ]

    def _build_server_result_property_lines(
        self,
        field_name: str,
        field_type_enum: str,
        field_type: str,
        builder_hint: str | None,
        reader_hint: str | None,
    ) -> list[str]:
        """Build property getter/setter lines for server-side result wrappers."""
        getter_type = field_type
        setter_type = field_type

        if field_type_enum == capnp_types.CapnpElementType.LIST and builder_hint and reader_hint:
            self._add_typing_import("Sequence")
            self._add_typing_import("Any")
            getter_type = builder_hint
            setter_type = f"{builder_hint} | {reader_hint} | Sequence[Any]"
        elif field_type_enum == capnp_types.CapnpElementType.STRUCT and builder_hint:
            self._add_typing_import("Any")
            getter_type = builder_hint
            setter_type = f"{field_type} | dict[str, Any]"

        return [
            "    @property",
            f"    def {field_name}(self) -> {getter_type}: ...",
            f"    @{field_name}.setter",
            f"    def {field_name}(self, value: {setter_type}) -> None: ...",
        ]

    def _append_server_result_init_overloads(self, lines: list[str], init_fields: list[tuple[str, str]]) -> None:
        """Append init() overloads for server-side named result wrappers."""
        if not init_fields:
            return

        self._add_typing_import("overload")
        self._add_typing_import("Literal")
        self._add_typing_import("Any")
        for field_name, return_type in init_fields:
            lines.extend(
                [
                    "    @overload",
                    f'    def init(self, field: Literal["{field_name}"], size: int | None = None) -> {return_type}: ...',
                ],
            )
        lines.extend(["    @overload", "    def init(self, field: str, size: int | None = None) -> Any: ..."])

    def _resolve_server_result_assignment_type(self, field_obj: FieldReader) -> str:
        """Resolve the input type accepted when a server assigns or returns a result field."""
        field_type_enum = field_obj.slot.type.which()
        field_type, builder_hint, reader_hint = self._resolve_named_result_field_type(field_obj, for_server=True)

        if field_type_enum == capnp_types.CapnpElementType.LIST and builder_hint and reader_hint:
            self._add_typing_import("Sequence")
            self._add_typing_import("Any")
            return f"{builder_hint} | {reader_hint} | Sequence[Any]"

        if field_type_enum == capnp_types.CapnpElementType.STRUCT and builder_hint:
            self._add_typing_import("Any")
            return f"{field_type} | dict[str, Any]"

        return field_type

    def _generate_direct_result_protocol_lines(
        self,
        method_info: MethodInfo,
        result_type: str,
        *,
        for_server: bool,
    ) -> list[str]:
        """Generate the Result protocol for a direct struct return."""
        self._add_typing_import("Awaitable")
        lines = [f"class {result_type}(Awaitable[{result_type}], Protocol):"]
        if method_info.result_schema is None:
            return lines

        for field_name in method_info.result_fields:
            field_obj = self._find_struct_field(method_info.result_schema, field_name)
            field_type = self._resolve_direct_result_field_type(field_obj, for_server=for_server)
            lines.append(f"    {field_name}: {field_type}")

        union_fields = self._collect_union_field_names(method_info.result_schema)
        if union_fields:
            self._add_typing_import("Literal")
            union_literal = ", ".join(f'"{field_name}"' for field_name in union_fields)
            lines.append(f"    def which(self) -> Literal[{union_literal}]: ...")
        return lines

    def _generate_void_result_protocol_lines(self, result_type: str) -> list[str]:
        """Generate the Result protocol for a void method."""
        self._add_typing_import("Awaitable")
        return [f"class {result_type}(Awaitable[None], Protocol):", "    ..."]

    def _generate_named_result_protocol_lines(
        self,
        method_info: MethodInfo,
        result_type: str,
        *,
        for_server: bool,
    ) -> list[str]:
        """Generate the Result protocol for named-field results."""
        if for_server:
            lines = [f"class {result_type}(_DynamicStructBuilder):"]
        else:
            self._add_typing_import("Awaitable")
            lines = [f"class {result_type}(Awaitable[{result_type}], Protocol):"]

        init_fields: list[tuple[str, str]] = []
        if method_info.result_schema is None:
            return lines

        for field_name in method_info.result_fields:
            field_obj = self._find_struct_field(method_info.result_schema, field_name)
            field_type_enum = field_obj.slot.type.which()
            field_type, builder_hint, reader_hint = self._resolve_named_result_field_type(
                field_obj, for_server=for_server
            )
            if for_server:
                if (
                    field_type_enum in {capnp_types.CapnpElementType.STRUCT, capnp_types.CapnpElementType.LIST}
                    and builder_hint
                ):
                    init_fields.append((field_name, builder_hint))
                lines.extend(
                    self._build_server_result_property_lines(
                        field_name,
                        field_type_enum,
                        field_type,
                        builder_hint,
                        reader_hint,
                    ),
                )
            else:
                lines.append(f"    {field_name}: {field_type}")

        if for_server:
            self._append_server_result_init_overloads(lines, init_fields)
        return lines

    def _generate_result_protocol(
        self,
        method_info: MethodInfo,
        result_type: str,
        *,
        is_direct_struct_return: bool,
        for_server: bool = False,
    ) -> list[str]:
        """Generate Result Protocol class for a method.

        Args:
            method_info: Information about the method
            result_type: The result type name (unscoped)
            is_direct_struct_return: Whether this is a direct struct return
            for_server: If True, generate server-side types (broader unions for AnyPointer)

        Returns:
            List of lines for the Result Protocol class

        """
        if is_direct_struct_return:
            return self._generate_direct_result_protocol_lines(method_info, result_type, for_server=for_server)

        if not method_info.result_fields:
            return self._generate_void_result_protocol_lines(result_type)

        return self._generate_named_result_protocol_lines(method_info, result_type, for_server=for_server)

    def _generate_request_helper_method(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
        request_class_name: str,
    ) -> list[str]:
        """Generate _request helper method for creating Request objects.

        Args:
            method_info: Information about the method
            parameters: List of processed parameters
            request_class_name: Name of the request helper type returned by the method

        Returns:
            List of lines for the _request helper method

        """
        method_name = helper.sanitize_name(method_info.method_name)

        # Build parameter list (similar to client method)
        param_list = ["self"] + [p.to_request_param() for p in parameters]
        param_str = ", ".join(param_list)

        return [f"def {method_name}_request({param_str}) -> {request_class_name}: ..."]

    @staticmethod
    def _sanitize_namedtuple_field_name(field_name: str) -> str:
        """Sanitize field name to avoid conflicts with NamedTuple/tuple methods.

        NamedTuple inherits from tuple, which has methods: count, index.
        If a field name conflicts, we append an underscore.

        Args:
            field_name: The original field name

        Returns:
            Sanitized field name safe for NamedTuple

        """
        # Reserved names from tuple that NamedTuple inherits
        reserved_names = {"count", "index"}

        if field_name in reserved_names:
            return f"{field_name}_"
        return field_name

    def _collect_result_fields_for_namedtuple(
        self,
        method_info: MethodInfo,
    ) -> list[tuple[str, str]]:
        """Collect result fields for NamedTuple definition.

        Gets the field names and assignment-friendly types for server NamedTuple
        result types so tuple construction matches what `context.results` setters
        accept.

        Args:
            method_info: Information about the method

        Returns:
            List of (field_name, field_type) tuples

        """
        fields: list[tuple[str, str]] = []

        if not method_info.result_fields or method_info.result_schema is None:
            return fields

        for field_name in method_info.result_fields:
            field_obj = self._find_struct_field(method_info.result_schema, field_name)
            field_type = self._resolve_server_result_assignment_type(field_obj)
            sanitized_name = self._sanitize_namedtuple_field_name(field_name)
            fields.append((sanitized_name, field_type))

        return fields

    def _get_single_server_result_type(self, method_info: MethodInfo) -> str | None:
        """Return the specialized single-field server result type, if one exists."""
        primitive_field_types = {
            "void",
            "bool",
            "int8",
            "int16",
            "int32",
            "int64",
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "float32",
            "float64",
            "text",
            "data",
        }
        if len(method_info.result_fields) != 1 or method_info.result_schema is None:
            return None

        result_type: str | None = None
        field_obj = self._find_struct_field(method_info.result_schema, method_info.result_fields[0])
        field_type_enum = field_obj.slot.type.which()
        if field_type_enum in primitive_field_types or field_type_enum == capnp_types.CapnpElementType.ENUM:
            result_type = self.get_type_name(field_obj.slot.type)
        else:
            result_type = self._resolve_server_result_assignment_type(field_obj)

        return result_type

    def _generate_server_method_signature(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
        call_context_type: str,
        result_tuple_type: str,
    ) -> str:
        """Generate server method signature for Server class.

        Server methods return NamedTuple results or None.
        - For void methods: return Awaitable[None]
        - For methods with results: return Awaitable[Server.XxxResult | None]

        Args:
            method_info: Information about the method
            parameters: List of processed parameters
            call_context_type: Type name used for the `_context` parameter
            result_tuple_type: Type name used for the server-side NamedTuple return helper

        Returns:
            Single-line server method signature

        """
        method_name = helper.sanitize_name(method_info.method_name)

        # Server methods have: self, params..., _context: CallContext, **kwargs
        param_parts = ["self"]
        param_parts.extend([p.to_server_param() for p in parameters])
        param_parts.append(f"_context: {call_context_type}")
        param_parts.append("**kwargs: object")
        param_str = ", ".join(param_parts)

        # Determine return type
        self._add_typing_import("Awaitable")
        if not method_info.result_fields:
            return_type_str = "Awaitable[None]"
        else:
            single_field_type = self._get_single_server_result_type(method_info)
            if single_field_type:
                return_type_str = f"Awaitable[{single_field_type} | {result_tuple_type} | None]"
            else:
                return_type_str = f"Awaitable[{result_tuple_type} | None]"

        return f"    def {method_name}({param_str}) -> {return_type_str}: ..."

    def _generate_server_context_method_signature(
        self,
        method_info: MethodInfo,
        call_context_type: str,
    ) -> str:
        """Generate server method signature with _context suffix.

        This is the alternative server method pattern where the method name ends in _context
        and receives only a context parameter (no individual params).

        Args:
            method_info: Information about the method
            call_context_type: Type name used for the `context` parameter

        Returns:
            Single-line server method signature with _context suffix

        """
        method_name = helper.sanitize_name(method_info.method_name)

        # _context variant only takes context parameter
        param_str = f"self, context: {call_context_type}"

        # _context methods can return promises but not direct values (other than None)
        self._add_typing_import("Awaitable")
        return_type_str = "Awaitable[None]"

        return f"    def {method_name}_context({param_str}) -> {return_type_str}: ..."

    def _generate_params_protocol(
        self,
        parameters: list[ParameterInfo],
        params_class_name: str,
    ) -> list[str]:
        """Generate Params Protocol class for server context.

        Args:
            parameters: List of processed parameters
            params_class_name: Name of the params helper class to generate

        Returns:
            List of lines for the Params Protocol class

        """
        lines = [helper.new_class_declaration(params_class_name, ["Protocol"])]

        for param in parameters:
            sanitized_name = helper.sanitize_name(param.name)
            lines.append(f"    {sanitized_name}: {param.server_type}")

        if not parameters:
            lines.append("    ...")

        return lines

    def _generate_callcontext_protocol(
        self,
        params_type_name: str,
        call_context_type_name: str,
        *,
        has_results: bool,
        result_type_for_context: str | None = None,
    ) -> list[str]:
        """Generate CallContext Protocol for server _context parameter.

        Args:
            params_type_name: Type name used by `CallContext.params`
            call_context_type_name: Name of the CallContext helper class to generate
            has_results: Whether the method has results
            result_type_for_context: Result helper type exposed by `CallContext.results`

        Returns:
            List of lines for CallContext Protocol

        """
        lines = [helper.new_class_declaration(call_context_type_name, ["Protocol"])]

        # CallContext.params points to the flattened Params helper.
        lines.append(f"    params: {params_type_name}")

        # CallContext.results points to the flattened Server Result helper
        # or to the direct struct Builder type.
        if has_results:
            fully_qualified_results = result_type_for_context or "Any"

            # Make results a read-only property
            lines.append("    @property")
            lines.append(f"    def results(self) -> {fully_qualified_results}: ...")
        # Void methods have no results field in CallContext

        return lines

    def _collect_method_parameters(self, method_info: MethodInfo) -> list[ParameterInfo]:
        """Collect processed parameter metadata for an interface method."""
        if method_info.param_schema is None:
            return []

        return [
            self._process_method_parameter(param_name, method_info.param_schema)
            for param_name in method_info.param_fields
        ]

    def _scope_interface_client_result_type(self, result_type: str) -> str:
        """Qualify a result protocol for client methods inside nested interfaces."""
        scope_path = self._get_scope_path()
        scope_depth = len([scope for scope in self.scope.trace if not scope.is_root])
        if scope_depth < 1 or not scope_path or result_type == "None":
            return result_type

        client_type_name = self._get_client_type_name_from_interface_path(scope_path)
        return f"{client_type_name}.{result_type}"

    def _generate_method_result_protocols(
        self,
        method_info: MethodInfo,
        type_names: InterfaceMethodTypeNames,
        *,
        is_direct_struct_return: bool,
    ) -> tuple[list[str], list[str]]:
        """Generate client/server result protocols for a method."""
        client_result_lines = self._generate_result_protocol(
            method_info,
            type_names.client_result_type_name,
            is_direct_struct_return=is_direct_struct_return,
            for_server=False,
        )
        server_result_lines: list[str] = []
        if method_info.result_fields and not is_direct_struct_return:
            server_result_lines = self._generate_result_protocol(
                method_info,
                type_names.server_result_type_name,
                is_direct_struct_return=False,
                for_server=True,
            )
        return client_result_lines, server_result_lines

    def _generate_method_callcontext_lines(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
        type_names: InterfaceMethodTypeNames,
        *,
        is_direct_struct_return: bool,
    ) -> tuple[list[str], list[str]]:
        """Generate Params and CallContext protocols for a server method."""
        direct_params_type = self._get_direct_struct_param_context_type(method_info)
        params_type_for_context = direct_params_type or type_names.params_type_name
        params_lines = (
            [] if direct_params_type else self._generate_params_protocol(parameters, type_names.params_type_name)
        )
        if is_direct_struct_return:
            if method_info.result_schema is None:
                msg = "Result schema is None for direct struct return"
                raise ValueError(msg)

            struct_type = self.get_type_by_id(method_info.result_schema.node.id)
            return (
                params_lines,
                self._generate_callcontext_protocol(
                    params_type_for_context,
                    type_names.call_context_type_name,
                    has_results=True,
                    result_type_for_context=self._get_flat_builder_alias(struct_type.scoped_name)
                    or self._build_scoped_builder_type(struct_type.scoped_name),
                ),
            )

        has_results = bool(method_info.result_fields)
        return (
            params_lines,
            self._generate_callcontext_protocol(
                params_type_for_context,
                type_names.call_context_type_name,
                has_results=has_results,
                result_type_for_context=type_names.server_result_type_name if has_results else None,
            ),
        )

    def _add_interface_server_method_artifacts(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
        type_names: InterfaceMethodTypeNames,
        server_collection: ServerMethodsCollection,
    ) -> None:
        """Add server signatures and NamedTuple metadata for a method."""
        if self._supports_regular_server_method_signature(method_info):
            server_collection.add_server_method(
                self._generate_server_method_signature(
                    method_info,
                    parameters,
                    type_names.call_context_type_name,
                    type_names.result_tuple_type_name,
                ),
            )
        server_collection.add_server_method(
            self._generate_server_context_method_signature(method_info, type_names.call_context_type_name)
        )
        if method_info.result_fields:
            result_fields = self._collect_result_fields_for_namedtuple(method_info)
            server_collection.add_namedtuple(type_names.result_tuple_type_name, result_fields)

    def _process_interface_method(
        self,
        context: InterfaceGenerationContext,
        method_info: MethodInfo,
        server_collection: ServerMethodsCollection,
    ) -> MethodSignatureCollection:
        """Process a single interface method and generate all its components.

        This is the main processing method that coordinates all the sub-tasks.

        Args:
            context: Interface-level metadata for the interface being generated
            method_info: Information about the method
            server_collection: Collection to add server method to

        Returns:
            MethodSignatureCollection with all generated components

        """
        collection = MethodSignatureCollection(method_info.method_name)
        parameters = self._collect_method_parameters(method_info)
        type_names = self._build_interface_method_type_names(context, method_info)
        result_type, is_direct_struct_return = self._process_method_results(method_info)
        client_result_type = type_names.client_result_type_name if result_type != "None" else "None"
        client_lines = self._generate_client_method(method_info, parameters, client_result_type)
        collection.set_client_method(client_lines)
        request_lines = self._generate_request_protocol(
            method_info,
            parameters,
            type_names.request_type_name,
            client_result_type,
        )
        collection.set_request_class(request_lines)
        self._emit_top_level_helper_class(type_names.request_type_name, request_lines)

        client_result_lines, server_result_lines = self._generate_method_result_protocols(
            method_info,
            type_names,
            is_direct_struct_return=is_direct_struct_return,
        )
        collection.set_client_result_class(client_result_lines)
        collection.set_server_result_class(server_result_lines)
        self._emit_top_level_helper_class(type_names.client_result_type_name, client_result_lines)
        if server_result_lines:
            self._emit_top_level_helper_class(type_names.server_result_type_name, server_result_lines)

        params_lines, call_context_lines = self._generate_method_callcontext_lines(
            method_info,
            parameters,
            type_names,
            is_direct_struct_return=is_direct_struct_return,
        )
        collection.server_context_lines.extend(params_lines + call_context_lines)
        self._emit_top_level_helper_class(type_names.params_type_name, params_lines)
        self._emit_top_level_helper_class(type_names.call_context_type_name, call_context_lines)
        collection.set_request_helper(
            self._generate_request_helper_method(method_info, parameters, type_names.request_type_name)
        )
        self._add_interface_server_method_artifacts(method_info, parameters, type_names, server_collection)
        if method_info.result_fields:
            self._emit_top_level_namedtuple_class(
                type_names.result_tuple_type_name,
                self._collect_result_fields_for_namedtuple(method_info),
            )

        return collection

    def _generate_server_class(
        self,
        context: InterfaceGenerationContext,
        server_collection: ServerMethodsCollection,
    ) -> None:
        """Generate the Server class with all server methods.

        Args:
            context: The interface generation context
            server_collection: Collection of server methods and NamedTuples
            server_result_lines: List of server Result protocol lines to add

        """
        server_base_classes = self._collect_server_base_classes(context.schema)
        if not server_collection.has_methods() and not server_base_classes:
            return

        self.scope.add(self._build_server_class_declaration(server_base_classes))
        self._add_server_method_signatures(server_collection)

    def _build_server_class_declaration(self, server_base_classes: list[str]) -> str:
        """Build the class declaration for a generated Server class."""
        return helper.new_class_declaration("Server", server_base_classes or ["_DynamicCapabilityServer"])

    def _add_server_method_signatures(self, server_collection: ServerMethodsCollection) -> None:
        """Add server method signatures or a placeholder for inherited-only Servers."""
        if server_collection.has_methods():
            for server_method in server_collection.server_methods:
                self.scope.add(server_method)
            return

        self.scope.add("    ...")

    def _open_interface_protocol_scope(self, context: InterfaceGenerationContext) -> None:
        """Create the protocol scope used for interface generation."""
        base_classes = context.base_classes or ["_InterfaceModule"]
        protocol_declaration = helper.new_class_declaration(context.protocol_class_name, base_classes)
        if context.parent_scope and context.parent_scope.is_root:
            self._root_module_class_names.add(context.protocol_class_name)
        _ = self.new_scope(
            context.protocol_class_name,
            context.schema.node,
            scope_heading=protocol_declaration,
        )

    def _collect_interface_method_components(
        self,
        context: InterfaceGenerationContext,
        methods: list[MethodInfo],
        server_collection: ServerMethodsCollection,
    ) -> tuple[list[str], list[str]]:
        """Generate and collect per-method interface artifacts."""
        client_method_collection: list[str] = []
        request_helper_collection: list[str] = []

        for method_info in methods:
            method_collection = self._process_interface_method(context, method_info, server_collection)
            client_method_collection.extend(method_collection.client_method_lines)
            request_helper_collection.extend(method_collection.request_helper_lines)
        return (client_method_collection, request_helper_collection)

    def _maybe_add_interface_new_client(
        self,
        context: InterfaceGenerationContext,
        server_collection: ServerMethodsCollection,
        server_base_classes: list[str],
    ) -> None:
        """Add the module-level _new_client helper when the interface exposes a Server."""
        if server_collection.has_methods() or server_base_classes:
            self._add_new_client_method(context.type_name, client_return_type=context.client_type_name)

    def _extract_interface_base_client_names(self, server_base_classes: list[str]) -> list[str]:
        """Convert inherited Server bases to their corresponding flat Client aliases."""
        base_client_names: list[str] = []
        for server_base in server_base_classes:
            if ".Server" not in server_base:
                continue
            protocol_name = server_base.replace(".Server", "")
            base_client_names.append(
                self._get_flat_client_alias(protocol_name)
                or f"{self._extract_name_from_protocol(protocol_name.split('.')[-1])}Client"
            )
        return base_client_names

    def _track_interface_client_cast_targets(
        self,
        context: InterfaceGenerationContext,
        server_base_classes: list[str],
    ) -> None:
        """Track interface/client aliases for generated cast_as overloads."""
        protocol_path = context.registered_type.scoped_name
        self._all_interfaces[protocol_path] = (
            context.client_type_name,
            self._extract_interface_base_client_names(server_base_classes),
        )

    def _track_interface_namedtuple_exports(
        self,
        context: InterfaceGenerationContext,
        server_collection: ServerMethodsCollection,
    ) -> None:
        """Track server NamedTuples for .py runtime module generation."""
        if not server_collection.namedtuples:
            return

        interface_full_name = context.registered_type.scoped_name
        namedtuple_map = self._all_server_namedtuples.setdefault(interface_full_name, {})
        for namedtuple_name, fields in server_collection.namedtuples.items():
            namedtuple_map[namedtuple_name] = (namedtuple_name, fields)

    @staticmethod
    def _is_nested_interface_context(context: InterfaceGenerationContext) -> bool:
        """Return whether an interface is nested inside another scope."""
        return bool(context.registered_type.scope and not context.registered_type.scope.is_root)

    def _build_result_alias_path(
        self,
        context: InterfaceGenerationContext,
        result_type_name: str,
    ) -> str:
        """Build the fully qualified Result alias path for an interface method."""
        return f"{context.client_type_name}.{result_type_name}"

    def _add_interface_type_aliases(
        self,
        context: InterfaceGenerationContext,
        type_alias_scope: Scope,
        *,
        should_generate_client: bool,
        should_generate_server: bool,
    ) -> None:
        """Register type aliases and annotations for generated interface helpers."""
        type_alias_scope.add(f"{context.type_name}: {context.protocol_class_name}")

        if should_generate_client:
            self._all_type_aliases[context.client_type_name] = (context.registered_type.scoped_name, "ClientClass")

        if should_generate_server:
            server_alias_name = f"{context.type_name}Server"
            server_alias_path = f"{context.registered_type.scoped_name}.Server"
            runtime_definition_name = context.schema.node.displayName.split(":", maxsplit=1)[1]
            self._runtime_server_aliases[server_alias_name] = f"{runtime_definition_name}.Server"
            if self._is_nested_interface_context(context):
                type_alias_scope.add(f"type {server_alias_name} = {server_alias_path}")
            self._all_type_aliases[server_alias_name] = (server_alias_path, "Server")

    def gen_interface(self, schema: _InterfaceSchema) -> CapnpType | None:
        """Generate an `interface` definition using Protocol pattern.

        At runtime, interfaces are _InterfaceModule objects with integer attributes.
        We generate a Protocol class _<Name>Module with nested components,
        then create TypeAliases <Name> and <Name>Client pointing to it.

        Each interface generates:
        - _<Name>Module Protocol with nested types
        - Nested Client Protocol class with client methods
        - Request/Result Protocol classes for each method
        - Server Protocol class with server method signatures
        - TypeAliases at parent scope for user-facing names

        Args:
            schema: The interface schema to generate

        Returns:
            The registered CapnpType or None if already imported

        """
        assert schema.node.which() == capnp_types.CapnpElementType.INTERFACE

        context = self._setup_interface_generation(schema)
        if context is None:
            return self.type_map.get(schema.node.id) or self.register_import(schema)

        type_alias_scope = context.parent_scope or self.scope
        self._open_interface_protocol_scope(context)
        self._generate_nested_types_for_interface(context.schema)
        self._add_module_schema_helpers(context.schema)

        methods = self._enumerate_interface_methods(context)
        server_collection = ServerMethodsCollection()
        client_method_collection, request_helper_collection = self._collect_interface_method_components(
            context,
            methods,
            server_collection,
        )
        server_base_classes = self._collect_server_base_classes(context.schema)
        self._maybe_add_interface_new_client(context, server_collection, server_base_classes)
        self._generate_server_class(context, server_collection)

        should_generate_client = bool(
            server_collection.has_methods() or server_base_classes or client_method_collection or methods
        )
        if should_generate_client:
            self._generate_flat_client_class(
                context,
                client_method_collection,
                request_helper_collection,
                server_base_classes,
            )
            self._track_interface_client_cast_targets(context, server_base_classes)

        self._track_interface_namedtuple_exports(context, server_collection)
        if not self.scope.lines:
            self.scope.add("...")

        should_generate_server = bool(server_collection.has_methods() or server_base_classes)
        self._add_interface_type_aliases(
            context,
            type_alias_scope,
            should_generate_client=should_generate_client,
            should_generate_server=should_generate_server,
        )
        self.return_from_scope()
        return context.registered_type

    def _collect_server_base_classes(self, schema: _InterfaceSchema) -> list[str]:
        """Collect Server base classes for an interface's Server class.

        Args:
            schema: The interface schema

        Returns:
            List of Server base class names (e.g., ["_IdentifiableModule.Server"])

        """
        server_base_classes: list[str] = []
        if schema.node.which() == "interface":
            interface_node = schema.node.interface
            for superclass in interface_node.superclasses:
                superclass_type = self._maybe_get_type_by_id(superclass.id)
                if superclass_type is None:
                    logger.debug("Could not resolve superclass %s for Server inheritance", superclass.id)
                    continue
                protocol_name = superclass_type.name
                if superclass_type.scope and not superclass_type.scope.is_root:
                    server_base = f"{superclass_type.scope.scoped_name}.{protocol_name}.Server"
                else:
                    server_base = f"{protocol_name}.Server"
                server_base_classes.append(server_base)
        return server_base_classes

    def _generate_flat_client_class(
        self,
        context: InterfaceGenerationContext,
        client_method_lines: list[str],
        request_helper_lines: list[str],
        server_base_classes: list[str],
    ) -> None:
        """Generate the Client typing class at module top level.

        Args:
            context: The interface generation context
            client_method_lines: List of client method lines to add
            request_helper_lines: List of request helper method lines to add
            server_base_classes: List of server base classes for inheritance resolution

        """
        if context.client_type_name in self._generated_client_classes:
            return
        self._generated_client_classes.add(context.client_type_name)

        # Build client base classes - inherit from superclass Clients
        client_base_classes: list[str] = []
        has_parent_clients = False
        for server_base in server_base_classes:
            # Extract protocol name from Server type and build Client type
            # e.g., "_IdentifiableInterfaceModule.Server" -> "IdentifiableClient"
            if ".Server" in server_base:
                protocol_name = server_base.replace(".Server", "")
                client_base_classes.append(
                    self._get_flat_client_alias(protocol_name)
                    or f"{self._extract_name_from_protocol(protocol_name.split('.')[-1])}Client"
                )
                has_parent_clients = True

        # Always inherit from _DynamicCapabilityClient as the base
        if not has_parent_clients:
            client_base_classes.insert(0, "_DynamicCapabilityClient")

        root_scope = self.scope.root
        root_scope.add(helper.new_class_declaration(context.client_type_name, client_base_classes))
        _ = self.new_scope(context.client_type_name, context.schema.node, register=False, parent_scope=root_scope)

        # Add client methods and request helpers with proper indentation
        all_method_lines = client_method_lines + request_helper_lines
        if all_method_lines:
            for line in all_method_lines:
                self.scope.add(line)
        else:
            self.scope.add("...")

        self.return_from_scope()

    def _generate_known_nested_schema(self, schema: capnp_types.SchemaType) -> bool:
        """Generate a schema instance when it already has a concrete runtime schema type."""
        if isinstance(schema, _EnumSchema):
            if not self.is_type_id_known(schema.node.id):
                _ = self.gen_enum(schema)
            return True
        if isinstance(schema, _InterfaceSchema):
            if not self.is_type_id_known(schema.node.id):
                _ = self.gen_interface(schema)
            return True
        if isinstance(schema, _StructSchema):
            if not self.is_type_id_known(schema.node.id):
                _ = self.gen_struct(schema)
            return True
        return False

    def _generate_const_nested_schema(self, schema: capnp_types.SchemaType) -> None:
        """Generate a nested const schema from a generic runtime schema."""
        if not isinstance(schema, _Schema):
            msg = f"Expected _Schema for const node, got {type(schema).__name__}"
            raise TypeError(msg)
        self.gen_const(schema)

    def _generate_struct_nested_schema(self, schema: capnp_types.SchemaType) -> None:
        """Generate a nested struct schema from either a concrete or generic schema."""
        if isinstance(schema, _StructSchema):
            _ = self.gen_struct(schema)
            return
        if isinstance(schema, _Schema):
            _ = self.gen_struct(schema.as_struct())
            return
        msg = f"Expected struct schema for struct node, got {type(schema).__name__}"
        raise TypeError(msg)

    def _generate_enum_nested_schema(self, schema: capnp_types.SchemaType) -> None:
        """Generate a nested enum schema from either a concrete or generic schema."""
        if isinstance(schema, _EnumSchema):
            _ = self.gen_enum(schema)
            return
        if isinstance(schema, _Schema):
            _ = self.gen_enum(schema.as_enum())
            return
        msg = f"Expected enum schema for enum node, got {type(schema).__name__}"
        raise TypeError(msg)

    def _generate_interface_nested_schema(self, schema: capnp_types.SchemaType) -> None:
        """Generate a nested interface schema from either a concrete or generic schema."""
        if isinstance(schema, _InterfaceSchema):
            _ = self.gen_interface(schema)
            return
        if isinstance(schema, _Schema):
            _ = self.gen_interface(schema.as_interface())
            return
        msg = f"Expected interface schema for interface node, got {type(schema).__name__}"
        raise TypeError(msg)

    def _generate_nested_by_node_kind(self, schema: capnp_types.SchemaType) -> None:
        """Generate a schema based on its node kind."""
        node_kind = schema.node.which()
        if node_kind == "file":
            logger.debug("Skipping file node: %s", schema.node.displayName)
            return

        if self.is_type_id_known(schema.node.id):
            return

        generators = {
            "const": self._generate_const_nested_schema,
            "struct": self._generate_struct_nested_schema,
            "enum": self._generate_enum_nested_schema,
            "interface": self._generate_interface_nested_schema,
        }
        generator = generators.get(node_kind)
        if generator is None:
            logger.warning("Skipping unknown node type '%s': %s", node_kind, schema.node.displayName)
            return
        generator(schema)

    def generate_nested(self, schema: capnp_types.SchemaType) -> None:
        """Generate the type for a nested schema.

        Args:
            schema (SchemaType): The schema to generate types for.
                Can be _StructSchema, _EnumSchema, _InterfaceSchema,
                _Schema, or a SchemaProxy wrapper.

        Raises:
            AssertionError: If the schema belongs to an unknown type.

        """
        if self._generate_known_nested_schema(schema):
            return
        self._generate_nested_by_node_kind(schema)

    def generate_all_nested(self) -> None:
        """Generate types for all nested nodes, recursively."""
        for node in self._schema.node.nestedNodes:
            try:
                nested_schema = self._schemas_by_id.get(node.id)
                if nested_schema:
                    self.generate_nested(nested_schema)
                else:
                    logger.debug("Could not find nested schema %s (id=%s) in schema mapping", node.name, hex(node.id))
            except TYPE_GENERATION_EXCEPTIONS as error:
                # capnpc may omit unused nodes from imported schemas in the CodeGeneratorRequest.
                # This results in "no schema node loaded" errors when trying to access them.
                # These are harmless if the nodes are indeed unused, so we log as debug.
                logger.debug("Could not generate nested node '%s': %s", node.name, error)

    def _schema_contains_nested_id(self, schema_obj: _Schema, target_id: int) -> bool:
        """Return whether a file schema contains the target nested schema ID."""
        for nested_node in schema_obj.node.nestedNodes:
            if nested_node.id == target_id:
                return True
            with contextlib.suppress(*SCHEMA_LOOKUP_EXCEPTIONS):
                nested_schema = self._schema_loader.get(nested_node.id)
                if self._schema_contains_nested_id(nested_schema, target_id):
                    return True
        return False

    def _find_import_matching_path(self, schema: capnp_types.SchemaType) -> pathlib.Path | None:
        """Find the source file path that owns an imported schema."""
        if schema.node.id in self._file_id_to_path:
            return pathlib.Path(self._file_id_to_path[schema.node.id])

        for file_id, path in self._file_id_to_path.items():
            with contextlib.suppress(*SCHEMA_LOOKUP_EXCEPTIONS):
                file_schema = self._schema_loader.get(file_id)
                if self._schema_contains_nested_id(file_schema, schema.node.id):
                    return pathlib.Path(path)
        return None

    def _find_file_id_for_path(self, matching_path: pathlib.Path) -> int | None:
        """Find the root file schema ID for a source path."""
        for file_id, file_path in self._file_id_to_path.items():
            if pathlib.Path(file_path) == matching_path:
                return file_id
        return None

    def _build_python_import_path(self, matching_path: pathlib.Path) -> str:
        """Build the Python import path for an imported schema file."""
        imported_module_annotation = None
        imported_file_schema_id = self._find_file_id_for_path(matching_path)
        if imported_file_schema_id is not None:
            generated_module_name = self._generated_module_names_by_schema_id.get(imported_file_schema_id)
            if generated_module_name is not None:
                return generated_module_name
            imported_module_annotation = self.get_python_module_for_schema(imported_file_schema_id)

        if self._python_module_path and imported_module_annotation:
            return f"{imported_module_annotation}.{matching_path.stem}_capnp"

        self_dir = self._module_path.parent
        if self_dir == matching_path.parent:
            return f"{matching_path.stem}_capnp"

        common_path = os.path.commonpath([self._module_path, matching_path])
        relative_module_path = self._module_path.relative_to(common_path)
        relative_import_path = matching_path.relative_to(common_path)
        dots_count = len(relative_module_path.parents) + 1
        return "." * dots_count + helper.replace_capnp_suffix(".".join(relative_import_path.parts))

    def _register_nested_import_definition(
        self,
        schema: capnp_types.SchemaType,
        definition_name: str,
        python_import_path: str,
    ) -> str:
        """Register imports for a nested definition and return its internal type name."""
        root_name = definition_name.split(".", maxsplit=1)[0]
        if schema.node.which() == capnp_types.CapnpElementType.STRUCT:
            self._add_import(f"from {python_import_path}.types.modules import _{root_name}StructModule")
            return ".".join(f"_{part}StructModule" for part in definition_name.split("."))

        if schema.node.which() == capnp_types.CapnpElementType.INTERFACE:
            client_name = f"{definition_name.rsplit('.', maxsplit=1)[-1]}Client"
            self._add_import(f"from {python_import_path} import {root_name}")
            self._add_import(f"from {python_import_path}.types.clients import {client_name}")
            self._add_import(f"from {python_import_path}.types.modules import _{root_name}InterfaceModule")
            self._imported_aliases.add(client_name)
            parts = definition_name.split(".")
            parts[-1] = f"_{parts[-1]}InterfaceModule"
            return ".".join(parts)

        self._add_import(f"from {python_import_path} import {root_name}")
        return definition_name

    def _register_top_level_import_definition(
        self,
        schema: capnp_types.SchemaType,
        definition_name: str,
        python_import_path: str,
    ) -> str:
        """Register imports for a top-level definition and return its internal type name."""
        if schema.node.which() == capnp_types.CapnpElementType.INTERFACE:
            protocol_name = f"_{definition_name}InterfaceModule"
            client_name = f"{definition_name}Client"
            self._add_import(f"from {python_import_path} import {definition_name}")
            self._add_import(f"from {python_import_path}.types.clients import {client_name}")
            self._add_import(f"from {python_import_path}.types.modules import {protocol_name}")
            self._imported_aliases.add(client_name)
            return protocol_name

        if schema.node.which() == capnp_types.CapnpElementType.ENUM:
            alias_name = f"{definition_name}Enum"
            self._add_import(f"from {python_import_path}.types.enums import {alias_name}")
            return alias_name

        protocol_name = f"_{definition_name}StructModule"
        reader_alias = f"{definition_name}Reader"
        builder_alias = f"{definition_name}Builder"
        self._add_import(f"from {python_import_path}.types.modules import {protocol_name}")
        self._add_import(f"from {python_import_path}.types.readers import {reader_alias}")
        self._add_import(f"from {python_import_path}.types.builders import {builder_alias}")
        self._imported_aliases.add(reader_alias)
        self._imported_aliases.add(builder_alias)
        return protocol_name

    def register_import(self, schema: capnp_types.SchemaType) -> CapnpType | None:
        """Determine, whether a schema is imported from the base module.

        If so, the type definition that the schema contains, is added to the type registry.

        Args:
            schema (SchemaType): The schema to check.

        Returns:
            Type | None: The type of the import, if the schema is imported,
                or None if the schema defines the base module itself.

        """
        module_name, definition_name = schema.node.displayName.split(":")

        if module_name == self.full_display_name:
            # This is the base module, not an import.
            return None

        matching_path = self._find_import_matching_path(schema)
        assert matching_path is not None, f"The module named {module_name} was not provided to the stub generator."

        self._imported_module_paths.add(matching_path)
        python_import_path = self._build_python_import_path(matching_path)
        registered_name = (
            self._register_nested_import_definition(schema, definition_name, python_import_path)
            if "." in definition_name
            else self._register_top_level_import_definition(schema, definition_name, python_import_path)
        )
        return self.register_type(schema.node.id, schema, name=registered_name, scope=self.scope.root)

    def register_type(
        self,
        type_id: int,
        schema: capnp_types.SchemaType,
        name: str = "",
        scope: Scope | None = None,
    ) -> CapnpType:
        """Register a new type in the writer's registry of types.

        Args:
            type_id (int): The identification number of the type.
            schema (SchemaType): The schema that defines the type.
            name (str, optional): An name to specify, if overriding the type name. Defaults to "".
            scope (Scope | None, optional): The scope in which the type is defined. Defaults to None.

        Returns:
            Type: The registered type.

        """
        if not name:
            name = helper.get_display_name(schema)

        if scope is None:
            scope = self.scope.parent

        if scope is None:
            msg = f"No valid scope was found for registering the type '{name}'."
            raise ValueError(msg)

        self.type_map[type_id] = retval = CapnpType(schema=schema, name=name, scope=scope)

        return retval

    def is_type_id_known(self, type_id: int) -> bool:
        """Check, whether a type ID was previously registered.

        Args:
            type_id (int): The type ID to check.

        Returns:
            bool: True, if the type ID is known, False otherwise.

        """
        return type_id in self.type_map

    def _is_schema_in_current_module(self, schema: capnp_types.SchemaType) -> bool:
        """Check if a schema belongs to the current module.

        Args:
            schema: The schema to check.

        Returns:
            True if the schema is in the current module, False otherwise.

        """
        # Check if it's the root schema
        if schema.node.id == self._schema.node.id:
            return True

        # Check if it's a direct nested node
        for nested in self._schema.node.nestedNodes:
            if nested.id == schema.node.id:
                return True

        # Recursively check nested nodes
        def check_nested(parent_schema: capnp_types.SchemaType, target_id: int) -> bool:
            for nested_node in parent_schema.node.nestedNodes:
                if nested_node.id == target_id:
                    return True
                # Check deeper
                nested_schema = self._schemas_by_id.get(nested_node.id)
                if nested_schema and check_nested(nested_schema, target_id):
                    return True
            return False

        return check_nested(self._schema, schema.node.id)

    def _maybe_get_type_by_id(self, type_id: int) -> CapnpType | None:
        """Resolve and return a type by ID, or ``None`` when it cannot be registered."""
        if self.is_type_id_known(type_id):
            return self.type_map[type_id]

        found_schema = self._schemas_by_id.get(type_id)
        if found_schema is None:
            try:
                found_schema = self._schema_loader.get(type_id)
            except SCHEMA_LOOKUP_EXCEPTIONS:
                return None
            self._schemas_by_id[type_id] = found_schema

        if self._is_schema_in_current_module(found_schema):
            self.generate_nested(found_schema)
        else:
            _ = self.register_import(found_schema)

        return self.type_map.get(type_id)

    def get_type_by_id(self, type_id: int) -> CapnpType:
        """Look up a type in the type registry, by means of its ID.

        Args:
            type_id (int): The identification number of the type.

        Raises:
            KeyError: If the type ID was not found in the registry.

        Returns:
            Type: The type, if it exists.

        """
        resolved_type = self._maybe_get_type_by_id(type_id)
        if resolved_type is not None:
            return resolved_type

        msg = f"The type ID '{type_id} was not found in the type registry.'"
        raise KeyError(msg)

    def new_scope(
        self,
        name: str,
        node: NodeReader,
        scope_heading: str = "",
        *,
        register: bool = True,
        parent_scope: Scope | None = None,
    ) -> Scope:
        """Create a new scope below the scope of the provided node.

        Args:
            name (str): The name of the new scope.
            node (Any): The node whose scope is the parent scope of the new scope.
            scope_heading (str): The line of code that starts this new scope.
            register (bool): Whether to register this scope.
            parent_scope (Scope | None): Optional explicit parent scope. If provided, uses this instead of looking up by node.scopeId.

        Returns:
            Scope: The parent of this scope.

        """
        if parent_scope is None:
            parent_scope = self.scopes_by_id.get(node.scopeId)
            if parent_scope is None:
                msg = f"The scope with name '{name}' has no parent."
                raise NoParentError(msg)

        # Add the heading of the scope to the parent scope.
        if scope_heading:
            parent_scope.add(scope_heading)

        # Then, make a new scope that is one indent level deeper.
        child_scope = Scope(name=name, id=node.id, parent=parent_scope, return_scope=self.scope)

        self.scope = child_scope

        if register:
            self.scopes_by_id[node.id] = child_scope

        return parent_scope

    def return_from_scope(self) -> None:
        """Return from the current scope."""
        assert self.scope is not None, "The current scope is not valid."
        assert not self.scope.is_root, "The current scope is the root scope and cannot be returned from."
        assert self.scope.parent is not None, "The current scope has no parent."
        assert self.scope.return_scope is not None, "The current scope does not define a scope to return to."

        # Find where the scope heading is in the parent's lines
        # The scope heading was added when new_scope() was called (for interfaces)
        # or manually added (for structs/enums)
        # We need to insert the child scope lines RIGHT AFTER the heading
        # Use word boundary to avoid matching "class TestSturdyRef" when looking for "class TestSturdyRefHostId"
        # Search from the END to find the most recently added class with this name
        scope_heading_pattern = f"class {self.scope.name}"
        logger.debug(
            "  Looking for pattern: '%s' in %s parent lines", scope_heading_pattern, len(self.scope.parent.lines)
        )
        heading_index = None
        for i in range(len(self.scope.parent.lines) - 1, -1, -1):
            line = self.scope.parent.lines[i]
            if scope_heading_pattern in line:
                # Ensure it's an exact match by checking what follows the class name
                # Should be either ':', '(' or whitespace
                pattern_end_pos = line.find(scope_heading_pattern) + len(scope_heading_pattern)
                if pattern_end_pos < len(line):
                    next_char = line[pattern_end_pos]
                    if next_char in (":", "(", " "):
                        heading_index = i
                        break
                else:
                    # Pattern is at the end of the line (shouldn't happen for class declarations)
                    heading_index = i
                    break

        if heading_index is not None:
            # Found the class heading in parent scope
            if self.scope.lines:
                # Insert child scope lines right after the heading
                self.scope.parent.lines = (
                    self.scope.parent.lines[: heading_index + 1]
                    + self.scope.lines
                    + self.scope.parent.lines[heading_index + 1 :]
                )

            else:
                # Empty class body - add a pass statement to avoid syntax error
                self.scope.parent.lines.insert(heading_index + 1, "    pass")
        else:
            # No class heading found - fallback: append to the end (old behavior)
            self.scope.parent.lines += self.scope.lines

        self.scope = self.scope.return_scope

    def _ensure_registered_type_generated(self, type_id: int, type_kind: str) -> None:
        """Generate a referenced struct or interface before resolving its registered type."""
        if self.is_type_id_known(type_id):
            return

        try:
            nested_schema = self._schemas_by_id.get(type_id)
            if nested_schema is not None:
                self.generate_nested(nested_schema)
        except TYPE_GENERATION_EXCEPTIONS as error:
            logger.debug("Could not pre-generate %s with ID %s: %s", type_kind, type_id, error)

    @staticmethod
    def _qualified_type_name(element_type: CapnpType) -> str:
        """Return the fully scoped type name for a registered schema type."""
        if element_type.scope.is_root:
            return element_type.name
        return f"{element_type.scope}.{element_type.name}"

    def _get_registered_type_name(self, type_reader: TypeReader, type_kind: str) -> str:
        """Return the registered type name for a struct, enum, or interface reader."""
        type_id = getattr(type_reader, type_kind).typeId
        if type_kind in {capnp_types.CapnpElementType.STRUCT, capnp_types.CapnpElementType.INTERFACE}:
            self._ensure_registered_type_generated(type_id, type_kind)
        return self._qualified_type_name(self.get_type_by_id(type_id))

    def get_type_name(self, type_reader: TypeReader) -> str:
        """Extract the type name from a type reader.

        The output type name is prepended by the scope name, if there is a parent scope.

        Args:
            type_reader (_DynamicStructReader ): The type reader to get the type name from.

        Returns:
            str: The extracted type name.

        """
        type_reader_type = type_reader.which()
        primitive_type = capnp_types.CAPNP_TYPE_TO_PYTHON.get(type_reader_type)
        if primitive_type is not None:
            return primitive_type
        if type_reader_type in {
            capnp_types.CapnpElementType.STRUCT,
            capnp_types.CapnpElementType.ENUM,
            capnp_types.CapnpElementType.INTERFACE,
        }:
            return self._get_registered_type_name(type_reader, type_reader_type)

        if type_reader_type == capnp_types.CapnpElementType.LIST:
            self._add_typing_import("Sequence")
            return f"Sequence[{self.get_type_name(type_reader.list.elementType)}]"

        if type_reader_type == capnp_types.CapnpElementType.ANY_POINTER:
            self._needs_dynamic_object_reader_augmentation = True
            return "_DynamicObjectReader"

        msg = f"Unknown type reader type '{type_reader_type}'."
        raise TypeError(msg)

    @staticmethod
    def _classify_dynamic_object_alias(
        alias_name: str,
        alias_data: GeneratedTypeAliasInfo,
    ) -> tuple[str, str] | None:
        """Classify an alias as a struct, list, or interface dynamic reader overload."""
        if len(alias_data) < MIN_ALIAS_DATA_PARTS:
            return None

        original_path, type_kind = alias_data[:2]
        if alias_name.endswith("Reader") and ".Reader" in original_path:
            reader_parent_path = original_path.removesuffix(".Reader")
            reader_parent_name = reader_parent_path.rsplit(".", maxsplit=1)[-1]
            if alias_name.endswith("ListReader") and reader_parent_name.endswith("List"):
                return "lists", reader_parent_path

            if "StructModule" in reader_parent_path:
                return "structs", reader_parent_path

        if alias_name.endswith("Client") and type_kind == "ClientClass":
            return "interfaces", original_path

        if alias_name.endswith("Client") and "Client" in original_path:
            parts = original_path.rsplit(".", maxsplit=1)
            if len(parts) == MODULE_PATH_PARTS and "InterfaceModule" in parts[0]:
                return "interfaces", parts[0]

        return None

    def get_dynamic_object_reader_types(
        self,
    ) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
        """Get struct, list, and interface types for _DynamicObjectReader augmentation.

        Returns type aliases that are ACTUALLY GENERATED in this module for overloads.

        Returns:
            Tuple of (struct_types, list_types, interface_types) where each is a list of (protocol_name, type_alias) tuples.
            struct_types: list of (Protocol class, TypeAlias) for structs
            list_types: list of (List class, TypeAlias) for lists
            interface_types: list of (Protocol class, TypeAlias) for interfaces

        """
        if not self._needs_dynamic_object_reader_augmentation:
            return ([], [], [])

        collected_types: dict[str, list[tuple[str, str]]] = {"structs": [], "lists": [], "interfaces": []}
        seen_types: dict[str, set[str]] = {"structs": set(), "lists": set(), "interfaces": set()}

        for alias_name, alias_data in self._all_type_aliases.items():
            dynamic_type = self._classify_dynamic_object_alias(alias_name, alias_data)
            if dynamic_type is None:
                continue

            type_kind, type_path = dynamic_type
            if type_path in seen_types[type_kind]:
                continue

            collected_types[type_kind].append((type_path, alias_name))
            seen_types[type_kind].add(type_path)

        logger.debug(
            "Module %s: Found %s structs, %s lists, %s interfaces",
            self._schema.node.displayName,
            len(collected_types["structs"]),
            len(collected_types["lists"]),
            len(collected_types["interfaces"]),
        )

        return (collected_types["structs"], collected_types["lists"], collected_types["interfaces"])

    def _ensure_root_scope(self, *, context: str) -> None:
        """Force the writer back to the root scope before emitting file output."""
        if self.scope.is_root:
            return

        logger.warning("Scope not at root when %s! name='%s', forcing return to root", context, self.scope.name)
        while self.scope.return_scope is not None:
            self.scope = self.scope.return_scope

    def _append_pointer_type_aliases(self, out: list[str]) -> None:
        """Append optional AnyPointer-related type aliases needed by this module."""
        alias_blocks = [
            (
                self._needs_anypointer_alias,
                "# Type alias for AnyPointer parameters (accepts all Cap'n Proto pointer types)",
                f"type AnyPointer = {ANYPOINTER_TYPE}",
            ),
            (
                self._needs_capability_alias,
                "# Type alias for Capability parameters",
                f"type Capability = {CAPABILITY_TYPE}",
            ),
            (
                self._needs_anystruct_alias,
                "# Type alias for AnyStruct parameters",
                f"type AnyStruct = {ANYSTRUCT_TYPE}",
            ),
            (
                self._needs_anylist_alias,
                "# Type alias for AnyList parameters",
                f"type AnyList = {ANYLIST_TYPE}",
            ),
        ]

        for should_add, comment, alias_line in alias_blocks:
            if not should_add:
                continue
            out.extend(["", comment, alias_line])

    def _format_top_level_type_alias(self, alias_name: str, alias_info: GeneratedTypeAliasInfo) -> str | None:
        """Format one generated top-level type alias line."""
        if len(alias_info) == ENUM_ALIAS_DATA_PARTS:
            full_path, type_kind, enum_values = alias_info
            if type_kind == "Enum":
                literal_values = ", ".join(f'"{value}"' for value in enum_values)
                return f"type {alias_name} = int | Literal[{literal_values}]"
            return f"type {alias_name} = {full_path}"

        full_path, type_kind = alias_info
        if type_kind in {"ReaderClass", "BuilderClass", "ClientClass"}:
            return None
        if type_kind == "Server":
            return f"{alias_name} = {full_path}"

        return f"type {alias_name} = {full_path}"

    def _append_top_level_type_aliases(self, out: list[str]) -> None:
        """Append generated Reader/Builder/Client type aliases."""
        if not self._all_type_aliases:
            return

        formatted_aliases = [
            alias_line
            for alias_name in sorted(self._all_type_aliases)
            if (alias_line := self._format_top_level_type_alias(alias_name, self._all_type_aliases[alias_name]))
        ]
        if not formatted_aliases:
            return

        out.extend(["", "# Top-level type aliases for use in type annotations", *formatted_aliases])

    def _dump_all_types_pyi(self) -> str:
        """Generate the private monolithic typing stub for this schema.

        Returns:
            str: The output string.

        """
        self._ensure_root_scope(context="dumping")
        out: list[str] = []
        out.append(self.docstring)
        out.extend(self.imports)

        if self._needs_dynamic_object_reader_augmentation:
            out.append("from capnp.lib.capnp import _DynamicObjectReader")

        self._append_pointer_type_aliases(out)
        out.append("")

        if self.type_vars:
            out.extend(f'{name} = TypeVar("{name}")' for name in sorted(self.type_vars))
            out.append("")

        out.extend(self.scope.lines)
        self._append_schema_helper_export_aliases(out)
        self._append_top_level_type_aliases(out)
        return "\n".join(out)

    def _append_schema_helper_export_aliases(self, out: list[str]) -> None:
        """Append top-level aliases for schema helper classes to the private monolithic stub."""
        if not self._schema_helper_export_targets:
            return

        alias_lines = [
            f"type {alias_name} = {target_path}"
            for alias_name, target_path in sorted(self._schema_helper_export_targets.items())
        ]
        out.extend(["", "# Public schema helper aliases", *alias_lines])

    @staticmethod
    def _empty_types_module_exports() -> dict[str, set[str]]:
        """Create an empty export bucket for each public types submodule."""
        return {
            "lists": set(),
            "builders": set(),
            "readers": set(),
            "clients": set(),
            "requests": set(),
            "contexts": set(),
            "common": set(),
            "servers": set(),
            "enums": set(),
            "modules": set(),
            "schemas": set(),
            "results/client": set(),
            "results/server": set(),
            "results/tuples": set(),
        }

    @staticmethod
    def _record_alias_export(exports: dict[str, set[str]], alias_name: str, type_kind: str) -> None:
        """Add one generated alias to the correct public types submodule."""
        export_module = {
            "Builder": "builders",
            "BuilderClass": "builders",
            "Reader": "readers",
            "ReaderClass": "readers",
            "ClientClass": "clients",
            "Server": "servers",
            "Enum": "enums",
        }.get(type_kind)
        if export_module is not None:
            exports[export_module].add(alias_name)

    @staticmethod
    def _record_interface_helper_export(exports: dict[str, set[str]], helper_name: str) -> None:
        """Add one generated interface helper class to the correct public types submodule."""
        if helper_name.endswith("ResultTuple"):
            exports["results/tuples"].add(helper_name)
            return

        if helper_name.endswith("ServerResult"):
            exports["results/server"].add(helper_name)
            return

        if helper_name.endswith("Result"):
            exports["results/client"].add(helper_name)
            return

        if helper_name.endswith("Request"):
            exports["requests"].add(helper_name)
            return

        if helper_name.endswith(("Params", "CallContext")):
            exports["contexts"].add(helper_name)

    def _build_types_module_exports(self) -> dict[str, list[str]]:
        """Classify generated typing-only names into public types submodules."""
        exports = self._empty_types_module_exports()

        for alias_name, alias_info in self._all_type_aliases.items():
            self._record_alias_export(exports, alias_name, alias_info[1])

        for helper_name in self._generated_interface_helper_types:
            self._record_interface_helper_export(exports, helper_name)

        if self._needs_anypointer_alias:
            exports["common"].add("AnyPointer")
        if self._needs_capability_alias:
            exports["common"].add("Capability")
        if self._needs_anystruct_alias:
            exports["common"].add("AnyStruct")
        if self._needs_anylist_alias:
            exports["common"].add("AnyList")
        if self._generated_list_types:
            exports["lists"].update(self._generated_list_types)
        if self._root_module_class_names:
            exports["modules"].update(self._root_module_class_names)
        if self._schema_helper_export_targets:
            exports["schemas"].update(self._schema_helper_export_targets)

        return {module_name: sorted(names) for module_name, names in exports.items()}

    def _build_runtime_helper_class_names(self) -> set[str]:
        """Collect top-level helper classes that should be hidden from the runtime stub."""
        helper_class_names = (
            set(self._generated_list_types)
            | set(self._generated_interface_helper_types)
            | set(self._root_module_class_names)
        )

        for alias_name, alias_info in self._all_type_aliases.items():
            if alias_info[1] in {"ReaderClass", "BuilderClass", "ClientClass"}:
                helper_class_names.add(alias_name)

        return helper_class_names

    @staticmethod
    def _extract_top_level_class_name(line: str) -> str | None:
        """Extract the top-level class name from one root-scope line."""
        if not line.startswith("class "):
            return None

        header = line.removeprefix("class ")
        return header.split("(", maxsplit=1)[0].split(":", maxsplit=1)[0].strip()

    @staticmethod
    def _extract_alias_name(line: str) -> str | None:
        """Extract a type alias name from one generated scope line."""
        stripped = line.lstrip()
        if not stripped.startswith("type "):
            return None

        return stripped.removeprefix("type ").split("=", maxsplit=1)[0].strip()

    @staticmethod
    def _extract_public_api_name(line: str) -> str | None:
        """Extract one public top-level API name from a generated line."""
        if line.startswith((" ", "\t")):
            return None

        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "from ", "import ")):
            return None

        class_name = Writer._extract_top_level_class_name(stripped)
        if class_name is not None:
            return class_name if not class_name.startswith("_") else None

        alias_name = Writer._extract_alias_name(stripped)
        if alias_name is not None:
            return alias_name if not alias_name.startswith("_") else None

        assignment_match = re.match(r"(?P<name>[A-Za-z][A-Za-z0-9_]*)\s*[:=]", stripped)
        if assignment_match is None:
            return None

        public_name = assignment_match.group("name")
        return public_name if not public_name.startswith("_") else None

    @staticmethod
    def _collapse_blank_lines(lines: list[str]) -> list[str]:
        """Collapse repeated blank lines while preserving section spacing."""
        collapsed: list[str] = []
        previous_blank = False

        for line in lines:
            is_blank = not line.strip()
            if is_blank and previous_blank:
                continue

            collapsed.append("" if is_blank else line)
            previous_blank = is_blank

        while collapsed and not collapsed[-1].strip():
            collapsed.pop()

        return collapsed

    def _build_module_types_scope_lines(self) -> list[str]:
        """Collect the top-level struct/interface module classes for `types.modules`."""
        return self._extract_named_top_level_scope_blocks(self._root_module_class_names)

    def _extract_named_top_level_scope_blocks(self, class_names: set[str]) -> list[str]:
        """Extract top-level class blocks whose names match the provided set."""
        if not class_names:
            return []

        extracted_lines: list[str] = []
        index = 0
        scope_lines = self.scope.lines

        while index < len(scope_lines):
            line = scope_lines[index]
            class_name = self._extract_top_level_class_name(line) if not line.startswith((" ", "\t")) else None
            if class_name is None or class_name not in class_names:
                index += 1
                continue

            if extracted_lines and extracted_lines[-1].strip():
                extracted_lines.append("")

            while index < len(scope_lines):
                current_line = scope_lines[index]
                if current_line and not current_line.startswith((" ", "\t")) and current_line != line:
                    break
                extracted_lines.append(current_line)
                index += 1

        return self._collapse_blank_lines(extracted_lines)

    def _build_common_alias_lines(self, export_names: list[str]) -> list[str]:
        """Build the common pointer alias definitions for the requested names."""
        alias_definitions = {
            "AnyPointer": (
                "# Type alias for AnyPointer parameters (accepts all Cap'n Proto pointer types)",
                f"type AnyPointer = {ANYPOINTER_TYPE}",
            ),
            "Capability": (
                "# Type alias for Capability parameters",
                f"type Capability = {CAPABILITY_TYPE}",
            ),
            "AnyStruct": (
                "# Type alias for AnyStruct parameters",
                f"type AnyStruct = {ANYSTRUCT_TYPE}",
            ),
            "AnyList": (
                "# Type alias for AnyList parameters",
                f"type AnyList = {ANYLIST_TYPE}",
            ),
        }
        lines: list[str] = []
        for export_name in export_names:
            alias_definition = alias_definitions.get(export_name)
            if alias_definition is None:
                continue
            comment, alias_line = alias_definition
            if lines:
                lines.append("")
            lines.extend([comment, alias_line])
        return lines

    def _build_schema_alias_lines(self, export_names: list[str]) -> list[str]:
        """Build the public schema helper alias definitions."""
        lines: list[str] = []
        for export_name in export_names:
            target_path = self._schema_helper_export_targets.get(export_name)
            if target_path is None:
                continue
            if lines:
                lines.append("")
            lines.append(f"type {export_name} = {target_path}")
        return lines

    def _build_top_level_alias_lines(self, export_names: list[str]) -> list[str]:
        """Build top-level alias lines for exported names backed by alias metadata."""
        lines: list[str] = []
        for export_name in export_names:
            alias_info = self._all_type_aliases.get(export_name)
            if alias_info is None:
                continue
            alias_line = self._format_top_level_type_alias(export_name, alias_info)
            if alias_line is None:
                continue
            if lines:
                lines.append("")
            lines.append(alias_line)
        return lines

    def _build_types_submodule_body_lines(
        self,
        module_name: str,
        exports: dict[str, list[str]],
    ) -> list[str]:
        """Build the raw body lines for one generated public `types` submodule."""
        export_names = exports[module_name]
        export_name_set = set(export_names)

        if module_name == "common":
            return self._build_common_alias_lines(export_names)
        if module_name == "schemas":
            return self._build_schema_alias_lines(export_names)

        class_block_lines = (
            self._build_module_types_scope_lines()
            if module_name == "modules"
            else self._extract_named_top_level_scope_blocks(export_name_set)
        )
        found_class_names = {
            self._extract_top_level_class_name(line)
            for line in class_block_lines
            if self._extract_top_level_class_name(line) is not None
        }
        remaining_export_names = [export_name for export_name in export_names if export_name not in found_class_names]
        alias_lines = self._build_top_level_alias_lines(remaining_export_names)

        return self._collapse_blank_lines(
            [*class_block_lines, *([""] if class_block_lines and alias_lines else []), *alias_lines]
        )

    @staticmethod
    def _types_submodule_alias_name(module_name: str) -> str:
        """Return the local alias used when importing one helper submodule."""
        return module_name.replace("/", "_")

    def _render_local_types_submodule_import(self, current_module: str, target_module: str, alias_name: str) -> str:
        """Render one import from another helper submodule in the same generated package."""
        types_import_base = self._current_annotated_types_package_import_base()
        if types_import_base is not None:
            if target_module.startswith("results/"):
                result_module_name = target_module.rsplit("/", maxsplit=1)[-1]
                return f"from {types_import_base}.results import {result_module_name} as {alias_name}"
            return f"from {types_import_base} import {target_module} as {alias_name}"

        if target_module.startswith("results/"):
            result_module_name = target_module.rsplit("/", maxsplit=1)[-1]
            if current_module.startswith("results/"):
                return f"from . import {result_module_name} as {alias_name}"
            return f"from .results import {result_module_name} as {alias_name}"

        if current_module.startswith("results/"):
            return f"from .. import {target_module} as {alias_name}"
        return f"from . import {target_module} as {alias_name}"

    def _build_local_types_stub_references(
        self,
        current_module: str,
        exports: dict[str, list[str]],
        raw_lines: list[str],
    ) -> tuple[dict[str, str], list[str]]:
        """Build sibling-submodule references used within one public `types` stub module."""
        joined_lines = "\n".join(raw_lines)
        references: dict[str, str] = {}
        import_lines: list[str] = []

        for module_name, exported_names in exports.items():
            if module_name == current_module or not exported_names:
                continue

            used_names = [
                exported_name
                for exported_name in exported_names
                if re.search(rf"\b{re.escape(exported_name)}\b", joined_lines)
            ]
            if not used_names:
                continue

            alias_name = self._types_submodule_alias_name(module_name)
            import_lines.append(self._render_local_types_submodule_import(current_module, module_name, alias_name))
            references.update({exported_name: f"{alias_name}.{exported_name}" for exported_name in used_names})

        return references, import_lines

    def _dump_types_submodule_pyi(
        self,
        module_name: str,
        docstring: str,
        exports: dict[str, list[str]],
    ) -> str:
        """Generate one public `types` submodule stub with concrete definitions."""
        raw_lines = self._build_types_submodule_body_lines(module_name, exports)
        local_references, local_import_lines = self._build_local_types_stub_references(module_name, exports, raw_lines)
        rewritten_lines = self._rewrite_runtime_helper_references(raw_lines, local_references)

        out: list[str] = [docstring]
        out.extend(self.imports)
        if self._needs_dynamic_object_reader_augmentation:
            out.append("from capnp.lib.capnp import _DynamicObjectReader")
        if local_import_lines:
            out.extend(local_import_lines)
        if self.type_vars:
            out.extend(["", *(f'{name} = TypeVar("{name}")' for name in sorted(self.type_vars))])

        out.extend(["", *(rewritten_lines or ["pass"])])
        return "\n".join(out)

    def _build_runtime_scope_lines(self, exports: dict[str, list[str]]) -> list[str]:
        """Filter helper-only root-scope declarations out of the runtime stub."""
        helper_class_names = self._build_runtime_helper_class_names()
        helper_alias_names = {name for names in exports.values() for name in names}

        filtered_lines: list[str] = []
        index = 0
        scope_lines = self.scope.lines

        while index < len(scope_lines):
            line = scope_lines[index]

            if not line.startswith((" ", "\t")):
                class_name = self._extract_top_level_class_name(line)
                if class_name is not None and class_name in helper_class_names:
                    index += 1
                    while index < len(scope_lines):
                        next_line = scope_lines[index]
                        if next_line and not next_line.startswith((" ", "\t")):
                            break
                        index += 1
                    continue

            alias_name = self._extract_alias_name(line)
            if alias_name is not None and alias_name in helper_alias_names:
                index += 1
                continue

            filtered_lines.append(line)
            index += 1

        return self._collapse_blank_lines(filtered_lines)

    @staticmethod
    def _types_package_module_path(module_name: str) -> str:
        """Return the public local `types` module path for one helper module."""
        if module_name.startswith("results/"):
            return f"types.results.{module_name.rsplit('/', maxsplit=1)[-1]}"
        return f"types.{module_name}"

    @staticmethod
    def _render_runtime_helper_module_import(import_path: str, module_name: str, alias_name: str) -> str:
        """Render one private helper-module import line for a runtime stub."""
        base_types_import = ".types" if import_path in {"", "."} else f"{import_path}.types"
        if module_name.startswith("results/"):
            result_module_name = module_name.rsplit("/", maxsplit=1)[-1]
            return f"from {base_types_import}.results import {result_module_name} as {alias_name}"

        return f"from {base_types_import} import {module_name} as {alias_name}"

    def _build_local_runtime_helper_references(
        self,
        exports: dict[str, list[str]],
    ) -> tuple[dict[str, str], list[str]]:
        """Build qualified references through the public local `types` package."""
        references: dict[str, str] = {}
        for module_name, exported_names in exports.items():
            if not exported_names:
                continue

            module_path = self._types_package_module_path(module_name)
            references.update({name: f"{module_path}.{name}" for name in exported_names})

        if not references:
            return references, []

        types_import_base = self._current_annotated_types_package_import_base()
        import_lines = (
            [f"from {types_import_base.removesuffix('.types')} import types as types"]
            if types_import_base is not None
            else ["from . import types as types"]
        )
        return references, import_lines

    @staticmethod
    def _parse_runtime_helper_import_line(import_line: str) -> tuple[str, str, str] | None:
        """Parse one direct helper import into (base module, helper module, imported name)."""
        direct_match = re.fullmatch(
            r"from (?P<module>.+)\.types\.(?P<helper>lists|builders|readers|clients|requests|contexts|common|servers|enums|modules|schemas) import (?P<name>\w+)",
            import_line,
        )
        if direct_match is not None:
            return direct_match.group("module"), direct_match.group("helper"), direct_match.group("name")

        result_match = re.fullmatch(
            r"from (?P<module>.+)\.types\.results\.(?P<helper>client|server|tuples) import (?P<name>\w+)",
            import_line,
        )
        if result_match is not None:
            helper_module = f"results/{result_match.group('helper')}"
            return result_match.group("module"), helper_module, result_match.group("name")

        return None

    @staticmethod
    def _build_external_runtime_helper_alias(import_path: str, module_name: str) -> str:
        """Build a deterministic private alias for one imported helper module."""
        leading_dots = len(import_path) - len(import_path.lstrip("."))
        relative_prefix = f"rel{leading_dots}" if leading_dots else ""
        sanitized_module_path = import_path.lstrip(".").replace(".", "_")
        sanitized_helper_module = module_name.replace("/", "_")
        parts = [part for part in (relative_prefix, sanitized_module_path, sanitized_helper_module) if part]
        return "_" + "_".join(parts or ["types"])

    def _build_external_runtime_helper_references(
        self,
    ) -> tuple[dict[str, str], list[str], set[str]]:
        """Build private imports and qualified references for externally imported helper names."""
        references: dict[str, str] = {}
        filtered_import_lines: set[str] = set()
        module_aliases: dict[tuple[str, str], str] = {}

        for import_line in self.imports:
            parsed_import = self._parse_runtime_helper_import_line(import_line)
            if parsed_import is None:
                continue

            import_path, module_name, imported_name = parsed_import
            filtered_import_lines.add(import_line)
            module_key = (import_path, module_name)
            module_alias = module_aliases.setdefault(
                module_key,
                self._build_external_runtime_helper_alias(import_path, module_name),
            )
            references[imported_name] = f"{module_alias}.{imported_name}"

        import_lines = [
            self._render_runtime_helper_module_import(
                import_path, module_name, module_aliases[(import_path, module_name)]
            )
            for import_path, module_name in sorted(module_aliases)
        ]
        return references, import_lines, filtered_import_lines

    @staticmethod
    def _rewrite_runtime_helper_references(lines: list[str], references: dict[str, str]) -> list[str]:
        """Rewrite helper names in runtime scope lines to private qualified references."""
        if not references:
            return lines

        pattern = re.compile(
            r"(?<!\.)\b(" + "|".join(sorted(map(re.escape, references), key=len, reverse=True)) + r")\b"
        )
        rewritten_lines: list[str] = []

        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("type "):
                line_prefix, separator, line_suffix = line.partition("=")
                rewritten_suffix = pattern.sub(lambda match: references[match.group(0)], line_suffix)
                rewritten_lines.append(f"{line_prefix}{separator}{rewritten_suffix}")
                continue
            if stripped.startswith("class "):
                class_match = re.match(r"(?P<indent>\s*class\s+\w+)(?P<rest>.*)", line)
                if class_match is None:
                    rewritten_lines.append(pattern.sub(lambda match: references[match.group(0)], line))
                    continue
                rewritten_rest = pattern.sub(lambda match: references[match.group(0)], class_match.group("rest"))
                rewritten_lines.append(f"{class_match.group('indent')}{rewritten_rest}")
                continue
            if stripped.startswith("def "):
                def_match = re.match(r"(?P<prefix>\s*def\s+\w+)(?P<rest>.*)", line)
                if def_match is None:
                    rewritten_lines.append(pattern.sub(lambda match: references[match.group(0)], line))
                    continue
                rewritten_rest = pattern.sub(lambda match: references[match.group(0)], def_match.group("rest"))
                rewritten_lines.append(f"{def_match.group('prefix')}{rewritten_rest}")
                continue
            if stripped.startswith("@") or ":" not in line:
                rewritten_lines.append(pattern.sub(lambda match: references[match.group(0)], line))
                continue

            line_prefix, separator, line_suffix = line.partition(":")
            rewritten_suffix = pattern.sub(lambda match: references[match.group(0)], line_suffix)
            rewritten_lines.append(f"{line_prefix}{separator}{rewritten_suffix}")

        return rewritten_lines

    def _build_runtime_imports_and_scope_lines(
        self,
        exports: dict[str, list[str]],
    ) -> tuple[list[str], list[str]]:
        """Build runtime imports and scope lines without exposing public helper aliases."""
        local_references, local_import_lines = self._build_local_runtime_helper_references(exports)
        external_references, external_import_lines, filtered_import_lines = (
            self._build_external_runtime_helper_references()
        )
        runtime_imports = [import_line for import_line in self.imports if import_line not in filtered_import_lines]

        helper_import_lines = [*local_import_lines, *external_import_lines]
        if helper_import_lines:
            runtime_imports.extend(helper_import_lines)
        types_import_base = self._current_annotated_types_package_import_base()
        local_types_import_line = (
            f"from {types_import_base.removesuffix('.types')} import types as types"
            if types_import_base is not None
            else "from . import types as types"
        )
        if local_types_import_line not in runtime_imports:
            runtime_imports.append(local_types_import_line)

        helper_references = {**external_references, **local_references}
        runtime_scope_lines = self._rewrite_runtime_helper_references(
            self._build_runtime_scope_lines(exports), helper_references
        )
        return runtime_imports, runtime_scope_lines

    @staticmethod
    def _render_stub_module(docstring: str, body_lines: list[str]) -> str:
        """Render one generated stub module."""
        out = [docstring]
        out.extend(["", *(body_lines or ["pass"])])
        return "\n".join(out)

    @staticmethod
    def _render_string_list_assignment(name: str, values: list[str]) -> str:
        """Render a deterministic list assignment for generated modules."""
        joined_values = ", ".join(f'"{value}"' for value in values)
        return f"{name} = [{joined_values}]"

    def _current_annotated_types_package_import_base(self) -> str | None:
        """Return the absolute import base for this module's `types` package when annotations allow it."""
        if self._python_module_path is None:
            return None
        return f"{self._python_module_path}.{helper.replace_capnp_suffix(self._module_path.name)}.types"

    @staticmethod
    def _public_types_package_modules() -> list[str]:
        """Return the public helper submodules exposed from `types`."""
        return [
            "lists",
            "builders",
            "readers",
            "clients",
            "requests",
            "contexts",
            "common",
            "servers",
            "enums",
            "modules",
            "schemas",
            "results",
        ]

    @staticmethod
    def _public_result_package_modules() -> list[str]:
        """Return the public helper submodules exposed from `types.results`."""
        return ["client", "server", "tuples"]

    def _build_types_package_init_lines(self) -> list[str]:
        """Build the public import surface for `types/__init__`."""
        modules = self._public_types_package_modules()
        types_import_base = self._current_annotated_types_package_import_base()
        if types_import_base is None:
            import_lines = [f"from . import {module_name} as {module_name}" for module_name in modules]
        else:
            import_lines = [
                f"from {types_import_base} import {module_name} as {module_name}" for module_name in modules
            ]
        return [*import_lines, "", self._render_string_list_assignment("__all__", modules)]

    def _build_results_package_init_lines(self) -> list[str]:
        """Build the public import surface for `types.results.__init__`."""
        modules = self._public_result_package_modules()
        types_import_base = self._current_annotated_types_package_import_base()
        if types_import_base is None:
            import_lines = [f"from . import {module_name} as {module_name}" for module_name in modules]
        else:
            import_lines = [
                f"from {types_import_base}.results import {module_name} as {module_name}" for module_name in modules
            ]
        return [*import_lines, "", self._render_string_list_assignment("__all__", modules)]

    def _dump_modules_types_pyi(self) -> str:
        """Generate the companion `types.modules` stub containing module helper classes."""
        exports = self._build_types_module_exports()
        return self._dump_types_submodule_pyi(
            "modules",
            f'"""Module helper types for `{self._module_path.name}`."""',
            exports,
        )

    def _build_public_runtime_exports(self, runtime_scope_lines: list[str]) -> list[str]:
        """Collect the public names that should be advertised from the runtime stub."""
        public_names = {
            public_name
            for line in runtime_scope_lines
            if (public_name := self._extract_public_api_name(line)) is not None
        }
        public_names.add("types")
        return sorted(public_names)

    def dumps_types_pyi_files(self) -> dict[str, str]:
        """Generate the companion types-package .pyi files for this schema."""
        exports = self._build_types_module_exports()
        return {
            "types/__init__.pyi": self._render_stub_module(
                f'"""Public typing helper modules for `{self._module_path.name}`."""',
                self._build_types_package_init_lines(),
            ),
            "types/lists.pyi": self._dump_types_submodule_pyi(
                "lists",
                f'"""List helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/modules.pyi": self._dump_modules_types_pyi(),
            "types/schemas.pyi": self._dump_types_submodule_pyi(
                "schemas",
                f'"""Schema helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/builders.pyi": self._dump_types_submodule_pyi(
                "builders",
                f'"""Builder helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/readers.pyi": self._dump_types_submodule_pyi(
                "readers",
                f'"""Reader helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/clients.pyi": self._dump_types_submodule_pyi(
                "clients",
                f'"""Client helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/requests.pyi": self._dump_types_submodule_pyi(
                "requests",
                f'"""Request helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/contexts.pyi": self._dump_types_submodule_pyi(
                "contexts",
                f'"""Context helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/common.pyi": self._dump_types_submodule_pyi(
                "common",
                f'"""Common typing aliases for `{self._module_path.name}`."""',
                exports,
            ),
            "types/servers.pyi": self._dump_types_submodule_pyi(
                "servers",
                f'"""Server helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/enums.pyi": self._dump_types_submodule_pyi(
                "enums",
                f'"""Enum helper aliases for `{self._module_path.name}`."""',
                exports,
            ),
            "types/results/__init__.pyi": self._render_stub_module(
                f'"""Result helper modules for `{self._module_path.name}`."""',
                self._build_results_package_init_lines(),
            ),
            "types/results/client.pyi": self._dump_types_submodule_pyi(
                "results/client",
                f'"""Client result helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/results/server.pyi": self._dump_types_submodule_pyi(
                "results/server",
                f'"""Server result helper types for `{self._module_path.name}`."""',
                exports,
            ),
            "types/results/tuples.pyi": self._dump_types_submodule_pyi(
                "results/tuples",
                f'"""Result tuple helper types for `{self._module_path.name}`."""',
                exports,
            ),
        }

    @staticmethod
    def _render_runtime_module(docstring: str, body_lines: list[str]) -> str:
        """Render one generated runtime placeholder module."""
        out = [docstring, "", "# pyright: reportUnusedClass=none"]
        if body_lines:
            out.extend(["", *body_lines])
        return "\n".join(out)

    def _build_runtime_module_helper_class_lines(self, schema: capnp_types.SchemaType) -> list[str]:
        """Build a minimal runtime class skeleton for one generated struct/interface module."""
        node_kind = schema.node.which()
        if node_kind not in {capnp_types.CapnpElementType.STRUCT, capnp_types.CapnpElementType.INTERFACE}:
            return []

        base_class = "_StructModule" if node_kind == capnp_types.CapnpElementType.STRUCT else "_InterfaceModule"
        class_name = self.get_type_by_id(schema.node.id).name
        body_lines: list[str] = []

        for nested_node in schema.node.nestedNodes:
            nested_schema = self._schemas_by_id.get(nested_node.id)
            if nested_schema is None:
                continue

            nested_helper_lines = self._build_runtime_module_helper_class_lines(nested_schema)
            if not nested_helper_lines:
                continue
            if body_lines:
                body_lines.append("")
            body_lines.extend(nested_helper_lines)

        if not body_lines:
            body_lines.append("pass")

        return [f"class {class_name}({base_class}):", *self._indent_relative_lines(body_lines)]

    def _build_runtime_module_types_py_lines(self) -> list[str]:
        """Build runtime helper classes for `types.modules.py`."""
        helper_lines: list[str] = [
            "from __future__ import annotations",
            "",
            "from capnp.lib.capnp import _InterfaceModule, _StructModule",
        ]

        module_class_lines: list[str] = []
        for nested_node in self._schema.node.nestedNodes:
            nested_schema = self._schemas_by_id.get(nested_node.id)
            if nested_schema is None:
                continue

            rendered_lines = self._build_runtime_module_helper_class_lines(nested_schema)
            if not rendered_lines:
                continue
            if module_class_lines:
                module_class_lines.append("")
            module_class_lines.extend(rendered_lines)

        if module_class_lines:
            helper_lines.extend(["", *module_class_lines])

        return helper_lines

    def dumps_types_py_files(self) -> dict[str, str]:
        """Generate runtime placeholder files for the companion types package."""
        type_modules = self._public_types_package_modules()
        result_modules = self._public_result_package_modules()
        result_tuple_module_lines = self._build_runtime_result_tuple_module_lines()
        types_import_base = self._current_annotated_types_package_import_base()
        type_package_imports = [
            "from typing import TYPE_CHECKING",
            "",
            "if TYPE_CHECKING:",
            *self._indent_relative_lines(
                (
                    [f"from . import {module_name} as {module_name}" for module_name in type_modules]
                    if types_import_base is None
                    else [
                        *[
                            f"from {types_import_base} import {module_name} as {module_name}"
                            for module_name in type_modules
                        ],
                    ]
                ),
            ),
            "",
            self._render_string_list_assignment("__all__", type_modules),
        ]
        result_package_imports = [
            "from typing import TYPE_CHECKING",
            "",
            "if TYPE_CHECKING:",
            *self._indent_relative_lines(
                [f"from . import {module_name} as {module_name}" for module_name in result_modules]
                if types_import_base is None
                else [
                    f"from {types_import_base}.results import {module_name} as {module_name}"
                    for module_name in result_modules
                ]
            ),
            "",
            self._render_string_list_assignment("__all__", result_modules),
        ]
        server_module_lines: list[str] = []
        if self._runtime_server_aliases:
            root_runtime_names = sorted(
                {runtime_path.split(".", maxsplit=1)[0] for runtime_path in self._runtime_server_aliases.values()}
            )
            server_module_lines.append(f"from .. import {', '.join(root_runtime_names)}")
            server_module_lines.extend(
                [
                    "",
                    *[
                        f"{alias_name} = {runtime_path}"
                        for alias_name, runtime_path in sorted(self._runtime_server_aliases.items())
                    ],
                ],
            )

        return {
            "types/__init__.py": self._render_runtime_module(
                f'"""Runtime placeholder package for typing helpers of `{self._module_path.name}`."""',
                type_package_imports,
            ),
            "types/lists.py": self._render_runtime_module(
                f'"""Runtime placeholder module for list helpers of `{self._module_path.name}`."""',
                [],
            ),
            "types/modules.py": self._render_runtime_module(
                f'"""Runtime placeholder module for module helper types of `{self._module_path.name}`."""',
                self._build_runtime_module_types_py_lines(),
            ),
            "types/schemas.py": self._render_runtime_module(
                f'"""Runtime placeholder module for schema helper types of `{self._module_path.name}`."""',
                [],
            ),
            "types/builders.py": self._render_runtime_module(
                f'"""Runtime placeholder module for builder helpers of `{self._module_path.name}`."""',
                [],
            ),
            "types/readers.py": self._render_runtime_module(
                f'"""Runtime placeholder module for reader helpers of `{self._module_path.name}`."""',
                [],
            ),
            "types/clients.py": self._render_runtime_module(
                f'"""Runtime placeholder module for client helpers of `{self._module_path.name}`."""',
                [],
            ),
            "types/requests.py": self._render_runtime_module(
                f'"""Runtime placeholder module for request helpers of `{self._module_path.name}`."""',
                [],
            ),
            "types/contexts.py": self._render_runtime_module(
                f'"""Runtime placeholder module for context helpers of `{self._module_path.name}`."""',
                [],
            ),
            "types/common.py": self._render_runtime_module(
                f'"""Runtime placeholder module for common typing helpers of `{self._module_path.name}`."""',
                [],
            ),
            "types/servers.py": self._render_runtime_module(
                f'"""Runtime placeholder module for server helpers of `{self._module_path.name}`."""',
                server_module_lines,
            ),
            "types/enums.py": self._render_runtime_module(
                f'"""Runtime placeholder module for enum helper aliases of `{self._module_path.name}`."""',
                [],
            ),
            "types/results/__init__.py": self._render_runtime_module(
                f'"""Runtime placeholder package for result helpers of `{self._module_path.name}`."""',
                result_package_imports,
            ),
            "types/results/client.py": self._render_runtime_module(
                f'"""Runtime placeholder module for client result helpers of `{self._module_path.name}`."""',
                [],
            ),
            "types/results/server.py": self._render_runtime_module(
                f'"""Runtime placeholder module for server result helpers of `{self._module_path.name}`."""',
                [],
            ),
            "types/results/tuples.py": self._render_runtime_module(
                f'"""Runtime placeholder module for result tuple helpers of `{self._module_path.name}`."""',
                result_tuple_module_lines,
            ),
        }

    def dumps_pyi(self) -> str:
        """Generate the runtime-facing .pyi stub output for this schema.

        Returns:
            str: The output string.

        """
        self._ensure_root_scope(context="dumping")
        exports = self._build_types_module_exports()
        runtime_imports, runtime_scope_lines = self._build_runtime_imports_and_scope_lines(exports)
        out: list[str] = []
        out.append(self.docstring)
        out.extend(runtime_imports)

        if self._needs_dynamic_object_reader_augmentation:
            out.append("from capnp.lib.capnp import _DynamicObjectReader")

        if self.type_vars:
            out.extend(f'{name} = TypeVar("{name}")' for name in sorted(self.type_vars))
            out.append("")

        out.extend(runtime_scope_lines)
        public_exports = self._build_public_runtime_exports(runtime_scope_lines)
        if public_exports:
            out.extend(["", self._render_string_list_assignment("__all__", public_exports)])
        return "\n".join(out)

    def _find_runtime_schema_access_segments_from_type(
        self,
        type_reader: TypeReader,
        target_id: int,
        seen: set[int],
    ) -> list[tuple[str, str | None]] | None:
        """Find runtime access path segments for a schema referenced by a type."""
        type_which = type_reader.which()

        if type_which in {"struct", "interface", "enum"}:
            schema_id = getattr(type_reader, type_which).typeId
            referenced_schema = self._schemas_by_id.get(schema_id)
            if referenced_schema is None:
                return None

            nested_segments = self._find_runtime_schema_access_segments(referenced_schema, target_id, seen)
            if nested_segments is None:
                return None

            return [("schema", None), *nested_segments]

        if type_which == "list":
            nested_segments = self._find_runtime_schema_access_segments_from_list_element(
                type_reader.list.elementType,
                target_id,
                seen,
            )
            if nested_segments is not None:
                return [("schema", None), ("elementType", None), *nested_segments]

        return None

    def _find_runtime_schema_access_segments_from_list_element(
        self,
        element_type: TypeReader,
        target_id: int,
        seen: set[int],
    ) -> list[tuple[str, str | None]] | None:
        """Find runtime access path segments for a list element schema."""
        element_which = element_type.which()

        if element_which == "list":
            nested_segments = self._find_runtime_schema_access_segments_from_list_element(
                element_type.list.elementType,
                target_id,
                seen,
            )
            if nested_segments is not None:
                return [("elementType", None), *nested_segments]
            return None

        if element_which in {"struct", "interface", "enum"}:
            schema_id = getattr(element_type, element_which).typeId
            referenced_schema = self._schemas_by_id.get(schema_id)
            if referenced_schema is None:
                return None

            return self._find_runtime_schema_access_segments(referenced_schema, target_id, seen)

        return None

    def _find_runtime_schema_access_segments_in_field(
        self,
        field: FieldReader,
        target_id: int,
        seen: set[int],
    ) -> list[tuple[str, str | None]] | None:
        """Find runtime field access path segments that resolve to the target schema."""
        if field.which() != "slot":
            return None

        nested_segments = self._find_runtime_schema_access_segments_from_type(field.slot.type, target_id, seen)
        if nested_segments is None:
            return None

        return [("fields", field.name), *nested_segments]

    def _find_runtime_segments_for_method_schema(
        self,
        schema_id: int,
        target_id: int,
        seen: set[int],
        method_name: str,
        attr_name: str,
    ) -> list[tuple[str, str | None]] | None:
        """Resolve runtime access segments through one method param/result schema."""
        method_schema = self._schemas_by_id.get(schema_id)
        if method_schema is None:
            return None

        nested_segments = self._find_runtime_schema_access_segments(method_schema, target_id, seen)
        if nested_segments is None:
            return None

        return [("methods", method_name), ("attr", attr_name), *nested_segments]

    def _find_runtime_segments_in_interface_methods(
        self,
        schema: capnp_types.SchemaType,
        target_id: int,
        seen: set[int],
    ) -> list[tuple[str, str | None]] | None:
        """Resolve runtime access segments through interface methods."""
        for method in schema.node.interface.methods:
            param_segments = self._find_runtime_segments_for_method_schema(
                method.paramStructType,
                target_id,
                seen,
                method.name,
                "param_type",
            )
            if param_segments is not None:
                return param_segments

            result_segments = self._find_runtime_segments_for_method_schema(
                method.resultStructType,
                target_id,
                seen,
                method.name,
                "result_type",
            )
            if result_segments is not None:
                return result_segments

        return None

    def _find_runtime_segments_in_struct_fields(
        self,
        schema: capnp_types.SchemaType,
        target_id: int,
        seen: set[int],
    ) -> list[tuple[str, str | None]] | None:
        """Resolve runtime access segments through struct fields."""
        for field in schema.node.struct.fields:
            nested_segments = self._find_runtime_schema_access_segments_in_field(field, target_id, seen)
            if nested_segments is not None:
                return nested_segments
        return None

    def _find_runtime_schema_access_segments(
        self,
        schema: capnp_types.SchemaType,
        target_id: int,
        seen: set[int] | None = None,
    ) -> list[tuple[str, str | None]] | None:
        """Find runtime access path segments that resolve a branded nested schema."""
        if seen is None:
            seen = set()

        schema_id = schema.node.id
        if schema_id in seen:
            return None
        seen.add(schema_id)

        if schema_id == target_id:
            return []

        node_which = schema.node.which()
        if node_which == capnp_types.CapnpElementType.INTERFACE:
            return self._find_runtime_segments_in_interface_methods(schema, target_id, seen)

        if node_which == capnp_types.CapnpElementType.STRUCT:
            return self._find_runtime_segments_in_struct_fields(schema, target_id, seen)

        return None

    def _build_runtime_nested_schema_expr(
        self,
        ancestor_schemas: list[tuple[str, object]],
        nested_schema: capnp_types.SchemaType,
    ) -> str | None:
        """Build the runtime expression for a nested schema from the nearest branded ancestor."""
        for ancestor_path, ancestor_schema in reversed(ancestor_schemas):
            if not isinstance(ancestor_schema, (_EnumSchema, _InterfaceSchema, _StructSchema, _Schema)):
                continue
            if (
                ancestor_schema.node.which() == capnp_types.CapnpElementType.INTERFACE
                and not self._should_emit_precise_interface_schema_helper(ancestor_schema)
            ):
                continue

            nested_segments = self._find_runtime_schema_access_segments(ancestor_schema, nested_schema.node.id)
            if nested_segments is None:
                continue

            expr = f"{ancestor_path}.schema"
            for segment_kind, segment_value in nested_segments:
                expr = self._advance_runtime_nested_schema_expr(expr, segment_kind, segment_value)
            return expr

        return None

    def _advance_runtime_nested_schema_expr(
        self,
        expr: str,
        segment_kind: str,
        segment_value: str | None,
    ) -> str:
        """Advance one runtime schema-access expression segment."""
        next_expr = expr

        if segment_kind == "methods":
            next_expr = f"{expr}.methods[{segment_value!r}]"
        elif segment_kind == "fields":
            next_expr = f"{expr}.fields[{segment_value!r}]"
        elif segment_kind == "attr":
            if segment_value == "param_type":
                next_expr = f"{expr}.param_type"
            elif segment_value == "result_type":
                next_expr = f"{expr}.result_type"
            else:
                next_expr = f"{expr}.{segment_value}"
        elif segment_kind == "schema":
            next_expr = f"{expr}.schema"
        elif segment_kind == "elementType":
            next_expr = f"{expr}.elementType"

        return next_expr

    def _runtime_module_constructor_name(self, schema: capnp_types.SchemaType) -> str | None:
        """Return the runtime constructor used for one generated module object."""
        node_kind = schema.node.which()
        if node_kind == capnp_types.CapnpElementType.ENUM:
            return "_EnumModule"
        if node_kind in {capnp_types.CapnpElementType.STRUCT, capnp_types.CapnpElementType.INTERFACE}:
            return self.get_type_by_id(schema.node.id).scoped_name
        return None

    def _build_runtime_module_construction_lines(
        self,
        full_path: str,
        nested_schema: capnp_types.SchemaType,
        ancestor_schemas: list[tuple[str, object]],
    ) -> list[str] | None:
        """Build runtime lines that instantiate a nested module."""
        nested_id = nested_schema.node.id
        nested_name = full_path.rsplit(".", 1)[-1]
        node_type = nested_schema.node.which()

        if node_type == capnp_types.CapnpElementType.CONST:
            return [f"{full_path} = _loader.get({hex(nested_id)}).as_const_value()"]

        module_constructor = self._runtime_module_constructor_name(nested_schema)
        cast_method = {
            capnp_types.CapnpElementType.STRUCT: "as_struct",
            capnp_types.CapnpElementType.INTERFACE: "as_interface",
            capnp_types.CapnpElementType.ENUM: "as_enum",
        }.get(node_type)
        if module_constructor is None or cast_method is None:
            return None

        schema_expr = self._build_runtime_nested_schema_expr(ancestor_schemas, nested_schema)
        if schema_expr is None:
            schema_expr = f"_loader.get({hex(nested_id)}).{cast_method}()"
            return [f"{full_path} = {module_constructor}({schema_expr}, {nested_name!r})"]

        return [
            f"{full_path} = {module_constructor}(",
            f"    {schema_expr},",
            f"    {nested_name!r},",
            ")",
        ]

    def _append_embedded_schema_nodes(self, out: list[str]) -> None:
        """Append base64-encoded embedded schema nodes."""
        out.extend(["# Embedded compiled schemas (base64-encoded)", "_SCHEMA_NODES = ["])

        root_bytes = self._schema.node.as_builder().to_bytes_packed()
        root_b64 = base64.b64encode(root_bytes).decode("ascii")
        out.append(f"    {root_b64!r},  # {self._schema.node.displayName}")

        seen_ids = {self._schema.node.id}
        for schema_id, schema in self._schemas_by_id.items():
            if schema_id in seen_ids:
                continue
            try:
                schema_bytes = schema.node.as_builder().to_bytes_packed()
                schema_b64 = base64.b64encode(schema_bytes).decode("ascii")
                out.append(f"    {schema_b64!r},  # {schema.node.displayName}")
                seen_ids.add(schema_id)
            except SCHEMA_SERIALIZATION_EXCEPTIONS as error:
                logger.debug("Could not serialize schema %s: %s", hex(schema_id), error)

        out.extend(["]", ""])

    def _append_runtime_loader_setup(self, out: list[str]) -> None:
        """Append runtime schema-loader initialization lines."""
        out.extend(
            [
                "# Load schemas and build module structure",
                "# Use a shared loader stored on capnp module so capabilities work across schema modules",
                "if not hasattr(capnp, '_embedded_schema_loader'):",
                "    capnp._embedded_schema_loader = capnp.SchemaLoader()",
                "_loader = capnp._embedded_schema_loader",
                "for _schema_b64 in _SCHEMA_NODES:",
                "    _schema_data = base64.b64decode(_schema_b64)",
                "    _node_reader = schema_capnp.Node.from_bytes_packed(_schema_data)",
                "    _loader.load_dynamic(_node_reader)",
                "",
            ],
        )

    def _extend_runtime_module_construction(
        self,
        out: list[str],
        schema_node: NodeReader,
        ancestor_schemas: list[tuple[str, object]],
        parent_path: str = "",
    ) -> None:
        """Append inline runtime module construction lines depth-first."""
        for nested_node in schema_node.nestedNodes:
            nested_schema = self._schemas_by_id.get(nested_node.id)
            if nested_schema is None:
                continue

            full_path = f"{parent_path}.{nested_node.name}" if parent_path else nested_node.name
            construction_lines = self._build_runtime_module_construction_lines(
                full_path, nested_schema, ancestor_schemas
            )
            if construction_lines is not None:
                out.extend(construction_lines)

            node_type = nested_schema.node.which()
            if node_type in (capnp_types.CapnpElementType.STRUCT, capnp_types.CapnpElementType.INTERFACE):
                self._extend_runtime_module_construction(
                    out,
                    nested_schema.node,
                    [*ancestor_schemas, (full_path, nested_schema)],
                    full_path,
                )

    def _build_runtime_result_tuple_module_lines(self) -> list[str]:
        """Build runtime ResultTuple definitions for `types.results.tuples`."""
        if not self._all_server_namedtuples:
            return []

        out = ["from typing import NamedTuple", ""]
        exported_names: list[str] = []
        for _, namedtuples_dict in sorted(self._all_server_namedtuples.items()):
            for _, (namedtuple_name, fields) in sorted(namedtuples_dict.items()):
                field_list = [f'("{field_name}", object)' for field_name, _ in fields]
                out.append(f"{namedtuple_name} = NamedTuple('{namedtuple_name}', [{', '.join(field_list)}])")
                exported_names.append(namedtuple_name)

        out.extend(["", self._render_string_list_assignment("__all__", sorted(exported_names))])
        return out

    def dumps_py(self) -> str:
        """Generate the .py loader module for this schema.

        The generated .py file embeds the .capnp source file, making it completely
        self-contained and independent of external .capnp files.

        Returns:
            str: The output string.

        """
        self._ensure_root_scope(context="dumping .py")
        construction_lines: list[str] = []
        self._extend_runtime_module_construction(construction_lines, self._schema.node, [])
        construction_source = "\n".join(construction_lines)
        runtime_import_names = [name for name in ("_EnumModule",) if f"{name}(" in construction_source]
        runtime_module_class_names = [
            name for name in sorted(self._root_module_class_names) if f"{name}(" in construction_source
        ]

        out: list[str] = []
        out.append("# pyright: reportAttributeAccessIssue=false, reportArgumentType=false")
        out.append(self.docstring)
        out.append("")
        out.append("import base64")
        out.append("")
        out.append("import capnp")
        out.append("import schema_capnp")
        if runtime_import_names:
            out.append(f"from capnp.lib.capnp import {', '.join(runtime_import_names)}")
        if runtime_module_class_names:
            types_import_base = self._current_annotated_types_package_import_base()
            out.append(
                f"from {types_import_base}.modules import {', '.join(runtime_module_class_names)}"
                if types_import_base is not None
                else f"from .types.modules import {', '.join(runtime_module_class_names)}"
            )

        out.append("")
        out.append("capnp.remove_import_hook()")
        out.append("")
        self._append_embedded_schema_nodes(out)
        self._append_runtime_loader_setup(out)
        out.extend(["# Build module structure inline", ""])
        out.extend(construction_lines)
        return "\n".join(out)
