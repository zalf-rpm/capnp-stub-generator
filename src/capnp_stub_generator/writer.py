"""Generate type hints for *.capnp schemas.

Note: This generator requires pycapnp >= 2.0.0.
"""

from __future__ import annotations

import base64
import contextlib
import logging
import os.path
import pathlib
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
from capnp_stub_generator.scope import CapnpType, NoParentError, Scope
from capnp_stub_generator.writer_dto import (
    EnumGenerationContext,
    InterfaceGenerationContext,
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

    def __init__(
        self,
        schema: _Schema,
        file_path: str,
        schema_loader: capnp.SchemaLoader,
        file_id_to_path: dict[int, str],
    ) -> None:
        """Initialize the stub writer with schema information.

        Args:
            schema: The root schema to parse and write stubs for.
            file_path: Path to the schema file (e.g., "path/to/schema.capnp").
            schema_loader: SchemaLoader instance with all nodes loaded.
            file_id_to_path: Mapping of schema IDs to file paths for resolving imports.

        """
        self.scope: Scope = Scope(name="", id=schema.node.id, parent=None, return_scope=None)
        self.scopes_by_id: dict[int, Scope] = {self.scope.id: self.scope}

        self._schema: _Schema = schema
        self._schema_loader: capnp.SchemaLoader = schema_loader
        self._file_id_to_path: dict[int, str] = file_id_to_path

        self._module_path: pathlib.Path = pathlib.Path(file_path)

        # Python module annotation ID (from python.capnp: annotation module(file): Text)
        self._python_module_annotation_id: int = 0x8C5EA3FEE3B0F96C
        self._python_module_path: str | None = self._get_python_module_annotation()

        # Build a flat mapping of all schemas by ID for nested type resolution
        self._schemas_by_id: dict[int, capnp_types.SchemaType] = {}
        self._build_schema_id_mapping()

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
        self._all_type_aliases: dict[str, tuple[str, str] | tuple[str, str, list[str]]] = {}

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
                    logger.info(f"Found Python module annotation: {module_path}")
                    return module_path
        except Exception as e:
            logger.debug(f"Error reading Python module annotation: {e}")
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
        except Exception as e:
            logger.debug(f"Error reading Python module annotation from schema {hex(schema_id)}: {e}")

        return None

    def _build_schema_id_mapping(self) -> None:
        """Build a flat mapping of all schemas by their ID.

        This walks through ALL schemas available in the loader, including:
        - The root schema
        - All nested nodes recursively
        - Schemas from other files (for cross-file references)
        """

        def add_schema_and_nested(schema: capnp_types.SchemaType) -> None:
            """Recursively add a schema and all its nested schemas to the mapping."""
            schema_id = schema.node.id
            if schema_id in self._schemas_by_id:
                return  # Already processed

            self._schemas_by_id[schema_id] = schema

            # Process all nested nodes
            for nested_node in schema.node.nestedNodes:
                nested_id = nested_node.id
                if nested_id in self._schemas_by_id:
                    continue  # Already processed

                # Try to get the nested schema from the loader
                try:
                    nested_schema = self._schema_loader.get(nested_id)
                    add_schema_and_nested(nested_schema)
                except Exception as e:
                    logger.debug(
                        f"Could not resolve nested schema {nested_node.name} (id={hex(nested_id)}) for {schema.node.displayName}: {e}",
                    )

            # Also collect schemas referenced by struct fields
            # This includes groups, and field types (structs, interfaces, lists of structs, etc.)
            if schema.node.which() == capnp_types.CapnpElementType.STRUCT:
                for field in schema.node.struct.fields:
                    # Handle group fields (unions/groups)
                    if field.which() == "group":
                        group_id = field.group.typeId
                        if group_id not in self._schemas_by_id:
                            try:
                                group_schema = self._schema_loader.get(group_id)
                                add_schema_and_nested(group_schema)
                            except Exception as e:
                                logger.warning(
                                    f"Group field {field.name} references schema {hex(group_id)} not in loader: {e}",
                                )
                    # Handle slot fields that reference other types
                    elif field.which() == "slot":
                        slot = field.slot
                        type_node = slot.type

                        # Recursively extract type IDs from complex types
                        def collect_type_ids(type_obj: TypeReader) -> list[int]:  # type: ignore[no-untyped-def]
                            """Extract all schema IDs referenced by a type."""
                            type_which = type_obj.which()
                            referenced_ids: list[int] = []

                            if type_which == "struct":
                                referenced_ids = [type_obj.struct.typeId]
                            elif type_which == "interface":
                                referenced_ids = [type_obj.interface.typeId]
                            elif type_which == "list":
                                referenced_ids = collect_type_ids(type_obj.list.elementType)
                            elif type_which == "enum":
                                referenced_ids = [type_obj.enum.typeId]

                            return referenced_ids

                        referenced_ids = collect_type_ids(type_node)
                        for ref_id in referenced_ids:
                            if ref_id not in self._schemas_by_id:
                                try:
                                    ref_schema = self._schema_loader.get(ref_id)
                                    add_schema_and_nested(ref_schema)
                                except Exception as e:
                                    logger.debug(
                                        f"Could not load referenced type {hex(ref_id)} for field {field.name}: {e}",
                                    )

            # Also collect schemas referenced by interface methods (params and results)
            # Interface method param and result structs are implicit and not listed as nested nodes
            if schema.node.which() == capnp_types.CapnpElementType.INTERFACE:
                for method in schema.node.interface.methods:
                    # Collect param struct
                    param_id = method.paramStructType
                    if param_id not in self._schemas_by_id:
                        try:
                            param_schema = self._schema_loader.get(param_id)
                            add_schema_and_nested(param_schema)
                        except Exception as e:
                            logger.debug(
                                f"Could not load param struct for method {method.name} (id={hex(param_id)}): {e}",
                            )

                    # Collect result struct
                    result_id = method.resultStructType
                    if result_id not in self._schemas_by_id:
                        try:
                            result_schema = self._schema_loader.get(result_id)
                            add_schema_and_nested(result_schema)
                        except Exception as e:
                            logger.debug(
                                f"Could not load result struct for method {method.name} (id={hex(result_id)}): {e}",
                            )

        # Add the root schema and all its references
        add_schema_and_nested(self._schema)

        logger.debug(f"Built schema ID mapping with {len(self._schemas_by_id)} schemas")
        if len(self._schemas_by_id) == 0:
            logger.warning("Schema ID mapping is empty! This will result in empty stubs.")
            logger.warning(f"Root schema ID: {hex(self._schema.node.id)}")

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

    def _get_builder_property_types(self, field: helper.TypeHintedVariable) -> tuple[str, str | None]:
        """Determine getter and setter types for Builder class fields.

        Args:
            field: The field to get the types for

        Returns:
            Tuple of (getter_type, setter_type). setter_type is None if same as getter.

        """
        # Handle generic parameters (AnyPointer with parameter)
        if field.is_generic_param:
            # Getter returns _DynamicObjectReader
            getter_type = field.primary_type_nested
            # Setter accepts only pointer types (structs, lists, blobs, interfaces)
            # Primitives (int, float, bool) are NOT allowed as Cap'n Proto generic parameters
            setter_type = "AnyPointer"
            self._needs_anypointer_alias = True
            return getter_type, setter_type

        # Handle AnyPointer fields (accepts all Cap'n Proto types including primitives)
        if field.is_any_pointer:
            getter_type = field.get_type_with_affixes([helper.BUILDER_NAME])
            setter_type = "AnyPointer"
            self._needs_anypointer_alias = True
            return getter_type, setter_type

        # Handle AnyStruct fields
        if field.is_any_struct:
            getter_type = field.get_type_with_affixes([helper.BUILDER_NAME])
            setter_type = "AnyStruct | dict[str, Any]"
            self._needs_anystruct_alias = True
            self._add_typing_import("Any")
            return getter_type, setter_type

        # Handle AnyList fields (accepts Sequence/list)
        if field.is_any_list:
            getter_type = field.get_type_with_affixes([helper.BUILDER_NAME])
            setter_type = "AnyList | Sequence[Any]"
            self._needs_anylist_alias = True
            self._add_typing_import("Sequence")
            self._add_typing_import("Any")
            return getter_type, setter_type

        # Handle Capability fields
        if field.is_capability:
            getter_type = field.primary_type_nested
            setter_type = "Capability"
            self._needs_capability_alias = True
            return getter_type, setter_type

        if field.has_type_hint_with_builder_affix:
            # For lists, use MutableSequence for Builder (lists are mutable)
            if field.nesting_depth == 1:
                getter_type = field.get_type_with_affixes([helper.BUILDER_NAME])
                # Replace Sequence with MutableSequence for builders (they support __setitem__)
                if "Sequence[" in getter_type:
                    getter_type = getter_type.replace("Sequence[", "MutableSequence[")
                    self._add_typing_import("MutableSequence")
                # Setter accepts Builder/Reader types + dict, but NOT the base type
                setter_types = [helper.BUILDER_NAME, helper.READER_NAME]
                setter_type = field.get_type_with_affixes(setter_types) + " | Sequence[dict[str, Any]]"
                self._add_typing_import("Sequence")
                self._add_typing_import("Any")
            else:
                # For non-list structs: setter accepts Builder/Reader + dict
                getter_type = field.get_type_with_affixes([helper.BUILDER_NAME])
                setter_types = [helper.BUILDER_NAME, helper.READER_NAME]
                setter_type = field.get_type_with_affixes(setter_types) + " | dict[str, Any]"
                self._add_typing_import("Any")
        # For interface fields: getter returns Protocol, setter accepts Protocol | Server
        elif len(field.type_hints) > 1 and any(".Server" in str(h) for h in field.type_hints):
            getter_type = field.primary_type_nested  # Protocol only
            setter_type = field.full_type_nested  # Protocol | Server
        else:
            # Primitive and enum fields (including primitive lists)
            getter_type = field.primary_type_nested
            # For Builder properties with list types, use MutableSequence
            if "Sequence[" in getter_type:
                getter_type = getter_type.replace("Sequence[", "MutableSequence[")
                self._add_typing_import("MutableSequence")
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
        total_init_overloads = len(init_choices) + len(list_init_choices) if list_init_choices else len(init_choices)
        use_overload = total_init_overloads > 1

        if use_overload:
            self._add_typing_import("overload")
        if init_choices or list_init_choices:
            self._add_typing_import("Literal")

        # Note: The init() method parameter is now LiteralString in pycapnp stubs
        # This allows our Literal["fieldname"] overloads to be compatible

        added_override = False

        # Add init method overloads for union/group fields (return their Builder type)
        for field_name, field_type in init_choices:
            if not added_override:
                self.scope.add("@override")
                added_override = True
            if use_overload:
                self.scope.add(helper.new_decorator("overload"))
            # Build builder type name - try flat alias first
            builder_alias = self._get_flat_builder_alias(field_type)
            builder_type = builder_alias or self._build_scoped_builder_type(field_type)

            # Parameter must be named "field" to match base class
            init_params = [
                "self",
                helper.TypeHintedVariable("field", [helper.TypeHint(f'Literal["{field_name}"]', primary=True)]),
                helper.TypeHintedVariable(
                    "size",
                    [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                    default="None",
                ),
            ]

            self.scope.add(
                helper.new_function(
                    "init",
                    parameters=init_params,
                    return_type=builder_type,
                ),
            )

        # Add init method overloads for lists (properly typed)
        for field_name, builder_type in list_init_choices:
            if not added_override:
                self.scope.add("@override")
                added_override = True
            if use_overload:
                self.scope.add(helper.new_decorator("overload"))

            # Parameter must be named "field" to match base class
            init_params_list = [
                "self",
                helper.TypeHintedVariable("field", [helper.TypeHint(f'Literal["{field_name}"]', primary=True)]),
                helper.TypeHintedVariable(
                    "size",
                    [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                    default="None",
                ),
            ]

            self.scope.add(
                helper.new_function(
                    "init",
                    parameters=init_params_list,
                    return_type=builder_type,
                ),
            )

        # Add catchall overload if we added any specific overloads
        if use_overload:
            if not added_override:
                self.scope.add("@override")
                added_override = True
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
        self._add_typing_import("Any")
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

        # Add **kwargs: Any to match base signature
        new_message_params.append("**kwargs: Any")

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
                try:
                    # Get the superclass type
                    superclass_type = self.get_type_by_id(superclass.id)
                    # superclass_type.name is now the interface module name (e.g., "_IdentifiableModule")
                    protocol_name = superclass_type.name
                    # Build scoped name
                    if superclass_type.scope and not superclass_type.scope.is_root:
                        base_protocol = f"{superclass_type.scope.scoped_name}.{protocol_name}"
                    else:
                        base_protocol = protocol_name
                    base_classes.append(base_protocol)
                except KeyError:
                    # Superclass not yet registered - try to generate it first
                    try:
                        # Try to get the superclass schema from the loader
                        superclass_schema = self._schema_loader.get(superclass.id)
                        self.generate_nested(superclass_schema)
                        superclass_type = self.get_type_by_id(superclass.id)
                        # superclass_type.name is now the interface module name
                        protocol_name = superclass_type.name
                        if superclass_type.scope and not superclass_type.scope.is_root:
                            base_protocol = f"{superclass_type.scope.scoped_name}.{protocol_name}"
                        else:
                            base_protocol = protocol_name
                        base_classes.append(base_protocol)
                    except Exception as e:
                        logger.debug(f"Could not resolve superclass {superclass.id}: {e}")

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
                    except Exception as load_error:
                        logger.debug(
                            f"Could not find or load nested type {nested_node.name} (id={hex(nested_node.id)}) in interface {schema.node.displayName}: {load_error}",
                        )
            except Exception as e:  # pragma: no cover
                logger.debug(
                    f"Could not generate nested type {nested_node.name} in interface {schema.node.displayName}: {e}",
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
        if client_return_type:
            # For nested interfaces: Calculator.Value -> Calculator.ValueClient
            # For top-level: Greeter -> GreeterClient
            # Use unquoted forward reference
            if scope_path and "." in scope_path:
                # Nested interface - replace last component with client name
                parts = scope_path.rsplit(".", 1)
                return_type = f"{parts[0]}.{client_return_type}"
            else:
                # Top-level interface
                return_type = client_return_type
        else:
            return_type = fully_qualified_interface

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

    def _generate_list_class(self, type_reader: TypeReader) -> tuple[str, str, str]:
        """Generate a specific List class for the given list type reader.

        Args:
            type_reader: The TypeReader for the list (must be of type LIST).

        Returns:
            Tuple of (list_class_name, reader_alias, builder_alias).

        """
        assert type_reader.which() == capnp_types.CapnpElementType.LIST
        element_type = type_reader.list.elementType
        element_which = element_type.which()

        # Determine element types and base name
        reader_type: str
        builder_type: str
        setter_type: str
        base_name: str
        has_init = False
        init_args: list[str] = []

        if element_which == capnp_types.CapnpElementType.STRUCT:
            # Struct list
            struct_name = self.get_type_name(element_type)
            # Use flat aliases if available
            builder_alias = self._get_flat_builder_alias(struct_name)
            reader_alias = self._get_flat_reader_alias(struct_name)

            reader_type = reader_alias or self._build_nested_reader_type(struct_name)
            builder_type = builder_alias or self._build_scoped_builder_type(struct_name)

            # Setter accepts Reader, Builder, or dict
            setter_type = f"{reader_type} | {builder_type} | dict[str, Any]"
            self._add_typing_import("Any")

            # Base name for list class (sanitize dots)
            # Use only the last component to avoid scoped names in list class
            last_component = struct_name.split(".")[-1]
            if last_component.startswith("_"):
                # Clean up protocol names: _CalculatorStructModule -> Calculator
                base_name = self._extract_name_from_protocol(last_component)
            else:
                base_name = last_component

            has_init = True
            # Match base class signature: init(self, index, size=None)
            init_args = ["self", "index: int", "size: int | None = None"]

        elif element_which == capnp_types.CapnpElementType.LIST:
            # List of lists
            inner_list_class, inner_reader_alias, inner_builder_alias = self._generate_list_class(element_type)
            reader_type = inner_reader_alias
            builder_type = inner_builder_alias

            # Setter accepts Reader, Builder, or Sequence
            setter_type = f"{reader_type} | {builder_type} | Sequence[Any]"
            self._add_typing_import("Sequence")
            self._add_typing_import("Any")

            base_name = inner_list_class
            base_name = base_name.removeprefix("_")  # Remove _ prefix but keep List suffix

            has_init = True
            # Match base class signature: init(self, index, size=None)
            # Although size is required for lists, we must match the base signature for type checking
            init_args = ["self", "index: int", "size: int | None = None"]

        elif element_which == capnp_types.CapnpElementType.ENUM:
            # Enum list
            enum_name = self.get_type_name(element_type)
            reader_type = enum_name
            builder_type = enum_name
            setter_type = enum_name

            base_name = enum_name.replace(".", "_")

        elif element_which == capnp_types.CapnpElementType.INTERFACE:
            # Interface list
            interface_name = self.get_type_name(element_type)
            # Use Client alias
            client_alias = self._get_flat_client_alias(interface_name)
            if not client_alias:
                # Try to extract from protocol name
                parts = interface_name.split(".")
                last = parts[-1]
                if last.startswith("_"):
                    client_alias = f"{self._extract_name_from_protocol(last)}Client"
                else:
                    client_alias = f"{interface_name}Client"

            reader_type = client_alias
            builder_type = client_alias
            setter_type = f"{client_alias} | {interface_name}.Server"

            base_name = client_alias

        elif element_which == capnp_types.CapnpElementType.ANY_POINTER:
            # AnyPointer list
            reader_type = "_DynamicObjectReader"
            builder_type = "_DynamicObjectBuilder"
            setter_type = "AnyPointer"
            self._needs_anypointer_alias = True
            base_name = "AnyPointer"

        else:
            # Primitive list
            python_type = capnp_types.CAPNP_TYPE_TO_PYTHON[element_which]
            reader_type = python_type
            builder_type = python_type
            setter_type = python_type
            base_name = element_which.title()  # e.g. Int32

        # Construct list class name
        list_class_name = f"_{base_name}List"

        # Register aliases
        reader_alias = f"{base_name}ListReader"
        builder_alias = f"{base_name}ListBuilder"

        # Check if already generated
        if list_class_name in self._generated_list_types:
            return list_class_name, reader_alias, builder_alias

        self._generated_list_types.add(list_class_name)

        # Register in self._all_type_aliases
        self._all_type_aliases[reader_alias] = (f"{list_class_name}.Reader", "Reader")
        self._all_type_aliases[builder_alias] = (f"{list_class_name}.Builder", "Builder")

        # Generate class
        self._add_typing_import("Iterator")
        self._add_typing_import("overload")
        self._add_typing_import("override")

        # We need to add this to the ROOT scope
        root_scope = self.scope.root

        # Reader class
        root_scope.add(f"class {list_class_name}:")
        root_scope.add("    class Reader(_DynamicListReader):")
        root_scope.add("        @override")
        root_scope.add("        def __len__(self) -> int: ...")
        root_scope.add("        @override")
        root_scope.add(f"        def __getitem__(self, key: int) -> {reader_type}: ...")
        root_scope.add("        @override")
        root_scope.add(f"        def __iter__(self) -> Iterator[{reader_type}]: ...")

        # Builder class
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
            init_sig = ", ".join(init_args)
            root_scope.add("        @override")
            root_scope.add(f"        def init({init_sig}) -> {builder_type}: ...")

        root_scope.add("")

        return list_class_name, reader_alias, builder_alias

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
        hinted_variable: helper.TypeHintedVariable | None
        field_slot_type = field.slot.type.which()

        if field_slot_type == capnp_types.CapnpElementType.LIST:
            hinted_variable = self.gen_list_slot(field)
            # Track list fields for init() overloads
            if list_init_choices is not None and hinted_variable:
                # Get the Builder type for the list
                builder_type = hinted_variable.get_type_with_affixes(["Builder"])
                list_init_choices.append((helper.sanitize_name(field.name), builder_type))

        elif field_slot_type in capnp_types.CAPNP_TYPE_TO_PYTHON:
            hinted_variable = self.gen_python_type_slot(field, field_slot_type)

        elif field_slot_type == capnp_types.CapnpElementType.ENUM:
            hinted_variable = self.gen_enum_slot(field, raw_field.schema)

        elif field_slot_type == capnp_types.CapnpElementType.STRUCT:
            hinted_variable = self.gen_struct_slot(field, raw_field.schema, init_choices)

            # Try to use flat TypeAliases for Builder/Reader if available
            type_name = hinted_variable.primary_type_hint.name
            builder_alias = self._get_flat_builder_alias(type_name)
            reader_alias = self._get_flat_reader_alias(type_name)

            if builder_alias and reader_alias:
                # Use flat aliases with affix only for lookup (flat_alias=True prevents appending affix)
                hinted_variable.add_type_hint(helper.TypeHint(builder_alias, affix="Builder", flat_alias=True))
                hinted_variable.add_type_hint(helper.TypeHint(reader_alias, affix="Reader", flat_alias=True))
            else:
                # Fall back to scoped names with affixes (old behavior)
                hinted_variable.add_builder_from_primary_type()
                hinted_variable.add_reader_from_primary_type()

        elif field_slot_type == capnp_types.CapnpElementType.ANY_POINTER:
            hinted_variable = self.gen_any_pointer_slot(field)

        elif field_slot_type == capnp_types.CapnpElementType.INTERFACE:
            # Interfaces are represented as Protocols; expose attribute with Protocol type
            # Ensure the interface type has been generated
            with contextlib.suppress(Exception):  # pragma: no cover - best effort for incomplete imported schemas
                self.generate_nested(raw_field.schema)
            try:
                type_name = self.get_type_name(field.slot.type)
            except Exception:
                type_name = "Any"
                self._add_typing_import("Union")
            # For interfaces, type_name from get_type_name is now the Protocol name (_<Name>InterfaceModule)
            # E.g., "_HeartbeatInterfaceModule" or "Calculator._FunctionInterfaceModule"
            if type_name != "Any":
                # Protocol name is already in _<Name>InterfaceModule format
                protocol_type_name = type_name

                # Extract user-facing name and build nested Client reference
                # E.g., "_HeartbeatInterfaceModule" -> "_HeartbeatInterfaceModule.HeartbeatClient"
                # E.g., "Calculator._FunctionInterfaceModule" -> "Calculator._FunctionInterfaceModule.FunctionClient"
                parts = type_name.split(".")
                last_part = parts[-1]  # "_HeartbeatInterfaceModule"
                # Extract base name: "_HeartbeatInterfaceModule" -> "Heartbeat"
                if last_part.startswith("_"):
                    user_facing_name = self._extract_name_from_protocol(last_part)
                    client_type = f"{protocol_type_name}.{user_facing_name}Client"
                else:
                    # Fallback for edge cases
                    client_type = f"{protocol_type_name}Client"
            else:
                protocol_type_name = type_name
                client_type = type_name
            # For reading: return the Client type (capabilities are always clients at runtime)
            # For writing (in Builder): accept Client | Server
            hints = [helper.TypeHint(client_type, primary=True)]
            # Add Server as a non-primary hint for Builder setter (using Protocol name)
            hints.append(helper.TypeHint(f"{protocol_type_name}.Server"))
            hinted_variable = helper.TypeHintedVariable(helper.sanitize_name(field.name), hints)

        else:
            msg = f"Unknown field slot type {field_slot_type}."
            raise TypeError(msg)

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

    def gen_enum_slot(self, field: FieldReader, schema: capnp_types.SchemaType) -> helper.TypeHintedVariable:
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
        try:
            type_name = self.get_type_name(field.slot.type)
            return helper.TypeHintedVariable(
                helper.sanitize_name(field.name),
                [helper.TypeHint(type_name, primary=True)],
            )
        except (AttributeError, TypeError):
            # Fallback if we can't get enumerants
            return helper.TypeHintedVariable(
                helper.sanitize_name(field.name),
                [helper.TypeHint("int", primary=True), helper.TypeHint("str")],
            )

    def gen_struct_slot(
        self,
        field: FieldReader,
        schema: capnp_types.SchemaType,
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
            if imported is None and isinstance(schema, _StructSchema):
                _ = self.gen_struct(schema)

        type_name = self.get_type_name(field.slot.type)
        init_choices.append((helper.sanitize_name(field.name), type_name))
        hints = [helper.TypeHint(type_name, primary=True)]
        # If this is an interface type, also allow passing its Server implementation
        with contextlib.suppress(Exception):
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
        try:
            enum_parent_scope = self.scopes_by_id.get(schema.node.scopeId, self.scope.root)
        except KeyError:
            enum_parent_scope = self.scope

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
            logger.warning(f"Skipping generation of {type_name} - parent scope not available")
            return None, ""

        # Register type with the Protocol class name for correct scoped_name generation
        # The type's scoped_name will be used for all internal type references
        new_type = self.register_type(schema.node.id, schema, name=protocol_class_name)

        # Create context with auto-generated names
        # Pass the original type_name for TypeAlias generation
        context = StructGenerationContext.create_with_protocol(schema, type_name, protocol_class_name, new_type, [])

        return context, protocol_declaration

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
        group_type = self.gen_struct(raw_field.schema, type_name=group_name)
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
        """Generate Reader class nested inside the main struct Module.

        Args:
            context: The generation context
            fields_collection: The processed fields collection

        """
        # Build the Reader class declaration inheriting from _DynamicStructReader
        # Nested classes should NOT be Generic - they use TypeVars from parent scope
        reader_class_declaration = helper.new_class_declaration("Reader", parameters=["_DynamicStructReader"])

        # Add the class declaration to the current scope (the struct scope)
        self.scope.add(reader_class_declaration)

        # Create a new scope for the Reader Protocol, explicitly using current scope as parent
        _ = self.new_scope("Reader", context.schema.node, register=False, parent_scope=self.scope)

        # Use flat alias for as_builder return type
        builder_return_type = context.builder_type_name

        self._gen_struct_reader_class(
            fields_collection.slot_fields,
            builder_return_type,
            context.schema,
        )

        self.return_from_scope()

    def _generate_nested_builder_class(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Generate Builder class nested inside the main struct Module.

        Args:
            context: The generation context
            fields_collection: The processed fields collection

        """
        # Build the Builder class declaration inheriting from _DynamicStructBuilder
        # Nested classes should NOT be Generic - they use TypeVars from parent scope
        builder_class_declaration = helper.new_class_declaration("Builder", parameters=["_DynamicStructBuilder"])

        # Add the class declaration to the current scope (the struct scope)
        self.scope.add(builder_class_declaration)

        # Create a new scope for the Builder Protocol, explicitly using current scope as parent
        _ = self.new_scope("Builder", context.schema.node, register=False, parent_scope=self.scope)

        # Use flat aliases for return types
        reader_return_type = context.reader_type_name

        self._gen_struct_builder_class(
            fields_collection.slot_fields,
            fields_collection.init_choices,
            fields_collection.list_init_choices,
            reader_return_type,
            context.schema,
        )

        self.return_from_scope()

    def _generate_struct_classes(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
        protocol_declaration: str,
    ) -> None:
        """Generate _StructModule with nested Reader and Builder classes, plus TypeAlias declarations.

        This generates:
        1. The _<Name>StructModule class (inheriting from _StructModule) with nested Reader and Builder classes
        2. TypeAlias declarations for <Name>Reader and <Name>Builder
        3. For top-level structs: TypeAlias for <Name> pointing to the Module
        4. For nested structs: attribute annotation linking to the Module

        Args:
            context: Generation context with names and metadata
            fields_collection: Processed fields and init choices
            protocol_declaration: The Module class declaration string

        """
        protocol_class_name = f"_{context.type_name}StructModule"
        is_nested = self.scope.parent and not self.scope.parent.is_root

        # Add Protocol class declaration to parent scope
        if self.scope.parent:
            self.scope.parent.add(protocol_declaration)

        # Generate nested Reader Protocol first (inside the main struct Protocol)
        self._generate_nested_reader_class(context, fields_collection)

        # Generate nested Builder Protocol (inside the main struct Protocol)
        self._generate_nested_builder_class(context, fields_collection)

        # Use flat alias for new_message return type
        builder_return_type_for_base = context.builder_type_name

        # Generate base Protocol methods (static methods, to_dict, etc.)
        self._gen_struct_base_class(
            fields_collection.slot_fields,
            context.reader_type_name,
            builder_return_type_for_base,
        )

        self.return_from_scope()

        # After the Protocol is complete and we've returned to the parent scope,
        # add type alias declarations at this level ONLY for nested types
        # Top-level types get their type aliases at module level
        if is_nested:
            # Add aliases for Reader and Builder at current scope for nested types
            # Use type statement (PEP 695) for consistency
            # Use the registered type's scope to ensure it goes to the right place (parent scope)
            target_scope = context.new_type.scope or self.scope
            target_scope.add(f"type {context.reader_type_name} = {protocol_class_name}.Reader")
            target_scope.add(f"type {context.builder_type_name} = {protocol_class_name}.Builder")

        # Track for top-level TypeAliases (both nested and top-level)
        # Use scoped names which include the full path (e.g., "_PersonModule._PhoneNumberModule.Reader")
        self._all_type_aliases[context.reader_type_name] = (context.scoped_reader_type_name, "Reader")
        self._all_type_aliases[context.builder_type_name] = (context.scoped_builder_type_name, "Builder")

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
            try:
                return self.get_type_by_id(schema.node.id)
            except KeyError:
                # In the NoParentError case, we need to register and return
                if not type_name:
                    type_name = helper.get_display_name(schema)
                return self.register_type(schema.node.id, schema, name=type_name, scope=self.scope.root)

        # Register TypeAliases early so they're available during field processing
        # This handles self-referential fields and forward references
        self._all_type_aliases[context.reader_type_name] = (context.scoped_reader_type_name, "Reader")
        self._all_type_aliases[context.builder_type_name] = (context.scoped_builder_type_name, "Builder")

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

        # IMPORTANT: Ensure parent scope exists before registering this interface
        # For nested interfaces, the parent interface must be generated first
        parent_scope = self.scopes_by_id.get(schema.node.scopeId)
        if parent_scope is None:
            # Parent scope doesn't exist yet - need to generate the parent first
            # Find the parent schema and generate it
            parent_schema = self._schemas_by_id.get(schema.node.scopeId)
            if parent_schema and parent_schema.node.which() == capnp_types.CapnpElementType.INTERFACE:
                logger.debug(
                    f"Generating parent interface {parent_schema.node.displayName} before nested {schema.node.displayName}",
                )
                # Recursively generate the parent interface first
                # Try to get it as an interface schema from the loader
                try:
                    interface_schema = self._schema_loader.get(parent_schema.node.id)
                    if hasattr(interface_schema, "as_interface"):
                        _ = self.gen_interface(interface_schema.as_interface())
                    elif isinstance(interface_schema, _InterfaceSchema):
                        _ = self.gen_interface(interface_schema)
                except Exception as e:
                    logger.debug(f"Could not generate parent interface: {e}")
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
        return InterfaceGenerationContext.create(
            schema=schema,
            type_name=name,
            registered_type=registered_type,
            base_classes=base_classes,
            parent_scope=parent_scope,
        )

    def _enumerate_interface_methods(self, context: InterfaceGenerationContext) -> list[MethodInfo]:
        """Enumerate methods from runtime interface.

        Args:
            context: The interface generation context

        Returns:
            List of MethodInfo objects

        """
        try:
            # Use the schema directly from context instead of traversing runtime objects
            iface_schema = context.schema
            method_items = iface_schema.methods.items()

            return [MethodInfo.from_runtime_method(method_name, method) for method_name, method in method_items]
        except Exception as e:
            logger.debug(f"Could not enumerate methods for {context.type_name}: {e}")
            return []

    def _process_method_parameter(
        self,
        param_name: str,
        param_schema: _StructSchema,
    ) -> ParameterInfo | None:
        """Process a single method parameter and determine its types.

        Args:
            param_name: Name of the parameter
            param_schema: Schema containing the parameter

        Returns:
            ParameterInfo with client/server/request types, or None if not found

        """
        try:
            field_obj = next(f for f in param_schema.node.struct.fields if f.name == param_name)

            # Get base type
            base_type = self.get_type_name(field_obj.slot.type)

            # Determine client, server, and request types based on field type
            client_type = base_type
            server_type = base_type
            request_type = base_type

            field_type = field_obj.slot.type.which()

            # Handle ANY_POINTER: client receives DynamicObjectReader, server receives AnyPointer
            if field_type == capnp_types.CapnpElementType.ANY_POINTER:
                client_type = "AnyPointer"
                server_type = "AnyPointer"
                request_type = "AnyPointer"
                self._needs_anypointer_alias = True

            # Handle ENUM: use type alias
            # Enum values are integers at runtime, but RPC accepts string literals
            elif field_type == capnp_types.CapnpElementType.ENUM:
                # Get enum type to extract name
                try:
                    type_name = self.get_type_name(field_obj.slot.type)
                    client_type = type_name
                    server_type = type_name
                    request_type = type_name
                except Exception as e:
                    logger.debug(f"Could not proces enum type for {param_name}: {e}")
                    # Fallback
                    client_type = "int | str"
                    server_type = client_type
                    request_type = client_type

            # Handle STRUCT: use type aliases for client if defined locally, Reader for server, Builder for request
            elif field_type == capnp_types.CapnpElementType.STRUCT:
                reader_type = self._build_nested_reader_type(base_type)
                builder_type = self._build_nested_builder_type(base_type)
                # For client methods, try to use flat type aliases if defined in this module
                builder_alias = self._get_flat_builder_alias(base_type)
                reader_alias = self._get_flat_reader_alias(base_type)
                if builder_alias and reader_alias:
                    # Type is defined in this module, use flat aliases
                    client_type = f"{builder_alias} | {reader_alias} | dict[str, Any]"
                    server_type = reader_alias
                    request_type = builder_alias
                else:
                    # Type is imported, use the module type with dict union
                    client_type = f"{base_type} | dict[str, Any]"
                    server_type = reader_type
                    request_type = builder_type  # Request fields use Builder type

            # Handle LIST: use generated list aliases
            elif field_type == capnp_types.CapnpElementType.LIST:
                # Generate list class and get aliases
                _, reader_alias, builder_alias = self._generate_list_class(field_obj.slot.type)

                self._add_typing_import("Sequence")
                self._add_typing_import("Any")

                # Client accepts Builder, Reader, or Sequence (list/tuple)
                client_type = f"{builder_alias} | {reader_alias} | Sequence[Any]"

                # Server receives Reader
                server_type = reader_alias

                # Request builder accepts same as client
                request_type = client_type

            # Handle INTERFACE: use Client alias if available
            elif field_type == capnp_types.CapnpElementType.INTERFACE:
                # Extract interface name for the Client alias
                # base_type is like "_IdentifiableInterfaceModule" or "_ParentStructModule._NestedInterfaceModule"
                last_part = base_type.split(".")[-1]
                if last_part.startswith("_"):
                    interface_name = self._extract_name_from_protocol(last_part)
                    client_alias = f"{interface_name}Client"
                else:
                    client_alias = None

                if client_alias:
                    # Use the Client alias (either local or imported)
                    client_type = f"{client_alias} | {base_type}.Server"
                    server_type = client_alias
                else:
                    # Fallback to module type
                    client_type = f"{base_type} | {base_type}.Server"
                    server_type = base_type
                request_type = client_type

            return ParameterInfo(
                name=param_name,
                client_type=client_type,
                server_type=server_type,
                request_type=request_type,
            )

        except Exception as e:
            logger.debug(f"Could not process parameter {param_name}: {e}")
            return None

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

    def _get_client_type_name_from_interface_path(self, interface_path: str) -> str:
        """Extract client type name from interface path.

        E.g., "_HolderInterfaceModule" -> "HolderClient"
              "_CalculatorInterfaceModule._FunctionInterfaceModule" -> "FunctionClient"

        Args:
            interface_path: The full interface path

        Returns:
            The client type name

        """
        # Get the last component: "_HolderInterfaceModule" -> "_HolderInterfaceModule"
        last_component = interface_path.rsplit(".", maxsplit=1)[-1]
        # Remove "_" prefix and "Module" suffix: "_HolderInterfaceModule" -> "Holder"
        name = self._extract_name_from_protocol(last_component)
        # Add "Client" suffix: "Holder" -> "HolderClient"
        return f"{name}Client"

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
            with contextlib.suppress(Exception):
                field_obj = next(f for f in method_info.param_schema.node.struct.fields if f.name == param.name)

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
            with contextlib.suppress(Exception):
                field_obj = next(f for f in method_info.param_schema.node.struct.fields if f.name == param.name)

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
        result_type: str,
    ) -> list[str]:
        """Generate Request Protocol class for a method.

        Args:
            method_info: Information about the method
            parameters: List of processed parameters
            result_type: The return type for send()

        Returns:
            List of lines for the Request Protocol class

        """
        request_class_name = f"{helper.sanitize_name(method_info.method_name).title()}Request"
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
                        f'    def init(self, name: Literal["{field_name}"], '
                        f"size: int = ...) -> {list_builder_type}: ...",
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
        # For direct struct returns, generate a Protocol with the struct's fields
        if is_direct_struct_return:
            lines = []
            result_class_name = result_type

            # Class declaration - Protocol that is Awaitable and has result fields
            self._add_typing_import("Awaitable")
            lines.append(f"class {result_class_name}(Awaitable[{result_class_name}], Protocol):")

            # Check if the struct has a union (for which() method)
            has_union = False
            union_fields: list[str] = []

            # Add the struct's fields
            if method_info.result_schema is not None:
                # Check for union
                struct_node = method_info.result_schema.node.struct
                for field_obj in struct_node.fields:
                    if field_obj.discriminantValue != DISCRIMINANT_NONE:  # Field is part of a union
                        has_union = True
                        union_fields.append(field_obj.name)

                for rf in method_info.result_fields:
                    try:
                        field_obj = next(f for f in struct_node.fields if f.name == rf)
                        field_type = self.get_type_name(field_obj.slot.type)

                        # For struct types, accept both Builder and Reader in Result Protocol
                        field_type_enum = field_obj.slot.type.which()

                        # For AnyPointer: different types for client vs server
                        if field_type_enum == capnp_types.CapnpElementType.ANY_POINTER:
                            # Check if it's a specific kind of AnyPointer (e.g. Capability)
                            any_pointer_kind = "anyKind"
                            try:
                                if field_obj.slot.type.anyPointer.which() == "unconstrained":
                                    any_pointer_kind = field_obj.slot.type.anyPointer.unconstrained.which()
                            except (AttributeError, IndexError):
                                pass

                            if for_server:
                                # Server can set any Cap'n Proto type
                                if any_pointer_kind == "capability":
                                    field_type = "_DynamicCapabilityClient | _DynamicCapabilityServer"
                                else:
                                    field_type = "AnyPointer"
                                    self._needs_anypointer_alias = True
                            # Client receives specific type if known, else _DynamicObjectReader
                            elif any_pointer_kind == "capability":
                                field_type = "_DynamicCapabilityClient"
                            elif any_pointer_kind == "struct":
                                field_type = "_DynamicStructReader"
                            elif any_pointer_kind == "list":
                                field_type = "_DynamicListReader"
                            else:
                                field_type = "_DynamicObjectReader"
                        elif field_type_enum == capnp_types.CapnpElementType.STRUCT:
                            builder_type = self._build_nested_builder_type(field_type)
                            reader_type = self._build_nested_reader_type(field_type)
                            # For client methods, try to use flat type aliases if defined in this module
                            builder_alias = self._get_flat_builder_alias(field_type)
                            reader_alias = self._get_flat_reader_alias(field_type)

                            if not for_server:
                                # Client receives Reader only
                                field_type = reader_alias or reader_type
                            # Server returns Builder | Reader
                            elif builder_alias and reader_alias:
                                field_type = f"{builder_alias} | {reader_alias}"
                            else:
                                field_type = f"{builder_type} | {reader_type}"
                        elif field_type_enum == capnp_types.CapnpElementType.INTERFACE:
                            # For interface types, use the nested Client class
                            # field_type is Protocol name like "_ReaderInterfaceModule" or "_ChannelStructModule._ReaderInterfaceModule"
                            parts = field_type.split(".")
                            last_part = parts[-1]
                            if last_part.startswith("_"):
                                # Extract user-facing name: "_ReaderInterfaceModule" -> "Reader"
                                user_facing_name = self._extract_name_from_protocol(last_part)
                                client_type = f"{field_type}.{user_facing_name}Client"
                                server_type = f"{field_type}.Server"
                            else:
                                # Fallback
                                client_type = f"{field_type}Client"
                                # If field_type is "Registry", then "Registry.Server" might be valid if Registry is the module
                                # But usually field_type is the Protocol name
                                server_type = f"{field_type}.Server"

                            field_type = f"{server_type} | {client_type}" if for_server else client_type
                        elif field_type_enum == capnp_types.CapnpElementType.LIST:
                            # Generate list class and get aliases
                            _, reader_alias, builder_alias = self._generate_list_class(field_obj.slot.type)

                            field_type = reader_alias if not for_server else f"{builder_alias} | {reader_alias}"

                        lines.append(f"    {rf}: {field_type}")
                    except Exception:
                        lines.append(f"    {rf}: Any")

                # Add which() method if the struct has a union
                if has_union and union_fields:
                    self._add_typing_import("Literal")
                    union_literal = ", ".join([f'"{f}"' for f in union_fields])
                    lines.append(f"    def which(self) -> Literal[{union_literal}]: ...")

            return lines

        # For void methods, generate an empty Result Protocol that is just Awaitable[None]
        if not method_info.result_fields:
            lines: list[str] = []
            result_class_name = result_type
            self._add_typing_import("Awaitable")
            lines.append(f"class {result_class_name}(Awaitable[None], Protocol):")
            lines.append("    ...")  # Empty protocol body
            return lines

        # For single or multiple named fields, generate Result Protocol
        # This handles both `method() -> (field: Type)` and `method() -> (a: X, b: Y)`
        lines = []
        result_class_name = result_type

        # Class declaration
        if for_server:
            # Server results are builders (mutable), so they inherit from _DynamicStructBuilder
            # They are NOT Awaitable (context.results is not a promise)
            # They are NOT Protocols (they are concrete builder wrappers in this stub)
            lines.append(f"class {result_class_name}(_DynamicStructBuilder):")
        else:
            # Client results are promises (Awaitable) and Protocols
            self._add_typing_import("Awaitable")
            lines.append(f"class {result_class_name}(Awaitable[{result_class_name}], Protocol):")

        # Collect fields for init() method generation (server only)
        init_fields: list[tuple[str, str]] = []

        # Add result fields with Builder | Reader types for structs
        if method_info.result_schema is not None:
            for rf in method_info.result_fields:
                try:
                    field_obj = next(f for f in method_info.result_schema.node.struct.fields if f.name == rf)
                    field_type = self.get_type_name(field_obj.slot.type)

                    # For struct types, accept both Builder and Reader in Result Protocol
                    field_type_enum = field_obj.slot.type.which()

                    # Initialize variables to avoid unbound errors
                    builder_alias = None
                    reader_alias = None
                    builder_type = None
                    reader_type = None

                    # For AnyPointer: different types for client vs server
                    if field_type_enum == capnp_types.CapnpElementType.ANY_POINTER:
                        # Check if it's a specific kind of AnyPointer (e.g. Capability)
                        any_pointer_kind = "anyKind"
                        try:
                            if field_obj.slot.type.anyPointer.which() == "unconstrained":
                                any_pointer_kind = field_obj.slot.type.anyPointer.unconstrained.which()
                        except (AttributeError, IndexError):
                            pass

                        if for_server:
                            # Server can set any Cap'n Proto type
                            if any_pointer_kind == "capability":
                                field_type = "Capability"
                                self._needs_capability_alias = True
                            elif any_pointer_kind == "struct":
                                field_type = "AnyStruct"
                                self._needs_anystruct_alias = True
                            elif any_pointer_kind == "list":
                                field_type = "AnyList"
                                self._needs_anylist_alias = True
                            else:
                                field_type = "AnyPointer"
                                self._needs_anypointer_alias = True
                        # Client receives specific type if known, else _DynamicObjectReader
                        # Note: At runtime, pycapnp returns _DynamicObjectReader for AnyStruct and AnyList too
                        elif any_pointer_kind in {"capability", "struct", "list"}:
                            field_type = "_DynamicObjectReader"
                        else:
                            field_type = "_DynamicObjectReader"
                    elif field_type_enum == capnp_types.CapnpElementType.STRUCT:
                        builder_type = self._build_nested_builder_type(field_type)
                        reader_type = self._build_nested_reader_type(field_type)
                        # For client methods, try to use flat type aliases if defined in this module
                        builder_alias = self._get_flat_builder_alias(field_type)
                        reader_alias = self._get_flat_reader_alias(field_type)

                        if not for_server:
                            # Client receives Reader only
                            field_type = reader_alias or reader_type
                        # Server returns Builder | Reader
                        elif builder_alias and reader_alias:
                            field_type = f"{builder_alias} | {reader_alias}"
                            # Add to init fields
                            init_fields.append((rf, builder_alias))
                        else:
                            field_type = f"{builder_type} | {reader_type}"
                            # Add to init fields
                            init_fields.append((rf, builder_type))
                    elif field_type_enum == capnp_types.CapnpElementType.INTERFACE:
                        # For interface types, use the nested Client class
                        # field_type is Protocol name like "_ReaderInterfaceModule" or "_ChannelStructModule._ReaderInterfaceModule"
                        parts = field_type.split(".")
                        last_part = parts[-1]
                        if last_part.startswith("_"):
                            # Extract user-facing name: "_ReaderInterfaceModule" -> "Reader"
                            user_facing_name = self._extract_name_from_protocol(last_part)
                            client_type = f"{field_type}.{user_facing_name}Client"
                            server_type = f"{field_type}.Server"
                        else:
                            # Fallback
                            client_type = f"{field_type}Client"
                            server_type = f"{field_type}.Server"

                        field_type = f"{server_type} | {client_type}" if for_server else client_type
                    elif field_type_enum == capnp_types.CapnpElementType.LIST:
                        # Generate list class and get aliases
                        _, reader_alias, builder_alias = self._generate_list_class(field_obj.slot.type)

                        if not for_server:
                            # Client receives Reader only
                            field_type = reader_alias
                        else:
                            # Server returns Builder | Reader
                            field_type = f"{builder_alias} | {reader_alias}"
                            # Add to init fields
                            init_fields.append((rf, builder_alias))

                    if for_server:
                        # For server, generate properties with setters
                        # Getter returns Builder (or specific type)
                        # Setter accepts Builder | Reader | Sequence (for lists) | dict (for structs)

                        getter_type = field_type
                        setter_type = field_type

                        if field_type_enum == capnp_types.CapnpElementType.LIST:
                            # Getter returns Builder
                            getter_type = builder_alias
                            # Setter accepts Builder | Reader | Sequence
                            self._add_typing_import("Sequence")
                            self._add_typing_import("Any")
                            setter_type = f"{builder_alias} | {reader_alias} | Sequence[Any]"
                        elif field_type_enum == capnp_types.CapnpElementType.STRUCT:
                            # Getter returns Builder
                            # builder_alias might be None if not defined in this module
                            # builder_type is always defined for structs
                            b_type = builder_alias or builder_type
                            getter_type = b_type
                            # Setter accepts Builder | Reader | dict
                            self._add_typing_import("Any")
                            setter_type = f"{field_type} | dict[str, Any]"

                        lines.append("    @property")
                        lines.append(f"    def {rf}(self) -> {getter_type}: ...")
                        lines.append(f"    @{rf}.setter")
                        lines.append(f"    def {rf}(self, value: {setter_type}) -> None: ...")
                    else:
                        lines.append(f"    {rf}: {field_type}")
                except Exception as e:
                    logger.warning(f"Could not get field type for {rf}: {e}")
                    lines.append(f"    {rf}: Any")

            # Add init() methods for server results
            if for_server and init_fields:
                self._add_typing_import("overload")
                self._add_typing_import("Literal")
                self._add_typing_import("Any")

                for field_name, return_type in init_fields:
                    lines.append("    @overload")
                    lines.append(
                        f'    def init(self, field: Literal["{field_name}"], size: int | None = None) -> {return_type}: ...',
                    )

                # Catch-all init
                lines.append("    @overload")
                lines.append("    def init(self, field: str, size: int | None = None) -> Any: ...")

        return lines

    def _generate_request_helper_method(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
    ) -> list[str]:
        """Generate _request helper method for creating Request objects.

        Args:
            method_info: Information about the method
            parameters: List of processed parameters

        Returns:
            List of lines for the _request helper method

        """
        method_name = helper.sanitize_name(method_info.method_name)
        request_class_name = f"{method_name.title()}Request"

        # Scope the request class name to the interface
        # Request classes are nested in the interface module, so we need the interface path
        interface_path = self._get_scope_path()
        scoped_request_class = f"{interface_path}.{request_class_name}" if interface_path else request_class_name

        # Build parameter list (similar to client method)
        param_list = ["self"] + [p.to_request_param() for p in parameters]
        param_str = ", ".join(param_list)

        return [f"def {method_name}_request({param_str}) -> {scoped_request_class}: ..."]

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

        Gets the field names and their types for Server NamedTuple result types.
        For structs, accepts both Builder and Reader types.
        For AnyPointer, uses Any since servers can return any Python type.

        Args:
            method_info: Information about the method

        Returns:
            List of (field_name, field_type) tuples

        """
        fields: list[tuple[str, str]] = []

        if not method_info.result_fields or method_info.result_schema is None:
            return fields

        for field_name in method_info.result_fields:
            try:
                field_obj = next(f for f in method_info.result_schema.node.struct.fields if f.name == field_name)

                # Get base type
                field_type = self.get_type_name(field_obj.slot.type)

                # Check the field type
                field_type_enum = field_obj.slot.type.which()

                # For AnyPointer in server results, use Cap'n Proto type union
                # Server can return: Text (str), Data (bytes), Struct, Interface (client or server)
                if field_type_enum == capnp_types.CapnpElementType.ANY_POINTER:
                    # Check kind
                    any_pointer_kind = "anyKind"
                    try:
                        if field_obj.slot.type.anyPointer.which() == "unconstrained":
                            any_pointer_kind = field_obj.slot.type.anyPointer.unconstrained.which()
                    except (AttributeError, IndexError):
                        pass

                    if any_pointer_kind == "capability":
                        field_type = "Capability"
                        self._needs_capability_alias = True
                    elif any_pointer_kind == "struct":
                        field_type = "AnyStruct"
                        self._needs_anystruct_alias = True
                    elif any_pointer_kind == "list":
                        field_type = "AnyList"
                        self._needs_anylist_alias = True
                    else:
                        field_type = "AnyPointer"
                        self._needs_anypointer_alias = True
                # For structs, accept both Builder and Reader
                elif field_type_enum == capnp_types.CapnpElementType.STRUCT:
                    builder_type = self._build_nested_builder_type(field_type)
                    reader_type = self._build_nested_reader_type(field_type)
                    # For client methods, try to use flat type aliases if defined in this module
                    builder_alias = self._get_flat_builder_alias(field_type)
                    reader_alias = self._get_flat_reader_alias(field_type)

                    # NamedTuples are always for Server, so we use Builder | Reader
                    if builder_alias and reader_alias:
                        field_type = f"{builder_alias} | {reader_alias}"
                    else:
                        field_type = f"{builder_type} | {reader_type}"
                # For interfaces in NamedTuples, server returns Interface.Server
                elif field_type_enum == capnp_types.CapnpElementType.INTERFACE:
                    # For interface types, use the nested Client class
                    # field_type is Protocol name like "_ReaderInterfaceModule" or "_ChannelStructModule._ReaderInterfaceModule"
                    parts = field_type.split(".")
                    last_part = parts[-1]
                    if last_part.startswith("_"):
                        # Extract user-facing name: "_ReaderInterfaceModule" -> "Reader"
                        user_facing_name = self._extract_name_from_protocol(last_part)
                        client_type = f"{field_type}.{user_facing_name}Client"
                        server_type = f"{field_type}.Server"
                    else:
                        # Fallback
                        client_type = f"{field_type}Client"
                        server_type = f"{field_type}.Server"

                    # NamedTuples are always for Server, so we accept both Server and Client
                    field_type = f"{server_type} | {client_type}"

                elif field_type_enum == capnp_types.CapnpElementType.LIST:
                    # Generate list class and get aliases
                    _, reader_alias, builder_alias = self._generate_list_class(field_obj.slot.type)

                    # NamedTuples are always for Server, so we use Builder | Reader
                    field_type = f"{builder_alias} | {reader_alias}"

                # Sanitize field name to avoid conflicts with tuple methods
                sanitized_name = self._sanitize_namedtuple_field_name(field_name)
                fields.append((sanitized_name, field_type))

            except Exception as e:
                logger.debug(f"Could not get field type for {field_name}: {e}")
                continue

        return fields

    def _generate_server_method_signature(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
        result_type: str,
    ) -> str:
        """Generate server method signature for Server class.

        Server methods return NamedTuple results or None.
        - For void methods: return Awaitable[None]
        - For methods with results: return Awaitable[Server.XxxResult | None]

        Args:
            method_info: Information about the method
            parameters: List of processed parameters
            result_type: The result type (Result Protocol name)

        Returns:
            Single-line server method signature

        """
        method_name = helper.sanitize_name(method_info.method_name)

        # Generate CallContext type name - it's inside Server class
        scope_path = self._get_scope_path()
        context_class_name = f"{method_name.title()}CallContext"
        context_type = f"{scope_path}.Server.{context_class_name}" if scope_path else f"Server.{context_class_name}"

        # Server methods have: self, params..., _context: CallContext, **kwargs
        param_parts = ["self"]
        param_parts.extend([p.to_server_param() for p in parameters])
        param_parts.append(f"_context: {context_type}")
        param_parts.append("**kwargs: Any")
        param_str = ", ".join(param_parts)

        # Determine return type
        self._add_typing_import("Awaitable")
        self._add_typing_import("Any")

        if not method_info.result_fields:
            # Void method - returns Awaitable[None]
            return_type_str = "Awaitable[None]"
        else:
            # Check if this is a single primitive/interface return
            is_single_primitive_or_interface = False
            single_field_type = None

            if len(method_info.result_fields) == 1 and method_info.result_schema is not None:
                field_name = method_info.result_fields[0]
                with contextlib.suppress(Exception):
                    field_obj = next(f for f in method_info.result_schema.node.struct.fields if f.name == field_name)
                    field_type_enum = field_obj.slot.type.which()

                    # Check if it's a primitive or interface
                    # Primitives are returned as strings like "bool", "float64", etc.
                    # Interfaces are the INTERFACE constant
                    if field_type_enum in (
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
                    ):
                        # Primitive type
                        is_single_primitive_or_interface = True
                        single_field_type = self.get_type_name(field_obj.slot.type)
                    elif field_type_enum == capnp_types.CapnpElementType.INTERFACE:
                        # Interface type - server returns Interface.Server
                        is_single_primitive_or_interface = True
                        interface_type = self.get_type_name(field_obj.slot.type)
                        single_field_type = f"{interface_type}.Server"
                    elif field_type_enum == capnp_types.CapnpElementType.ENUM:
                        # Enum type - server returns Enum alias
                        is_single_primitive_or_interface = True
                        try:
                            single_field_type = self.get_type_name(field_obj.slot.type)
                        except Exception:
                            single_field_type = "int"
                    elif field_type_enum == capnp_types.CapnpElementType.STRUCT:
                        # Struct type - server returns Builder | Reader
                        is_single_primitive_or_interface = True
                        struct_type = self.get_type_name(field_obj.slot.type)
                        struct_builder = self._build_nested_builder_type(struct_type)
                        struct_reader = self._build_nested_reader_type(struct_type)

                        builder_alias = self._get_flat_builder_alias(struct_type)
                        reader_alias = self._get_flat_reader_alias(struct_type)

                        if builder_alias and reader_alias:
                            single_field_type = f"{builder_alias} | {reader_alias}"
                        else:
                            single_field_type = f"{struct_builder} | {struct_reader}"
                    elif field_type_enum == capnp_types.CapnpElementType.LIST:
                        # List type - server returns Sequence (list)
                        is_single_primitive_or_interface = True
                        single_field_type = self.get_type_name(field_obj.slot.type)

                        # If list of structs, use Builder | Reader for elements
                        element_type_obj = field_obj.slot.type.list.elementType
                        if element_type_obj.which() == capnp_types.CapnpElementType.STRUCT:
                            element_type_name = self.get_type_name(element_type_obj)
                            element_builder = self._build_nested_builder_type(element_type_name)
                            element_reader = self._build_nested_reader_type(element_type_name)

                            builder_alias = self._get_flat_builder_alias(element_type_name)
                            reader_alias = self._get_flat_reader_alias(element_type_name)

                            if builder_alias and reader_alias:
                                element_replacement = f"{builder_alias} | {reader_alias}"
                            else:
                                element_replacement = f"{element_builder} | {element_reader}"

                            single_field_type = single_field_type.replace(element_type_name, element_replacement)
                    elif field_type_enum == capnp_types.CapnpElementType.ANY_POINTER:
                        # AnyPointer type
                        is_single_primitive_or_interface = True
                        single_field_type = "AnyPointer"
                        self._needs_anypointer_alias = True

            # Generate return type - use NamedTuple with "Tuple" suffix
            full_server_path = f"{scope_path}.Server.{result_type}Tuple" if scope_path else f"Server.{result_type}Tuple"

            if is_single_primitive_or_interface and single_field_type:
                # For single primitive/interface: allow both the primitive/interface.Server and the NamedTuple
                return_type_str = f"Awaitable[{single_field_type} | {full_server_path} | None]"
            else:
                # For struct or multiple fields: return NamedTuple
                return_type_str = f"Awaitable[{full_server_path} | None]"

        return f"    def {method_name}({param_str}) -> {return_type_str}: ..."

    def _generate_server_context_method_signature(
        self,
        method_info: MethodInfo,
    ) -> str:
        """Generate server method signature with _context suffix.

        This is the alternative server method pattern where the method name ends in _context
        and receives only a context parameter (no individual params).

        Args:
            method_info: Information about the method

        Returns:
            Single-line server method signature with _context suffix

        """
        method_name = helper.sanitize_name(method_info.method_name)

        # Generate CallContext type name - it's inside Server class
        scope_path = self._get_scope_path()
        context_class_name = f"{method_name.title()}CallContext"
        context_type = f"{scope_path}.Server.{context_class_name}" if scope_path else f"Server.{context_class_name}"

        # _context variant only takes context parameter
        param_str = f"self, context: {context_type}"

        # _context methods can return promises but not direct values (other than None)
        self._add_typing_import("Awaitable")
        return_type_str = "Awaitable[None]"

        return f"    def {method_name}_context({param_str}) -> {return_type_str}: ..."

    def _generate_params_protocol(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
    ) -> list[str]:
        """Generate Params Protocol class for server context.

        Args:
            method_info: Information about the method
            parameters: List of processed parameters

        Returns:
            List of lines for the Params Protocol class

        """
        method_name = helper.sanitize_name(method_info.method_name)
        params_class_name = f"{method_name.title()}Params"

        lines = [helper.new_class_declaration(params_class_name, ["Protocol"])]

        for param in parameters:
            sanitized_name = helper.sanitize_name(param.name)
            lines.append(f"    {sanitized_name}: {param.server_type}")

        if not parameters:
            lines.append("    ...")

        return lines

    def _generate_callcontext_protocol(
        self,
        method_info: MethodInfo,
        *,
        has_results: bool,
        result_type_for_context: str | None = None,
        is_direct_struct_return: bool = False,
    ) -> list[str]:
        """Generate CallContext Protocol for server _context parameter.

        Args:
            method_info: Information about the method
            has_results: Whether the method has results
            result_type_for_context: Result type name (points to interface-level Protocol or struct name)
            is_direct_struct_return: Whether this is a direct struct return

        Returns:
            List of lines for CallContext Protocol

        """
        method_name = helper.sanitize_name(method_info.method_name)
        context_name = f"{method_name.title()}CallContext"

        lines = [helper.new_class_declaration(context_name, ["Protocol"])]

        scope_path = self._get_scope_path()

        # CallContext.params points to the Params Protocol (nested in Server class)
        params_type = f"{method_name.title()}Params"
        fully_qualified_params = f"{scope_path}.Server.{params_type}" if scope_path else f"Server.{params_type}"
        lines.append(f"    params: {fully_qualified_params}")

        # CallContext.results points to the Server Result Protocol (nested in Server class)
        # OR to the Builder type for direct struct returns
        if has_results:
            if is_direct_struct_return and result_type_for_context:
                # For direct struct returns, use the Builder type
                # result_type_for_context is the struct name (e.g. "IdInformation")
                builder_alias = self._get_flat_builder_alias(result_type_for_context)
                fully_qualified_results = builder_alias or self._build_scoped_builder_type(result_type_for_context)
            elif result_type_for_context:
                if scope_path:
                    # Use Server-nested Result Protocol: e.g., "_HolderModule.Server.ValueResult"
                    fully_qualified_results = f"{scope_path}.Server.{result_type_for_context}"
                else:
                    fully_qualified_results = f"Server.{result_type_for_context}"
            else:
                # Shouldn't happen, but fallback
                fully_qualified_results = "Any"

            # Make results a read-only property
            lines.append("    @property")
            lines.append(f"    def results(self) -> {fully_qualified_results}: ...")
        # Void methods have no results field in CallContext

        return lines

    def _process_interface_method(
        self,
        method_info: MethodInfo,
        server_collection: ServerMethodsCollection,
    ) -> MethodSignatureCollection:
        """Process a single interface method and generate all its components.

        This is the main processing method that coordinates all the sub-tasks.

        Args:
            method_info: Information about the method
            server_collection: Collection to add server method to

        Returns:
            MethodSignatureCollection with all generated components

        """
        collection = MethodSignatureCollection(method_info.method_name)

        # Process parameters
        parameters: list[ParameterInfo] = []
        for param_name in method_info.param_fields:
            if method_info.param_schema is not None:
                param_info = self._process_method_parameter(param_name, method_info.param_schema)
                if param_info:
                    parameters.append(param_info)

        # Process results
        result_type, is_direct_struct_return = self._process_method_results(method_info)

        # Determine scoping for result type in client methods:
        # Result classes are nested inside Client class
        scope_depth = len([s for s in self.scope.trace if not s.is_root])
        interface_path = self._get_scope_path()

        if scope_depth >= 1 and interface_path and result_type != "None":
            # Client methods return Client.ResultName (nested in Client class)
            # e.g., "_HolderModule.HolderClient.ValueResult"
            client_type_name = self._get_client_type_name_from_interface_path(interface_path)
            scoped_result_type = f"{interface_path}.{client_type_name}.{result_type}"
        else:
            # No interface scope (shouldn't happen for interface methods)
            scoped_result_type = result_type

        # Generate client method
        client_lines = self._generate_client_method(method_info, parameters, scoped_result_type)
        collection.set_client_method(client_lines)

        # Generate Request Protocol
        request_lines = self._generate_request_protocol(method_info, parameters, scoped_result_type)
        collection.set_request_class(request_lines)

        # Generate Client Result Protocol (will be nested in Client class)
        client_result_lines = self._generate_result_protocol(
            method_info,
            result_type,
            is_direct_struct_return=is_direct_struct_return,
            for_server=False,
        )
        collection.set_client_result_class(client_result_lines)

        # Generate Server Result Protocol (will be nested in Server class)
        server_result_lines = self._generate_result_protocol(
            method_info,
            result_type,
            is_direct_struct_return=is_direct_struct_return,
            for_server=True,
        )
        collection.set_server_result_class(server_result_lines)

        # Generate CallContext for server - points to Result Protocol at interface level
        # Also generate Params Protocol for CallContext.params
        params_lines = self._generate_params_protocol(method_info, parameters)
        for line in params_lines:
            collection.server_context_lines.append(line)

        if is_direct_struct_return:
            # Direct struct return: CallContext.results points to interface-level Result Protocol
            has_results = True

            # Get struct name for Builder type generation
            # Use get_type_by_id to ensure the type is generated and get its Protocol name
            # e.g. "_IdInformationStructModule"
            if method_info.result_schema is None:
                msg = "Result schema is None for direct struct return"
                raise ValueError(msg)

            struct_type = self.get_type_by_id(method_info.result_schema.node.id)
            struct_name = struct_type.scoped_name

            callcontext_lines = self._generate_callcontext_protocol(
                method_info,
                has_results=has_results,
                result_type_for_context=struct_name,
                is_direct_struct_return=True,
            )
            for line in callcontext_lines:
                collection.server_context_lines.append(line)
        else:
            # Named field return or void: CallContext.results points to Result Protocol
            has_results = bool(method_info.result_fields)
            # Pass result_type so CallContext can reference the Protocol
            result_type_for_ctx = f"{method_info.method_name.title()}Result" if has_results else None
            callcontext_lines = self._generate_callcontext_protocol(
                method_info,
                has_results=has_results,
                result_type_for_context=result_type_for_ctx,
                is_direct_struct_return=False,
            )
            for line in callcontext_lines:
                collection.server_context_lines.append(line)

        # Generate _request helper
        helper_lines = self._generate_request_helper_method(method_info, parameters)
        collection.set_request_helper(helper_lines)

        # Generate server method signature
        server_sig = self._generate_server_method_signature(method_info, parameters, result_type)
        server_collection.add_server_method(server_sig)

        # Generate server _context variant method signature
        server_context_sig = self._generate_server_context_method_signature(method_info)
        server_collection.add_server_method(server_context_sig)

        # Collect NamedTuple definition for server results with "Tuple" suffix
        if method_info.result_fields:
            result_fields_for_namedtuple = self._collect_result_fields_for_namedtuple(method_info)
            # Add "Tuple" suffix to distinguish from Protocol
            namedtuple_name = f"{result_type}Tuple"
            server_collection.add_namedtuple(namedtuple_name, result_fields_for_namedtuple)

        return collection

    def _generate_server_class(
        self,
        context: InterfaceGenerationContext,
        server_collection: ServerMethodsCollection,
        server_result_lines: list[str],
    ) -> None:
        """Generate the Server class with all server methods.

        Args:
            context: The interface generation context
            server_collection: Collection of server methods and NamedTuples
            server_result_lines: List of server Result protocol lines to add

        """
        # Build Server base classes (superclass Servers)
        server_base_classes: list[str] = []
        if context.schema.node.which() == "interface":
            interface_node = context.schema.node.interface
            for superclass in interface_node.superclasses:
                try:
                    superclass_type = self.get_type_by_id(superclass.id)
                    # superclass_type.name is now the Protocol name (e.g., "_IdentifiableInterfaceModule")
                    # Use it directly instead of adding another Module suffix
                    protocol_name = superclass_type.name
                    if superclass_type.scope and not superclass_type.scope.is_root:
                        server_base = f"{superclass_type.scope.scoped_name}.{protocol_name}.Server"
                    else:
                        server_base = f"{protocol_name}.Server"
                    server_base_classes.append(server_base)
                except KeyError:
                    logger.debug(f"Could not resolve superclass {superclass.id} for Server inheritance")

        # Only generate Server class if we have methods OR inheritance
        if not server_collection.has_methods() and not server_base_classes:
            return

        # Generate Server class declaration with inheritance
        if server_base_classes:
            server_declaration = helper.new_class_declaration("Server", server_base_classes)
        else:
            # Server inherits from _DynamicCapabilityServer
            server_declaration = helper.new_class_declaration("Server", ["_DynamicCapabilityServer"])

        self.scope.add(server_declaration)

        # Add Server Result protocols first (nested inside Server)
        for line in server_result_lines:
            self.scope.add(f"    {line}")
        if server_result_lines:
            self.scope.add("")

        # Add NamedTuple result types
        if server_collection.namedtuples:
            self._add_typing_import("NamedTuple")
            for result_type, fields in server_collection.namedtuples.items():
                # Generate NamedTuple class
                self.scope.add(f"    class {result_type}(NamedTuple):")
                if fields:
                    for field_name, field_type in fields:
                        self.scope.add(f"        {field_name}: {field_type}")
                else:
                    # Empty NamedTuple (void return)
                    self.scope.add("        pass")
            self.scope.add("")

        # Add context classes (CallContext and ResultsBuilder) inside Server class
        if server_collection.context_classes:
            # Update indentation for context classes to be inside Server
            for line in server_collection.context_classes:
                if line.startswith("class ") or line.strip():
                    self.scope.add(f"    {line}")
                else:
                    self.scope.add(line)
            self.scope.add("")

        # Add all server method signatures
        if server_collection.has_methods():
            for server_method in server_collection.server_methods:
                self.scope.add(server_method)
        else:
            # Empty server class (inherits everything from superclasses)
            self.scope.add("    ...")

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

        # Phase 1: Setup and registration
        context = self._setup_interface_generation(schema)
        if context is None:
            # Already imported
            return self.register_import(schema)

        # Track the interface's parent scope (may differ from current scope when generated lazily)
        type_alias_scope = context.parent_scope or self.scope

        # Add type alias import removed - using type statement now

        # Create interface module class declaration - use regular class (not Protocol)
        # Interface modules at runtime are _InterfaceModule instances, not Protocols
        if context.base_classes:
            # Inherit from parent interface modules only (they already inherit from _InterfaceModule)
            protocol_declaration = helper.new_class_declaration(context.protocol_class_name, context.base_classes)
        else:
            # No parent interfaces - inherit directly from _InterfaceModule
            protocol_declaration = helper.new_class_declaration(context.protocol_class_name, ["_InterfaceModule"])

        # Open interface Protocol scope
        _ = self.new_scope(
            context.protocol_class_name,
            context.schema.node,
            scope_heading=protocol_declaration,
        )

        # Phase 2: Generate nested types
        self._generate_nested_types_for_interface(context.schema)

        # Phase 3: Enumerate and process methods
        methods = self._enumerate_interface_methods(context)
        server_collection = ServerMethodsCollection()
        client_method_collection: list[str] = []  # Collect client methods for nested Client class
        request_helper_collection: list[str] = []  # Collect request helpers for Client class
        client_result_collection: list[str] = []  # Collect client Result protocols
        server_result_collection: list[str] = []  # Collect server Result protocols
        result_type_names: list[str] = []  # Collect result type names for top-level aliases

        for method_info in methods:
            method_collection = self._process_interface_method(method_info, server_collection)

            # Collect client methods and request helpers for Client class
            client_method_collection.extend(method_collection.client_method_lines)
            request_helper_collection.extend(method_collection.request_helper_lines)
            client_result_collection.extend(method_collection.client_result_lines)

            # Collect result type name for top-level type alias
            result_type_name = f"{helper.sanitize_name(method_info.method_name).title()}Result"
            result_type_names.append(result_type_name)

            # Add Request classes to interface Protocol (at module level)
            for line in method_collection.request_class_lines:
                self.scope.add(line)

            # Collect server Result protocols for Server class
            server_result_collection.extend(method_collection.server_result_lines)

            # Store context lines for Server class
            server_collection.add_context_lines(method_collection.server_context_lines)

        # Phase 3.5: Add _new_client class method to interface Protocol
        # Only add if Server class will be generated (has methods or inheritance)
        server_base_classes = self._collect_server_base_classes(context.schema)

        # Only add _new_client if Server class will exist
        if server_collection.has_methods() or server_base_classes:
            # _new_client returns nested Client class
            nested_client_name = f"{context.protocol_class_name}.{context.client_type_name}"
            self._add_new_client_method(context.type_name, client_return_type=nested_client_name)

        # Phase 4: Generate Server class inside interface Protocol
        self._generate_server_class(context, server_collection, server_result_collection)

        # Phase 5: Generate Client Protocol class INSIDE interface Protocol (not at parent level)
        should_generate_client = (
            server_collection.has_methods() or server_base_classes or client_method_collection or methods
        )

        if should_generate_client:
            self._generate_client_class_nested(
                context,
                client_method_collection,
                request_helper_collection,
                client_result_collection,
                server_base_classes,
            )

            # Track this interface for cast_as overloads with inheritance info
            # Store Protocol path (for parameter type) and Client TypeAlias (for return type)
            # Protocol path: e.g., "_CalculatorInterfaceModule" or "_CalculatorInterfaceModule._FunctionInterfaceModule"
            protocol_path = context.registered_type.scoped_name

            # Client TypeAlias: Use flat name (e.g., "FunctionClient" not "Calculator.FunctionClient")
            # The flat TypeAlias is available at module level for all interfaces
            # E.g., "CalculatorClient", "FunctionClient", "ValueClient"
            client_full_name = context.client_type_name  # This is already the flat name like "FunctionClient"

            # Build list of base client TypeAlias names (also flat)
            base_client_names: list[str] = []
            for server_base in server_base_classes:
                if ".Server" in server_base:
                    # Extract protocol name: _IdentifiableInterfaceModule.Server -> _IdentifiableInterfaceModule
                    protocol_name = server_base.replace(".Server", "")
                    # Get user-facing interface name from protocol name
                    interface_name = self._extract_name_from_protocol(protocol_name.split(".")[-1])
                    # Use flat Client TypeAlias name
                    base_client_names.append(f"{interface_name}Client")

            # Store: protocol_path -> (client_alias, base_clients)
            # e.g., "_CalculatorInterfaceModule._FunctionInterfaceModule" -> ("FunctionClient", [])
            self._all_interfaces[protocol_path] = (client_full_name, base_client_names)
            self._all_interfaces[protocol_path] = (client_full_name, base_client_names)

        # Track NamedTuples globally for .py file export
        if server_collection.namedtuples:
            interface_full_name = context.registered_type.scoped_name
            if interface_full_name not in self._all_server_namedtuples:
                self._all_server_namedtuples[interface_full_name] = {}

            for namedtuple_name, fields in server_collection.namedtuples.items():
                method_name = namedtuple_name.replace("ResultTuple", "Result").replace("Result", "").lower()
                if not method_name:
                    method_name = namedtuple_name.replace("Tuple", "").lower()

                self._all_server_namedtuples[interface_full_name][method_name] = (namedtuple_name, fields)

        # Ensure interface Protocol has some content
        if not self.scope.lines:
            self.scope.add("...")

        # Phase 6: Add type annotations and aliases at the recorded parent scope
        # Annotation for the interface module (better matches runtime behavior)
        type_alias_scope.add(f"{context.type_name}: {context.protocol_class_name}")

        # TypeAlias for the Client class (for convenience)
        if should_generate_client:
            # Check if this is a nested interface
            is_nested_interface = context.registered_type.scope and not context.registered_type.scope.is_root

            # Build full client path
            if is_nested_interface:
                # Use scoped name for nested interfaces (e.g., "_CalculatorModule._ValueModule.ValueClient")
                client_alias_path = f"{context.registered_type.scoped_name}.{context.client_type_name}"
            else:
                # Top-level interface
                client_alias_path = f"{context.protocol_class_name}.{context.client_type_name}"

            # Only add class-level type alias for nested interfaces
            if is_nested_interface:
                type_alias_scope.add(f"type {context.client_type_name} = {client_alias_path}")

            # Track for top-level TypeAlias (both nested and top-level)
            self._all_type_aliases[context.client_type_name] = (client_alias_path, "Client")

            # Track Result types for top-level TypeAliases
            for result_type_name in result_type_names:
                # Result types are nested inside Client class
                if is_nested_interface:
                    result_alias_path = (
                        f"{context.registered_type.scoped_name}.{context.client_type_name}.{result_type_name}"
                    )
                else:
                    result_alias_path = f"{context.protocol_class_name}.{context.client_type_name}.{result_type_name}"

                # Track for top-level TypeAlias
                self._all_type_aliases[result_type_name] = (result_alias_path, "Result")

        # Add TypeAlias for Server class if it exists
        should_generate_server = server_collection.has_methods() or server_base_classes
        if should_generate_server:
            server_alias_name = f"{context.type_name}Server"
            server_alias_path = f"{context.registered_type.scoped_name}.Server"

            # Only add class-level type alias for nested interfaces
            is_nested_interface = context.registered_type.scope and not context.registered_type.scope.is_root
            if is_nested_interface:
                type_alias_scope.add(f"type {server_alias_name} = {server_alias_path}")

            # Track for top-level TypeAlias
            self._all_type_aliases[server_alias_name] = (server_alias_path, "Server")

        # Return from the interface Protocol scope
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
                try:
                    superclass_type = self.get_type_by_id(superclass.id)
                    # superclass_type.name is now the Protocol name
                    protocol_name = superclass_type.name
                    if superclass_type.scope and not superclass_type.scope.is_root:
                        server_base = f"{superclass_type.scope.scoped_name}.{protocol_name}.Server"
                    else:
                        server_base = f"{protocol_name}.Server"
                    server_base_classes.append(server_base)
                except KeyError:
                    logger.debug(f"Could not resolve superclass {superclass.id} for Server inheritance")
        return server_base_classes

    def _generate_client_class_nested(
        self,
        context: InterfaceGenerationContext,
        client_method_lines: list[str],
        request_helper_lines: list[str],
        client_result_lines: list[str],
        server_base_classes: list[str],
    ) -> None:
        """Generate the Client Protocol class NESTED inside the interface Protocol.

        Args:
            context: The interface generation context
            client_method_lines: List of client method lines to add
            request_helper_lines: List of request helper method lines to add
            client_result_lines: List of client Result protocol lines to add
            server_base_classes: List of server base classes for inheritance resolution

        """
        # Build client base classes - inherit from superclass Clients
        client_base_classes: list[str] = []
        has_parent_clients = False
        for server_base in server_base_classes:
            # Extract protocol name from Server type and build Client type
            # e.g., "_IdentifiableInterfaceModule.Server" -> "_IdentifiableInterfaceModule.IdentifiableClient"
            if ".Server" in server_base:
                protocol_name = server_base.replace(".Server", "")
                # Extract interface name from protocol name: _IdentifiableInterfaceModule -> Identifiable
                interface_name = self._extract_name_from_protocol(protocol_name.split(".")[-1])
                client_base_classes.append(f"{protocol_name}.{interface_name}Client")
                has_parent_clients = True

        # Always inherit from _DynamicCapabilityClient as the base
        if not has_parent_clients:
            client_base_classes.insert(0, "_DynamicCapabilityClient")

        # Generate Client class declaration
        self.scope.add(helper.new_class_declaration(context.client_type_name, client_base_classes))

        # Add client Result protocols (nested inside Client)
        for line in client_result_lines:
            self.scope.add(f"    {line}")

        # Add client methods and request helpers with proper indentation
        all_method_lines = client_method_lines + request_helper_lines
        if all_method_lines:
            for line in all_method_lines:
                # Methods come without indentation, add class-level indentation
                self.scope.add(f"    {line}")
        elif not client_result_lines:
            # Empty client class (inherits everything from superclasses and has no Results)
            self.scope.add("    ...")

    def generate_nested(self, schema: capnp_types.SchemaType) -> None:
        """Generate the type for a nested schema.

        Args:
            schema (SchemaType): The schema to generate types for.
                Can be _StructSchema, _EnumSchema, _InterfaceSchema,
                _Schema, or a SchemaProxy wrapper.

        Raises:
            AssertionError: If the schema belongs to an unknown type.

        """
        if isinstance(schema, _EnumSchema):
            if not self.is_type_id_known(schema.node.id):
                _ = self.gen_enum(schema)
            return
        if isinstance(schema, _InterfaceSchema):
            if not self.is_type_id_known(schema.node.id):
                _ = self.gen_interface(schema)
            return
        if isinstance(schema, _StructSchema):
            if not self.is_type_id_known(schema.node.id):
                _ = self.gen_struct(schema)
            return

        # Generate based on node type
        if schema.node.which() == "const":
            if not self.is_type_id_known(schema.node.id):
                self.gen_const(schema)

        elif schema.node.which() == "struct":
            if not self.is_type_id_known(schema.node.id):
                _ = self.gen_struct(schema.as_struct())
        elif schema.node.which() == "enum":
            if not self.is_type_id_known(schema.node.id):
                _ = self.gen_enum(schema.as_enum())
        elif schema.node.which() == "interface":
            if not self.is_type_id_known(schema.node.id):
                _ = self.gen_interface(schema.as_interface())
        elif schema.node.which() == "file":
            # File nodes are skipped - they're just containers
            logger.debug(f"Skipping file node: {schema.node.displayName}")
            return
        else:
            # Unknown node type (annotation, etc.)
            logger.warning(f"Skipping unknown node type '{schema.node.which()}': {schema.node.displayName}")
            return

    def generate_all_nested(self) -> None:
        """Generate types for all nested nodes, recursively."""
        for node in self._schema.node.nestedNodes:
            try:
                nested_schema = self._schemas_by_id.get(node.id)
                if nested_schema:
                    self.generate_nested(nested_schema)
                else:
                    logger.debug(f"Could not find nested schema {node.name} (id={hex(node.id)}) in schema mapping")
            except Exception as e:
                # capnpc may omit unused nodes from imported schemas in the CodeGeneratorRequest.
                # This results in "no schema node loaded" errors when trying to access them.
                # These are harmless if the nodes are indeed unused, so we log as debug.
                logger.debug(f"Could not generate nested node '{node.name}': {e}")

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

        common_path: str
        matching_path: pathlib.Path | None = None

        # First check if this schema is in the file_id_to_path mapping
        if schema.node.id in self._file_id_to_path:
            matching_path = pathlib.Path(self._file_id_to_path[schema.node.id])
        else:
            # Find the path by checking which file contains this schema as a nested node
            def search_nested_nodes(schema_obj: _Schema, target_id: int) -> bool:
                """Recursively search for a target ID in nested nodes."""
                for nested_node in schema_obj.node.nestedNodes:
                    if nested_node.id == target_id:
                        return True
                    # Recursively search deeper by getting the nested schema from loader
                    with contextlib.suppress(Exception):
                        nested_schema = self._schema_loader.get(nested_node.id)
                        if search_nested_nodes(nested_schema, target_id):
                            return True
                return False

            for file_id, path in self._file_id_to_path.items():
                with contextlib.suppress(Exception):
                    file_schema = self._schema_loader.get(file_id)
                    if search_nested_nodes(file_schema, schema.node.id):
                        matching_path = pathlib.Path(path)
                        break

        # Since this is an import, there must be a parent module.
        assert matching_path is not None, f"The module named {module_name} was not provided to the stub generator."

        # Track this imported module path for later use in capnp.load imports
        self._imported_module_paths.add(matching_path)

        # Determine import path based on Python module annotations
        # If both current and imported schema have module annotations, use absolute imports
        # Otherwise use relative imports

        # Get the file schema ID for the imported file (not the nested type ID)
        # Find the file schema ID from file_id_to_path by matching the path
        imported_file_schema_id = None
        for file_id, file_path in self._file_id_to_path.items():
            if pathlib.Path(file_path) == matching_path:
                imported_file_schema_id = file_id
                break

        imported_module_annotation = None
        if imported_file_schema_id:
            imported_module_annotation = self.get_python_module_for_schema(imported_file_schema_id)

        if self._python_module_path and imported_module_annotation:
            # Both schemas have Python module annotations - use absolute imports
            # e.g., "from mas.schema.common.date_capnp import Date"
            module_name_without_extension = matching_path.stem  # e.g., "date"
            python_import_path = f"{imported_module_annotation}.{module_name_without_extension}_capnp"
        else:
            # No module annotations - need to build import path
            # For pycapnp 2.0+ with module folders, use absolute imports when possible
            # Check if both modules are in the same directory
            self_dir = self._module_path.parent
            import_dir = matching_path.parent

            if self_dir == import_dir:
                # Same directory - use absolute import (e.g., "from import_base_capnp import ...")
                module_name_without_extension = matching_path.stem
                python_import_path = f"{module_name_without_extension}_capnp"
            else:
                # Different directories - use relative imports
                # Find the relative path to go from the parent module, to this imported module.
                common_path = os.path.commonpath([self._module_path, matching_path])

                relative_module_path = self._module_path.relative_to(common_path)
                relative_import_path = matching_path.relative_to(common_path)

                # Shape the relative path to a relative Python import statement.
                # Since pycapnp 2.0+ generates stubs in module folders (e.g., schema_capnp/__init__.pyi),
                # we need an extra level to go up from __init__.pyi to its parent directory
                dots_count = len(relative_module_path.parents) + 1
                python_import_path = "." * dots_count + helper.replace_capnp_suffix(
                    ".".join(relative_import_path.parts),
                )

        # Import the regular definition name, alongside its builder and reader for structs
        # Enums and Interfaces don't have Builder/Reader variants
        # For deeply nested types (e.g., Params.Irrigation.Parameters), we import the root parent
        # and Python will resolve the full path via attribute access

        registered_name: str

        # Check if this is a nested type (contains dots)
        if "." in definition_name:
            # Get the root parent (e.g., "Params" from "Params.Irrigation.Parameters")
            root_name = definition_name.split(".")[0]

            if schema.node.which() == capnp_types.CapnpElementType.STRUCT:
                protocol_root_name = f"_{root_name}StructModule"
                self._add_import(f"from {python_import_path} import {protocol_root_name}")
                # Register with Protocol-based path: replace ALL struct names with Protocol names
                # E.g., "Params.OrganicFertilization.OrganicMatterParameters"
                # becomes "_ParamsStructModule._OrganicFertilizationStructModule._OrganicMatterParametersStructModule"
                parts = definition_name.split(".")
                protocol_parts = [f"_{part}StructModule" for part in parts]
                registered_name = ".".join(protocol_parts)
            elif schema.node.which() == capnp_types.CapnpElementType.INTERFACE:
                # For nested interfaces, register with Protocol name
                # E.g., "Channel.Reader" -> "Channel._ReaderInterfaceModule"
                parts = definition_name.split(".")
                last_part = parts[-1]
                parts[-1] = f"_{last_part}InterfaceModule"
                registered_name = ".".join(parts)
                self._add_import(f"from {python_import_path} import {root_name}")
            else:
                self._add_import(f"from {python_import_path} import {root_name}")
                registered_name = definition_name
        elif schema.node.which() == capnp_types.CapnpElementType.INTERFACE:
            # For interfaces, import the Protocol class, the TypeAlias, and the Client alias
            protocol_name = f"_{definition_name}InterfaceModule"
            client_name = f"{definition_name}Client"
            self._add_import(f"from {python_import_path} import {protocol_name}, {definition_name}, {client_name}")

            # Track imported aliases
            self._imported_aliases.add(client_name)
            registered_name = protocol_name
        elif schema.node.which() == capnp_types.CapnpElementType.ENUM:
            # Enums just need the enum itself
            alias_name = f"{definition_name}Enum"
            self._add_import(f"from {python_import_path} import {alias_name}")
            registered_name = alias_name
        else:
            # Structs: import the Protocol class (_<Name>StructModule) for internal type references
            # The TypeAlias can be accessed if needed, but internal references use the Protocol
            protocol_name = f"_{definition_name}StructModule"
            reader_alias = f"{definition_name}Reader"
            builder_alias = f"{definition_name}Builder"

            self._add_import(f"from {python_import_path} import {protocol_name}, {reader_alias}, {builder_alias}")

            # Track imported aliases
            self._imported_aliases.add(reader_alias)
            self._imported_aliases.add(builder_alias)
            registered_name = protocol_name

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

    def get_type_by_id(self, type_id: int) -> CapnpType:
        """Look up a type in the type registry, by means of its ID.

        Args:
            type_id (int): The identification number of the type.

        Raises:
            KeyError: If the type ID was not found in the registry.

        Returns:
            Type: The type, if it exists.

        """
        if self.is_type_id_known(type_id):
            return self.type_map[type_id]

        # Try to find the type in the schema ID mapping
        found_schema = self._schemas_by_id.get(type_id)
        if found_schema:
            # Found it!
            # If it's in the current module, generate it
            if self._is_schema_in_current_module(found_schema):
                self.generate_nested(found_schema)
            else:
                # If it's in another module, register it as an import
                _ = self.register_import(found_schema)

            if self.is_type_id_known(type_id):
                return self.type_map[type_id]

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
            try:
                parent_scope = self.scopes_by_id[node.scopeId]

            except KeyError as e:
                msg = f"The scope with name '{name}' has no parent."
                raise NoParentError(msg) from e

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
        logger.debug(f"  Looking for pattern: '{scope_heading_pattern}' in {len(self.scope.parent.lines)} parent lines")
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

    def get_type_name(self, type_reader: TypeReader) -> str:
        """Extract the type name from a type reader.

        The output type name is prepended by the scope name, if there is a parent scope.

        Args:
            type_reader (_DynamicStructReader ): The type reader to get the type name from.

        Returns:
            str: The extracted type name.

        """
        try:
            return capnp_types.CAPNP_TYPE_TO_PYTHON[type_reader.which()]

        except KeyError:
            pass

        type_reader_type = type_reader.which()

        element_type: CapnpType | None = None

        if type_reader_type == capnp_types.CapnpElementType.STRUCT:
            # Check if the type is registered; if not, try to generate it first
            type_id = type_reader.struct.typeId
            if not self.is_type_id_known(type_id):
                # Try to generate the struct before using it
                try:
                    # Look up the schema by ID in our mapping
                    if type_id in self._schemas_by_id:
                        nested_schema = self._schemas_by_id[type_id]
                        self.generate_nested(nested_schema)
                except Exception as e:
                    logger.debug(f"Could not pre-generate struct with ID {type_id}: {e}")

            element_type = self.get_type_by_id(type_id)
            type_name = element_type.name

        elif type_reader_type == capnp_types.CapnpElementType.ENUM:
            element_type = self.get_type_by_id(type_reader.enum.typeId)
            type_name = element_type.name

        elif type_reader_type == capnp_types.CapnpElementType.LIST:
            # Recursively get the element type and wrap it in Sequence
            element_type_name = self.get_type_name(type_reader.list.elementType)
            self._add_typing_import("Sequence")
            type_name = f"Sequence[{element_type_name}]"
            element_type = None  # List itself doesn't have an element_type in our registry

        elif type_reader_type == capnp_types.CapnpElementType.INTERFACE:
            type_id = type_reader.interface.typeId
            if not self.is_type_id_known(type_id):
                # Try to generate the interface before using it
                try:
                    # Look up the schema by ID in our mapping
                    if type_id in self._schemas_by_id:
                        nested_schema = self._schemas_by_id[type_id]
                        self.generate_nested(nested_schema)
                except Exception as e:
                    logger.debug(f"Could not pre-generate interface with ID {type_id}: {e}")

            element_type = self.get_type_by_id(type_id)
            type_name = element_type.name

            # Traverse down to the innermost nested list element.
            while type_name == capnp_types.CapnpElementType.LIST:
                type_name += type_reader.list.elementType.which()

        elif type_reader_type == capnp_types.CapnpElementType.ANY_POINTER:
            # AnyPointer becomes _DynamicObjectReader for better type safety
            # Track that we need augmentation for this module
            self._needs_dynamic_object_reader_augmentation = True
            type_name = "_DynamicObjectReader"
            element_type = None

        else:
            msg = f"Unknown type reader type '{type_reader_type}'."
            raise TypeError(msg)

        if element_type and (not element_type.scope.is_root):
            return f"{element_type.scope}.{type_name}"

        return type_name

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

        struct_types: list[tuple[str, str]] = []
        list_types: list[tuple[str, str]] = []
        interface_types: list[tuple[str, str]] = []

        # Track what we've already added to avoid duplicates
        seen_structs: set[str] = set()
        seen_lists: set[str] = set()
        seen_interfaces: set[str] = set()

        # Use _all_type_aliases which contains ONLY the types generated in this module
        for alias_name, alias_data in self._all_type_aliases.items():
            if len(alias_data) >= MIN_ALIAS_DATA_PARTS:
                original_path, _ = alias_data[0], alias_data[1]

                # For Reader types - could be struct or list
                if alias_name.endswith("Reader"):
                    # Check if it's a list (contains "List" in the name)
                    if "List" in alias_name:
                        # List type like "BoolListReader", "PersonListReader"
                        # original_path is like "_BoolList.Reader" or "_PersonList.Reader"
                        if ".Reader" in original_path:
                            list_class = original_path.replace(".Reader", "")
                            if list_class not in seen_lists:
                                list_types.append((list_class, alias_name))
                                seen_lists.add(list_class)
                    # Struct type
                    # original_path is like "_PersonStructModule.Reader"
                    elif ".Reader" in original_path:
                        protocol_path = original_path.replace(".Reader", "")
                        # Only include if it's a StructModule (not a List)
                        if "StructModule" in protocol_path and protocol_path not in seen_structs:
                            struct_types.append((protocol_path, alias_name))
                            seen_structs.add(protocol_path)

                # For Client types (interfaces)
                elif alias_name.endswith("Client") and "Client" in original_path:
                    parts = original_path.rsplit(".", 1)
                    if len(parts) == MODULE_PATH_PARTS:
                        protocol_path = parts[0]
                        # Only include InterfaceModule types
                        if "InterfaceModule" in protocol_path and protocol_path not in seen_interfaces:
                            interface_types.append((protocol_path, alias_name))
                            seen_interfaces.add(protocol_path)

        logger.debug(
            f"Module {self._schema.node.displayName}: Found {len(struct_types)} structs, {len(list_types)} lists, {len(interface_types)} interfaces",
        )

        return (struct_types, list_types, interface_types)

    def dumps_pyi(self) -> str:
        """Generate the .pyi stub output for this schema.

        Returns:
            str: The output string.

        """
        # Ensure we're at root scope before dumping
        if not self.scope.is_root:
            logger.warning(f"Scope not at root when dumping! name='{self.scope.name}', forcing return to root")
            # Force return to root
            while self.scope.return_scope is not None:
                self.scope = self.scope.return_scope

        out: list[str] = []
        out.append(self.docstring)
        out.extend(self.imports)

        # Add _DynamicObjectReader import if needed (for AnyPointer types)
        # We import the actual class from capnp.lib.capnp rather than generating a Protocol
        if self._needs_dynamic_object_reader_augmentation:
            out.append("from capnp.lib.capnp import _DynamicObjectReader")

        # Add AnyPointer type alias if needed (for generic parameter fields)
        if self._needs_anypointer_alias:
            out.append("")
            out.append("# Type alias for AnyPointer parameters (accepts all Cap'n Proto pointer types)")
            out.append(f"type AnyPointer = {ANYPOINTER_TYPE}")

        if self._needs_capability_alias:
            out.append("")
            out.append("# Type alias for Capability parameters")
            out.append(f"type Capability = {CAPABILITY_TYPE}")

        if self._needs_anystruct_alias:
            out.append("")
            out.append("# Type alias for AnyStruct parameters")
            out.append(f"type AnyStruct = {ANYSTRUCT_TYPE}")

        if self._needs_anylist_alias:
            out.append("")
            out.append("# Type alias for AnyList parameters")
            out.append(f"type AnyList = {ANYLIST_TYPE}")

        out.append("")

        if self.type_vars:
            out.extend(f'{name} = TypeVar("{name}")' for name in sorted(self.type_vars))
            out.append("")

        out.extend(self.scope.lines)

        # Add top-level TypeAliases for all Reader/Builder/Client types
        # For enums, add instance annotations instead of type aliases
        # This allows using these types in type annotations even though module types are now variables
        if self._all_type_aliases:
            out.append("")
            out.append("# Top-level type aliases for use in type annotations")
            for alias_name in sorted(self._all_type_aliases.keys()):
                alias_info = self._all_type_aliases[alias_name]

                if len(alias_info) == ENUM_ALIAS_DATA_PARTS:
                    # Enum with values: (full_path, type_kind, enum_values)
                    full_path, type_kind, enum_values = alias_info
                    if type_kind == "Enum":
                        # For enums, generate a single type alias that accepts int | Literal[...]
                        # This allows both Operator.add (int) and string literals to be accepted
                        literal_values = ", ".join(f'"{v}"' for v in enum_values)
                        out.append(f"type {alias_name} = int | Literal[{literal_values}]")
                    else:
                        # Regular type alias (use type statement for consistency)
                        out.append(f"type {alias_name} = {full_path}")
                else:
                    # Old format: (full_path, type_kind)
                    full_path, type_kind = alias_info
                    # All types use type alias now
                    out.append(f"type {alias_name} = {full_path}")

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
            for method in schema.node.interface.methods:
                param_schema = self._schemas_by_id.get(method.paramStructType)
                if param_schema is not None:
                    nested_segments = self._find_runtime_schema_access_segments(param_schema, target_id, seen)
                    if nested_segments is not None:
                        return [("methods", method.name), ("attr", "param_type"), *nested_segments]

                result_schema = self._schemas_by_id.get(method.resultStructType)
                if result_schema is not None:
                    nested_segments = self._find_runtime_schema_access_segments(result_schema, target_id, seen)
                    if nested_segments is not None:
                        return [("methods", method.name), ("attr", "result_type"), *nested_segments]

        if node_which == capnp_types.CapnpElementType.STRUCT:
            for field in schema.node.struct.fields:
                nested_segments = self._find_runtime_schema_access_segments_in_field(field, target_id, seen)
                if nested_segments is not None:
                    return nested_segments

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

            nested_segments = self._find_runtime_schema_access_segments(ancestor_schema, nested_schema.node.id)
            if nested_segments is None:
                continue

            expr = f"{ancestor_path}.schema"
            for segment_kind, segment_value in nested_segments:
                if segment_kind == "methods":
                    expr = f"{expr}.methods[{segment_value!r}]"
                elif segment_kind == "fields":
                    expr = f"{expr}.fields[{segment_value!r}]"
                elif segment_kind == "attr":
                    expr = f"{expr}.{segment_value}"
                elif segment_kind in {"schema", "elementType"}:
                    expr = f"{expr}.{segment_kind}"
            return expr

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

        constructor_by_type = {
            capnp_types.CapnpElementType.STRUCT: ("_StructModule", "as_struct"),
            capnp_types.CapnpElementType.INTERFACE: ("_InterfaceModule", "as_interface"),
            capnp_types.CapnpElementType.ENUM: ("_EnumModule", "as_enum"),
        }
        constructor_info = constructor_by_type.get(node_type)
        if constructor_info is None:
            return None

        module_constructor, cast_method = constructor_info
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

    def dumps_py(self) -> str:
        """Generate the .py loader module for this schema.

        The generated .py file embeds the .capnp source file, making it completely
        self-contained and independent of external .capnp files.

        Returns:
            str: The output string.

        """
        # Ensure we're at root scope before dumping
        if not self.scope.is_root:
            logger.warning(f"Scope not at root when dumping .py! name='{self.scope.name}', forcing return to root")
            # Force return to root
            while self.scope.return_scope is not None:
                self.scope = self.scope.return_scope

        out: list[str] = []
        out.append("# pyright: reportAttributeAccessIssue=false, reportArgumentType=false")
        out.append(self.docstring)
        out.append("")
        out.append("import base64")
        out.append("")
        out.append("import capnp")
        out.append("import schema_capnp")
        out.append("from capnp.lib.capnp import _EnumModule, _InterfaceModule, _StructModule")

        # Add NamedTuple import if we have server namedtuples
        if self._all_server_namedtuples:
            out.append("from typing import NamedTuple")

        out.append("")
        out.append("capnp.remove_import_hook()")
        out.append("")

        # Embed schemas as binary and manually build module structure
        # This replicates SchemaParser's behavior using SchemaLoader
        out.append("# Embedded compiled schemas (base64-encoded)")
        out.append("_SCHEMA_NODES = [")

        # Add root schema first
        root_bytes = self._schema.node.as_builder().to_bytes_packed()
        root_b64 = base64.b64encode(root_bytes).decode("ascii")
        out.append(f"    {root_b64!r},  # {self._schema.node.displayName}")

        # Add all other schemas from our mapping
        # We embed all schemas to ensure all dependencies are available at runtime.
        # Trying to track only "necessary" schemas is error-prone because schemas can reference
        # each other in complex ways (interface methods, const values, group fields, etc.)
        seen_ids = {self._schema.node.id}
        for schema_id, schema in self._schemas_by_id.items():
            if schema_id not in seen_ids:
                try:
                    schema_bytes = schema.node.as_builder().to_bytes_packed()
                    schema_b64 = base64.b64encode(schema_bytes).decode("ascii")
                    out.append(f"    {schema_b64!r},  # {schema.node.displayName}")
                    seen_ids.add(schema_id)
                except Exception as e:
                    logger.debug(f"Could not serialize schema {hex(schema_id)}: {e}")

        out.append("]")
        out.append("")

        # Load schemas and build module structure
        # Use a shared loader so capabilities work across schema modules
        out.append("# Load schemas and build module structure")
        out.append("# Use a shared loader stored on capnp module so capabilities work across schema modules")
        out.append("if not hasattr(capnp, '_embedded_schema_loader'):")
        out.append("    capnp._embedded_schema_loader = capnp.SchemaLoader()")
        out.append("_loader = capnp._embedded_schema_loader")
        out.append("for _schema_b64 in _SCHEMA_NODES:")
        out.append("    _schema_data = base64.b64decode(_schema_b64)")
        out.append("    _node_reader = schema_capnp.Node.from_bytes_packed(_schema_data)")
        out.append("    _loader.load_dynamic(_node_reader)")
        out.append("")

        # Build module structure inline by traversing the schema hierarchy
        # We build modules depth-first to ensure parents exist before children
        out.append("# Build module structure inline")
        out.append("")

        # Helper function to generate inline module construction code
        def generate_module_construction(
            schema_node: NodeReader,
            ancestor_schemas: list[tuple[str, object]],
            parent_path: str = "",
        ) -> None:
            """Generate code to construct a module and its nested modules."""
            # For each nested node in this schema
            for nested_node in schema_node.nestedNodes:
                nested_id = nested_node.id
                nested_name = nested_node.name

                # Skip nodes not in our schema mapping (shouldn't happen, but safe)
                if nested_id not in self._schemas_by_id:
                    continue

                nested_schema = self._schemas_by_id[nested_id]
                nested_node_proto = nested_schema.node

                # Determine the full path to this module
                full_path = f"{parent_path}.{nested_name}" if parent_path else nested_name

                construction_lines = self._build_runtime_module_construction_lines(
                    full_path=full_path,
                    nested_schema=nested_schema,
                    ancestor_schemas=ancestor_schemas,
                )
                if construction_lines is not None:
                    out.extend(construction_lines)

                # Recursively generate code for nested modules
                # Only structs and interfaces can have nested types
                node_type = nested_node_proto.which()
                if node_type in (capnp_types.CapnpElementType.STRUCT, capnp_types.CapnpElementType.INTERFACE):
                    generate_module_construction(
                        nested_node_proto,
                        [*ancestor_schemas, (full_path, nested_schema)],
                        full_path,
                    )

        # Start generating from the root schema
        generate_module_construction(self._schema.node, [])

        # Add Server.InfoResult NamedTuples for interfaces
        if self._all_server_namedtuples:
            out.append("")
            for interface_name, namedtuples_dict in sorted(self._all_server_namedtuples.items()):
                for _, (namedtuple_name, fields) in sorted(namedtuples_dict.items()):
                    # Convert Protocol path to runtime path
                    # E.g., "_HostPortResolverModule.Registrar" -> "HostPortResolver.Registrar"
                    runtime_interface_name = self._protocol_path_to_runtime_path(interface_name)

                    # Create NamedTuple and attach to Server class
                    # Use object as type for all fields to avoid import issues in .py file
                    # Type information is in the .pyi file for static type checkers
                    field_list = [f'("{field_name}", object)' for field_name, _ in fields]
                    out.append(
                        f"{runtime_interface_name}.Server.{namedtuple_name} = "
                        f"NamedTuple('{namedtuple_name}', [{', '.join(field_list)}])",
                    )

        return "\n".join(out)
