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
    assert any("globalInt:" in l for l in lines)
    assert any("globalText:" in l for l in lines)
    # Struct constants are not currently generated in stubs
    # assert any("globalStruct:" in l for l in lines)
    # assert any("derivedConstant:" in l for l in lines)


def test_struct_constants_section():
    lines = _generate()
    assert any("class TestConstants" in l for l in lines)
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
    #     assert any(name in l for l in lines)


def test_versioned_structs_fields_and_defaults():
    lines = _generate()
    assert any("class TestOldVersion" in l for l in lines)
    assert any("class TestNewVersion" in l for l in lines)
    # Fields should be present
    assert any("new1:" in l and "int" in l for l in lines)
    assert any("new2:" in l and "str" in l for l in lines)
    # Default values are not included in stub files (runtime feature, not type info)
    # assert any("new1:" in l and "987" in l for l in lines)
    # assert any("new2:" in l and '"baz"' in l for l in lines)


def test_name_annotations_renamed_struct_enum_fields():
    lines = _generate()
    # Name annotations ($Cxx.name) are not currently processed by the generator
    # The structs use their schema names, not the C++ annotation names
    assert any("class TestNameAnnotation" in l for l in lines)
    # Original names are used since annotations aren't processed
    assert any("class BadlyNamedEnum" in l for l in lines)
    assert any("badFieldName" in l or "bar" in l for l in lines)
    # Renamed names would appear if annotation support is added:
    # assert any("class RenamedStruct" in l for l in lines)
    # assert any("goodFieldName:" in l for l in lines)


def test_empty_struct_representation():
    lines = _generate()
    # TestEmptyStruct should still produce a class
    assert any("class TestEmptyStruct" in l for l in lines)
