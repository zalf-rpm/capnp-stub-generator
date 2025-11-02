"""Tests for enum and basic all-types sections of dummy.capnp split out."""

from __future__ import annotations

import pytest
from conftest import read_stub_file


@pytest.fixture(scope="module")
def dummy_stub_lines(generate_core_stubs):
    """Read dummy.capnp stub file lines."""
    stub_path = generate_core_stubs / "dummy_capnp.pyi"
    return read_stub_file(stub_path)


def test_enum_definition_and_imports(dummy_stub_lines):
    lines = dummy_stub_lines
    # Enum import present and TestEnum defined as real Enum subclass
    assert any(l.startswith("from enum import") and "Enum" in l for l in lines)
    assert any(l.strip().startswith("class TestEnum(Enum):") for l in lines)
    # A few members
    for name in ["foo", "bar", "baz", "qux"]:
        assert any(l.strip() == f'{name} = "{name}"' for l in lines)


def test_testalltypes_field_presence_and_collections_import(dummy_stub_lines):
    lines = dummy_stub_lines
    # collections.abc import for Iterator, Sequence
    assert any(
        l.startswith("from collections.abc import") and "Sequence" in l and "Iterator" in l
        for l in lines
    )
    # Basic scalar fields
    for field in ["voidField", "boolField", "int8Field", "float64Field", "textField", "dataField"]:
        assert any(field + ":" in l for l in lines)
    # Nested struct and enum field annotations
    assert any("structField:" in l and "TestAllTypes" in l for l in lines)
    assert any("enumField:" in l and "TestEnum" in l for l in lines)
    # List field typing includes Sequence
    assert any("voidList:" in l and "Sequence" in l for l in lines)


def test_builder_reader_classes_for_all_types(dummy_stub_lines):
    lines = dummy_stub_lines
    assert any(l.strip().startswith("class TestAllTypesReader(TestAllTypes):") for l in lines)
    assert any(l.strip().startswith("class TestAllTypesBuilder(TestAllTypes):") for l in lines)
    # from_bytes contextmanager present
    assert any(l.strip().startswith("def from_bytes(") for l in lines) or any(
        "@contextmanager" in l for l in lines
    )
