"""Tests for enum and basic all-types sections of dummy.capnp split out."""

from __future__ import annotations


def test_enum_definition_and_imports(dummy_stub_lines):
    lines = dummy_stub_lines
    # Enums are now simple classes with int attributes
    assert any(line.strip().startswith("class _TestEnumEnumModule:") for line in lines)
    # Type alias at top level (not instance annotation)
    assert any(line.strip().startswith("type TestEnumEnum = int | Literal[") for line in lines)
    # Enum values are now int annotations (e.g., "foo: int")
    for name in ["foo", "bar", "baz", "qux"]:
        assert any(f"{name}: int" in line for line in lines)


def test_testalltypes_field_presence_and_collections_import(dummy_stub_lines):
    lines = dummy_stub_lines
    # collections.abc import for Sequence (Iterator no longer needed since static methods inherited)
    assert any(line.startswith("from collections.abc import") and "Sequence" in line for line in lines)
    # Basic scalar fields (now as properties)
    for field in ["voidField", "boolField", "int8Field", "float64Field", "textField", "dataField"]:
        assert any(f"def {field}(self)" in line for line in lines)
    # Nested struct and enum field annotations (now as properties)
    assert any("def structField(self)" in line and "TestAllTypes" in line for line in lines)
    assert any("def enumField(self)" in line for line in lines)
    # List field typing uses specific list classes (now as properties)
    assert any("def voidList(self) -> VoidListReader" in line for line in lines)


def test_builder_reader_classes_for_all_types(dummy_stub_lines):
    lines = dummy_stub_lines
    # With nested structure, check for TypeAlias declarations and nested classes
    assert any("TestAllTypesReader = _TestAllTypesStructModule.Reader" in line for line in lines)
    assert any("TestAllTypesBuilder = _TestAllTypesStructModule.Builder" in line for line in lines)
    # Reader and Builder are now nested inside TestAllTypes as Protocols
    assert any(line.strip().startswith("class Reader(_DynamicStructReader):") for line in lines)
    assert any(line.strip().startswith("class Builder(_DynamicStructBuilder):") for line in lines)
    # Static methods like from_bytes are inherited from _StructModule
    # Imports are now multiline, so check for individual imports
    content = "".join(lines)
    assert "_DynamicStructBuilder" in content
    assert "_DynamicStructReader" in content
    assert "_StructModule" in content
