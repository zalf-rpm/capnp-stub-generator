"""Generate type hints for *.capnp schemas.

Note: This generator requires pycapnp >= 2.0.0.
"""

from __future__ import annotations

import logging
import os.path
import pathlib
from collections.abc import Iterator
from copy import copy
from types import ModuleType
from typing import TYPE_CHECKING, Any, Literal

import capnp
from capnp.lib.capnp import _DynamicStructReader, _StructSchema

from capnp_stub_generator import capnp_types, helper
from capnp_stub_generator.scope import CapnpType, NoParentError, Scope
from capnp_stub_generator.writer_dto import (
    InterfaceGenerationContext,
    MethodInfo,
    MethodSignatureCollection,
    ParameterInfo,
    ServerMethodsCollection,
    StructFieldsCollection,
    StructGenerationContext,
)

capnp.remove_import_hook()

logger = logging.getLogger(__name__)

InitChoice = tuple[str, str]

# Constants
DISCRIMINANT_NONE = 65535  # Value indicating no discriminant (not part of a union)


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
        "NamedTuple",
        "Self",
        "TypeAlias",
    ]

    def __init__(
        self,
        module: ModuleType,
        module_registry: capnp_types.ModuleRegistryType,
        output_directory: str | None = None,
        import_paths: list[str] | None = None,
    ):
        """Initialize the stub writer with a module definition.

        Args:
            module (ModuleType): The module definition to parse and write a stub for.
            module_registry (ModuleRegistryType): The module registry, for finding dependencies between loaded modules.
            output_directory (str | None): The directory where output files are written, if different from schema location.
            import_paths (list[str] | None): Additional import paths for resolving absolute imports (e.g., /capnp/c++.capnp).
        """
        self.scope = Scope(name="", id=module.schema.node.id, parent=None, return_scope=None)
        self.scopes_by_id: dict[int, Scope] = {self.scope.id: self.scope}

        self._module = module
        self._module_registry = module_registry
        self._output_directory = pathlib.Path(output_directory) if output_directory else None
        self._import_paths = [pathlib.Path(p) for p in import_paths] if import_paths else []

        if self._module.__file__:
            self._module_path = pathlib.Path(self._module.__file__)

        else:
            raise ValueError("The module has no file path attached to it.")

        self._imports: list[str] = []
        self._add_import("from __future__ import annotations")

        self._typing_imports: set[Writer.VALID_TYPING_IMPORTS] = set()

        self.type_vars: set[str] = set()
        self.type_map: dict[int, CapnpType] = {}

        # Track imported module paths for capnp.load imports parameter
        self._imported_module_paths: set[pathlib.Path] = set()

        # Track all server NamedTuples globally (scope_name -> {method_name: (namedtuple_name, fields)})
        self._all_server_namedtuples: dict[str, dict[str, tuple[str, list[tuple[str, str]]]]] = {}

        # Track all interfaces for cast_as overloads (interface_name -> (client_name, base_client_names))
        self._all_interfaces: dict[str, tuple[str, list[str]]] = {}

        self.docstring = f'"""This is an automatically generated stub for `{self._module_path.name}`."""'

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

    # ===== Static Method Generators =====

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
                default="...",
            ),
            helper.TypeHintedVariable(
                "nesting_limit",
                [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                default="...",
            ),
        ]

    def _add_from_bytes_methods(self, scoped_reader_type: str):
        """Add from_bytes and from_bytes_packed static methods to current scope.

        Args:
            scoped_reader_type (str): The fully qualified Reader type name.
        """
        self._add_typing_import("Iterator")
        self._add_import("from contextlib import contextmanager")

        # from_bytes method (returns Iterator for context manager usage)
        data_param = helper.TypeHintedVariable("data", [helper.TypeHint("bytes", primary=True)])
        self._add_static_method(
            "from_bytes",
            parameters=[data_param] + self._create_capnp_limit_params(),
            return_type=helper.new_type_group("Iterator", [scoped_reader_type]),
            decorators=["contextmanager"],
        )

        # from_bytes_packed method
        self._add_static_method(
            "from_bytes_packed",
            parameters=[data_param] + self._create_capnp_limit_params(),
            return_type=scoped_reader_type,
        )

    def _add_read_methods(self, scoped_reader_type: str):
        """Add read and read_packed static methods to current scope.

        Args:
            scoped_reader_type (str): The fully qualified Reader type name.
        """
        self._add_typing_import("BinaryIO")

        file_param = helper.TypeHintedVariable("file", [helper.TypeHint("BinaryIO", primary=True)])

        # read method
        self._add_static_method(
            "read",
            parameters=[file_param] + self._create_capnp_limit_params(),
            return_type=scoped_reader_type,
        )

        # read_packed method
        self._add_static_method(
            "read_packed",
            parameters=[file_param] + self._create_capnp_limit_params(),
            return_type=scoped_reader_type,
        )

    def _add_write_methods(self):
        """Add write and write_packed static methods to current scope."""
        self._add_import("from io import BufferedWriter")

        file_param = helper.TypeHintedVariable("file", [helper.TypeHint("BufferedWriter", primary=True)])

        self._add_static_method("write", [file_param])
        self._add_static_method("write_packed", [file_param])

    def _add_static_method(
        self,
        name: str,
        parameters: list[helper.TypeHintedVariable] | list[str] | None = None,
        return_type: str | None = None,
        decorators: list[str] | None = None,
    ) -> None:
        """Add a static method to the current scope.

        This is a convenience method that combines decorator and function generation.
        Always adds @staticmethod, plus any additional decorators specified.

        Args:
            name: The method name
            parameters: Method parameters (TypeHintedVariable list or string list)
            return_type: Method return type (None if no return type)
            decorators: Additional decorators to add before @staticmethod
                       (e.g., ["contextmanager"] for from_bytes)

        Examples:
            # Simple static method
            self._add_static_method("write", [file_param])

            # Static method with return type
            self._add_static_method("new_message", params, "MyStruct.Builder")

            # Static method with additional decorator
            self._add_static_method(
                "from_bytes",
                [data_param, ...],
                "Iterator[MyStruct.Reader]",
                decorators=["contextmanager"]
            )
        """
        # Add any additional decorators first (they go above @staticmethod)
        if decorators:
            for decorator in decorators:
                self.scope.add(helper.new_decorator(decorator))

        # Add @staticmethod decorator
        self.scope.add(helper.new_decorator("staticmethod"))

        # Add the function definition
        self.scope.add(helper.new_function(name, parameters, return_type))

    def _add_base_properties(self, slot_fields: list[helper.TypeHintedVariable]):
        """Add read-only properties to base struct class.

        Args:
            slot_fields (list[helper.TypeHintedVariable]): The fields to add as properties.
        """
        # Base class (StructModule) does not have field properties
        # Properties are only on Reader and Builder classes
        pass

    def _add_reader_properties(self, slot_fields: list[helper.TypeHintedVariable]):
        """Add read-only properties to Reader class.

        Args:
            slot_fields (list[helper.TypeHintedVariable]): The fields to add as properties.
        """
        # Reader class needs all properties, not just those with Reader affix
        for slot_field in slot_fields:
            if slot_field.has_type_hint_with_reader_affix:
                field_copy = copy(slot_field)
                # Get the narrowed Reader-only type for this field
                reader_type = field_copy.get_type_with_affixes([helper.READER_NAME])
                for line in helper.new_property(slot_field.name, reader_type):
                    self.scope.add(line)
            else:
                # Add primitive and other fields with their primary type
                field_type = slot_field.primary_type_nested
                for line in helper.new_property(slot_field.name, field_type):
                    self.scope.add(line)

    def _add_builder_properties(self, slot_fields: list[helper.TypeHintedVariable]):
        """Add mutable properties with setters to Builder class.

        Args:
            slot_fields (list[helper.TypeHintedVariable]): The fields to add as properties.
        """
        for slot_field in slot_fields:
            field_copy = copy(slot_field)
            # Determine getter and setter types based on field characteristics
            if slot_field.has_type_hint_with_builder_affix:
                # For lists, use Sequence[ElementBuilder] for compatibility
                if slot_field.nesting_depth == 1:
                    getter_type = field_copy.get_type_with_affixes([helper.BUILDER_NAME])
                    # Setter accepts Builder/Reader types + dict, but NOT the base type
                    setter_types = [helper.BUILDER_NAME, helper.READER_NAME]
                    setter_type = field_copy.get_type_with_affixes(setter_types) + " | Sequence[dict[str, Any]]"
                    self._add_typing_import("Sequence")
                    self._add_typing_import("Any")
                else:
                    # For non-list structs: setter accepts Builder/Reader + dict, but NOT the base type
                    getter_type = field_copy.get_type_with_affixes([helper.BUILDER_NAME])
                    setter_types = [helper.BUILDER_NAME, helper.READER_NAME]
                    setter_type = field_copy.get_type_with_affixes(setter_types) + " | dict[str, Any]"
                    self._add_typing_import("Any")
            # For interface fields: getter returns Protocol, setter accepts Protocol | Server
            elif len(slot_field.type_hints) > 1 and any(".Server" in str(h) for h in slot_field.type_hints):
                getter_type = field_copy.primary_type_nested  # Protocol only
                setter_type = field_copy.full_type_nested  # Protocol | Server
            else:
                # Primitive and enum fields
                getter_type = field_copy.primary_type_nested
                setter_type = field_copy.full_type_nested if field_copy.full_type_nested != getter_type else None

            for line in helper.new_property(slot_field.name, getter_type, with_setter=True, setter_type=setter_type):
                self.scope.add(line)

    def _add_base_init_overloads(self, init_choices: list[InitChoice]):
        """Add init method overloads to base struct class.

        Args:
            init_choices (list[InitChoice]): List of (field_name, field_type) tuples for overloads.
        """
        if not init_choices:
            return

        self._add_typing_import("Literal")
        self._add_typing_import("Any")
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

        # Add catch-all implementation (required when using @overload)
        if use_overload:
            self.scope.add(
                helper.new_function(
                    "init",
                    parameters=[
                        helper.TypeHintedVariable("self", [helper.TypeHint("Any", primary=True)]),
                        helper.TypeHintedVariable("name", [helper.TypeHint("str", primary=True)]),
                        helper.TypeHintedVariable("size", [helper.TypeHint("int", primary=True)], default="..."),
                    ],
                    return_type="Any",
                )
            )

    def _add_builder_init_overloads(
        self,
        init_choices: list[InitChoice],
        list_init_choices: list[tuple[str, str, bool]],
    ):
        """Add init method overloads to Builder class.

        Args:
            init_choices (list[InitChoice]): List of (field_name, field_type) tuples for struct/group fields.
            list_init_choices (list[tuple[str, str, bool]]): List of (field_name, element_type, needs_builder) for list fields.
        """
        total_init_overloads = len(init_choices) + len(list_init_choices) if list_init_choices else len(init_choices)
        use_overload = total_init_overloads > 1

        if use_overload:
            self._add_typing_import("overload")
        if init_choices or list_init_choices:
            self._add_typing_import("Literal")

        # Add init method overloads for union/group fields (return their Builder type)
        for field_name, field_type in init_choices:
            if use_overload:
                self.scope.add(helper.new_decorator("overload"))
            # Build builder type name (respect scoped names)
            builder_type = self._build_scoped_builder_type(field_type)

            # Use self: Any only when using overloads (for compatibility with catch-all)
            if use_overload:
                init_params = [
                    helper.TypeHintedVariable("self", [helper.TypeHint("Any", primary=True)]),
                    helper.TypeHintedVariable("name", [helper.TypeHint(f'Literal["{field_name}"]', primary=True)]),
                ]
            else:
                init_params = [
                    "self",
                    f'name: Literal["{field_name}"]',
                ]

            self.scope.add(
                helper.new_function(
                    "init",
                    parameters=init_params,
                    return_type=builder_type,
                )
            )

        # Add init method overloads for lists (properly typed)
        for field_name, element_type, needs_builder in list_init_choices:
            if use_overload:
                self.scope.add(helper.new_decorator("overload"))
            element_type_for_list = self._build_scoped_builder_type(element_type) if needs_builder else element_type

            # Use self: Any only when using overloads
            if use_overload:
                init_params_list = [
                    helper.TypeHintedVariable("self", [helper.TypeHint("Any", primary=True)]),
                    helper.TypeHintedVariable("name", [helper.TypeHint(f'Literal["{field_name}"]', primary=True)]),
                    helper.TypeHintedVariable("size", [helper.TypeHint("int", primary=True)], default="..."),
                ]
            else:
                init_params_list = [
                    "self",
                    f'name: Literal["{field_name}"]',
                    "size: int = ...",
                ]

            self.scope.add(
                helper.new_function(
                    "init",
                    parameters=init_params_list,
                    return_type=f"Sequence[{element_type_for_list}]",
                )
            )

        # Add generic init method for other cases (catch-all)
        if use_overload:
            self._add_typing_import("Any")
            self.scope.add(
                helper.new_function(
                    "init",
                    parameters=[
                        helper.TypeHintedVariable("self", [helper.TypeHint("Any", primary=True)]),
                        helper.TypeHintedVariable("name", [helper.TypeHint("str", primary=True)]),
                        helper.TypeHintedVariable("size", [helper.TypeHint("int", primary=True)], default="..."),
                    ],
                    return_type="Any",
                )
            )

    # ===== Struct Generation Helper Methods =====

    def _add_new_message_method(
        self,
        slot_fields: list[helper.TypeHintedVariable],
        scoped_builder_type: str,
    ):
        """Add new_message static method with field parameters as kwargs.

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields to add as parameters.
            scoped_builder_type (str): The fully qualified Builder type name to return.
        """
        self._add_typing_import("Any")
        new_message_params: list[helper.TypeHintedVariable] = [
            helper.TypeHintedVariable(
                "num_first_segment_words",
                [helper.TypeHint("int", primary=True), helper.TypeHint("None")],
                default="None",
            ),
            helper.TypeHintedVariable(
                "allocate_seg_callable",
                [helper.TypeHint("Any", primary=True)],
                default="None",
            ),
        ]

        # Add each field as an optional kwarg parameter
        for slot_field in slot_fields:
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

        self._add_static_method(
            "new_message",
            new_message_params,
            scoped_builder_type,
        )

    def _gen_struct_base_class(
        self,
        slot_fields: list[helper.TypeHintedVariable],
        init_choices: list[InitChoice],
        schema: _StructSchema,
        scoped_reader_type: str,
        scoped_builder_type: str,
    ):
        """Generate the base struct class with properties and methods.

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields.
            init_choices (list[InitChoice]): Init method overload choices.
            schema (_StructSchema): The struct schema.
            scoped_reader_type (str): Fully qualified Reader type name.
            scoped_builder_type (str): Fully qualified Builder type name.
        """
        # Add the slot fields as properties
        if slot_fields:
            self._add_base_properties(slot_fields)

        # Add the `which` function for unions
        if schema.node.struct.discriminantCount:
            self._add_typing_import("Literal")
            field_names = [
                f'"{field.name}"' for field in schema.node.struct.fields if field.discriminantValue != DISCRIMINANT_NONE
            ]
            return_type = helper.new_type_group("Literal", field_names)
            self.scope.add(helper.new_function("which", parameters=["self"], return_type=return_type))

        # Add init method overloads
        self._add_base_init_overloads(init_choices)

        # Add static methods
        self._add_from_bytes_methods(scoped_reader_type)
        self._add_new_message_method(slot_fields, scoped_builder_type)
        self._add_read_methods(scoped_reader_type)

        # Add to_dict method
        self._add_typing_import("Any")
        self.scope.add(helper.new_function("to_dict", parameters=["self"], return_type="dict[str, Any]"))

    def _gen_struct_reader_class(
        self,
        slot_fields: list[helper.TypeHintedVariable],
        new_type: CapnpType,
        registered_params: list[str],
        reader_type_name: str,
        scoped_builder_type: str,
        schema: _StructSchema,
    ):
        """Generate the Reader class for a struct.

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields.
            new_type (CapnpType): The registered type.
            registered_params (list[str]): Generic type parameters.
            reader_type_name (str): The Reader class name (unused, kept for compatibility).
            scoped_builder_type (str): Fully qualified Builder type name.
            schema (_StructSchema): The struct schema.
        """
        # Add the reader slot fields as properties
        self._add_reader_properties(slot_fields)

        # Add the `which` function for unions
        if schema.node.struct.discriminantCount:
            self._add_typing_import("Literal")
            field_names = [
                f'"{field.name}"' for field in schema.node.struct.fields if field.discriminantValue != DISCRIMINANT_NONE
            ]
            return_type = helper.new_type_group("Literal", field_names)
            self.scope.add(helper.new_function("which", parameters=["self"], return_type=return_type))

        # Add as_builder method
        self.scope.add(
            helper.new_function(
                "as_builder",
                parameters=["self"],
                return_type=scoped_builder_type,
            )
        )

        # If scope is empty, add pass statement
        if not self.scope.lines:
            self.scope.add("pass")

    def _gen_struct_builder_class(
        self,
        slot_fields: list[helper.TypeHintedVariable],
        init_choices: list[InitChoice],
        list_init_choices: list[tuple[str, str, bool]],
        new_type: CapnpType,
        registered_params: list[str],
        builder_type_name: str,
        scoped_builder_type: str,
        scoped_reader_type: str,
        schema: _StructSchema,
    ):
        """Generate the Builder class for a struct.

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields.
            init_choices (list[InitChoice]): Init method overload choices for structs.
            list_init_choices (list[tuple[str, str, bool]]): Init method overload choices for lists.
            new_type (CapnpType): The registered type.
            registered_params (list[str]): Generic type parameters.
            builder_type_name (str): The Builder class name (unused, kept for compatibility).
            scoped_builder_type (str): Fully qualified Builder type name.
            scoped_reader_type (str): Fully qualified Reader type name.
            schema (_StructSchema): The struct schema.
        """
        # Add all builder slot fields with setters
        self._add_builder_properties(slot_fields)

        # Add the `which` function for unions
        if schema.node.struct.discriminantCount:
            self._add_typing_import("Literal")
            field_names = [
                f'"{field.name}"' for field in schema.node.struct.fields if field.discriminantValue != DISCRIMINANT_NONE
            ]
            return_type = helper.new_type_group("Literal", field_names)
            self.scope.add(helper.new_function("which", parameters=["self"], return_type=return_type))

        # Add from_dict method
        self._add_typing_import("Any")
        self._add_static_method(
            "from_dict",
            [helper.TypeHintedVariable("dictionary", [helper.TypeHint("dict[str, Any]", primary=True)])],
            scoped_builder_type,
        )

        # Add init method overloads
        self._add_builder_init_overloads(init_choices, list_init_choices)

        # Add utility methods
        self.scope.add(helper.new_function("copy", parameters=["self"], return_type=scoped_builder_type))
        self.scope.add(helper.new_function("to_bytes", parameters=["self"], return_type="bytes"))
        self.scope.add(helper.new_function("to_bytes_packed", parameters=["self"], return_type="bytes"))
        self.scope.add(
            helper.new_function(
                "to_segments",
                parameters=["self"],
                return_type=helper.new_type_group("list", ["bytes"]),
            )
        )

        # Add as_reader method
        self.scope.add(
            helper.new_function(
                "as_reader",
                parameters=["self"],
                return_type=scoped_reader_type,
            )
        )

        # Add write methods
        self._add_write_methods()

        # If scope is empty, add pass statement
        if not self.scope.lines:
            self.scope.add("pass")

    # ===== Interface Generation Helper Methods =====

    def _collect_interface_base_classes(self, schema: _StructSchema) -> list[str]:
        """Collect base classes for an interface (superclasses + Protocol).

        Args:
            schema (_StructSchema): The interface schema.

        Returns:
            list[str]: List of base class names.
        """
        base_classes = []

        # Process interface inheritance (extends)
        if schema.node.which() == "interface":
            interface_node = schema.node.interface
            for superclass in interface_node.superclasses:
                try:
                    # Get the superclass type
                    superclass_type = self.get_type_by_id(superclass.id)
                    base_classes.append(superclass_type.scoped_name)
                except KeyError:
                    # Superclass not yet registered - try to generate it first
                    try:
                        # Try to find and generate the superclass from the module registry
                        for module_id, (path, module) in self._module_registry.items():
                            if module_id == superclass.id:
                                # Found the superclass module, generate it
                                self.generate_nested(module.schema)
                                superclass_type = self.get_type_by_id(superclass.id)
                                base_classes.append(superclass_type.scoped_name)
                                break

                            # Check if it's a nested type in the module
                            def find_nested_schema(schema_obj, target_id):
                                for nested_node in schema_obj.node.nestedNodes:
                                    if nested_node.id == target_id:
                                        return schema_obj.get_nested(nested_node.name)
                                    try:
                                        nested_schema = schema_obj.get_nested(nested_node.name)
                                        result = find_nested_schema(nested_schema, target_id)
                                        if result:
                                            return result
                                    except Exception:
                                        pass
                                return None

                            found_schema = find_nested_schema(module.schema, superclass.id)
                            if found_schema:
                                self.generate_nested(found_schema)
                                superclass_type = self.get_type_by_id(superclass.id)
                                base_classes.append(superclass_type.scoped_name)
                                break
                    except Exception as e:
                        logger.debug(f"Could not resolve superclass {superclass.id}: {e}")

        # Always add Protocol as the last base class
        base_classes.append("Protocol")

        return base_classes

    def _generate_nested_types_for_interface(self, schema: _StructSchema, name: str):
        """Generate all nested types for an interface.

        Args:
            schema (_StructSchema): The interface schema.
            name (str): The interface name.
        """
        # Build runtime path for this interface (handles nested interfaces)
        # Use self.scope.trace to get the full path including current interface
        runtime_path = []
        for s in self.scope.trace:
            if s.is_root:
                continue
            runtime_path.append(s.name)

        # Save current interface scope before generating nested types
        interface_scope = self.scope

        for nested_node in schema.node.nestedNodes:
            try:
                # Navigate to the nested type through runtime module
                runtime_obj = self._module
                for path_segment in runtime_path:
                    runtime_obj = getattr(runtime_obj, path_segment)
                runtime_nested = getattr(runtime_obj, nested_node.name)
                nested_schema = runtime_nested.schema
                self.generate_nested(nested_schema)
            except Exception as e:  # pragma: no cover
                logger.debug(f"Could not generate nested type {nested_node.name}: {e}")

        # Restore interface scope after generating nested types
        self.scope = interface_scope

    def _add_new_client_method(
        self, name: str, base_classes: list[str], schema: _StructSchema, client_return_type: str | None = None
    ):
        """Add _new_client() class method to create capability client from Server.

        Args:
            name (str): The interface name.
            base_classes (list[str]): The interface base classes.
            schema (_StructSchema): The interface schema.
            client_return_type (str | None): Optional client class name to return (default: interface name).
        """
        scope_path = self._get_scope_path()
        fully_qualified_interface = scope_path if scope_path else name

        # Build server parameter type - should accept this Server OR ANY ancestor Server types
        # This ensures compatibility with inherited _new_client signatures
        # We need to recursively collect all ancestors, not just direct parents
        def collect_all_ancestor_servers(node_id: int, visited: set[int] | None = None) -> set[str]:
            """Recursively collect all ancestor Server types by node ID."""
            if visited is None:
                visited = set()

            # Avoid infinite loops
            if node_id in visited:
                return set()
            visited.add(node_id)

            ancestors = set()

            # Try to get the schema for this node ID
            schema_node = None
            if node_id in self.type_map:
                type_info = self.type_map[node_id]
                if hasattr(type_info, "schema") and hasattr(type_info.schema, "node"):
                    schema_node = type_info.schema.node

            # If not found in current module, check the module registry
            if schema_node is None:
                for module_id, (path, module) in self._module_registry.items():
                    if module_id == node_id:
                        schema_node = module.schema.node
                        break
                    # Check all top-level types in this module
                    for attr_name in dir(module.schema):
                        if attr_name.startswith("_"):
                            continue
                        try:
                            attr = getattr(module.schema, attr_name)
                            if hasattr(attr, "schema") and hasattr(attr.schema, "node"):
                                if attr.schema.node.id == node_id:
                                    schema_node = attr.schema.node
                                    break
                        except (AttributeError, TypeError):
                            continue
                    if schema_node:
                        break

            # If we found the schema, process its superclasses
            if schema_node and schema_node.which() == "interface":
                for superclass in schema_node.interface.superclasses:
                    try:
                        superclass_type = self.get_type_by_id(superclass.id)
                        ancestor_server_type = f"{superclass_type.scoped_name}.Server"
                        ancestors.add(ancestor_server_type)
                        # Recursively collect ancestors of this superclass
                        ancestors.update(collect_all_ancestor_servers(superclass.id, visited))
                    except (KeyError, AttributeError):
                        pass

            return ancestors

        server_types = [f"{fully_qualified_interface}.Server"]
        ancestor_servers = collect_all_ancestor_servers(schema.node.id)
        server_types.extend(sorted(ancestor_servers))  # Sort for consistency

        server_param_type = " | ".join(server_types)

        # Determine return type
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

        self.scope.add("@classmethod")
        self.scope.add(
            helper.new_function(
                "_new_client",
                parameters=["cls", f"server: {server_param_type}"],
                return_type=return_type,
            )
        )

    # ===== Slot Generation Methods =====

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
                list_init_choices.append((helper.sanitize_name(field.name), element_type, needs_builder))

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
            # For reading: return the Client type (capabilities are always clients at runtime)
            # For writing (in Builder): accept Client | Server
            client_type = f"{type_name}Client"
            hints = [helper.TypeHint(client_type, primary=True)]
            # Add Server as a non-primary hint for Builder setter
            hints.append(helper.TypeHint(f"{type_name}.Server"))
            hinted_variable = helper.TypeHintedVariable(helper.sanitize_name(field.name), hints)

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
                    # Use getattr to safely access elementType which may not exist on all schema types
                    next_element = getattr(next_schema_element, "elementType", None)
                    if next_element is None:
                        break
                    next_schema_element = next_element

                except (AttributeError, capnp.KjException):
                    break

                else:
                    yield next_schema_element

        def list_elements(
            list_: _DynamicStructReader,
        ) -> Iterator[_DynamicStructReader]:
            """An iterator over the list elements of nested lists.

            Args:
                list_ (_DynamicStructReader): A list element.

            Returns:
                Iterator[_DynamicStructReader]: The next deeper nested list element.
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
        new_type = None

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
                # Check if it has the required attributes for a struct schema
                if hasattr(last_element, "node") and hasattr(last_element, "as_struct"):
                    if TYPE_CHECKING:
                        # For type checking, cast via object to satisfy type checker
                        from typing import cast

                        self.generate_nested(cast(_StructSchema, cast(object, last_element)))
                    else:
                        self.generate_nested(last_element)
                    type_name = self.get_type_name(field.slot.type.list.elementType)
                else:
                    raise AttributeError("Not a struct schema")
            except AttributeError:
                # This is a built-in type and does not require generation.
                create_extended_types = False
                type_name = self.get_type_name(last_element)

            list_depth = len(nested_list_elements)

        self._add_typing_import("Sequence")

        hinted_variable = helper.TypeHintedVariable(
            helper.sanitize_name(field.name),
            [helper.TypeHint(type_name, primary=True)],
            nesting_depth=list_depth,
        )

        # Do not create extended types for enum/interface lists; enums/interfaces
        # lack builder/reader variants.
        try:
            base_list_element = field.slot.type.list.elementType.which()
        except Exception:
            base_list_element = None
        if base_list_element in (
            capnp_types.CapnpElementType.ENUM,
            capnp_types.CapnpElementType.INTERFACE,
        ):
            create_extended_types = False

        # Also check if the new_type (when registered) is an interface
        try:
            if new_type and new_type.schema.node.which() == capnp_types.CapnpElementType.INTERFACE:
                create_extended_types = False
        except Exception:
            pass

        if create_extended_types:
            hinted_variable.add_builder_from_primary_type()
            hinted_variable.add_reader_from_primary_type()

        return hinted_variable

    def gen_python_type_slot(self, field: capnp._DynamicStructReader, field_type: str) -> helper.TypeHintedVariable:
        """Generate a slot, which contains a regular Python type.

        Args:
            field (_DynamicStructReader): The field reader.
            field_type (str): The (primitive) type of the slot.

        Returns:
            helper.HintedVariable: The extracted hinted variable object.
        """
        python_type_name: str = capnp_types.CAPNP_TYPE_TO_PYTHON[field_type]
        return helper.TypeHintedVariable(
            helper.sanitize_name(field.name), [helper.TypeHint(python_type_name, primary=True)]
        )

    def gen_enum_slot(self, field: capnp._DynamicStructReader, schema: _StructSchema) -> helper.TypeHintedVariable:
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
                helper.sanitize_name(field.name),
                [helper.TypeHint(type_name, primary=True), helper.TypeHint(literal_type)],
            )
        except (AttributeError, TypeError):
            # Fallback if we can't get enumerants
            return helper.TypeHintedVariable(
                helper.sanitize_name(field.name),
                [helper.TypeHint(type_name, primary=True), helper.TypeHint("str")],
            )

    def gen_struct_slot(
        self,
        field: capnp._DynamicStructReader,
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
                self.gen_struct(schema)

        type_name = self.get_type_name(field.slot.type)
        init_choices.append((helper.sanitize_name(field.name), type_name))
        hints = [helper.TypeHint(type_name, primary=True)]
        # If this is an interface type, also allow passing its Server implementation
        try:
            if field.slot.type.which() == capnp_types.CapnpElementType.INTERFACE:
                hints.append(helper.TypeHint(f"{type_name}.Server"))
        except Exception:
            pass
        return helper.TypeHintedVariable(helper.sanitize_name(field.name), hints)

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
            # Check if this is a generic parameter
            param = field.slot.type.anyPointer.parameter
            type_name = new_type.generic_params[param.parameterIndex]
            return helper.TypeHintedVariable(
                helper.sanitize_name(field.name), [helper.TypeHint(type_name, primary=True)]
            )

        except (capnp.KjException, AttributeError, IndexError):
            # Not a parameter, treat as a plain AnyPointer -> Any
            self._add_typing_import("Any")
            return helper.TypeHintedVariable(helper.sanitize_name(field.name), [helper.TypeHint("Any", primary=True)])

    def gen_const(self, schema: _StructSchema) -> None:
        """Generate a `const` object.

        Args:
            schema (_StructSchema): The schema to generate the `const` object out of.
        """
        assert schema.node.which() == capnp_types.CapnpElementType.CONST

        const_type = schema.node.const.type.which()
        name = helper.get_display_name(schema)

        if const_type in capnp_types.CAPNP_TYPE_TO_PYTHON:
            python_type = capnp_types.CAPNP_TYPE_TO_PYTHON[schema.node.const.type.which()]
            self.scope.add(helper.TypeHintedVariable(name, [helper.TypeHint(python_type, primary=True)]))

        elif const_type == "struct":
            pass

    def gen_enum(self, schema: _StructSchema) -> CapnpType | None:
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

    def gen_generic(self, schema: _StructSchema) -> list[str]:
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
            if field.slot.type.which() == "anyPointer" and field.slot.type.anyPointer.which() == "parameter":
                param = field.slot.type.anyPointer.parameter

                # Try to get the type, but skip if not found (forward reference)
                try:
                    t = self.get_type_by_id(param.scopeId)
                    if t is not None:
                        param_source = t.schema
                        source_params: list[str] = [param.name for param in param_source.node.parameters]
                        referenced_params.append(source_params[param.parameterIndex])
                except KeyError:
                    # Type not yet registered, skip for now
                    pass

        return [self.register_type_var(param) for param in generic_params + referenced_params]

    # ===== Struct Generation Helper Methods (Phase 2 Refactoring) =====

    def _setup_struct_generation(
        self, schema: _StructSchema, type_name: str
    ) -> tuple[StructGenerationContext | None, str]:
        """Setup struct generation by checking imports, creating type, and preparing context.

        This method handles the initial setup phase of struct generation including:
        - Checking if the struct is already imported
        - Determining the type name
        - Handling generic parameters
        - Creating the class declaration
        - Setting up the scope
        - Registering the type

        Args:
            schema: The Cap'n Proto struct schema
            type_name: Optional type name override (empty string to auto-generate)

        Returns:
            A tuple of (context, class_declaration) where:
            - context is None if the struct should be skipped (already imported or no parent)
            - class_declaration is the string for the class declaration
        """
        # Check if already imported
        imported = self.register_import(schema)
        if imported is not None:
            return None, ""

        # Determine type name
        if not type_name:
            type_name = helper.get_display_name(schema)

        # Handle generics
        registered_params: list[str] = []
        if schema.node.isGeneric:
            registered_params = self.gen_generic(schema)

        # Create class declaration
        if registered_params:
            parameter = helper.new_type_group("Generic", registered_params)
            class_declaration = helper.new_class_declaration(type_name, parameters=[parameter])
        else:
            class_declaration = helper.new_class_declaration(type_name)

        # Create scope
        try:
            self.new_scope(type_name, schema.node)
        except NoParentError:
            logger.warning(f"Skipping generation of {type_name} - parent scope not available")
            return None, ""

        # Register type
        new_type = self.register_type(schema.node.id, schema, name=type_name)
        new_type.generic_params = registered_params

        # Create context with auto-generated names
        context = StructGenerationContext.create(schema, type_name, new_type, registered_params)

        return context, class_declaration

    def _resolve_nested_schema(
        self, nested_node: Any, parent_schema: _StructSchema, parent_type_name: str
    ) -> _StructSchema | None:
        """Resolve a nested schema from a nested node, with fallback strategies.

        Args:
            nested_node: The nested node to resolve
            parent_schema: The parent struct schema
            parent_type_name: The name of the parent type (for runtime fallback)

        Returns:
            The nested schema or None if it cannot be resolved
        """
        try:
            return parent_schema.get_nested(nested_node.name)
        except Exception:
            # Fallback: access via runtime module (needed for nested interfaces)
            try:
                runtime_parent = getattr(self._module, parent_type_name)
                runtime_nested = getattr(runtime_parent, nested_node.name)
                return runtime_nested.schema
            except Exception as e:
                logger.debug(f"Could not resolve nested node {nested_node.name}: {e}")
                return None

    def _generate_nested_types(self, schema: _StructSchema, type_name: str) -> None:
        """Generate all nested types (structs, enums, interfaces) within this struct.

        Nested types must be generated before processing fields so they're available
        for reference in field types.

        Args:
            schema: The struct schema containing nested nodes
            type_name: The name of the parent type (for error messages and fallback)
        """
        for nested_node in schema.node.nestedNodes:
            nested_schema = self._resolve_nested_schema(nested_node, schema, type_name)
            if nested_schema:
                try:
                    self.generate_nested(nested_schema)
                except Exception as e:
                    logger.debug(f"Failed generating nested node {nested_node.name}: {e}")

    def _process_slot_field(
        self,
        field: Any,
        raw_field: Any,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Process a SLOT field and add to collection.

        Args:
            field: The field descriptor
            raw_field: The raw field from the schema
            context: The struct generation context
            fields_collection: The collection to add the field to
        """
        slot_field = self.gen_slot(
            raw_field,
            field,
            context.new_type,
            fields_collection.init_choices,
            fields_collection.list_init_choices,
        )

        if slot_field is not None:
            fields_collection.add_slot_field(slot_field)

    def _process_group_field(
        self,
        field: Any,
        raw_field: Any,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Process a GROUP field and add to collection.

        GROUP fields are essentially nested structs that are generated recursively.

        Args:
            field: The field descriptor
            raw_field: The raw field from the schema
            fields_collection: The collection to add the field to
        """
        # Capitalize first letter for group type name
        group_name = field.name[0].upper() + field.name[1:]
        assert group_name != field.name

        # Generate the group struct recursively
        raw_schema = raw_field.schema
        group_type = self.gen_struct(raw_schema, type_name=group_name)
        group_scoped_name = group_type.scoped_name

        # Create hinted variable for the group field
        hinted_variable = helper.TypeHintedVariable(
            helper.sanitize_name(field.name),
            [helper.TypeHint(group_scoped_name, primary=True)],
        )
        hinted_variable.add_builder_from_primary_type()
        hinted_variable.add_reader_from_primary_type()

        # Add to collections
        fields_collection.add_slot_field(hinted_variable)
        fields_collection.add_init_choice(helper.sanitize_name(field.name), group_scoped_name)

    def _process_struct_fields(self, schema: _StructSchema, context: StructGenerationContext) -> StructFieldsCollection:
        """Process all fields in a struct and collect field metadata.

        Args:
            schema: The struct schema
            context: The generation context

        Returns:
            Collection of processed fields and metadata
        """
        fields_collection = StructFieldsCollection()

        for field, raw_field in zip(schema.node.struct.fields, schema.as_struct().fields_list):
            field_type = field.which()

            if field_type == capnp_types.CapnpFieldType.SLOT:
                self._process_slot_field(field, raw_field, context, fields_collection)
            elif field_type == capnp_types.CapnpFieldType.GROUP:
                self._process_group_field(field, raw_field, fields_collection)
            else:
                raise AssertionError(f"{schema.node.displayName}: {field.name}: {field.which()}")

        return fields_collection

    def _generate_nested_reader_class(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Generate Reader class nested inside the main struct class.

        Args:
            context: The generation context
            fields_collection: The processed fields collection
        """
        # Build the class declaration WITHOUT Generic parameters (nested classes don't repeat them)
        reader_class_declaration = helper.new_class_declaration("Reader", parameters=[])

        # Add the class declaration to the current scope (the struct scope)
        self.scope.add(reader_class_declaration)

        # Create a new scope for the Reader class, explicitly using current scope as parent
        self.new_scope("Reader", context.schema.node, register=False, parent_scope=self.scope)

        self._gen_struct_reader_class(
            fields_collection.slot_fields,
            context.new_type,
            context.registered_params,
            "Reader",  # Use simple name since it's nested
            context.scoped_builder_type_name,
            context.schema,
        )

        self.return_from_scope()

    def _generate_nested_builder_class(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Generate Builder class nested inside the main struct class.

        Args:
            context: The generation context
            fields_collection: The processed fields collection
        """
        # Build the class declaration WITHOUT Generic parameters (nested classes don't repeat them)
        builder_class_declaration = helper.new_class_declaration("Builder", parameters=[])

        # Add the class declaration to the current scope (the struct scope)
        self.scope.add(builder_class_declaration)

        # Create a new scope for the Builder class, explicitly using current scope as parent
        self.new_scope("Builder", context.schema.node, register=False, parent_scope=self.scope)

        self._gen_struct_builder_class(
            fields_collection.slot_fields,
            fields_collection.init_choices,
            fields_collection.list_init_choices,
            context.new_type,
            context.registered_params,
            "Builder",  # Use simple name since it's nested
            context.scoped_builder_type_name,
            context.scoped_reader_type_name,
            context.schema,
        )

        self.return_from_scope()

    def _generate_reader_class_with_scope(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Generate reader class with automatic scope management.

        Args:
            context: The generation context
            fields_collection: The processed fields collection
        """
        self.new_scope(context.reader_type_name, context.schema.node, register=False)

        self._gen_struct_reader_class(
            fields_collection.slot_fields,
            context.new_type,
            context.registered_params,
            context.reader_type_name,
            context.scoped_builder_type_name,
            context.schema,
        )

        self.return_from_scope()

    def _generate_builder_class_with_scope(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
    ) -> None:
        """Generate builder class with automatic scope management.

        Args:
            context: The generation context
            fields_collection: The processed fields collection
        """
        self.new_scope(context.builder_type_name, context.schema.node, register=False)

        self._gen_struct_builder_class(
            fields_collection.slot_fields,
            fields_collection.init_choices,
            fields_collection.list_init_choices,
            context.new_type,
            context.registered_params,
            context.builder_type_name,
            context.scoped_builder_type_name,
            context.scoped_reader_type_name,
            context.schema,
        )

        self.return_from_scope()

    def _generate_struct_classes(
        self,
        context: StructGenerationContext,
        fields_collection: StructFieldsCollection,
        class_declaration: str,
    ) -> None:
        """Generate base class with nested Reader and Builder classes for the struct.

        Args:
            context: Generation context with names and metadata
            fields_collection: Processed fields and init choices
            class_declaration: The class declaration string
        """
        # Add TypeAlias declarations at the same level as the class
        # These allow using InnerBuilder instead of Inner.Builder for convenience
        if self.scope.parent:
            self._add_typing_import("TypeAlias")
            self.scope.parent.add(f"{context.builder_type_name}: TypeAlias = {context.type_name}.Builder")
            self.scope.parent.add(f"{context.reader_type_name}: TypeAlias = {context.type_name}.Reader")

        # Add class declaration after nested types are generated
        if self.scope.parent:
            self.scope.parent.add(class_declaration)

        # Generate nested Reader class first (inside the main struct class)
        self._generate_nested_reader_class(context, fields_collection)

        # Generate nested Builder class (inside the main struct class)
        self._generate_nested_builder_class(context, fields_collection)

        # Generate base class methods (static methods, to_dict, etc.)
        self._gen_struct_base_class(
            fields_collection.slot_fields,
            fields_collection.init_choices,
            context.schema,
            context.scoped_reader_type_name,
            context.scoped_builder_type_name,
        )

        self.return_from_scope()

    def gen_struct(self, schema: _StructSchema, type_name: str = "") -> CapnpType:  # noqa: C901
        """Generate a `struct` object.

        This orchestrator delegates to specialized methods for clarity and testability.

        Args:
            schema (_StructSchema): The schema to generate the `struct` object out of.
            type_name (str, optional): A type name to override the display name of the struct. Defaults to "".

        Returns:
            Type: The `struct`-type module that was generated.
        """
        assert schema.node.which() == capnp_types.CapnpElementType.STRUCT

        # Phase 1: Setup and initialization
        context, class_declaration = self._setup_struct_generation(schema, type_name)
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

        # Phase 2: Generate nested types (must be done before field processing)
        self._generate_nested_types(schema, context.type_name)

        # Phase 3: Process all struct fields
        fields_collection = self._process_struct_fields(schema, context)

        # Phase 4: Generate the three class variants
        self._generate_struct_classes(context, fields_collection, class_declaration)

        return context.new_type

    # ===== Interface Generation Helper Methods (Phase 2 Extraction) =====

    def _setup_interface_generation(self, schema: _StructSchema) -> InterfaceGenerationContext | None:
        """Setup interface generation by checking imports and preparing context.

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

        # Get display name
        name = helper.get_display_name(schema)

        # Register type
        parent_scope = self.scopes_by_id.get(schema.node.scopeId, self.scope.root)
        registered_type = self.register_type(schema.node.id, schema, name=name, scope=parent_scope)

        # Add typing imports
        self._add_typing_import("Protocol")
        self._add_typing_import("Iterator")
        self._add_typing_import("Any")

        # Collect base classes
        base_classes = self._collect_interface_base_classes(schema)

        # Create and return context
        return InterfaceGenerationContext.create(
            schema=schema,
            name=name,
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
            runtime_iface = self._module
            for s in self.scope.trace:
                if s.is_root:
                    continue
                runtime_iface = getattr(runtime_iface, s.name)

            method_items = runtime_iface.schema.methods.items()

            return [MethodInfo.from_runtime_method(method_name, method) for method_name, method in method_items]
        except Exception as e:
            logger.debug(f"Could not enumerate methods for {context.name}: {e}")
            return []

    def _add_enum_literal_union(self, field_obj, base_type: str) -> str:
        """Add Literal union for enum types.

        Args:
            field_obj: The field object containing enum type info
            base_type: The base enum type name

        Returns:
            Type string with Literal union added, or base_type if failed
        """
        try:
            enum_type_id = field_obj.slot.type.enum.typeId
            enum_type = self.get_type_by_id(enum_type_id)

            if enum_type and enum_type.schema:
                enum_values = [e.name for e in enum_type.schema.node.enum.enumerants]
                literal_values = ", ".join(f'"{v}"' for v in enum_values)
                literal_type = f"Literal[{literal_values}]"
                self._add_typing_import("Literal")
                return f"{base_type} | {literal_type}"
        except Exception as e:
            logger.debug(f"Could not add enum literals: {e}")

        return base_type

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

            # Handle ENUM: add Literal union
            if field_type == capnp_types.CapnpElementType.ENUM:
                client_type = self._add_enum_literal_union(field_obj, base_type)
                server_type = client_type
                request_type = client_type

            # Handle STRUCT: add dict union for client, Reader for server, Builder for request
            elif field_type == capnp_types.CapnpElementType.STRUCT:
                reader_type = self._build_nested_reader_type(base_type)
                builder_type = self._build_nested_builder_type(base_type)
                client_type = f"{base_type} | dict[str, Any]"
                server_type = reader_type
                request_type = builder_type  # Request fields use Builder type

            # Handle LIST: check for struct lists
            elif field_type == capnp_types.CapnpElementType.LIST:
                self._add_typing_import("Sequence")
                element_type = field_obj.slot.type.list.elementType.which()
                if element_type == capnp_types.CapnpElementType.STRUCT:
                    # Get element type name
                    elem_type_name = self.get_type_name(field_obj.slot.type.list.elementType)
                    elem_reader_type = self._build_nested_reader_type(elem_type_name)
                    client_type = f"Sequence[{elem_type_name}] | Sequence[dict[str, Any]]"
                    server_type = f"Sequence[{elem_reader_type}]"
                    request_type = client_type

            # Handle INTERFACE: add Server union
            elif field_type == capnp_types.CapnpElementType.INTERFACE:
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
        if not method_info.result_fields:
            return "None", False

        # Check if result schema is a direct struct return (not a synthetic $Results struct)
        # When you write `method() -> Struct`, pycapnp gives you the Struct schema directly
        # When you write `method() -> (field: Type)`, pycapnp creates a synthetic "method$Results" schema
        is_direct_struct = False
        if method_info.result_schema is not None:
            display_name = method_info.result_schema.node.displayName
            is_direct_struct = not display_name.endswith("$Results")

        if is_direct_struct:
            # Direct struct return: use Result Protocol with struct's fields expanded
            result_class_name = f"{helper.sanitize_name(method_info.method_name).title()}Result"
            return result_class_name, True

        # Named field return (single or multiple): use Result Protocol
        result_class_name = f"{helper.sanitize_name(method_info.method_name).title()}Result"
        return result_class_name, False

    def _get_list_parameters(
        self,
        method_info: MethodInfo,
        parameters: list[ParameterInfo],
    ) -> list[tuple[str, str, bool]]:
        """Extract list parameters that need init() overloads.

        Args:
            method_info: Information about the method
            parameters: List of processed parameters

        Returns:
            List of (field_name, element_type, needs_builder) tuples
        """
        list_params = []

        if method_info.param_schema is None:
            return list_params

        for param in parameters:
            try:
                field_obj = next(f for f in method_info.param_schema.node.struct.fields if f.name == param.name)

                if field_obj.slot.type.which() == capnp_types.CapnpElementType.LIST:
                    element_type_obj = field_obj.slot.type.list.elementType
                    element_type_name = self.get_type_name(element_type_obj)
                    needs_builder = element_type_obj.which() == capnp_types.CapnpElementType.STRUCT
                    list_params.append((param.name, element_type_name, needs_builder))
            except Exception:
                continue

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
        struct_params = []

        if method_info.param_schema is None:
            return struct_params

        for param in parameters:
            try:
                field_obj = next(f for f in method_info.param_schema.node.struct.fields if f.name == param.name)

                if field_obj.slot.type.which() == capnp_types.CapnpElementType.STRUCT:
                    struct_type_name = self.get_type_name(field_obj.slot.type)
                    # Get the Builder type for the struct
                    builder_type = self._build_scoped_builder_type(struct_type_name)
                    struct_params.append((param.name, builder_type))
            except Exception:
                continue

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
        lines = [f"def {method_name}({param_str}) -> {wrapped_result_type}: ..."]

        return lines

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
        lines = []

        # Class declaration
        lines.append(f"class {request_class_name}(Protocol):")

        # Add parameter fields
        for param in parameters:
            lines.append(f"    {param.name}: {param.request_type}")

        # Collect parameters that need init() overloads
        list_params = self._get_list_parameters(method_info, parameters)
        struct_params = self._get_struct_parameters(method_info, parameters)

        # Add init() overloads if there are list or struct parameters
        if list_params or struct_params:
            self._add_typing_import("overload")
            self._add_typing_import("Literal")

            # Add list init overloads
            if list_params:
                self._add_typing_import("Sequence")
                for field_name, element_type, needs_builder in list_params:
                    lines.append("    @overload")
                    if needs_builder:
                        element_type_for_list = self._build_scoped_builder_type(element_type)
                    else:
                        element_type_for_list = element_type
                    lines.append(
                        f'    def init(self, name: Literal["{field_name}"], '
                        f"size: int = ...) -> Sequence[{element_type_for_list}]: ..."
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
        is_direct_struct_return: bool,
    ) -> list[str]:
        """Generate Result Protocol class for a method.

        Args:
            method_info: Information about the method
            result_type: The result type name (unscoped)
            is_direct_struct_return: Whether this is a direct struct return

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
            union_fields = []

            # Add the struct's fields
            if method_info.result_schema is not None:
                # Check for union
                struct_node = method_info.result_schema.node.struct
                for field_obj in struct_node.fields:
                    if field_obj.discriminantValue != 65535:  # Field is part of a union
                        has_union = True
                        union_fields.append(field_obj.name)

                for rf in method_info.result_fields:
                    try:
                        field_obj = next(f for f in struct_node.fields if f.name == rf)
                        field_type = self.get_type_name(field_obj.slot.type)

                        # For struct types, accept both Builder and Reader in Result Protocol
                        field_type_enum = field_obj.slot.type.which()
                        if field_type_enum == capnp_types.CapnpElementType.STRUCT:
                            builder_type = self._build_nested_builder_type(field_type)
                            reader_type = self._build_nested_reader_type(field_type)
                            field_type = f"{builder_type} | {reader_type}"
                        elif field_type_enum == capnp_types.CapnpElementType.INTERFACE:
                            # For interface types, use the Client class (capabilities are always clients)
                            field_type = f"{field_type}Client"
                        elif field_type_enum == capnp_types.CapnpElementType.LIST:
                            # For lists of structs, accept both Builder and Reader for elements
                            element_type_obj = field_obj.slot.type.list.elementType
                            if element_type_obj.which() == capnp_types.CapnpElementType.STRUCT:
                                element_type_name = self.get_type_name(element_type_obj)
                                element_builder = self._build_nested_builder_type(element_type_name)
                                element_reader = self._build_nested_reader_type(element_type_name)
                                field_type = field_type.replace(
                                    element_type_name, f"{element_builder} | {element_reader}"
                                )

                        lines.append(f"    {rf}: {field_type}")
                    except Exception:
                        lines.append(f"    {rf}: Any")

                # Add which() method if the struct has a union
                if has_union and union_fields:
                    self._add_typing_import("Literal")
                    union_literal = ", ".join([f'"{f}"' for f in union_fields])
                    lines.append(f"    def which(self) -> Literal[{union_literal}]: ...")

            return lines

        # For void methods (no result fields), no Result Protocol
        if not method_info.result_fields:
            return []

        # For single or multiple named fields, generate Result Protocol
        # This handles both `method() -> (field: Type)` and `method() -> (a: X, b: Y)`
        lines = []
        result_class_name = result_type

        # Class declaration - Protocol that is Awaitable and has result fields
        self._add_typing_import("Awaitable")
        lines.append(f"class {result_class_name}(Awaitable[{result_class_name}], Protocol):")

        # Add result fields with Builder | Reader types for structs
        if method_info.result_schema is not None:
            for rf in method_info.result_fields:
                try:
                    field_obj = next(f for f in method_info.result_schema.node.struct.fields if f.name == rf)
                    field_type = self.get_type_name(field_obj.slot.type)

                    # For struct types, accept both Builder and Reader in Result Protocol
                    field_type_enum = field_obj.slot.type.which()
                    if field_type_enum == capnp_types.CapnpElementType.STRUCT:
                        builder_type = self._build_nested_builder_type(field_type)
                        reader_type = self._build_nested_reader_type(field_type)
                        field_type = f"{builder_type} | {reader_type}"
                    elif field_type_enum == capnp_types.CapnpElementType.INTERFACE:
                        # For interface types, use the Client class (capabilities are always clients)
                        field_type = f"{field_type}Client"
                    elif field_type_enum == capnp_types.CapnpElementType.LIST:
                        # For lists of structs, accept both Builder and Reader for elements
                        element_type_obj = field_obj.slot.type.list.elementType
                        if element_type_obj.which() == capnp_types.CapnpElementType.STRUCT:
                            element_type_name = self.get_type_name(element_type_obj)
                            element_builder = self._build_nested_builder_type(element_type_name)
                            element_reader = self._build_nested_reader_type(element_type_name)
                            field_type = field_type.replace(element_type_name, f"{element_builder} | {element_reader}")

                    lines.append(f"    {rf}: {field_type}")
                except Exception:
                    lines.append(f"    {rf}: Any")

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
        if interface_path:
            scoped_request_class = f"{interface_path}.{request_class_name}"
        else:
            scoped_request_class = request_class_name

        # Build parameter list (similar to client method)
        param_list = ["self"] + [p.to_request_param() for p in parameters]
        param_str = ", ".join(param_list)

        lines = [f"def {method_name}_request({param_str}) -> {scoped_request_class}: ..."]

        return lines

    def _get_server_method_return_type(
        self,
        method_info: MethodInfo,
    ) -> str:
        """Get the return type for a server method (base type for single field).

        For single-field results, returns the field type (base type, not Builder).
        For multi-field results, returns empty string (must use _context.results).

        Args:
            method_info: Information about the method

        Returns:
            The field type for single-field results, empty string otherwise
        """
        if not method_info.result_fields or len(method_info.result_fields) != 1:
            return ""

        if method_info.result_schema is None:
            return ""

        field_name = method_info.result_fields[0]
        try:
            field_obj = next(f for f in method_info.result_schema.node.struct.fields if f.name == field_name)

            # Get base type (not Builder, not Reader)
            field_type = self.get_type_name(field_obj.slot.type)
            return field_type

        except Exception as e:
            logger.debug(f"Could not get server return type for {field_name}: {e}")
            return ""

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

        Args:
            method_info: Information about the method

        Returns:
            List of (field_name, field_type) tuples
        """
        fields = []

        if not method_info.result_fields or method_info.result_schema is None:
            return fields

        for field_name in method_info.result_fields:
            try:
                field_obj = next(f for f in method_info.result_schema.node.struct.fields if f.name == field_name)

                # Get base type
                field_type = self.get_type_name(field_obj.slot.type)

                # For structs, accept both Builder and Reader
                field_type_enum = field_obj.slot.type.which()
                if field_type_enum == capnp_types.CapnpElementType.STRUCT:
                    builder_type = self._build_nested_builder_type(field_type)
                    reader_type = self._build_nested_reader_type(field_type)
                    field_type = f"{builder_type} | {reader_type}"
                # For interfaces in NamedTuples, server returns Interface.Server
                elif field_type_enum == capnp_types.CapnpElementType.INTERFACE:
                    field_type = f"{field_type}.Server"

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
        is_direct_struct_return: bool,
    ) -> str:
        """Generate server method signature for Server class.

        Server methods return NamedTuple results or None.
        - For void methods: return Awaitable[None]
        - For methods with results: return Awaitable[Server.XxxResult | None]

        Args:
            method_info: Information about the method
            parameters: List of processed parameters
            result_type: The result type (Result Protocol name)
            is_direct_struct_return: Whether this is a direct struct return

        Returns:
            Single-line server method signature
        """
        method_name = helper.sanitize_name(method_info.method_name)

        # Generate CallContext type name - it's inside Server class
        scope_path = self._get_scope_path()
        context_class_name = f"{method_name.title()}CallContext"
        if scope_path:
            # CallContext is now under Server, not at interface level
            context_type = f"{scope_path}.Server.{context_class_name}"
        else:
            context_type = f"Server.{context_class_name}"

        # Server methods have: self, params..., _context: CallContext, **kwargs
        param_parts = ["self"]
        param_parts.extend([p.to_server_param() for p in parameters])
        param_parts.append(f"_context: {context_type}")
        param_parts.append("**kwargs: Any")
        param_str = ", ".join(param_parts)

        # Determine return type
        self._add_typing_import("Awaitable")

        if not method_info.result_fields:
            # Void method - returns Awaitable[None]
            return_type_str = "Awaitable[None]"
        else:
            # Check if this is a single primitive/interface return
            is_single_primitive_or_interface = False
            single_field_type = None

            if len(method_info.result_fields) == 1 and method_info.result_schema is not None:
                field_name = method_info.result_fields[0]
                try:
                    field_obj = next(f for f in method_info.result_schema.node.struct.fields if f.name == field_name)
                    field_type_enum = field_obj.slot.type.which()

                    # Check if it's a primitive or interface
                    # Primitives are returned as strings like "bool", "float64", etc.
                    # Interfaces are the INTERFACE constant
                    if isinstance(field_type_enum, str) and field_type_enum in (
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
                except Exception:
                    pass

            # Generate return type - use NamedTuple with "Tuple" suffix
            if scope_path:
                full_server_path = f"{scope_path}.Server.{result_type}Tuple"
            else:
                full_server_path = f"Server.{result_type}Tuple"

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
        if scope_path:
            # CallContext is now under Server, not at interface level
            context_type = f"{scope_path}.Server.{context_class_name}"
        else:
            context_type = f"Server.{context_class_name}"

        # _context variant only takes context parameter
        param_str = f"self, context: {context_type}"

        # _context methods can return promises but not direct values (other than None)
        self._add_typing_import("Awaitable")
        return_type_str = "Awaitable[None]"

        return f"    def {method_name}_context({param_str}) -> {return_type_str}: ..."

    def _generate_results_builder_protocol(
        self,
        method_info: MethodInfo,
        result_fields_info: list[tuple[str, str]],
    ) -> list[str]:
        """Generate ResultsBuilder Protocol for server context.results.

        Args:
            method_info: Information about the method
            result_fields_info: List of (field_name, builder_type) tuples

        Returns:
            List of lines for ResultsBuilder Protocol
        """
        method_name = helper.sanitize_name(method_info.method_name)
        results_builder_name = f"{method_name.title()}ResultsBuilder"

        lines = [helper.new_class_declaration(results_builder_name, ["Protocol"])]

        for field_name, builder_type in result_fields_info:
            lines.append(f"    {field_name}: {builder_type}")

        return lines

    def _generate_callcontext_protocol(
        self,
        method_info: MethodInfo,
        has_results: bool,
        result_type_for_context: str | None = None,
    ) -> list[str]:
        """Generate CallContext Protocol for server _context parameter.

        Args:
            method_info: Information about the method
            has_results: Whether the method has results
            result_type_for_context: Result type name (points to interface-level Protocol)

        Returns:
            List of lines for CallContext Protocol
        """
        method_name = helper.sanitize_name(method_info.method_name)
        context_name = f"{method_name.title()}CallContext"

        lines = [helper.new_class_declaration(context_name, ["Protocol"])]

        scope_path = self._get_scope_path()

        # CallContext.params points to the Request Protocol at interface level
        request_type = f"{method_name.title()}Request"
        if scope_path:
            fully_qualified_params = f"{scope_path}.{request_type}"
        else:
            fully_qualified_params = request_type
        lines.append(f"    params: {fully_qualified_params}")

        # CallContext.results points to the Result Protocol at interface level (only if method has results)
        if has_results:
            if result_type_for_context:
                if scope_path:
                    # Use interface-level Result Protocol
                    fully_qualified_results = f"{scope_path}.{result_type_for_context}"
                else:
                    fully_qualified_results = result_type_for_context
            else:
                # Shouldn't happen, but fallback
                fully_qualified_results = "Any"

            lines.append(f"    results: {fully_qualified_results}")
        # Void methods have no results field in CallContext

        return lines

    def _process_result_fields_for_server(
        self,
        method_info: MethodInfo,
    ) -> list[tuple[str, str]]:
        """Process result fields to get Builder|Reader types for server.

        Args:
            method_info: Information about the method

        Returns:
            List of (field_name, type) tuples where type can be Builder | Reader for structs
        """
        result_fields_info = []

        if not method_info.result_fields or method_info.result_schema is None:
            return result_fields_info

        for field_name in method_info.result_fields:
            try:
                field_obj = next(f for f in method_info.result_schema.node.struct.fields if f.name == field_name)

                field_type = self.get_type_name(field_obj.slot.type)
                result_type = field_type

                field_type_enum = field_obj.slot.type.which()

                # For structs, accept both Builder and Reader
                if field_type_enum == capnp_types.CapnpElementType.STRUCT:
                    builder_type = self._build_nested_builder_type(field_type)
                    reader_type = self._build_nested_reader_type(field_type)
                    result_type = f"{builder_type} | {reader_type}"

                # For lists of structs, accept both Builder and Reader for elements
                elif field_type_enum == capnp_types.CapnpElementType.LIST:
                    element_type_obj = field_obj.slot.type.list.elementType
                    if element_type_obj.which() == capnp_types.CapnpElementType.STRUCT:
                        element_type_name = self.get_type_name(element_type_obj)
                        element_builder = self._build_nested_builder_type(element_type_name)
                        element_reader = self._build_nested_reader_type(element_type_name)
                        # Replace element type with Builder | Reader union
                        result_type = result_type.replace(element_type_name, f"{element_builder} | {element_reader}")

                result_fields_info.append((field_name, result_type))

            except Exception as e:
                logger.debug(f"Could not process result field {field_name}: {e}")
                result_fields_info.append((field_name, "Any"))

        return result_fields_info

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
        # - All interfaces (depth >= 1): prefix with full interface path (e.g., "TestIface.PingResult" or "Metadata.Supported.CategoriesResult")
        # - This is necessary because Result classes are nested inside the interface class
        scope_depth = len([s for s in self.scope.trace if not s.is_root])
        interface_path = self._get_scope_path()

        if scope_depth >= 1 and interface_path and result_type != "None":
            # Interface at any depth: prefix with full interface path for proper scoping
            scoped_result_type = f"{interface_path}.{result_type}"
        else:
            # No interface scope (shouldn't happen for interface methods)
            scoped_result_type = result_type

        # Generate client method
        client_lines = self._generate_client_method(method_info, parameters, scoped_result_type)
        collection.set_client_method(client_lines)

        # Generate Request Protocol
        request_lines = self._generate_request_protocol(method_info, parameters, scoped_result_type)
        collection.set_request_class(request_lines)

        # Generate Result Protocol (if needed)
        result_lines = self._generate_result_protocol(method_info, result_type, is_direct_struct_return)
        collection.set_result_class(result_lines)

        # Generate CallContext for server - points to Result Protocol at interface level
        if is_direct_struct_return:
            # Direct struct return: CallContext.results points to interface-level Result Protocol
            has_results = True
            callcontext_lines = self._generate_callcontext_protocol(
                method_info, has_results, result_type_for_context=result_type
            )
            for line in callcontext_lines:
                collection.server_context_lines.append(line)
        else:
            # Named field return or void: CallContext.results points to Result Protocol
            has_results = bool(method_info.result_fields)
            # Pass result_type so CallContext can reference the Protocol
            result_type_for_ctx = f"{method_info.method_name.title()}Result" if has_results else None
            callcontext_lines = self._generate_callcontext_protocol(
                method_info, has_results, result_type_for_context=result_type_for_ctx
            )
            for line in callcontext_lines:
                collection.server_context_lines.append(line)

        # Generate _request helper
        helper_lines = self._generate_request_helper_method(method_info, parameters)
        collection.set_request_helper(helper_lines)

        # Generate server method signature
        server_sig = self._generate_server_method_signature(
            method_info, parameters, result_type, is_direct_struct_return
        )
        collection.set_server_method(server_sig)
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
    ) -> None:
        """Generate the Server class with all server methods.

        Args:
            context: The interface generation context
            server_collection: Collection of server methods and NamedTuples
        """
        # Build Server base classes (superclass Servers)
        server_base_classes = []
        if context.schema.node.which() == "interface":
            interface_node = context.schema.node.interface
            for superclass in interface_node.superclasses:
                try:
                    superclass_type = self.get_type_by_id(superclass.id)
                    server_base_classes.append(f"{superclass_type.scoped_name}.Server")
                except KeyError:
                    logger.debug(f"Could not resolve superclass {superclass.id} for Server inheritance")

        # Only generate Server class if we have methods OR inheritance
        if not server_collection.has_methods() and not server_base_classes:
            return

        # Generate Server class declaration with inheritance
        if server_base_classes:
            server_declaration = helper.new_class_declaration("Server", server_base_classes)
        else:
            server_declaration = helper.new_class_declaration("Server", ["Protocol"])

        self.scope.add(server_declaration)

        # Add NamedTuple result types first
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
                if line.startswith("class "):
                    self.scope.add(f"    {line}")
                elif line.strip():
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

    def gen_interface(self, schema: _StructSchema) -> CapnpType | None:
        """Generate an `interface` definition.

        This orchestrator delegates to specialized methods for clarity and testability.
        Each interface generates:
        - Interface module with nested types and factory methods
        - Separate Client Protocol class with client methods
        - Request/Result Protocol classes for each method
        - Server class with server method signatures

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
            imported_type = self.register_import(schema)
            return imported_type

        # Open interface scope (no Protocol - this is _InterfaceModule)
        self.new_scope(
            context.name,
            context.schema.node,
            scope_heading=f"class {context.name}:",
        )

        # Phase 2: Generate nested types
        self._generate_nested_types_for_interface(context.schema, context.name)

        # Phase 3: Enumerate and process methods
        methods = self._enumerate_interface_methods(context)
        server_collection = ServerMethodsCollection()
        client_method_collection = []  # Collect client methods for separate Client class
        request_helper_collection = []  # Collect request helpers for Client class

        for method_info in methods:
            method_collection = self._process_interface_method(method_info, server_collection)

            # Collect client methods and request helpers for Client class (don't add to interface)
            client_method_collection.extend(method_collection.client_method_lines)
            request_helper_collection.extend(method_collection.request_helper_lines)

            # Add Request/Result classes to interface module
            for line in method_collection.request_class_lines:
                self.scope.add(line)

            for line in method_collection.result_class_lines:
                self.scope.add(line)

            # Store context lines for Server class (not at interface level)
            server_collection.add_context_lines(method_collection.server_context_lines)

        # Phase 3.5: Add _new_client class method to interface module
        # Only add if Server class will be generated (has methods or inheritance)
        server_base_classes = []
        if context.schema.node.which() == "interface":
            interface_node = context.schema.node.interface
            for superclass in interface_node.superclasses:
                try:
                    superclass_type = self.get_type_by_id(superclass.id)
                    server_base_classes.append(f"{superclass_type.scoped_name}.Server")
                except KeyError:
                    logger.debug(f"Could not resolve superclass {superclass.id} for _new_client check")

        # Only add _new_client if Server class will exist
        if server_collection.has_methods() or server_base_classes:
            # _new_client returns Client class
            client_class_name = f"{context.name}Client"
            self._add_new_client_method(
                context.name, context.base_classes, context.schema, client_return_type=client_class_name
            )

        # Phase 4: Generate Server class
        self._generate_server_class(context, server_collection)

        # Track NamedTuples globally for .py file export
        if server_collection.namedtuples:
            # Use scoped name to handle nested interfaces correctly
            interface_full_name = context.registered_type.scoped_name
            if interface_full_name not in self._all_server_namedtuples:
                self._all_server_namedtuples[interface_full_name] = {}

            for namedtuple_name, fields in server_collection.namedtuples.items():
                # Extract method name from namedtuple name (remove "Tuple" suffix and convert to method name)
                # e.g., "SaveResultTuple" -> "save"
                method_name = namedtuple_name.replace("ResultTuple", "Result").replace("Result", "").lower()
                if not method_name:
                    # Fallback: use the namedtuple name without Tuple
                    method_name = namedtuple_name.replace("Tuple", "").lower()

                self._all_server_namedtuples[interface_full_name][method_name] = (namedtuple_name, fields)

        # Save parent scope BEFORE closing interface scope
        parent_scope = self.scope.parent if self.scope.parent else self.scope

        # Ensure interface has some content (even if methods failed to generate)
        if not self.scope.lines:
            self.scope.add("...")

        # Close interface scope
        self.return_from_scope()

        # Phase 5: Generate separate Client Protocol class at saved parent scope level
        if server_collection.has_methods() or server_base_classes or client_method_collection:
            # Temporarily set scope to parent, generate client, then restore
            current_scope = self.scope
            self.scope = parent_scope
            self._generate_client_class(
                context, client_method_collection, request_helper_collection, server_base_classes
            )
            self.scope = current_scope

            # Track this interface for cast_as overloads with inheritance info
            interface_full_name = context.registered_type.scoped_name
            client_full_name = f"{interface_full_name}Client"

            # Build list of base client names from server_base_classes
            base_client_names = []
            for server_base in server_base_classes:
                if ".Server" in server_base:
                    interface_name = server_base.replace(".Server", "")
                    base_client_names.append(f"{interface_name}Client")

            self._all_interfaces[interface_full_name] = (client_full_name, base_client_names)

        return context.registered_type

    def _generate_client_class(
        self,
        context: InterfaceGenerationContext,
        client_method_lines: list[str],
        request_helper_lines: list[str],
        server_base_classes: list[str],
    ) -> None:
        """Generate the Client Protocol class with all client methods.

        Args:
            context: The interface generation context
            client_method_lines: List of client method lines to add
            request_helper_lines: List of request helper method lines to add
            server_base_classes: List of server base classes for inheritance resolution
        """
        client_class_name = f"{context.name}Client"

        # Build client base classes - inherit from superclass Clients
        client_base_classes = []
        has_parent_clients = False
        for server_base in server_base_classes:
            # Extract interface name from Server type and build Client type
            # e.g., "Calculator.Server" -> "CalculatorClient"
            # e.g., "Identifiable.Server" -> "IdentifiableClient"
            if ".Server" in server_base:
                interface_name = server_base.replace(".Server", "")
                client_base_classes.append(f"{interface_name}Client")
                has_parent_clients = True

        # Only add Protocol if there are no parent Client classes
        if not has_parent_clients:
            client_base_classes.insert(0, "Protocol")

        # Generate Client class declaration
        self.scope.add(helper.new_class_declaration(client_class_name, client_base_classes))

        # Add client methods and request helpers with proper indentation
        all_method_lines = client_method_lines + request_helper_lines
        if all_method_lines:
            for line in all_method_lines:
                # Methods come without indentation, add class-level indentation
                self.scope.add(f"    {line}")
        else:
            # Empty client class (inherits everything from superclasses)
            self.scope.add("    ...")

    def generate_nested(self, schema: _StructSchema) -> None:
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

    def register_import(self, schema: _StructSchema) -> CapnpType | None:
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

        # First check if this schema is a top-level module in the registry
        if schema.node.id in self._module_registry:
            matching_path = pathlib.Path(self._module_registry[schema.node.id][0])
        else:
            # Find the path of the parent module, from which this schema is imported.
            # We need to search recursively through nested nodes since schemas can be deeply nested
            def search_nested_nodes(schema_obj, target_id):
                """Recursively search for a target ID in nested nodes."""
                for nested_node in schema_obj.node.nestedNodes:
                    if nested_node.id == target_id:
                        return True
                    # Recursively search deeper by getting the nested schema
                    try:
                        nested_schema = schema_obj.get_nested(nested_node.name)
                        if search_nested_nodes(nested_schema, target_id):
                            return True
                    except Exception:
                        # If we can't get nested schema, just continue
                        pass
                return False

            for module_id, (path, module) in self._module_registry.items():
                if search_nested_nodes(module.schema, schema.node.id):
                    matching_path = pathlib.Path(path)
                    break

        # Since this is an import, there must be a parent module.
        assert matching_path is not None, f"The module named {module_name} was not provided to the stub generator."

        # Track this imported module path for later use in capnp.load imports
        self._imported_module_paths.add(matching_path)

        # Find the relative path to go from the parent module, to this imported module.
        common_path = os.path.commonpath([self._module_path, matching_path])

        relative_module_path = self._module_path.relative_to(common_path)
        relative_import_path = matching_path.relative_to(common_path)

        # Shape the relative path to a relative Python import statement.
        python_import_path = "." * len(relative_module_path.parents) + helper.replace_capnp_suffix(
            ".".join(relative_import_path.parts)
        )

        # Import the regular definition name, alongside its builder and reader for structs
        # Enums and Interfaces don't have Builder/Reader variants
        # For deeply nested types (e.g., Params.Irrigation.Parameters), we import the root parent
        # and Python will resolve the full path via attribute access

        # Check if this is a nested type (contains dots)
        if "." in definition_name:
            # Get the root parent (e.g., "Params" from "Params.Irrigation.Parameters")
            root_name = definition_name.split(".")[0]
            # Import only the root parent
            self._add_import(f"from {python_import_path} import {root_name}")
        else:
            # Regular non-nested import
            node_type = schema.node.which()
            if node_type in (
                capnp_types.CapnpElementType.ENUM,
                capnp_types.CapnpElementType.INTERFACE,
            ):
                if node_type == capnp_types.CapnpElementType.INTERFACE:
                    # For interfaces, import both the interface module and the Client class
                    client_name = f"{definition_name}Client"
                    self._add_import(f"from {python_import_path} import {definition_name}, {client_name}")
                else:
                    # Enums just need the enum itself
                    self._add_import(f"from {python_import_path} import {definition_name}")
            else:
                # Structs now have nested Reader/Builder classes, so just import the struct
                self._add_import(f"from {python_import_path} import {definition_name}")

        return self.register_type(schema.node.id, schema, name=definition_name, scope=self.scope.root)

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
        schema: _StructSchema,
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
        self, name: str, node: Any, scope_heading: str = "", register: bool = True, parent_scope: Scope | None = None
    ) -> Scope:
        """Creates a new scope below the scope of the provided node.

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

    def get_type_name(self, type_reader: _DynamicStructReader) -> str:
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

        element_type: Any | None = None

        if type_reader_type == capnp_types.CapnpElementType.STRUCT:
            # Check if the type is registered; if not, try to generate it first
            type_id = type_reader.struct.typeId
            if not self.is_type_id_known(type_id):
                # Try to generate the struct before using it
                try:
                    # Use capnp's internal method to get the schema by ID
                    all_nested = list(self._module.schema.node.nestedNodes)
                    for nested_node in all_nested:
                        if nested_node.id == type_id:
                            nested_schema = self._module.schema.get_nested(nested_node.name)
                            self.generate_nested(nested_schema)
                            break
                except Exception as e:
                    logger.debug(f"Could not pre-generate struct with ID {type_id}: {e}")

            element_type = self.get_type_by_id(type_id)
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

        elif type_reader_type == capnp_types.CapnpElementType.ANY_POINTER:
            # AnyPointer is represented as Any in Python typing
            self._add_typing_import("Any")
            type_name = "Any"
            element_type = None

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

        # Add NamedTuple import if we have server namedtuples
        if self._all_server_namedtuples:
            out.append("from typing import NamedTuple")

        out.append("capnp.remove_import_hook()")
        out.append("here = os.path.dirname(os.path.abspath(__file__))")

        # Determine where the .capnp file is relative to the generated .py file
        if self._output_directory:
            # Output is in a different directory from the schema
            # Calculate relative path from output directory to schema file
            try:
                rel_to_schema = os.path.relpath(self._module_path, self._output_directory)
                out.append(f'module_file = os.path.abspath(os.path.join(here, "{rel_to_schema}"))')
            except (ValueError, OSError):
                # Fallback for different drives on Windows
                out.append(f'module_file = "{self._module_path.as_posix()}"')
        else:
            # Output is in the same directory as the schema (default behavior)
            out.append(f'module_file = os.path.abspath(os.path.join(here, "{self.display_name}"))')

        # Build import_path with relative paths to imported modules
        import_paths = ["here"]

        # Determine the reference point for import paths
        # If output_directory is set, we need paths relative to where the generated file will be
        # Otherwise, paths relative to where the schema file is
        reference_dir = self._output_directory if self._output_directory else self._module_path.parent

        # Add import paths from CLI (-I flags) - these take precedence
        if self._import_paths:
            for import_path_dir in sorted(self._import_paths):
                try:
                    # Calculate relative path from reference directory to import path
                    rel_path = os.path.relpath(import_path_dir, reference_dir)
                    # Only add if it's not the same directory (not just ".")
                    if rel_path != ".":
                        import_paths.append(f'os.path.join(here, "{rel_path}")')
                except (ValueError, OSError):
                    # If relative path calculation fails (e.g., different drives on Windows), skip
                    pass

        # Add paths to imported modules (schemas that import each other)
        if self._imported_module_paths:
            # Calculate relative paths from reference directory to imported modules
            unique_import_dirs: set[str] = set()

            for imported_path in sorted(self._imported_module_paths):
                try:
                    # Get the directory of the imported module
                    imported_dir = imported_path.parent

                    # Calculate relative path from reference directory to imported module's directory
                    rel_path = os.path.relpath(imported_dir, reference_dir)

                    # Only add if it's not the same directory (not just ".")
                    if rel_path != ".":
                        unique_import_dirs.add(rel_path)
                except (ValueError, OSError):
                    # If relative path calculation fails (e.g., different drives on Windows), skip
                    pass

            for rel_path in sorted(unique_import_dirs):
                import_paths.append(f'os.path.join(here, "{rel_path}")')

        out.append(f"import_path = [{', '.join(import_paths)}]")

        for scope in self.scopes_by_id.values():
            if scope.parent is not None and scope.parent.is_root:
                out.append(f"{scope.name} = capnp.load(module_file, imports=import_path).{scope.name}")

        # Add Server.InfoResult NamedTuples for interfaces
        if self._all_server_namedtuples:
            out.append("")
            for interface_name, namedtuples_dict in sorted(self._all_server_namedtuples.items()):
                for method_name, (namedtuple_name, fields) in sorted(namedtuples_dict.items()):
                    # Create NamedTuple and attach to Server class
                    # Use object as type for all fields to avoid import issues in .py file
                    # Type information is in the .pyi file for static type checkers
                    field_list = [f'("{field_name}", object)' for field_name, _ in fields]
                    out.append(
                        f"{interface_name}.Server.{namedtuple_name} = "
                        f"NamedTuple('{namedtuple_name}', [{', '.join(field_list)}])"
                    )

        return "\n".join(out)
