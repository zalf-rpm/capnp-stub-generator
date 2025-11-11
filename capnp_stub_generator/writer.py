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
from typing import TYPE_CHECKING, Any, Literal

import capnp
from capnp.lib.capnp import _DynamicStructReader, _StructSchema

from capnp_stub_generator import capnp_types, helper
from capnp_stub_generator.scope import CapnpType, NoParentError, Scope

capnp.remove_import_hook()

logger = logging.getLogger(__name__)

# Type aliases for capnp types
TypeReader = _DynamicStructReader

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

        self.docstring = f'"""This is an automatically generated stub for `{self._module_path.name}`."""'

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
        """Build Builder type name respecting scoped names and generics.

        Args:
            field_type (str): The base field type (e.g., "MyStruct", "Outer.Inner", or "Env[T]").

        Returns:
            str: The Builder type name (e.g., "MyStructBuilder", "Outer.InnerBuilder", or "EnvBuilder[T]").
        """
        # Check if there's a generic parameter
        if "[" in field_type:
            base_name, generic_part = field_type.split("[", 1)
            # Now handle scoping in the base name
            if "." in base_name:
                parts = base_name.rsplit(".", 1)
                return f"{parts[0]}.{parts[1]}Builder[{generic_part}"
            else:
                return f"{base_name}Builder[{generic_part}"
        elif "." in field_type:
            parts = field_type.rsplit(".", 1)
            return f"{parts[0]}.{parts[1]}Builder"
        else:
            return f"{field_type}Builder"

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

    def _add_from_bytes_methods(self, scoped_reader_type: str):
        """Add from_bytes and from_bytes_packed static methods to current scope.

        Args:
            scoped_reader_type (str): The fully qualified Reader type name.
        """
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
                return_type=helper.new_type_group("Iterator", [scoped_reader_type]),
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
                return_type=scoped_reader_type,
            )
        )

    def _add_read_methods(self, scoped_reader_type: str):
        """Add read and read_packed static methods to current scope.

        Args:
            scoped_reader_type (str): The fully qualified Reader type name.
        """
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
                return_type=scoped_reader_type,
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
                return_type=scoped_reader_type,
            )
        )

    def _add_write_methods(self):
        """Add write and write_packed static methods to current scope."""
        self._add_import("from io import BufferedWriter")

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(
            helper.new_function(
                "write",
                parameters=[helper.TypeHintedVariable("file", [helper.TypeHint("BufferedWriter", primary=True)])],
            )
        )

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(
            helper.new_function(
                "write_packed",
                parameters=[helper.TypeHintedVariable("file", [helper.TypeHint("BufferedWriter", primary=True)])],
            )
        )

    def _add_base_properties(self, slot_fields: list[helper.TypeHintedVariable]):
        """Add read-only properties to base struct class.

        Args:
            slot_fields (list[helper.TypeHintedVariable]): The fields to add as properties.
        """
        for slot_field in slot_fields:
            # Base class uses properties without setters (read-only interface)
            # Use only the primary (base) type, not the union with Reader/Builder
            field_type = slot_field.primary_type_nested
            for line in helper.new_property(slot_field.name, field_type):
                self.scope.add(line)

    def _add_reader_properties(self, slot_fields: list[helper.TypeHintedVariable]):
        """Add read-only properties to Reader class.

        Args:
            slot_fields (list[helper.TypeHintedVariable]): The fields to add as properties.
        """
        for slot_field in slot_fields:
            if slot_field.has_type_hint_with_reader_affix:
                field_copy = copy(slot_field)
                # Get the narrowed Reader-only type for this field
                reader_type = field_copy.get_type_with_affixes([helper.READER_NAME])
                for line in helper.new_property(slot_field.name, reader_type):
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
                    setter_type = field_copy.full_type_nested + " | Sequence[dict[str, Any]]"
                    self._add_typing_import("Sequence")
                    self._add_typing_import("Any")
                else:
                    # For non-list structs
                    getter_type = field_copy.get_type_with_affixes([helper.BUILDER_NAME])
                    setter_type = field_copy.full_type_nested + " | dict[str, Any]"
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
            self._add_import("from capnp import _DynamicListBuilder")
            element_type_for_list = f"{element_type}Builder" if needs_builder else element_type

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
                    return_type=f"_DynamicListBuilder[{element_type_for_list}]",
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

        self.scope.add(helper.new_decorator("staticmethod"))
        self.scope.add(
            helper.new_function(
                "new_message",
                parameters=new_message_params,
                return_type=scoped_builder_type,
            )
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
    ):
        """Generate the Reader class for a struct.

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields.
            new_type (CapnpType): The registered type.
            registered_params (list[str]): Generic type parameters.
            reader_type_name (str): The Reader class name.
            scoped_builder_type (str): Fully qualified Builder type name.
        """
        # Add the reader slot fields as properties
        self._add_reader_properties(slot_fields)

        # Build Reader class declaration with generic params
        reader_params = [new_type.scoped_name]
        if registered_params:
            generic_param = helper.new_type_group("Generic", registered_params)
            reader_params.append(generic_param)
        reader_class_declaration = helper.new_class_declaration(reader_type_name, parameters=reader_params)

        # Add the class declaration to parent scope
        if self.scope.parent:
            self.scope.parent.add(reader_class_declaration)

        # Add as_builder method
        self.scope.add(
            helper.new_function(
                "as_builder",
                parameters=["self"],
                return_type=scoped_builder_type,
            )
        )

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
    ):
        """Generate the Builder class for a struct.

        Args:
            slot_fields (list[TypeHintedVariable]): The struct fields.
            init_choices (list[InitChoice]): Init method overload choices for structs.
            list_init_choices (list[tuple[str, str, bool]]): Init method overload choices for lists.
            new_type (CapnpType): The registered type.
            registered_params (list[str]): Generic type parameters.
            builder_type_name (str): The Builder class name.
            scoped_builder_type (str): Fully qualified Builder type name.
            scoped_reader_type (str): Fully qualified Reader type name.
        """
        # Add all builder slot fields with setters
        self._add_builder_properties(slot_fields)

        # Add from_dict method
        self.scope.add(helper.new_decorator("staticmethod"))
        self._add_typing_import("Any")
        self.scope.add(
            helper.new_function(
                "from_dict",
                parameters=[helper.TypeHintedVariable("dictionary", [helper.TypeHint("dict[str, Any]", primary=True)])],
                return_type=scoped_builder_type,
            )
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

        # Build Builder class declaration with generic params
        builder_params = [new_type.scoped_name]
        if registered_params:
            generic_param = helper.new_type_group("Generic", registered_params)
            builder_params.append(generic_param)
        builder_class_declaration = helper.new_class_declaration(builder_type_name, parameters=builder_params)

        # Add the class declaration to parent scope
        if self.scope.parent:
            self.scope.parent.add(builder_class_declaration)

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

    def _add_new_client_method(self, name: str, base_classes: list[str], schema: _StructSchema):
        """Add _new_client() class method to create capability client from Server.

        Args:
            name (str): The interface name.
            base_classes (list[str]): The interface base classes.
            schema (_StructSchema): The interface schema.
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

        self.scope.add("@classmethod")
        self.scope.add(
            helper.new_function(
                "_new_client",
                parameters=["cls", f"server: {server_param_type}"],
                return_type=fully_qualified_interface,
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
            # For reading: return only the Protocol type
            # For writing (in Builder): accept Protocol | Server
            hints = [helper.TypeHint(type_name, primary=True)]
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
            list_: TypeReader,
        ) -> Iterator[TypeReader]:
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

    def gen_enum_slot(
        self, field: capnp._DynamicStructReader, schema: _StructSchema
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

    # FIXME: refactor for reducing complexity
    def gen_struct(self, schema: _StructSchema, type_name: str = "") -> CapnpType:  # noqa: C901
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
        list_init_choices: list[tuple[str, str, bool]] = []  # Track (field_name, element_type, needs_builder) for lists
        slot_fields: list[helper.TypeHintedVariable] = []

        for field, raw_field in zip(schema.node.struct.fields, schema.as_struct().fields_list):
            field_type = field.which()

            if field_type == capnp_types.CapnpFieldType.SLOT:
                slot_field = self.gen_slot(raw_field, field, new_type, init_choices, list_init_choices)

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
                    helper.sanitize_name(field.name),
                    [helper.TypeHint(group_scoped_name, primary=True)],
                )
                hinted_variable.add_builder_from_primary_type()
                hinted_variable.add_reader_from_primary_type()

                # Don't add type_scope here since we already have the full scoped name

                slot_fields.append(hinted_variable)
                init_choices.append((helper.sanitize_name(field.name), group_scoped_name))

            else:
                raise AssertionError(f"{schema.node.displayName}: {field.name}: {field.which()}")

        # Finally, add the class declaration after the expansion of all nested schemas.
        parent_scope.add(class_declaration)

        # Generate base struct class
        self._gen_struct_base_class(
            slot_fields,
            init_choices,
            schema,
            scoped_new_reader_type_name,
            scoped_new_builder_type_name,
        )

        self.return_from_scope()

        # Generate the reader class
        parent_scope = self.new_scope(new_reader_type_name, schema.node, register=False)

        self._gen_struct_reader_class(
            slot_fields,
            new_type,
            registered_params,
            new_reader_type_name,
            scoped_new_builder_type_name,
        )

        self.return_from_scope()

        # Generate the builder class
        parent_scope = self.new_scope(new_builder_type_name, schema.node, register=False)

        self._gen_struct_builder_class(
            slot_fields,
            init_choices,
            list_init_choices,
            new_type,
            registered_params,
            new_builder_type_name,
            scoped_new_builder_type_name,
            scoped_new_reader_type_name,
        )

        self.return_from_scope()

        return new_type

    def gen_interface(self, schema: _StructSchema) -> CapnpType | None:
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

        # Collect base classes (superclasses + Protocol)
        base_classes = self._collect_interface_base_classes(schema)

        # Open protocol scope
        parent_scope = self.new_scope(name, schema.node, scope_heading=helper.new_class_declaration(name, base_classes))

        # We'll generate a Server class with method signatures after collecting them

        # Generate all nested types (interfaces, structs, enums)
        self._generate_nested_types_for_interface(schema, name)

        # Access runtime interface to enumerate methods (parsed schema lacks methods)
        try:
            runtime_iface = self._module
            for s in self.scope.trace:
                if s.is_root:
                    continue
                runtime_iface = getattr(runtime_iface, s.name)
            methods = runtime_iface.schema.methods.items()
        except Exception as e:
            logger.debug(f"Could not enumerate methods for {name}: {e}")
            methods = []

        # Collect server method signatures to add to Server class
        server_methods: list[str] = []

        # Initialize dict to store NamedTuple info for direct struct returns
        self._server_namedtuples = {}

        for method_name, method in methods:
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

            # Build parameters for client methods (with dict union for structs)
            # and separate parameters for server methods (Reader types only)
            parameters: list[str] = ["self"]
            server_parameters: list[str] = ["self"]

            for pf in param_fields:
                try:
                    if param_schema is not None:
                        field_obj = next(f for f in param_schema.node.struct.fields if f.name == pf)
                        # Use get_type_name to resolve complex types (struct, enum, interface, list)
                        param_type = self.get_type_name(field_obj.slot.type)

                        # Start with base type for server
                        server_param_type = param_type

                        # For enum parameters, also accept string literals (like enum fields do)
                        if field_obj.slot.type.which() == capnp_types.CapnpElementType.ENUM:
                            try:
                                # Get the enum schema to extract literal values
                                enum_type_id = field_obj.slot.type.enum.typeId
                                enum_type = self.get_type_by_id(enum_type_id)
                                # Access the enum schema through the type map
                                if enum_type and enum_type.schema:
                                    enum_values = [e.name for e in enum_type.schema.node.enum.enumerants]
                                    literal_values = ", ".join(f'"{v}"' for v in enum_values)
                                    literal_type = f"Literal[{literal_values}]"
                                    self._add_typing_import("Literal")
                                    param_type = f"{param_type} | {literal_type}"
                                    # Server methods receive the enum type, not string
                                    server_param_type = param_type
                            except Exception as e:
                                logger.debug(f"Could not add enum literals for {pf}: {e}")

                        # For struct parameters in CLIENT methods, also accept dict (pycapnp dict-to-struct conversion)
                        # For SERVER methods, use the Reader type specifically
                        elif field_obj.slot.type.which() == capnp_types.CapnpElementType.STRUCT:
                            # Server receives Reader objects from pycapnp
                            # Get the Reader type (handles generics properly)
                            server_param_type = helper.new_reader(param_type)
                            # Client can pass dict or struct
                            param_type = f"{param_type} | dict[str, Any]"
                            self._add_typing_import("Any")

                        # Client-side: all parameters are optional (Cap'n Proto allows calling without setting all params)
                        parameters.append(f"{pf}: {param_type} | None = None")
                        # Server-side: parameters remain required for type safety
                        server_parameters.append(f"{pf}: {server_param_type}")
                    else:
                        # Client-side: all parameters are optional
                        parameters.append(f"{pf}: Any = None")
                        # Server-side: parameters remain required
                        server_parameters.append(f"{pf}: Any")
                except Exception as e:
                    logger.debug(f"Could not resolve parameter type for {pf}: {e}")
                    # Client-side: all parameters are optional
                    parameters.append(f"{pf}: Any = None")
                    # Server-side: parameters remain required
                    server_parameters.append(f"{pf}: Any")
            # Generate return type - for RPC methods with result fields, create a Protocol
            # with those fields as attributes so users can access promise.field_name
            # The result is also awaitable, so it inherits from Awaitable
            return_type = "None"

            # Check if the result is a direct struct return or a result with named fields
            # Methods like `read() -> Msg` return the struct directly (no $ in display name)
            # Methods like `reader() -> (r :Reader)` have internal result structs ($ in display name)
            is_direct_struct_return = False
            if result_schema and result_fields:
                result_display_name = helper.get_display_name(result_schema)
                # If the display name doesn't contain $, it's a user struct returned directly
                is_direct_struct_return = "$" not in result_display_name

            # Initialize variables for server NamedTuple (used later if is_direct_struct_return)
            server_result_namedtuple_name: str | None = None
            server_result_namedtuple_fields: list[tuple[str, str]] | None = None

            # Generate CallContext for server methods
            # Every server method receives a _context parameter with a results attribute
            context_class_name = f"{method_name.capitalize()}CallContext"
            context_result_class_name = f"{method_name.capitalize()}ResultsBuilder"

            # Build fully qualified ResultsBuilder name for use in CallContext
            # Since both are nested classes, we need to qualify the reference
            scope_path = self._get_scope_path()
            fully_qualified_results_builder = (
                f"{scope_path}.{context_result_class_name}" if scope_path else context_result_class_name
            )

            if result_fields and not is_direct_struct_return:
                # Create a result Protocol class with the result fields (for client)
                result_class_name = f"{method_name.capitalize()}Result"
                self._add_typing_import("Awaitable")
                result_lines = [
                    helper.new_class_declaration(result_class_name, [f"Awaitable[{result_class_name}]", "Protocol"])
                ]

                # Also create the CallContext for server methods (with Builder types)
                context_lines = []

                # Generate the results builder Protocol for the server's _context.results
                context_lines.append(helper.new_class_declaration(context_result_class_name, ["Protocol"]))

                for rf in result_fields:
                    try:
                        if result_schema is not None:
                            field_obj = next(f for f in result_schema.node.struct.fields if f.name == rf)
                            # Use get_type_name to resolve complex types (struct, enum, interface, list)
                            field_type = self.get_type_name(field_obj.slot.type)

                            # For the CLIENT result protocol (result_lines): use Reader variant
                            # because pycapnp returns Reader objects when awaiting promises
                            client_field_type = field_type
                            if field_obj.slot.type.which() == capnp_types.CapnpElementType.STRUCT:
                                client_field_type = helper.new_reader(field_type)
                            # For list fields containing structs, wrap the Reader type
                            elif field_obj.slot.type.which() == capnp_types.CapnpElementType.LIST:
                                # Check if the list element is a struct
                                try:
                                    element_type = field_obj.slot.type.list.elementType
                                    if element_type.which() == capnp_types.CapnpElementType.STRUCT:
                                        # Get the element type name
                                        element_type_name = self.get_type_name(element_type)
                                        # Rebuild the field_type with Reader suffix on the element
                                        # field_type is like "Sequence[ElementType]", replace with "Sequence[ElementTypeReader]"
                                        client_field_type = client_field_type.replace(
                                            element_type_name, helper.new_reader(element_type_name)
                                        )
                                except Exception:
                                    pass  # Keep original field_type

                            result_lines.append(f"    {rf}: {client_field_type}")

                            # For the SERVER context results (context_lines): use Builder variant
                            # Server sets results using Builder objects
                            server_field_type = field_type
                            if field_obj.slot.type.which() == capnp_types.CapnpElementType.STRUCT:
                                server_field_type = helper.new_builder(field_type)
                            elif field_obj.slot.type.which() == capnp_types.CapnpElementType.LIST:
                                # Check if the list element is a struct
                                try:
                                    element_type = field_obj.slot.type.list.elementType
                                    if element_type.which() == capnp_types.CapnpElementType.STRUCT:
                                        element_type_name = self.get_type_name(element_type)
                                        # Use Builder for list elements in context.results
                                        server_field_type = server_field_type.replace(
                                            element_type_name, helper.new_builder(element_type_name)
                                        )
                                except Exception:
                                    pass

                            context_lines.append(f"    {rf}: {server_field_type}")
                        else:
                            result_lines.append(f"    {rf}: Any")
                            context_lines.append(f"    {rf}: Any")
                    except Exception as e:
                        logger.debug(f"Could not resolve return type for {rf}: {e}")
                        result_lines.append(f"    {rf}: Any")
                        context_lines.append(f"    {rf}: Any")

                # Add the result Protocol class to the current scope
                for line in result_lines:
                    self.scope.add(line)

                # Add the context results Protocol
                for line in context_lines:
                    self.scope.add(line)

                # Create the CallContext Protocol with the results attribute
                self.scope.add(helper.new_class_declaration(context_class_name, ["Protocol"]))
                self.scope.add(f"    results: {fully_qualified_results_builder}")

                return_type = result_class_name

            elif is_direct_struct_return:
                # Method returns a struct directly, e.g., info() -> IdInformation
                # Create a Result protocol with the struct's fields
                # Both client and server return Awaitable[InfoResult]
                self._add_typing_import("Awaitable")
                result_class_name = f"{method_name.capitalize()}Result"

                if result_schema is not None:
                    try:
                        # Get the struct type from the type map or generate it
                        struct_type_id = result_schema.node.id
                        if self.is_type_id_known(struct_type_id):
                            registered_type = self.get_type_by_id(struct_type_id)
                        else:
                            # Try to generate it - result_schema is guaranteed to be a struct schema here
                            # since we checked is_direct_struct_return
                            try:
                                self.generate_nested(result_schema)
                            except Exception:
                                pass
                            if self.is_type_id_known(struct_type_id):
                                registered_type = self.get_type_by_id(struct_type_id)

                        # Create a Result Protocol with the struct's fields (for client)
                        result_lines = [helper.new_class_declaration(result_class_name, ["Protocol"])]

                        # Check if the struct has unions
                        has_union = result_schema.node.struct.discriminantCount > 0

                        # Collect field names and types for server NamedTuple return
                        server_result_field_names = []
                        server_result_field_types = []

                        # Get all fields from the struct
                        for field in result_schema.node.struct.fields:
                            field_type = self.get_type_name(field.slot.type)
                            # For client side, use Reader variant for struct fields
                            client_field_type = field_type
                            if field.slot.type.which() == capnp_types.CapnpElementType.STRUCT:
                                client_field_type = helper.new_reader(field_type)
                            elif field.slot.type.which() == capnp_types.CapnpElementType.LIST:
                                try:
                                    element_type = field.slot.type.list.elementType
                                    if element_type.which() == capnp_types.CapnpElementType.STRUCT:
                                        element_type_name = self.get_type_name(element_type)
                                        client_field_type = client_field_type.replace(
                                            element_type_name, helper.new_reader(element_type_name)
                                        )
                                except Exception:
                                    pass
                            result_lines.append(f"    {field.name}: {client_field_type}")

                            # For server return, collect field names and base field types (not Reader variant)
                            server_result_field_names.append(field.name)
                            server_result_field_types.append(field_type)

                        # If the struct has unions, add the which() method
                        if has_union:
                            self._add_typing_import("Literal")
                            # Get all field names for the union
                            field_names = [f'"{field.name}"' for field in result_schema.node.struct.fields]
                            which_return_type = f"Literal[{', '.join(field_names)}]"
                            result_lines.append(f"    def which(self) -> {which_return_type}: ...")

                        # Add the Result protocol to the scope
                        for line in result_lines:
                            self.scope.add(line)

                        # Build fully qualified Result name for references within the same interface scope
                        scope_path = self._get_scope_path()
                        fully_qualified_result = (
                            f"{scope_path}.{result_class_name}" if scope_path else result_class_name
                        )

                        return_type = f"Awaitable[{fully_qualified_result}]"

                        # Store server result info for later generation in Server class
                        # We'll use the same name (InfoResult) but it will be a NamedTuple under Server scope
                        server_result_namedtuple_name = result_class_name
                        server_result_namedtuple_fields = list(
                            zip(server_result_field_names, server_result_field_types)
                        )

                        # Generate CallContext for server
                        # For direct struct return, _context.results should be typed as the Result protocol
                        # since that's what server code actually interacts with
                        self.scope.add(helper.new_class_declaration(context_class_name, ["Protocol"]))
                        self.scope.add(f"    results: {fully_qualified_result}")
                    except Exception as e:
                        logger.debug(f"Could not resolve direct struct return type: {e}")
                        return_type = "Awaitable[Any]"
                        self._add_typing_import("Any")
                        # Still generate CallContext
                        self.scope.add(f"{context_result_class_name} = Any")
                        self.scope.add("")
                        self.scope.add(helper.new_class_declaration(context_class_name, ["Protocol"]))
                        self.scope.add(f"    results: {fully_qualified_results_builder}")
                else:
                    return_type = "Awaitable[Any]"
                    self._add_typing_import("Any")
                    # Generate CallContext with Any
                    self.scope.add(helper.new_class_declaration(context_result_class_name, ["Protocol"]))
                    self.scope.add("    value: Any")
                    self.scope.add(helper.new_class_declaration(context_class_name, ["Protocol"]))
                    self.scope.add(f"    results: {fully_qualified_results_builder}")

            # ALL interface client methods return promises (awaitable), even void methods
            # So if return_type is still "None", wrap it in Awaitable[None]
            if return_type == "None":
                self._add_typing_import("Awaitable")
                return_type = "Awaitable[None]"
                # Generate CallContext for void methods
                self.scope.add(helper.new_class_declaration(context_result_class_name, ["Protocol"]))
                self.scope.add("    ...")
                self.scope.add(helper.new_class_declaration(context_class_name, ["Protocol"]))
                self.scope.add(f"    results: {fully_qualified_results_builder}")

            self.scope.add(helper.new_function(method_name, parameters=parameters, return_type=return_type))

            # Collect server method signature (server methods are async and accept **kwargs)
            # Server methods return the actual value, not the Result protocol
            # Extract the actual return type from result schema
            # If return_type is already Awaitable[X], unwrap it first (from direct struct return or void)
            if return_type.startswith("Awaitable[") and return_type.endswith("]"):
                server_return_type = return_type[10:-1]  # Remove "Awaitable[" and "]"
            else:
                server_return_type = return_type
            is_interface_return = False
            result_type_scope = None

            # Special case: direct struct returns return a NamedTuple
            # Server returns a NamedTuple (Server.InfoResult) that pycapnp unpacks into _context.results
            # The NamedTuple will be generated inside the Server class
            if is_direct_struct_return:
                # Use Server.ResultName for the return type
                # We'll store the info and generate the NamedTuple later when creating the Server class
                if server_result_namedtuple_name is not None and server_result_namedtuple_fields is not None:
                    # Store this info for later use in server method generation
                    # Build fully qualified name: Identifiable.Server.InfoResult
                    scope_path = self._get_scope_path()
                    if scope_path:
                        server_return_type = f"{scope_path}.Server.{server_result_namedtuple_name}"
                    else:
                        server_return_type = f"Server.{server_result_namedtuple_name}"
                    # Store the info in a way we can access it later
                    if not hasattr(self, "_server_namedtuples"):
                        self._server_namedtuples = {}
                    self._server_namedtuples[method_name] = (
                        server_result_namedtuple_name,
                        server_result_namedtuple_fields,
                    )
                    # Mark that this type is already fully scoped
                    result_type_scope = self.scope  # This will prevent additional scoping
                else:
                    server_return_type = "None"
                    # Mark that this is already properly typed
                    result_type_scope = self.scope

            # Try to get the result type from the result_schema directly
            # The result_schema represents the actual return type (e.g., IdInformation)
            # BUT: skip internal Cap'n Proto result structs (contain $)
            elif result_schema is not None and return_type != "None":
                try:
                    # Check if this is an internal Cap'n Proto result struct (has $ in name)
                    result_display_name = helper.get_display_name(result_schema)
                    if "$" not in result_display_name:
                        # This is a user-defined type, use it
                        result_type_id = result_schema.node.id
                        if self.is_type_id_known(result_type_id):
                            registered_result = self.get_type_by_id(result_type_id)
                            server_return_type = registered_result.scoped_name
                            result_type_scope = registered_result.scope
                            # Check if it's an interface
                            is_interface_return = result_schema.node.which() == "interface"
                        else:
                            # Try to generate it if not known
                            self.generate_nested(result_schema)
                            if self.is_type_id_known(result_type_id):
                                registered_result = self.get_type_by_id(result_type_id)
                                server_return_type = registered_result.scoped_name
                                result_type_scope = registered_result.scope
                except Exception as e:
                    logger.debug(f"Could not resolve result schema type: {e}")
                    # Fall back to old logic
                    pass

            # Fallback: if we couldn't get the type from result_schema, try extracting from fields
            if server_return_type == return_type and result_fields and return_type != "None":
                # For single result field, unwrap the type
                if len(result_fields) == 1:
                    # Try to get the type of the single result field
                    try:
                        if result_schema is not None:
                            result_field = next(
                                f for f in result_schema.node.struct.fields if f.name == result_fields[0]
                            )
                            field_type = result_field.slot.type
                            # Try to get the properly scoped type name from registered types
                            try:
                                field_type_kind = field_type.which()
                                if field_type_kind in (
                                    capnp_types.CapnpElementType.STRUCT,
                                    capnp_types.CapnpElementType.INTERFACE,
                                ):
                                    # Get type ID for struct or interface
                                    if field_type_kind == capnp_types.CapnpElementType.STRUCT:
                                        type_id = field_type.struct.typeId
                                    else:
                                        type_id = field_type.interface.typeId

                                    if self.is_type_id_known(type_id):
                                        registered_type = self.get_type_by_id(type_id)
                                        server_return_type = registered_type.scoped_name
                                        result_type_scope = registered_type.scope
                                    else:
                                        server_return_type = self.get_type_name(field_type)
                                else:
                                    server_return_type = self.get_type_name(field_type)
                            except Exception:
                                server_return_type = self.get_type_name(field_type)
                            # Check if this is an interface type
                            is_interface_return = field_type.which() == capnp_types.CapnpElementType.INTERFACE
                    except Exception:
                        server_return_type = "Any"
                elif len(result_fields) > 1:
                    # For multiple result fields, server returns a tuple
                    # Get types for each field
                    field_types = []
                    try:
                        if result_schema is not None:
                            for rf in result_fields:
                                result_field = next(f for f in result_schema.node.struct.fields if f.name == rf)
                                field_type_name = self.get_type_name(result_field.slot.type)
                                field_types.append(field_type_name)

                            # Build tuple type
                            server_return_type = f"tuple[{', '.join(field_types)}]"
                    except Exception as e:
                        logger.debug(f"Could not resolve multiple result field types: {e}")
                        server_return_type = "Any"

            # If we got a registered type from root scope, it's already properly scoped
            # Otherwise, check if we need to add interface scope
            # Don't add scope for primitive types or already scoped types
            primitive_types = set(capnp_types.CAPNP_TYPE_TO_PYTHON.values())
            primitive_types.update(["None", "Any", "Sequence"])

            # Get interface name (current scope)
            interface_name = self.scope.name if not self.scope.is_root else ""

            if result_type_scope is None or not result_type_scope.is_root:
                # Only add scope if the type doesn't already have a dot (isn't already scoped)
                # and isn't a primitive type
                # Also check if the return type is the interface itself (self-reference)
                # Don't scope tuple types or generic types with brackets
                if (
                    server_return_type not in primitive_types
                    and "." not in server_return_type
                    and not server_return_type.startswith("Sequence[")
                    and not server_return_type.startswith("tuple[")
                    and server_return_type != interface_name  # Don't scope self-references
                ):
                    # Get interface scope path (excluding root)
                    scope_path = self._get_scope_path()
                    if scope_path:
                        server_return_type = f"{scope_path}.{server_return_type}"

            # For interface return types, also accept Server implementations
            if is_interface_return:
                server_return_type = f"{server_return_type} | {server_return_type}.Server"

            # Server methods are async, so wrap in Awaitable (including void methods)
            # Allow None return to support using _context.results directly
            self._add_typing_import("Awaitable")
            server_return_type = f"Awaitable[{server_return_type} | None]"

            # Server method signatures: pycapnp always passes _context parameter
            # Make it mandatory and properly typed so implementations must include it
            # Get the fully qualified context class name
            scope_path = self._get_scope_path()
            if scope_path:
                fully_qualified_context = f"{scope_path}.{context_class_name}"
            else:
                fully_qualified_context = context_class_name

            # kwargs can't be properly typed as they're used internally by pycapnp
            server_params = server_parameters + [f"_context: {fully_qualified_context}", "**kwargs: Any"]

            server_method_sig = helper.new_function(
                method_name, parameters=server_params, return_type=server_return_type
            )
            server_methods.append(server_method_sig)

            # Generate the corresponding _request method
            # In capnp, for each method like evaluate(), there's also evaluate_request()
            # that returns a request builder object with parameter fields and send() method
            request_method_name = f"{method_name}_request"
            request_class_name = f"{method_name.capitalize()}Request"

            # Create request builder Protocol with parameter fields and send() method
            request_lines = [helper.new_class_declaration(request_class_name, ["Protocol"])]

            # Track init choices for request builder (similar to struct generation)
            request_init_choices: list[InitChoice] = []
            request_list_init_choices: list[tuple[str, str, bool]] = []

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
                            # Handle scoped names and generic types properly
                            field_type = self._build_scoped_builder_type(field_type)
                            # Add to init choices for struct/group fields
                            base_type = self.get_type_name(field_obj.slot.type)
                            request_init_choices.append((pf, base_type))
                        elif field_obj.slot.type.which() == capnp_types.CapnpElementType.LIST:
                            # Track list fields for init() overloads
                            element_type = field_obj.slot.type.list.elementType
                            element_type_name = self.get_type_name(element_type)
                            needs_builder = element_type.which() == capnp_types.CapnpElementType.STRUCT
                            request_list_init_choices.append((pf, element_type_name, needs_builder))

                        request_lines.append(f"    {pf}: {field_type}")
                    else:
                        request_lines.append(f"    {pf}: Any")
                except Exception:
                    request_lines.append(f"    {pf}: Any")

            # Add init method overloads to the Request Protocol (like Builder classes)
            if request_init_choices or request_list_init_choices:
                total_init_overloads = len(request_init_choices) + len(request_list_init_choices)
                use_overload = total_init_overloads > 1

                if use_overload:
                    self._add_typing_import("overload")
                if request_init_choices or request_list_init_choices:
                    self._add_typing_import("Literal")

                # Add init method overloads for union/group fields (return their Builder type)
                for field_name, field_type in request_init_choices:
                    if use_overload:
                        request_lines.append("    @overload")
                    # Build builder type name (respect scoped names)
                    builder_type = self._build_scoped_builder_type(field_type)

                    if use_overload:
                        request_lines.append(f'    def init(self, name: Literal["{field_name}"]) -> {builder_type}: ...')
                    else:
                        request_lines.append(f'    def init(self, name: Literal["{field_name}"]) -> {builder_type}: ...')

                # Add init method overloads for lists (properly typed)
                for field_name, element_type, needs_builder in request_list_init_choices:
                    if use_overload:
                        request_lines.append("    @overload")
                    self._add_import("from capnp import _DynamicListBuilder")
                    element_type_for_list = f"{element_type}Builder" if needs_builder else element_type

                    request_lines.append(
                        f'    def init(self, name: Literal["{field_name}"], size: int = ...) -> '
                        f"_DynamicListBuilder[{element_type_for_list}]: ..."
                    )

                # Add generic init method for other cases (catch-all)
                if use_overload:
                    self._add_typing_import("Any")
                    request_lines.append("    def init(self, name: str, size: int = ...) -> Any: ...")

            # Add send() method that returns the result type
            # Use fully qualified name for the result type to avoid forward reference issues
            if return_type != "None":
                # Check if return_type is already fully qualified (contains Awaitable[...] from direct struct return)
                if return_type.startswith("Awaitable["):
                    # Direct struct return - already properly typed, don't add scope path
                    send_return_type = return_type
                else:
                    # Build fully qualified result type name (e.g., Calculator.EvaluateResult or Calculator.Value.ReadResult)
                    # Get the full scope path excluding root
                    scope_path = self._get_scope_path()
                    send_return_type = f"{scope_path}.{return_type}" if scope_path else return_type
            else:
                send_return_type = "Any"
            request_lines.append(f"    def send(self) -> {send_return_type}: ...")

            # Add the request builder to scope
            for line in request_lines:
                self.scope.add(line)

            # Now add the _request method with kwargs parameters (like new_message)
            # Build parameter list with typed kwargs
            request_params: list[helper.TypeHintedVariable | str] = ["self"]
            
            # Add each parameter field as an optional kwarg
            if param_schema is not None:
                for pf in param_fields:
                    try:
                        field_obj = next(f for f in param_schema.node.struct.fields if f.name == pf)
                        field_type = self.get_type_name(field_obj.slot.type)
                        
                        # Determine the appropriate type for the kwarg
                        param_type_hints = [helper.TypeHint(field_type, primary=True)]
                        
                        # For struct parameters, also accept dict (like new_message)
                        if field_obj.slot.type.which() == capnp_types.CapnpElementType.STRUCT:
                            param_type_hints.append(helper.TypeHint("dict[str, Any]"))
                            self._add_typing_import("Any")
                        # For list of struct parameters, accept Sequence[dict]
                        elif field_obj.slot.type.which() == capnp_types.CapnpElementType.LIST:
                            try:
                                element_type = field_obj.slot.type.list.elementType
                                if element_type.which() == capnp_types.CapnpElementType.STRUCT:
                                    param_type_hints.append(helper.TypeHint("Sequence[dict[str, Any]]"))
                                    self._add_typing_import("Sequence")
                                    self._add_typing_import("Any")
                            except Exception:
                                pass
                        
                        param_type_hints.append(helper.TypeHint("None"))
                        
                        # Create the parameter
                        param_var = helper.TypeHintedVariable(
                            pf,
                            param_type_hints,
                            default="None",
                        )
                        request_params.append(param_var)
                    except Exception:
                        # Fallback for unresolvable parameters
                        pass
            
            self.scope.add(
                helper.new_function(request_method_name, parameters=request_params, return_type=request_class_name)
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
        # Add _new_client() class method
        self._add_new_client_method(name, base_classes, schema)

        # Now add the Server class with method signatures
        # Server class should also inherit from superclass Server classes
        server_base_classes = []
        if schema.node.which() == "interface":
            interface_node = schema.node.interface
            for superclass in interface_node.superclasses:
                try:
                    superclass_type = self.get_type_by_id(superclass.id)
                    server_base_classes.append(f"{superclass_type.scoped_name}.Server")
                except KeyError:
                    logger.debug(f"Could not resolve superclass {superclass.id} for Server inheritance")

        # Create a nested scope for the Server class
        if server_base_classes:
            self.scope.add(helper.new_class_declaration("Server", server_base_classes))
        else:
            self.scope.add(helper.new_class_declaration("Server"))

        server_scope = Scope(
            name="Server",
            id=schema.node.id + 1,  # Use a pseudo-ID
            parent=self.scope,
            return_scope=self.scope,
        )
        prev_scope = self.scope
        self.scope = server_scope

        # Add NamedTuple definitions for direct struct returns
        # These are generated inside the Server class as Server.InfoResult
        if hasattr(self, "_server_namedtuples") and self._server_namedtuples:
            self._add_typing_import("NamedTuple")
            # Store in global dict for later use in .py file generation
            # Use the fully qualified path for nested interfaces
            fully_qualified_name = self._get_scope_path(prev_scope)
            if not fully_qualified_name:
                fully_qualified_name = name
            self._all_server_namedtuples[fully_qualified_name] = self._server_namedtuples
            for method_name, (namedtuple_name, fields) in self._server_namedtuples.items():
                self.scope.add(f"class {namedtuple_name}(NamedTuple):")
                for field_name, field_type in fields:
                    self.scope.add(f"    {field_name}: {field_type}")

        if server_methods:
            # Add all collected server method signatures
            for method_sig in server_methods:
                self.scope.add(method_sig)
        else:
            # Empty server class
            self.scope.add("...")

        # Merge server scope lines back to parent
        prev_scope.lines += self.scope.lines
        self.scope = prev_scope

        # Ensure interface has some content (even if methods failed to generate)
        if not self.scope.lines:
            self.scope.add("...")

        self.return_from_scope()
        return None

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
                self._add_import(f"from {python_import_path} import {definition_name}")
            else:
                # Structs have Builder/Reader variants
                self._add_import(
                    f"from {python_import_path} import "
                    f"{definition_name}, {helper.new_builder(definition_name)}, {helper.new_reader(definition_name)}"
                )

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

    def new_scope(self, name: str, node: Any, scope_heading: str = "", register: bool = True) -> Scope:
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
        assert not self.scope.is_root, "The current scope is the root scope and cannot be returned from."
        assert self.scope.parent is not None, "The current scope has no parent."
        assert self.scope.return_scope is not None, "The current scope does not define a scope to return to."

        # Find where the scope heading is in the parent's lines
        # The scope heading was added when new_scope() was called (for interfaces)
        # or manually added (for structs/enums)
        # We need to insert the child scope lines RIGHT AFTER the heading
        # Use word boundary to avoid matching "class TestSturdyRef" when looking for "class TestSturdyRefHostId"
        scope_heading_pattern = f"class {self.scope.name}"
        heading_index = None
        for i, line in enumerate(self.scope.parent.lines):
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

    def get_type_name(self, type_reader: capnp._DynamicStructReader | TypeReader) -> str:
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
                out.append(f"{helper.new_builder(scope.name)} = {scope.name}")
                out.append(f"{helper.new_reader(scope.name)} = {scope.name}")

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
