"""Tests for list encoding sizes, list defaults, and small struct behaviors in dummy.capnp."""

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


def test_lists_small_struct_and_listlist_fields():
    lines = _generate()
    assert any("class TestLists" in l for l in lines)
    # Representative fields from each category
    for field in [
        "list0:",
        "list1:",
        "list8:",
        "list16:",
        "list32:",
        "list64:",
        "listP:",
        "listlist0:",
        "listlist1:",
        "listlist8:",
        "listlist16:",
        "listlist32:",
        "listlist64:",
        "listlistP:",
        "list0c:",
        "list1c:",
        "list8c:",
        "list16c:",
        "list32c:",
        "list64c:",
        "listPc:",
        "int32ListList:",
        "textListList:",
        "structListList:",
    ]:
        assert any(field in l for l in lines), f"Missing field {field}"


def test_list_defaults_struct_and_scalar_lists_present():
    lines = _generate()
    assert any("class TestListDefaults" in l for l in lines)
    # Default values are not included in stub files (they're runtime info, not type info)
    # Check that the fields exist with proper types instead
    for field in ["list0:", "list1:", "list8:"]:
        assert any(field in l for l in lines), f"Missing field {field}"


def test_field_zero_bit_and_defaults():
    lines = _generate()
    assert any("class TestFieldZeroIsBit" in l for l in lines)
    # Check fields exist
    assert any("bit:" in l and "bool" in l for l in lines)
    assert any("secondBit:" in l and "bool" in l for l in lines)
    assert any("thirdField:" in l and "int" in l for l in lines)
    # Default values are not shown in stub files
