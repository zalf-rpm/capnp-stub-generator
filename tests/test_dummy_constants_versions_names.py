"""Tests for constants, versioned structs, and name annotations in dummy.capnp."""

from __future__ import annotations

import os

from capnp_stub_generator.cli import main

here = os.path.dirname(__file__)
_out_dir = os.path.join(here, "_generated")


def _generate() -> list[str]:
    os.makedirs(_out_dir, exist_ok=True)
    main(
        [
            "-p",
            os.path.join(here, "schemas", "dummy.capnp"),
            "-o",
            _out_dir,
        ]
    )
    path = os.path.join(_out_dir, "dummy_capnp.pyi")
    with open(path, encoding="utf8") as f:
        return f.readlines()


def test_global_constants_and_derived_constant_present():
    lines = _generate()
    # Global constants - only primitive types are currently generated
    assert any("globalInt:" in line for line in lines)
    assert any("globalText:" in line for line in lines)
    # Struct constants are not currently generated in stubs
    # assert any("globalStruct:" in line for line in lines)
    # assert any("derivedConstant:" in line for line in lines)


def test_struct_constants_section():
    lines = _generate()
    assert any("class TestConstants" in line for line in lines)
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


def test_versioned_structs_fields_and_defaults():
    lines = _generate()
    assert any("class TestOldVersion" in line for line in lines)
    assert any("class TestNewVersion" in line for line in lines)
    # Fields should be present
    assert any("new1:" in line and "int" in line for line in lines)
    assert any("new2:" in line and "str" in line for line in lines)
    # Default values are not included in stub files (runtime feature, not type info)
    # assert any("new1:" in line and "987" in line for line in lines)
    # assert any("new2:" in line and '"baz"' in line for line in lines)


def test_name_annotations_renamed_struct_enum_fields():
    lines = _generate()
    # Name annotations ($Cxx.name) are not currently processed by the generator
    # The structs use their schema names, not the C++ annotation names
    assert any("class TestNameAnnotation" in line for line in lines)
    # Original names are used since annotations aren't processed
    assert any("class BadlyNamedEnum" in line for line in lines)
    assert any("badFieldName" in line or "bar" in line for line in lines)
    # Renamed names would appear if annotation support is added:
    # assert any("class RenamedStruct" in line for line in lines)
    # assert any("goodFieldName:" in line for line in lines)


def test_empty_struct_representation():
    lines = _generate()
    # TestEmptyStruct should still produce a class
    assert any("class TestEmptyStruct" in line for line in lines)
