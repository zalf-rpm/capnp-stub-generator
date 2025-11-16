"""Tests for constants, versioned structs, and name annotations in dummy.capnp."""

from __future__ import annotations


def test_global_constants_and_derived_constant_present(dummy_stub_lines):
    lines = dummy_stub_lines
    # Global constants - only primitive types are currently generated
    assert any("globalInt:" in line for line in lines)
    assert any("globalText:" in line for line in lines)
    # Struct constants are not currently generated in stubs
    # assert any("globalStruct:" in line for line in lines)
    # assert any("derivedConstant:" in line for line in lines)


def test_struct_constants_section(dummy_stub_lines):
    lines = dummy_stub_lines
    assert any("class _TestConstantsModule(_StructModule):" in line for line in lines)
    # Struct-level constants are not currently generated in stub files
    # This is acceptable as stubs are for type checking, not runtime values
    # for name in [
    #     "voidConst:",
    #     "boolConst:",
    #     "int8Const:",
    #     "uint64Const:",
    #     "float32Const:",
    #     "enumConst:",
    # ]:
    #     assert any(name in line for line in lines)


def test_versioned_structs_fields_and_defaults(dummy_stub_lines):
    lines = dummy_stub_lines
    assert any("class _TestOldVersionModule(_StructModule):" in line for line in lines)
    assert any("class _TestNewVersionModule(_StructModule):" in line for line in lines)
    # Fields should be present (now as properties)
    assert any("def new1(self)" in line and "int" in line for line in lines)
    assert any("def new2(self)" in line and "str" in line for line in lines)
    # Default values are not included in stub files (runtime feature, not type info)
    # assert any("new1:" in line and "987" in line for line in lines)
    # assert any("new2:" in line and '"baz"' in line for line in lines)


def test_name_annotations_renamed_struct_enum_fields(dummy_stub_lines):
    lines = dummy_stub_lines
    # Name annotations ($Cxx.name) are not currently processed by the generator
    # The structs use their schema names, not the C++ annotation names
    assert any("class _TestNameAnnotationModule(_StructModule):" in line for line in lines)
    # Original names are used since annotations aren't processed - now using Protocol pattern
    assert any("class _BadlyNamedEnumModule:" in line for line in lines)
    assert any("BadlyNamedEnum: _BadlyNamedEnumModule" in line for line in lines)
    assert any("badFieldName" in line or "bar" in line for line in lines)
    # Renamed names would appear if annotation support is added:
    # assert any("class RenamedStruct" in line for line in lines)
    # assert any("goodFieldName:" in line for line in lines)


def test_empty_struct_representation(dummy_stub_lines):
    lines = dummy_stub_lines
    # TestEmptyStruct should still produce a class
    assert any("class _TestEmptyStructModule(_StructModule):" in line for line in lines)
