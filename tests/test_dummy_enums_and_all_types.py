"""Tests for enum and basic all-types sections of dummy.capnp split out."""

from __future__ import annotations


def test_enum_definition_and_imports(dummy_stub_lines):
    lines = dummy_stub_lines
    # Enum import present and TestEnum defined as real Enum subclass
    assert any(line.startswith("from enum import") and "Enum" in line for line in lines)
    assert any(line.strip().startswith("class TestEnum(Enum):") for line in lines)
    # A few members
    for name in ["foo", "bar", "baz", "qux"]:
        assert any(line.strip() == f'{name} = "{name}"' for line in lines)


def test_testalltypes_field_presence_and_collections_import(dummy_stub_lines):
    lines = dummy_stub_lines
    # collections.abc import for Iterator, Sequence
    assert any(
        line.startswith("from collections.abc import") and "Sequence" in line and "Iterator" in line for line in lines
    )
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
    assert any(line.strip().startswith("class TestAllTypesReader(TestAllTypes):") for line in lines)
    assert any(line.strip().startswith("class TestAllTypesBuilder(TestAllTypes):") for line in lines)
    # from_bytes contextmanager present
    assert any(line.strip().startswith("def from_bytes(") for line in lines) or any(
        "@contextmanager" in line for line in lines
    )
