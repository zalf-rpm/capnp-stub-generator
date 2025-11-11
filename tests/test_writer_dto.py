"""Tests for writer_dto.py - Data Transfer Objects.

These tests verify that the DTOs work correctly and provide the expected
functionality for struct generation.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from capnp_stub_generator import helper
from capnp_stub_generator.writer_dto import StructFieldsCollection, StructGenerationContext


class TestStructGenerationContext:
    """Tests for StructGenerationContext."""

    def test_create_factory_method(self):
        """Test that the factory method creates context with all name variants."""
        # Create mock objects
        mock_schema = Mock()
        mock_new_type = Mock()
        mock_new_type.name = "Person"
        mock_new_type.scoped_name = "Company.Person"

        # Create context using factory
        context = StructGenerationContext.create(
            schema=mock_schema,
            type_name="Person",
            new_type=mock_new_type,
            registered_params=["T"],
        )

        # Verify all attributes are set
        assert context.schema == mock_schema
        assert context.type_name == "Person"
        assert context.new_type == mock_new_type
        assert context.registered_params == ["T"]

        # Verify generated names
        assert context.reader_type_name == "PersonReader"
        assert context.builder_type_name == "PersonBuilder"
        assert context.scoped_reader_type_name == "Company.PersonReader"
        assert context.scoped_builder_type_name == "Company.PersonBuilder"

    def test_create_with_empty_generic_params(self):
        """Test context creation with no generic parameters."""
        mock_schema = Mock()
        mock_new_type = Mock()
        mock_new_type.name = "Person"
        mock_new_type.scoped_name = "Person"

        context = StructGenerationContext.create(
            schema=mock_schema, type_name="Person", new_type=mock_new_type, registered_params=[]
        )

        assert context.registered_params == []
        assert context.reader_type_name == "PersonReader"

    def test_create_with_nested_type(self):
        """Test context creation with nested type names."""
        mock_schema = Mock()
        mock_new_type = Mock()
        mock_new_type.name = "Inner"
        mock_new_type.scoped_name = "Outer.Middle.Inner"

        context = StructGenerationContext.create(
            schema=mock_schema, type_name="Inner", new_type=mock_new_type, registered_params=[]
        )

        assert context.scoped_reader_type_name == "Outer.Middle.InnerReader"
        assert context.scoped_builder_type_name == "Outer.Middle.InnerBuilder"


class TestStructFieldsCollection:
    """Tests for StructFieldsCollection."""

    def test_initialization(self):
        """Test that collection initializes with empty lists."""
        collection = StructFieldsCollection()

        assert collection.slot_fields == []
        assert collection.init_choices == []
        assert collection.list_init_choices == []

    def test_add_slot_field(self):
        """Test adding slot fields."""
        collection = StructFieldsCollection()
        mock_field = Mock(spec=helper.TypeHintedVariable)

        collection.add_slot_field(mock_field)

        assert len(collection.slot_fields) == 1
        assert collection.slot_fields[0] == mock_field

    def test_add_multiple_slot_fields(self):
        """Test adding multiple slot fields."""
        collection = StructFieldsCollection()
        field1 = Mock(spec=helper.TypeHintedVariable)
        field2 = Mock(spec=helper.TypeHintedVariable)

        collection.add_slot_field(field1)
        collection.add_slot_field(field2)

        assert len(collection.slot_fields) == 2
        assert collection.slot_fields == [field1, field2]

    def test_add_init_choice(self):
        """Test adding init choices."""
        collection = StructFieldsCollection()

        collection.add_init_choice("address", "Address")

        assert len(collection.init_choices) == 1
        assert collection.init_choices[0] == ("address", "Address")

    def test_add_list_init_choice(self):
        """Test adding list init choices."""
        collection = StructFieldsCollection()

        collection.add_list_init_choice("phones", "PhoneNumber", needs_builder=True)

        assert len(collection.list_init_choices) == 1
        assert collection.list_init_choices[0] == ("phones", "PhoneNumber", True)

    def test_add_list_init_choice_without_builder(self):
        """Test adding list init choice for primitive types."""
        collection = StructFieldsCollection()

        collection.add_list_init_choice("numbers", "int", needs_builder=False)

        assert len(collection.list_init_choices) == 1
        assert collection.list_init_choices[0] == ("numbers", "int", False)

    def test_repr(self):
        """Test string representation for debugging."""
        collection = StructFieldsCollection()
        collection.add_slot_field(Mock(spec=helper.TypeHintedVariable))
        collection.add_init_choice("field1", "Type1")
        collection.add_list_init_choice("field2", "Type2", True)

        repr_str = repr(collection)

        assert "StructFieldsCollection" in repr_str
        assert "slot_fields=1" in repr_str
        assert "init_choices=1" in repr_str
        assert "list_init_choices=1" in repr_str

    def test_complex_workflow(self):
        """Test a realistic workflow of building up field collections."""
        collection = StructFieldsCollection()

        # Add several fields like gen_struct would do
        field1 = Mock(spec=helper.TypeHintedVariable)
        field2 = Mock(spec=helper.TypeHintedVariable)
        field3 = Mock(spec=helper.TypeHintedVariable)

        collection.add_slot_field(field1)
        collection.add_init_choice("address", "Address")
        collection.add_slot_field(field2)
        collection.add_list_init_choice("emails", "str", False)
        collection.add_slot_field(field3)
        collection.add_init_choice("company", "Company")
        collection.add_list_init_choice("phones", "PhoneNumber", True)

        # Verify final state
        assert len(collection.slot_fields) == 3
        assert len(collection.init_choices) == 2
        assert len(collection.list_init_choices) == 2

        # Verify order is preserved
        assert collection.init_choices == [("address", "Address"), ("company", "Company")]
        assert collection.list_init_choices == [("emails", "str", False), ("phones", "PhoneNumber", True)]


class TestIntegration:
    """Integration tests for using DTOs together."""

    def test_dto_workflow(self):
        """Test typical workflow using both DTOs together."""
        # Setup context
        mock_schema = Mock()
        mock_new_type = Mock()
        mock_new_type.name = "Person"
        mock_new_type.scoped_name = "AddressBook.Person"

        context = StructGenerationContext.create(
            schema=mock_schema,
            type_name="Person",
            new_type=mock_new_type,
            registered_params=[],
        )

        # Build field collection
        fields = StructFieldsCollection()
        fields.add_slot_field(Mock(spec=helper.TypeHintedVariable))
        fields.add_init_choice("address", "Address")

        # Verify both objects work together
        assert context.type_name == "Person"
        assert context.builder_type_name == "PersonBuilder"
        assert len(fields.slot_fields) == 1
        assert len(fields.init_choices) == 1

        # This simulates what the refactored gen_struct would do:
        # pass context and fields to helper methods instead of 8+ parameters
