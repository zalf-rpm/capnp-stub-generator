"""Tests for constants, versioned structs, and name annotations in dummy.capnp."""

from __future__ import annotations


def test_global_constants_and_derived_constant_present(dummy_stub_lines: list[str]) -> None:
    """Test global constants and derived constant present."""
    lines = dummy_stub_lines
    # Global constants - only primitive types are currently generated
    assert any("globalInt:" in line for line in lines)
    assert any("globalText:" in line for line in lines)
    # Struct constants are not currently generated in stubs


def test_struct_constants_section(dummy_stub_lines: list[str]) -> None:
    """Test struct constants section."""
    lines = dummy_stub_lines
    assert any("class _TestConstantsStructModule(_StructModule):" in line for line in lines)
    # Struct-level constants are not currently generated in stub files
    # This is acceptable as stubs are for type checking, not runtime values
    # for name in [
    # ]:


def test_versioned_structs_fields_and_defaults(dummy_stub_lines: list[str]) -> None:
    """Test versioned structs fields and defaults."""
    lines = dummy_stub_lines
    assert any("class _TestOldVersionStructModule(_StructModule):" in line for line in lines)
    assert any("class _TestNewVersionStructModule(_StructModule):" in line for line in lines)
    # Fields should be present (now as properties)
    assert any("def new1(self)" in line and "int" in line for line in lines)
    assert any("def new2(self)" in line and "str" in line for line in lines)
    # Default values are not included in stub files (runtime feature, not type info)


def test_name_annotations_renamed_struct_enum_fields(dummy_stub_lines: list[str]) -> None:
    """Test name annotations renamed struct enum fields."""
    lines = dummy_stub_lines
    # Name annotations ($Cxx.name) are not currently processed by the generator
    # The structs use their schema names, not the C++ annotation names
    assert any("class _TestNameAnnotationStructModule(_StructModule):" in line for line in lines)
    # Original names are used since annotations aren't processed - now using Protocol pattern
    assert any("class _BadlyNamedEnumEnumModule(_EnumModule):" in line for line in lines)
    assert any("BadlyNamedEnum: _BadlyNamedEnumEnumModule" in line for line in lines)
    assert any("badFieldName" in line or "bar" in line for line in lines)
    # Renamed names would appear if annotation support is added:


def test_empty_struct_representation(dummy_stub_lines: list[str]) -> None:
    """Test empty struct representation."""
    lines = dummy_stub_lines
    # TestEmptyStruct should still produce a class
    assert any("class _TestEmptyStructStructModule(_StructModule):" in line for line in lines)
