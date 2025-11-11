"""Data Transfer Objects for writer.py refactoring.

This module contains cohesive data objects that group related parameters
and reduce coupling between methods in the Writer class.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from capnp.lib.capnp import _StructSchema

    from capnp_stub_generator import helper
    from capnp_stub_generator.scope import CapnpType


# Type alias for init choice tuples
InitChoice = tuple[str, str]


@dataclass
class StructGenerationContext:
    """Context object containing all metadata needed for struct generation.

    This object groups together all the type names and metadata that are passed
    around during struct generation, reducing the number of parameters from 8+ to 1.

    Attributes:
        schema: The Cap'n Proto struct schema being processed
        type_name: The name of the type being generated
        new_type: The registered CapnpType object
        registered_params: List of generic type parameters (e.g., ["T", "U"])
        reader_type_name: Name of the Reader class (e.g., "PersonReader")
        builder_type_name: Name of the Builder class (e.g., "PersonBuilder")
        scoped_reader_type_name: Fully qualified Reader name (e.g., "Outer.PersonReader")
        scoped_builder_type_name: Fully qualified Builder name (e.g., "Outer.PersonBuilder")
    """

    schema: _StructSchema
    type_name: str
    new_type: CapnpType
    registered_params: list[str]
    reader_type_name: str
    builder_type_name: str
    scoped_reader_type_name: str
    scoped_builder_type_name: str

    @classmethod
    def create(
        cls,
        schema: _StructSchema,
        type_name: str,
        new_type: CapnpType,
        registered_params: list[str],
    ) -> StructGenerationContext:
        """Factory method to create context with auto-generated name variants.

        This factory ensures consistency by automatically generating all the
        Reader and Builder name variants from the base type name.

        Args:
            schema: The Cap'n Proto struct schema
            type_name: The base type name
            new_type: The registered type object
            registered_params: Generic type parameters

        Returns:
            A fully initialized StructGenerationContext
        """
        from capnp_stub_generator import helper

        reader_type_name = helper.new_reader(new_type.name)
        builder_type_name = helper.new_builder(new_type.name)
        scoped_reader_type_name = helper.new_reader(new_type.scoped_name)
        scoped_builder_type_name = helper.new_builder(new_type.scoped_name)

        return cls(
            schema=schema,
            type_name=type_name,
            new_type=new_type,
            registered_params=registered_params,
            reader_type_name=reader_type_name,
            builder_type_name=builder_type_name,
            scoped_reader_type_name=scoped_reader_type_name,
            scoped_builder_type_name=scoped_builder_type_name,
        )


class StructFieldsCollection:
    """Collection of processed struct fields and their metadata.

    This class encapsulates the three lists that track field information
    during struct generation, providing explicit methods for adding items
    instead of direct list manipulation.

    Attributes:
        slot_fields: List of processed field variables with type hints
        init_choices: List of (field_name, type_name) tuples for struct/group fields
            that need init() method overloads
        list_init_choices: List of (field_name, element_type, needs_builder) tuples
            for list fields that need init() method overloads
    """

    def __init__(self) -> None:
        """Initialize empty collections."""
        self.slot_fields: list[helper.TypeHintedVariable] = []
        self.init_choices: list[InitChoice] = []
        self.list_init_choices: list[tuple[str, str, bool]] = []

    def add_slot_field(self, field: helper.TypeHintedVariable) -> None:
        """Add a slot field to the collection.

        Args:
            field: The type-hinted variable representing the field
        """
        self.slot_fields.append(field)

    def add_init_choice(self, field_name: str, type_name: str) -> None:
        """Add an init choice for struct or group fields.

        Init choices are used to generate overloaded init() methods that return
        the appropriate Builder type for the field.

        Args:
            field_name: The name of the field
            type_name: The type name to return (e.g., "PersonBuilder")
        """
        self.init_choices.append((field_name, type_name))

    def add_list_init_choice(self, field_name: str, element_type: str, needs_builder: bool) -> None:
        """Add an init choice for list fields.

        List init choices are used to generate overloaded init() methods that
        return Sequence[ElementType] or Sequence[ElementTypeBuilder].

        Args:
            field_name: The name of the list field
            element_type: The element type (without Builder suffix)
            needs_builder: Whether the element type needs a Builder suffix
        """
        self.list_init_choices.append((field_name, element_type, needs_builder))

    def __repr__(self) -> str:
        """Return a readable representation for debugging."""
        return (
            f"StructFieldsCollection("
            f"slot_fields={len(self.slot_fields)}, "
            f"init_choices={len(self.init_choices)}, "
            f"list_init_choices={len(self.list_init_choices)})"
        )
