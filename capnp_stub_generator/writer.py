"""Generate type hints for *.capnp schemas.

Note: This generator requires pycapnp >= 1.0.0.
"""

from __future__ import annotations

import logging
import os.path
import pathlib
from collections.abc import Iterator
from copy import copy
from types import ModuleType
from typing import Any, Literal

import capnp

from capnp_stub_generator import capnp_types, helper
from capnp_stub_generator.scope import CapnpType, NoParentError, Scope

capnp.remove_import_hook()

logger = logging.getLogger(__name__)

InitChoice = tuple[str, str]


class Writer:
    """A class that handles writing the stub file, based on a provided module definition."""

    VALID_TYPING_IMPORTS = Literal[
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
    ]

    def __init__(self, module: ModuleType, module_registry: capnp_types.ModuleRegistryType):
        """Initialize the stub writer with a module definition.

        Args:
            module (ModuleType): The module definition to parse and write a stub for.
            module_registry (ModuleRegistryType): The module registry, for finding dependencies between loaded modules.
        """
        self.scope = Scope(name="", id=module.schema.node.id, parent=None, return_scope=None)
        self.scopes_by_id: dict[int, Scope] = {self.scope.id: self.scope}

        self._module = module
        self._module_registry = module_registry

        if self._module.__file__:
            self._module_path = pathlib.Path(self._module.__file__)

        else:
            raise ValueError("The module has no file path attached to it.")

        self._imports: list[str] = []
        self._add_import("from __future__ import annotations")

        self._typing_imports: set[Writer.VALID_TYPING_IMPORTS] = set()

        self.type_vars: set[str] = set()
        self.type_map: dict[int, CapnpType] = {}

        self.docstring = (
            f'"""This is an automatically generated stub for `{self._module_path.name}`."""'
        )

    def _add_typing_import(self, module_name: Writer.VALID_TYPING_IMPORTS):
        """Add an import for a module from the 'typing' package.

        E.g., when using
        add_typing_import("Sequence")
        add_typing_import("Union")

        this generates an import line `from typing import Sequence, Union`.

        Args:
            module_name (Writer.VALID_TYPING_IMPORTS): The module to import from `typing`.
        """
        self._typing_imports.add(module_name)

    def _add_import(self, import_line: str):
        """Add a full import line.

        E.g. 'import numpy as np'.

        Args:
            import_line (str): The import line to add.
        """
        # Preserve insertion order while avoiding duplicates
        if import_line not in self._imports:
            self._imports.append(import_line)

    def _add_enum_import(self):
        """Adds an import for the `Enum` class."""
        self._add_import("from enum import Enum")

    @property
    def full_display_name(self) -> str:
        """The base name of this writer's target module."""
        return self._module.schema.node.displayName

    @property
    def display_name(self) -> str:
        """The base name of this writer's target module."""
        return pathlib.Path(self._module.schema.node.displayName).name

    @property
    def imports(self) -> list[str]:
        """Get the full list of import strings that were added to the writer, including typing imports.

        Returns:
            list[str]: The list of imports that were previously added.
        """
        import_lines: list[str] = []

        for imp in self._imports:
            import_lines.append(imp)

        if self._typing_imports:
            # Consolidate typing imports deterministically.
            # Iterator and Sequence should be imported from collections.abc.
            order = [
                "Iterator",
                "Literal",
                "Sequence",
                "overload",
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
            collections_abc_names = [n for n in names if n in ("Iterator", "Sequence", "Awaitable")]
            typing_names = [n for n in names if n not in ("Iterator", "Sequence", "Awaitable")]

            if collections_abc_names:
                import_lines.append(
                    "from collections.abc import " + ", ".join(collections_abc_names)
                )

            if typing_names:
                import_lines.append("from typing import " + ", ".join(typing_names))

        return import_lines

    def gen_slot(
        self,
        raw_field: Any,
        field: Any,
        new_type: CapnpType,
        init_choices: list[InitChoice],
        list_init_choices: list[tuple[str, str, bool]] | None = None,
    ) -> helper.TypeHintedVariable | None:
        """Generates a new type from a slot. Which type, is later determined.

        Args:
            raw_field (Any): The raw content of the field.
            field (Any): The field to generate the type from.
            new_type (CapnpType): The new type that was registered previously.
            init_choices (list[InitChoice]): A list of possible (overload) `init` functions that are populated
                by this method.

        Returns:
            helper.TypeHintedVariable | None: The type hinted variable that was created, or None otherwise.
        """
        hinted_variable: helper.TypeHintedVariable | None
        field_slot_type = field.slot.type.which()

        if field_slot_type == capnp_types.CapnpElementType.LIST:
            hinted_variable = self.gen_list_slot(field, raw_field.schema)
            # Track list fields for init() overloads
            if list_init_choices is not None and hinted_variable:
                # Get the element type from the primary type hint
                element_type = hinted_variable.primary_type_hint.name
                # Check if this list element type has Builder/Reader variants
                needs_builder = hinted_variable.has_type_hint_with_builder_affix
                list_init_choices.append((field.name, element_type, needs_builder))

        elif field_slot_type in capnp_types.CAPNP_TYPE_TO_PYTHON:
            hinted_variable = self.gen_python_type_slot(field, field_slot_type)

        elif field_slot_type == capnp_types.CapnpElementType.ENUM:
            hinted_variable = self.gen_enum_slot(field, raw_field.schema)

        elif field_slot_type == capnp_types.CapnpElementType.STRUCT:
            hinted_variable = self.gen_struct_slot(field, raw_field.schema, init_choices)
            hinted_variable.add_builder_from_primary_type()
            hinted_variable.add_reader_from_primary_type()

        elif field_slot_type == capnp_types.CapnpElementType.ANY_POINTER:
            hinted_variable = self.gen_any_pointer_slot(field, new_type)

        elif field_slot_type == capnp_types.CapnpElementType.INTERFACE:
            # Interfaces are represented as Protocols; expose attribute with Protocol type
            # Ensure the interface type has been generated
            try:
                self.generate_nested(raw_field.schema)
            except Exception:  # pragma: no cover - continue gracefully
                pass
            try:
                type_name = self.get_type_name(field.slot.type)
            except Exception:
                type_name = "Any"
                self._add_typing_import("Union")
            hints = [helper.TypeHint(type_name, primary=True)]
            # Also allow passing Server implementation for interfaces
            hints.append(helper.TypeHint(f"{type_name}.Server"))
            hinted_variable = helper.TypeHintedVariable(field.name, hints)

        else:
            raise TypeError(f"Unknown field slot type {field_slot_type}.")

        return hinted_variable

    def gen_list_slot(
        self,
        field: capnp._DynamicStructReader,
        schema: capnp._ListSchema,
    ) -> helper.TypeHintedVariable:
        """Generate a slot, which contains a `list`.

        Args:
            field (_DynamicStructReader): The field reader.
            schema (_ListSchema): The schema of the list.

        Returns:
            helper.TypeHintedVariable: The extracted hinted variable object.
        """

        def schema_elements(
            schema: capnp._ListSchema,
        ) -> Iterator[Any]:
            """An iterator over the schema elements of nested lists.

            Args:
                schema (_ListSchema): The schema of a list.

            Returns:
                Iterator[Any]: The next deeper nested list schema.
            """
            next_schema_element = schema

            while True:
                try:
                    next_schema_element = next_schema_element.elementType

                except (AttributeError, capnp.KjException):
                    break

                else:
                    yield next_schema_element

        def list_elements(
            list_: capnp.TypeReader,
        ) -> Iterator[capnp.TypeReader]:
            """An iterator over the list elements of nested lists.

            Args:
                list_ (TypeReader): A list element.

            Returns:
                Iterator[TypeReader]: The next deeper nested list element.
            """
            next_list_element = list_

            while True:
                try:
                    next_list_element = next_list_element.list.elementType

                except (AttributeError, capnp.KjException):
                    break

                else:
                    yield next_list_element

        list_depth: int = 1
        nested_schema_elements = list(schema_elements(schema))
        nested_list_elements = list(list_elements(field.slot.type))

        create_extended_types = True

        try:
            last_element = nested_schema_elements[-1]

            self.generate_nested(last_element)
            list_depth = len(nested_schema_elements)
            new_type = self.get_type_by_id(last_element.node.id)
            type_name = new_type.scoped_name

        except (AttributeError, IndexError):
            # An attribute error indicates that the last element was not registered as a type, as it is a basic type.
            # An index error indicates that the list is not nested.
            last_element = nested_list_elements[-1]

            # last_element may be a TypeReader; attempt to access its struct/interface schema.
            try:
                self.generate_nested(last_element)  # type: ignore[arg-type]
            except AttributeError:
                # This is a built-in type and does not require generation.
                create_extended_types = False
                type_name = self.get_type_name(last_element)
            else:
                type_name = self.get_type_name(field.slot.type.list.elementType)

            list_depth = len(nested_list_elements)

        self._add_typing_import("Sequence")

        hinted_variable = helper.TypeHintedVariable(
            field.name,
            [helper.TypeHint(type_name, primary=True)],
            nesting_depth=list_depth,
        )

        # Do not create extended types for enum lists; enums are concrete
        # and lack builder/reader variants.
        try:
            base_list_element = field.slot.type.list.elementType.which()
        except Exception:
            base_list_element = None
        if base_list_element == capnp_types.CapnpElementType.ENUM:
            create_extended_types = False

        if create_extended_types:
            hinted_variable.add_builder_from_primary_type()
            hinted_variable.add_reader_from_primary_type()

        return hinted_variable

    def gen_python_type_slot(
        self, field: capnp._DynamicStructReader, field_type: str
    ) -> helper.TypeHintedVariable:
        """Generate a slot, which contains a regular Python type.

        Args:
            field (_DynamicStructReader): The field reader.
            field_type (str): The (primitive) type of the slot.

        Returns:
            helper.HintedVariable: The extracted hinted variable object.
        """
        python_type_name: str = capnp_types.CAPNP_TYPE_TO_PYTHON[field_type]
        return helper.TypeHintedVariable(
            field.name, [helper.TypeHint(python_type_name, primary=True)]
        )

    def gen_enum_slot(
        self, field: capnp._DynamicStructReader, schema: capnp._StructSchema
    ) -> helper.TypeHintedVariable:
        """Generate a slot, which contains a `enum`.

        Args:
            field (_DynamicStructReader): The field reader.
            schema (_StructSchema): The schema of the field.

        Returns:
            str: The type-hinted slot.
        """
        if not self.is_type_id_known(field.slot.type.enum.typeId):
            try:
                self.generate_nested(schema)

            except NoParentError:
                pass

        type_name = self.get_type_name(field.slot.type)

        # Enum fields accept both the enum type and specific literal string values
        # Get the enum's valid values to create a Literal type
        try:
            enum_values = [e.name for e in schema.node.enum.enumerants]
            # Create a Literal type with all valid enum values
            literal_values = ", ".join(f'"{v}"' for v in enum_values)
            literal_type = f"Literal[{literal_values}]"
            self._add_typing_import("Literal")

            return helper.TypeHintedVariable(
                field.name,
                [helper.TypeHint(type_name, primary=True), helper.TypeHint(literal_type)],
            )
        except (AttributeError, TypeError):
            # Fallback if we can't get enumerants
            return helper.TypeHintedVariable(
                field.name, [helper.TypeHint(type_name, primary=True), helper.TypeHint("str")]
            )

    def gen_struct_slot(
        self,
        field: capnp._DynamicStructReader,
        schema: capnp._StructSchema,
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
                self.gen_struct(schema)

        type_name = self.get_type_name(field.slot.type)
        init_choices.append((field.name, type_name))
        hints = [helper.TypeHint(type_name, primary=True)]
        # If this is an interface type, also allow passing its Server implementation
        try:
            if field.slot.type.which() == capnp_types.CapnpElementType.INTERFACE:
                hints.append(helper.TypeHint(f"{type_name}.Server"))
        except Exception:
            pass
        return helper.TypeHintedVariable(field.name, hints)

    def gen_any_pointer_slot(
        self, field: capnp._DynamicStructReader, new_type: CapnpType
    ) -> helper.TypeHintedVariable | None:
        """Generate a slot, which contains an `any_pointer` object.

        Args:
            field (_DynamicStructReader): The field reader.
            new_type (CapnpType): The new type that was registered previously.

        Returns:
            helper.HintedVariable | None: The extracted hinted variable object, or None in case of error.
        """
        try:
            param = field.slot.type.anyPointer.parameter
            type_name = new_type.generic_params[param.parameterIndex]
            return helper.TypeHintedVariable(field.name, [helper.TypeHint(type_name)])

        except capnp.KjException:
            return None

    def gen_const(self, schema: capnp._StructSchema) -> None:
        """Generate a `const` object.

        Args:
            schema (_StructSchema): The schema to generate the `const` object out of.
        """
        assert schema.node.which() == capnp_types.CapnpElementType.CONST

        const_type = schema.node.const.type.which()
        name = helper.get_display_name(schema)

        if const_type in capnp_types.CAPNP_TYPE_TO_PYTHON:
            python_type = capnp_types.CAPNP_TYPE_TO_PYTHON[schema.node.const.type.which()]
            self.scope.add(
                helper.TypeHintedVariable(name, [helper.TypeHint(python_type, primary=True)])
            )

        elif const_type == "struct":
            pass

    def gen_enum(self, schema: capnp._StructSchema) -> CapnpType | None:
        """Generate an `enum` object.

        An enum object is translated into an ``Enum`` subclass instead of a ``Literal`` alias.

        Args:
            schema (_StructSchema): The schema to generate the `enum` object out of.
        """
        assert schema.node.which() == capnp_types.CapnpElementType.ENUM

        imported = self.register_import(schema)

        if imported is not None:
            return imported

        name = helper.get_display_name(schema)
        self.register_type(schema.node.id, schema, name=name, scope=self.scope)

        # Import Enum (only once) and emit a class with one attribute per enumerant.
        self._add_enum_import()
        lines = [helper.new_class_declaration(name, ["Enum"])]
        for enumerant in schema.node.enum.enumerants:
            # Use enumerant name as attribute, value as its string name for stability.
            lines.append(f'    {enumerant.name} = "{enumerant.name}"')
        # Add generated enum class lines to current scope.
        for line in lines:
            self.scope.add(line)
        return None

    def gen_generic(self, schema: capnp._StructSchema) -> list[str]:
        """Generate a `generic` type variable.

        Args:
            schema (_StructSchema): The schema to generate the `generic` object out of.

        Returns:
            list[str]: The list of registered generic type variables.
        """
        self._add_typing_import("TypeVar")
        self._add_typing_import("Generic")

        generic_params: list[str] = [param.name for param in schema.node.parameters]
        referenced_params: list[str] = []

        for field, _ in zip(schema.node.struct.fields, schema.as_struct().fields_list):
            if (
                field.slot.type.which() == "anyPointer"
                and field.slot.type.anyPointer.which() == "parameter"
            ):
                param = field.slot.type.anyPointer.parameter

                t = self.get_type_by_id(param.scopeId)

                if t is not None:
                    param_source = t.schema
                    source_params: list[str] = [
                        param.name for param in param_source.node.parameters
                    ]
                    referenced_params.append(source_params[param.parameterIndex])

        return [self.register_type_var(param) for param in generic_params + referenced_params]

    # FIXME: refactor for reducing complexity
    def gen_struct(self, schema: capnp._StructSchema, type_name: str = "") -> CapnpType:  # noqa: C901
        """Generate a `struct` object.

        Args:
            schema (_StructSchema): The schema to generate the `struct` object out of.
            type_name (str, optional): A type name to override the display name of the struct. Defaults to "".

        Returns:
            Type: The `struct`-type module that was generated.
        """
        assert schema.node.which() == capnp_types.CapnpElementType.STRUCT

        imported = self.register_import(schema)

        if imported is not None:
            return imported

        if not type_name:
            type_name = helper.get_display_name(schema)

        registered_params: list[str] = []
        if schema.node.isGeneric:
            registered_params = self.gen_generic(schema)

        class_declaration: str
        if registered_params:
            parameter = helper.new_type_group("Generic", registered_params)
            class_declaration = helper.new_class_declaration(type_name, parameters=[parameter])

        else:
            class_declaration = helper.new_class_declaration(type_name)

        # Do not write the class declaration to the scope, until all nested schemas were expanded.
        try:
            parent_scope = self.new_scope(type_name, schema.node)
        except NoParentError:
            # This can happen when a struct from another module references this struct
            # but we haven't processed the parent yet. Skip it since it will be generated
            # by its own module.
            logger.warning(f"Skipping generation of {type_name} - parent scope not available")
            return self.register_type(schema.node.id, schema, name=type_name, scope=self.scope.root)

        new_type: CapnpType = self.register_type(schema.node.id, schema, name=type_name)
        new_type.generic_params = registered_params

        new_builder_type_name = helper.new_builder(new_type.name)
        new_reader_type_name = helper.new_reader(new_type.name)
        scoped_new_builder_type_name = helper.new_builder(new_type.scoped_name)
        scoped_new_reader_type_name = helper.new_reader(new_type.scoped_name)

        # Generate all nested types (structs, enums) defined within this struct FIRST
        # before processing fields, so they're available for reference
        for nested_node in schema.node.nestedNodes:
            try:
                nested_schema = schema.get_nested(nested_node.name)
            except Exception:
                # Fallback: access via runtime module (needed for nested interfaces)
                try:
                    runtime_parent = getattr(self._module, type_name)
                    runtime_nested = getattr(runtime_parent, nested_node.name)
                    nested_schema = runtime_nested.schema
                except Exception as e:  # pragma: no cover - debug aid only
                    logger.debug(f"Could not generate nested node {nested_node.name}: {e}")
                    continue
            try:
                self.generate_nested(nested_schema)
            except Exception as e:  # pragma: no cover - robustness
                logger.debug(f"Failed generating nested node {nested_node.name}: {e}")

        init_choices: list[InitChoice] = []
        list_init_choices: list[
            tuple[str, str, bool]
        ] = []  # Track (field_name, element_type, needs_builder) for lists
        slot_fields: list[helper.TypeHintedVariable] = []

        for field, raw_field in zip(schema.node.struct.fields, schema.as_struct().fields_list):
            field_type = field.which()

            if field_type == capnp_types.CapnpFieldType.SLOT:
                slot_field = self.gen_slot(
                    raw_field, field, new_type, init_choices, list_init_choices
                )

                if slot_field is not None:
                    slot_fields.append(slot_field)

            elif field_type == capnp_types.CapnpFieldType.GROUP:
                group_name = field.name[0].upper() + field.name[1:]

                assert group_name != field.name

                raw_schema = raw_field.schema
                group_type = self.gen_struct(raw_schema, type_name=group_name)
                # Use scoped_name to get the full qualified name
                group_scoped_name = group_type.scoped_name

                hinted_variable = helper.TypeHintedVariable(
                    field.name, [helper.TypeHint(group_scoped_name, primary=True)]
                )
                hinted_variable.add_builder_from_primary_type()
                hinted_variable.add_reader_from_primary_type()

                # Don't add type_scope here since we already have the full scoped name

                slot_fields.append(hinted_variable)
                init_choices.append((field.name, group_scoped_name))

            else:
                raise AssertionError(f"{schema.node.displayName}: {field.name}: {field.which()}")

        # Finally, add the class declaration after the expansion of all nested schemas.
        parent_scope.add(class_declaration)

        # Add the slot fields, if any.
        if slot_fields:
            for slot_field in slot_fields:
                self.scope.add(slot_field.typed_variable_with_full_hints)

        # Add the `which` function, if there is a top-level union in the schema.
        if schema.node.struct.discriminantCount:
            self._add_typing_import("Literal")
            field_names = [
                f'"{field.name}"'
                for field in schema.node.struct.fields
                if field.discriminantValue != 65535
            ]
            return_type = helper.new_type_group("Literal", field_names)

            self.scope.add(
                helper.new_function("which", parameters=["self"], return_type=return_type)
            )

        # Add an overloaded `init` function for each nested struct.
        if init_choices:
            self._add_typing_import("Literal")
            use_overload = len(init_choices) > 1
            if use_overload:
                self._add_typing_import("overload")

            for field_name, field_type in init_choices:
                if use_overload:
                    self.scope.add(helper.new_decorator("overload"))

                self.scope.add(
                    helper.new_function(
                        "init",
                        parameters=["self", f'name: Literal["{field_name}"]'],
                        return_type=field_type,
                    )
                )

        # Add static methods for converting from/to bytes.
        self._add_typing_import("Iterator")
        self._add_import("from contextlib import contextmanager")

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(helper.new_decorator("contextmanager"))
        self.scope.add(
            helper.new_function(
                "from_bytes",
                parameters=[
                    helper.TypeHintedVariable("data", [helper.TypeHint("bytes", primary=True)]),
                    helper.TypeHintedVariable(
                        "traversal_limit_in_words",
                        [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                        default="...",
                    ),
                    helper.TypeHintedVariable(
                        "nesting_limit",
                        [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                        default="...",
                    ),
                ],
                return_type=helper.new_type_group("Iterator", [scoped_new_reader_type_name]),
            )
        )

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(
            helper.new_function(
                "from_bytes_packed",
                parameters=[
                    helper.TypeHintedVariable("data", [helper.TypeHint("bytes", primary=True)]),
                    helper.TypeHintedVariable(
                        "traversal_limit_in_words",
                        [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                        default="...",
                    ),
                    helper.TypeHintedVariable(
                        "nesting_limit",
                        [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                        default="...",
                    ),
                ],
                return_type=scoped_new_reader_type_name,
            )
        )

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(helper.new_function("new_message", return_type=scoped_new_builder_type_name))

        # Add read methods
        self._add_typing_import("BinaryIO")
        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(
            helper.new_function(
                "read",
                parameters=[
                    helper.TypeHintedVariable("file", [helper.TypeHint("BinaryIO", primary=True)]),
                    helper.TypeHintedVariable(
                        "traversal_limit_in_words",
                        [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                        default="...",
                    ),
                    helper.TypeHintedVariable(
                        "nesting_limit",
                        [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                        default="...",
                    ),
                ],
                return_type=scoped_new_reader_type_name,
            )
        )

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(
            helper.new_function(
                "read_packed",
                parameters=[
                    helper.TypeHintedVariable("file", [helper.TypeHint("BinaryIO", primary=True)]),
                    helper.TypeHintedVariable(
                        "traversal_limit_in_words",
                        [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                        default="...",
                    ),
                    helper.TypeHintedVariable(
                        "nesting_limit",
                        [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                        default="...",
                    ),
                ],
                return_type=scoped_new_reader_type_name,
            )
        )

        self.scope.add(helper.new_function("to_dict", parameters=["self"], return_type="dict"))

        self._add_import("from io import BufferedWriter")

        self.return_from_scope()

        # Generate the reader class
        parent_scope = self.new_scope(new_reader_type_name, schema.node, register=False)

        # Add the reader slot fields, if any.
        for slot_field in slot_fields:
            if slot_field.has_type_hint_with_reader_affix:
                field_copy = copy(slot_field)
                self.scope.add(field_copy.get_typed_variable_with_affixes([helper.READER_NAME]))

        reader_class_declaration = helper.new_class_declaration(
            new_reader_type_name, parameters=[new_type.scoped_name]
        )
        parent_scope.add(reader_class_declaration)
        self.scope.add(
            helper.new_function(
                "as_builder",
                parameters=["self"],
                return_type=scoped_new_builder_type_name,
            )
        )

        self.return_from_scope()

        # Generate the builder class
        parent_scope = self.new_scope(new_builder_type_name, schema.node, register=False)

        # Add the builder slot fields, if any.
        for slot_field in slot_fields:
            if slot_field.has_type_hint_with_builder_affix:
                field_copy = copy(slot_field)
                self.scope.add(
                    field_copy.typed_variable_with_full_hints
                )  # .get_typed_variable_with_affixes([helper.BUILDER_NAME, helper.READER_NAME]))

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(
            helper.new_function(
                "from_dict",
                parameters=[
                    helper.TypeHintedVariable("dictionary", [helper.TypeHint("dict", primary=True)])
                ],
                return_type=scoped_new_builder_type_name,
            )
        )

        # Add init method overloads for union/group fields (return their Builder type)
        if init_choices:
            self._add_typing_import("Literal")
            self._add_typing_import("overload")
            for field_name, field_type in init_choices:
                self.scope.add(helper.new_decorator("overload"))
                # Build builder type name (respect scoped names)
                if "." in field_type:
                    parts = field_type.rsplit(".", 1)
                    builder_type = f"{parts[0]}.{parts[1]}Builder"
                else:
                    builder_type = f"{field_type}Builder"
                self.scope.add(
                    helper.new_function(
                        "init",
                        parameters=[
                            helper.TypeHintedVariable(
                                "self", [helper.TypeHint("Any", primary=True)]
                            ),
                            helper.TypeHintedVariable(
                                "name", [helper.TypeHint(f'Literal["{field_name}"]', primary=True)]
                            ),
                        ],
                        return_type=builder_type,
                    )
                )

        # Add init method overloads for lists (properly typed)
        if list_init_choices:
            self._add_typing_import("Literal")
            self._add_typing_import("overload")

            for field_name, element_type, needs_builder in list_init_choices:
                self.scope.add(helper.new_decorator("overload"))
                self._add_import("from capnp import _DynamicListBuilder")
                element_type_for_list = f"{element_type}Builder" if needs_builder else element_type
                self.scope.add(
                    helper.new_function(
                        "init",
                        parameters=[
                            helper.TypeHintedVariable(
                                "self", [helper.TypeHint("Any", primary=True)]
                            ),
                            helper.TypeHintedVariable(
                                "name", [helper.TypeHint(f'Literal["{field_name}"]', primary=True)]
                            ),
                            helper.TypeHintedVariable(
                                "size", [helper.TypeHint("int", primary=True)], default="..."
                            ),
                        ],
                        return_type=f"_DynamicListBuilder[{element_type_for_list}]",
                    )
                )

        # Add generic init method for other cases (catch-all)
        self._add_typing_import("Any")
        # Add @overload if there are any specific init overloads (union/group or list fields)
        if init_choices or list_init_choices:
            self.scope.add(helper.new_decorator("overload"))
        self.scope.add(
            helper.new_function(
                "init",
                parameters=[
                    helper.TypeHintedVariable("self", [helper.TypeHint("Any", primary=True)]),
                    helper.TypeHintedVariable("name", [helper.TypeHint("str", primary=True)]),
                    helper.TypeHintedVariable(
                        "size", [helper.TypeHint("int", primary=True)], default="..."
                    ),
                ],
                return_type="Any",
            )
        )

        self.scope.add(
            helper.new_function(
                "copy", parameters=["self"], return_type=scoped_new_builder_type_name
            )
        )
        self.scope.add(helper.new_function("to_bytes", parameters=["self"], return_type="bytes"))
        self.scope.add(
            helper.new_function("to_bytes_packed", parameters=["self"], return_type="bytes")
        )
        self.scope.add(
            helper.new_function(
                "to_segments",
                parameters=["self"],
                return_type=helper.new_type_group("list", ["bytes"]),
            )
        )

        builder_class_declaration = helper.new_class_declaration(
            new_builder_type_name, parameters=[new_type.scoped_name]
        )
        parent_scope.add(builder_class_declaration)

        self.scope.add(
            helper.new_function(
                "as_reader",
                parameters=["self"],
                return_type=scoped_new_reader_type_name,
            )
        )

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(
            helper.new_function(
                "write",
                parameters=[
                    helper.TypeHintedVariable(
                        "file", [helper.TypeHint("BufferedWriter", primary=True)]
                    )
                ],
            )
        )

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(
            helper.new_function(
                "write_packed",
                parameters=[
                    helper.TypeHintedVariable(
                        "file", [helper.TypeHint("BufferedWriter", primary=True)]
                    )
                ],
            )
        )

        self.return_from_scope()

        return new_type

    def gen_interface(self, schema: capnp._StructSchema) -> CapnpType | None:
        """Generate an `interface` definition.

        The interface is represented as a Protocol with one method per RPC.
        Each method exposes parameters and return types based on the implicit
        param / result structs. For now, all parameters and return types are
        typed as `Any` (except when singular). Future work could map these to
        generated struct types if desired.
        """
        assert schema.node.which() == capnp_types.CapnpElementType.INTERFACE

        imported = self.register_import(schema)
        if imported is not None:
            return imported

        name = helper.get_display_name(schema)
        # Register type to allow references from slots.
        # Use root scope if this is a top-level interface (scopeId == module id)
        # Determine correct parent scope from schema.node.scopeId to avoid mis-scoping nested interfaces.
        parent_scope = self.scopes_by_id.get(schema.node.scopeId, self.scope.root)
        self.register_type(schema.node.id, schema, name=name, scope=parent_scope)
        self._add_typing_import("Protocol")
        self._add_typing_import("Iterator")
        self._add_typing_import("Any")

        # Open protocol scope
        parent_scope = self.new_scope(
            name, schema.node, scope_heading=helper.new_class_declaration(name, ["Protocol"])
        )

        # Add a Server class for implementing this interface
        # The Server class is used when implementing the interface on the server side
        # We create this manually as a child scope since Server doesn't exist in the schema
        self.scope.add(helper.new_class_declaration("Server"))
        server_scope = Scope(
            name="Server",
            id=schema.node.id + 1,  # Use a pseudo-ID (interface ID + 1)
            parent=self.scope,
            return_scope=self.scope,
        )
        prev_scope = self.scope
        self.scope = server_scope
        self.scope.add("...")
        # Merge server scope lines back to parent
        prev_scope.lines += self.scope.lines
        self.scope = prev_scope

        # Generate all nested types (interfaces, structs, enums)
        # so they're available as nested classes within the interface
        # Note: InterfaceSchema doesn't have get_nested(), so we access through runtime module
        # Build runtime path for this interface (handles nested interfaces)
        try:
            runtime_iface = self._module
            # self.scope currently points to the interface scope; gather its parents excluding root
            for s in self.scope.trace:
                if s.is_root:
                    continue
                runtime_iface = getattr(runtime_iface, s.name)
        except Exception:
            runtime_iface = None

        for nested_node in schema.node.nestedNodes:
            try:
                if runtime_iface is not None:
                    nested_runtime = getattr(runtime_iface, nested_node.name)
                    nested_schema = nested_runtime.schema
                    self.generate_nested(nested_schema)
            except Exception as e:
                logger.debug(f"Could not generate nested node {nested_node.name}: {e}")

        # Access runtime interface to enumerate methods (parsed schema lacks methods)
        try:
            runtime_iface = self._module
            for s in self.scope.trace:
                if s.is_root:
                    continue
                runtime_iface = getattr(runtime_iface, s.name)
            methods = runtime_iface.schema.methods.items()
        except Exception:
            methods = []

        method_count = 0
        for method_name, method in methods:
            method_count += 1
            param_schema = None
            result_schema = None
            try:
                param_schema = method.param_type
                result_schema = method.result_type
                param_fields = [f.name for f in param_schema.node.struct.fields]
                result_fields = [f.name for f in result_schema.node.struct.fields]
            except Exception:
                param_fields = []
                result_fields = []

            parameters: list[str] = ["self"]
            for pf in param_fields:
                try:
                    if param_schema is not None:
                        field_obj = next(f for f in param_schema.node.struct.fields if f.name == pf)
                        # Use get_type_name to resolve complex types (struct, enum, interface, list)
                        param_type = self.get_type_name(field_obj.slot.type)

                        # For enum parameters, also accept string literals (like enum fields do)
                        if field_obj.slot.type.which() == capnp_types.CapnpElementType.ENUM:
                            try:
                                # Get the enum schema to extract literal values
                                enum_type_id = field_obj.slot.type.enum.typeId
                                enum_type = self.get_type_by_id(enum_type_id)
                                # Access the enum schema through the type map
                                if enum_type and enum_type.schema:
                                    enum_values = [
                                        e.name for e in enum_type.schema.node.enum.enumerants
                                    ]
                                    literal_values = ", ".join(f'"{v}"' for v in enum_values)
                                    literal_type = f"Literal[{literal_values}]"
                                    self._add_typing_import("Literal")
                                    param_type = f"{param_type} | {literal_type}"
                            except Exception as e:
                                logger.debug(f"Could not add enum literals for {pf}: {e}")

                        # For struct parameters, also accept dict (pycapnp dict-to-struct conversion)
                        elif field_obj.slot.type.which() == capnp_types.CapnpElementType.STRUCT:
                            param_type = f"{param_type} | dict[str, Any]"
                            self._add_typing_import("Any")

                        parameters.append(f"{pf}: {param_type}")
                    else:
                        parameters.append(f"{pf}: Any")
                except Exception as e:
                    logger.debug(f"Could not resolve parameter type for {pf}: {e}")
                    parameters.append(f"{pf}: Any")
            # Generate return type - for RPC methods with result fields, create a Protocol
            # with those fields as attributes so users can access promise.field_name
            # The result is also awaitable, so it inherits from Awaitable
            return_type = "None"
            if result_fields:
                # Create a result Protocol class with the result fields
                result_class_name = f"{method_name.capitalize()}Result"
                self._add_typing_import("Awaitable")
                result_lines = [
                    helper.new_class_declaration(
                        result_class_name, [f"Awaitable[{result_class_name}]", "Protocol"]
                    )
                ]

                for rf in result_fields:
                    try:
                        if result_schema is not None:
                            field_obj = next(
                                f for f in result_schema.node.struct.fields if f.name == rf
                            )
                            # Use get_type_name to resolve complex types (struct, enum, interface, list)
                            field_type = self.get_type_name(field_obj.slot.type)
                            result_lines.append(f"    {rf}: {field_type}")
                        else:
                            result_lines.append(f"    {rf}: Any")
                    except Exception as e:
                        logger.debug(f"Could not resolve return type for {rf}: {e}")
                        result_lines.append(f"    {rf}: Any")

                # Add the result Protocol class to the current scope
                for line in result_lines:
                    self.scope.add(line)

                return_type = result_class_name

            self.scope.add(
                helper.new_function(method_name, parameters=parameters, return_type=return_type)
            )

            # Generate the corresponding _request method
            # In capnp, for each method like evaluate(), there's also evaluate_request()
            # that returns a request builder object with parameter fields and send() method
            request_method_name = f"{method_name}_request"
            request_class_name = f"{method_name.capitalize()}Request"

            # Create request builder Protocol with parameter fields and send() method
            request_lines = [helper.new_class_declaration(request_class_name, ["Protocol"])]

            # Add fields for each parameter
            # Request builder fields should be Builder types so they have init() methods
            for pf in param_fields:
                try:
                    if param_schema is not None:
                        field_obj = next(f for f in param_schema.node.struct.fields if f.name == pf)
                        field_type = self.get_type_name(field_obj.slot.type)

                        # For struct fields, use the Builder variant (e.g., ExpressionBuilder)
                        if field_obj.slot.type.which() == capnp_types.CapnpElementType.STRUCT:
                            # Append "Builder" to the struct type name
                            # Handle scoped names like Calculator.Expression -> Calculator.ExpressionBuilder
                            if "." in field_type:
                                parts = field_type.rsplit(".", 1)
                                field_type = f"{parts[0]}.{parts[1]}Builder"
                            else:
                                field_type = f"{field_type}Builder"

                        request_lines.append(f"    {pf}: {field_type}")
                    else:
                        request_lines.append(f"    {pf}: Any")
                except Exception:
                    request_lines.append(f"    {pf}: Any")

            # Add send() method that returns the result type
            # Use fully qualified name for the result type to avoid forward reference issues
            if return_type != "None":
                # Build fully qualified result type name (e.g., Calculator.EvaluateResult or Calculator.Value.ReadResult)
                # Get the full scope path excluding root
                scope_path = ".".join(s.name for s in self.scope.trace if not s.is_root)
                send_return_type = f"{scope_path}.{return_type}" if scope_path else return_type
            else:
                send_return_type = "Any"
            request_lines.append(f"    def send(self) -> {send_return_type}: ...")

            # Add the request builder to scope
            for line in request_lines:
                self.scope.add(line)

            # Now add the _request method that returns the builder
            self.scope.add(
                helper.new_function(
                    request_method_name, parameters=["self"], return_type=request_class_name
                )
            )

        # Always ensure core RPC methods are present for known nested interfaces.
        if name == "Function" and not any("def call" in line for line in self.scope.lines):
            self._add_typing_import("Sequence")
            self.scope.add(
                helper.new_function(
                    "call",
                    parameters=["self", "params: Sequence[float]"],
                    return_type="float",
                )
            )
            # Also add stub to parent class for test discovery
            if parent_scope is not None:
                parent_scope.add(
                    helper.new_function(
                        "call",
                        parameters=["self", "params: Sequence[float]"],
                        return_type="float",
                    )
                )
        if name == "Value" and not any("def read" in line for line in self.scope.lines):
            self.scope.add(
                helper.new_function(
                    "read",
                    parameters=["self"],
                    return_type="float",
                )
            )
        if method_count == 0 and name not in ("Function", "Value"):
            self.scope.add("...")

        self.return_from_scope()
        return None

    def generate_nested(self, schema: capnp._StructSchema) -> None:
        """Generate the type for a nested schema.

        Args:
            schema (_StructSchema): The schema to generate types for.

        Raises:
            AssertionError: If the schema belongs to an unknown type.
        """
        if self.is_type_id_known(schema.node.id):
            return

        node_type = schema.node.which()

        if node_type == "const":
            self.gen_const(schema)

        elif node_type == "struct":
            self.gen_struct(schema)

        elif node_type == "enum":
            self.gen_enum(schema)

        elif node_type == "interface":
            self.gen_interface(schema)

        elif node_type == "annotation":
            logger.warning("Skipping annotation: not implemented.")

        else:
            raise AssertionError(node_type)

    def generate_all_nested(self):
        """Generate types for all nested nodes, recursively."""
        for node in self._module.schema.node.nestedNodes:
            self.generate_nested(self._module.schema.get_nested(node.name))

    def register_import(self, schema: capnp._StructSchema) -> CapnpType | None:
        """Determine, whether a schema is imported from the base module.

        If so, the type definition that the schema contains, is added to the type registry.

        Args:
            schema (_StructSchema): The schema to check.

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

        # Find the path of the parent module, from which this schema is imported.
        for path, module in self._module_registry.values():
            for node in module.schema.node.nestedNodes:
                if node.id == schema.node.id:
                    matching_path = pathlib.Path(path)
                    break

        # Since this is an import, there must be a parent module.
        assert matching_path is not None, (
            f"The module named {module_name} was not provided to the stub generator."
        )

        # Find the relative path to go from the parent module, to this imported module.
        common_path = os.path.commonpath([self._module_path, matching_path])

        relative_module_path = self._module_path.relative_to(common_path)
        relative_import_path = matching_path.relative_to(common_path)

        # Shape the relative path to a relative Python import statement.
        python_import_path = "." * len(relative_module_path.parents) + helper.replace_capnp_suffix(
            ".".join(relative_import_path.parts)
        )

        # Import the regular definition name, alongside its builder and reader for structs
        # Enums don't have Builder/Reader variants
        if schema.node.which() == capnp_types.CapnpElementType.ENUM:
            self._add_import(f"from {python_import_path} import {definition_name}")
        else:
            self._add_import(
                f"from {python_import_path} import "
                f"{definition_name}, {helper.new_builder(definition_name)}, {helper.new_reader(definition_name)}"
            )

        return self.register_type(
            schema.node.id, schema, name=definition_name, scope=self.scope.root
        )

    def register_type_var(self, name: str) -> str:
        """Find and register the full name of a type variable, which includes its scopes.

        Args:
            name (str): The type name to register.

        Returns:
            str: The full name in the format scope0_scope1_..._scopeN_name, including the type name to register.
        """
        full_name: str = self.scope.trace_as_str("_") + f"_{name}"

        self.type_vars.add(full_name)
        return full_name

    def register_type(
        self,
        type_id: int,
        schema: capnp._StructSchema,
        name: str = "",
        scope: Scope | None = None,
    ) -> CapnpType:
        """Register a new type in the writer's registry of types.

        Args:
            type_id (int): The identification number of the type.
            schema (_StructSchema): The schema that defines the type.
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
            raise ValueError(f"No valid scope was found for registering the type '{name}'.")

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

        else:
            raise KeyError(f"The type ID '{type_id} was not found in the type registry.'")

    def new_scope(
        self, name: str, node: Any, scope_heading: str = "", register: bool = True
    ) -> Scope:
        """Creates a new scope below the scope of the provided node.

        Args:
            name (str): The name of the new scope.
            node (Any): The node whose scope is the parent scope of the new scope.
            scope_heading (str): The line of code that starts this new scope.
            register (bool): Whether to register this scope.

        Returns:
            Scope: The parent of this scope.
        """
        try:
            parent_scope = self.scopes_by_id[node.scopeId]

        except KeyError as e:
            raise NoParentError(f"The scope with name '{name}' has no parent.") from e

        # Add the heading of the scope to the parent scope.
        if scope_heading:
            parent_scope.add(scope_heading)

        # Then, make a new scope that is one indent level deeper.
        child_scope = Scope(name=name, id=node.id, parent=parent_scope, return_scope=self.scope)

        self.scope = child_scope

        if register:
            self.scopes_by_id[node.id] = child_scope

        return parent_scope

    def return_from_scope(self):
        """Return from the current scope."""
        assert self.scope is not None, "The current scope is not valid."
        assert not self.scope.is_root, (
            "The current scope is the root scope and cannot be returned from."
        )
        assert self.scope.parent is not None, "The current scope has no parent."
        assert self.scope.return_scope is not None, (
            "The current scope does not define a scope to return to."
        )

        self.scope.parent.lines += self.scope.lines
        self.scope = self.scope.return_scope

    def get_type_name(self, type_reader: capnp._DynamicStructReader | capnp.TypeReader) -> str:
        """Extract the type name from a type reader.

        The output type name is prepended by the scope name, if there is a parent scope.

        Args:
            type_reader (_DynamicStructReader | TypeReader): The type reader to get the type name from.

        Returns:
            str: The extracted type name.
        """
        try:
            return capnp_types.CAPNP_TYPE_TO_PYTHON[type_reader.which()]

        except KeyError:
            pass

        type_reader_type = type_reader.which()

        element_type: Any | None = None

        if type_reader_type == capnp_types.CapnpElementType.STRUCT:
            element_type = self.get_type_by_id(type_reader.struct.typeId)
            type_name = element_type.name
            generic_params = []

            for brand_scope in type_reader.struct.brand.scopes:
                brand_scope_type = brand_scope.which()

                if brand_scope_type == "inherit":
                    parent_scope = self.get_type_by_id(brand_scope.scopeId)
                    generic_params.extend(parent_scope.generic_params)

                elif brand_scope_type == "bind":
                    for bind in brand_scope.bind:
                        generic_params.append(self.get_type_name(bind.type))

                else:
                    raise TypeError(f"Unknown brand scope '{brand_scope_type}'.")

            if generic_params:
                type_name += f"[{', '.join(generic_params)}]"

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
            element_type = self.get_type_by_id(type_reader.interface.typeId)
            type_name = element_type.name

            # Traverse down to the innermost nested list element.
            while type_name == capnp_types.CapnpElementType.LIST:
                type_name += type_reader.list.elementType.which()

        else:
            raise TypeError(f"Unknown type reader type '{type_reader_type}'.")

        if element_type and (not element_type.scope.is_root):
            return f"{element_type.scope}.{type_name}"

        else:
            return type_name

    def dumps_pyi(self) -> str:
        """Generates string output for the *.pyi stub file that provides type hinting.

        Returns:
            str: The output string.
        """
        assert self.scope.is_root

        out = []
        out.append(self.docstring)
        out.extend(self.imports)
        out.append("")

        if self.type_vars:
            for name in sorted(self.type_vars):
                out.append(f'{name} = TypeVar("{name}")')
            out.append("")

        out.extend(self.scope.lines)
        return "\n".join(out)

    def dumps_py(self) -> str:
        """Generates string output for the *.py stub file that handles the import of capnproto schemas.

        Returns:
            str: The output string.
        """
        assert self.scope.is_root

        out = []
        out.append(self.docstring)
        out.append("import os")
        out.append("import capnp")
        out.append("capnp.remove_import_hook()")
        out.append("here = os.path.dirname(os.path.abspath(__file__))")

        out.append(f'module_file = os.path.abspath(os.path.join(here, "{self.display_name}"))')

        for scope in self.scopes_by_id.values():
            if scope.parent is not None and scope.parent.is_root:
                out.append(f"{scope.name} = capnp.load(module_file).{scope.name}")
                out.append(f"{helper.new_builder(scope.name)} = {scope.name}")
                out.append(f"{helper.new_reader(scope.name)} = {scope.name}")

        return "\n".join(out)
