"""Tests for enum and basic all-types sections of dummy.capnp split out."""

from __future__ import annotations


def test_enum_definition_and_imports(dummy_stub_lines):
    lines = dummy_stub_lines
    # Enum import present and TestEnum defined as Enum with TypeAlias
    assert any(line.startswith("from enum import") and "Enum" in line for line in lines)
    assert any(line.startswith("from typing import") and "TypeAlias" in line for line in lines)
    assert any(line.strip().startswith("class _TestEnumModule(Enum):") for line in lines)
    assert any(line.strip() == "TestEnum: TypeAlias = _TestEnumModule" for line in lines)
    # Enum values are now Enum members with integer values
    for name in ["foo", "bar", "baz", "qux"]:
        # Check for enum member assignments (e.g., "foo = 0")
        assert any(f"{name} =" in line for line in lines)


def test_testalltypes_field_presence_and_collections_import(dummy_stub_lines):
    lines = dummy_stub_lines
    # collections.abc import for Sequence (Iterator no longer needed since static methods inherited)
    assert any(line.startswith("from collections.abc import") and "Sequence" in line for line in lines)
    # Basic scalar fields (now as properties)
    for field in ["voidField", "boolField", "int8Field", "float64Field", "textField", "dataField"]:
        assert any(f"def {field}(self)" in line for line in lines)
    # Nested struct and enum field annotations (now as properties)
    assert any("def structField(self)" in line and "TestAllTypes" in line for line in lines)
    assert any("def enumField(self)" in line and "TestEnum" in line for line in lines)
    # List field typing includes Sequence (now as properties)
    assert any("def voidList(self)" in line and "Sequence" in line for line in lines)


def test_builder_reader_classes_for_all_types(dummy_stub_lines):
    lines = dummy_stub_lines
    # With nested structure, check for TypeAlias declarations and nested classes
    assert any("TestAllTypesReader: TypeAlias = _TestAllTypesModule.Reader" in line for line in lines)
    assert any("TestAllTypesBuilder: TypeAlias = _TestAllTypesModule.Builder" in line for line in lines)
    # Reader and Builder are now nested inside TestAllTypes as Protocols
    assert any(line.strip().startswith("class Reader(_DynamicStructReader):") for line in lines)
    assert any(line.strip().startswith("class Builder(_DynamicStructBuilder):") for line in lines)
    # Static methods like from_bytes are inherited from _StructModule
    assert any("from capnp.lib.capnp import _DynamicStructBuilder, _DynamicStructReader, _StructModule" in line for line in lines)
