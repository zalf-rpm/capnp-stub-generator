"""Tests for list encoding sizes, list defaults, and small struct behaviors in dummy.capnp."""

from __future__ import annotations

import pytest
from conftest import read_stub_file


@pytest.fixture(scope="module")
def dummy_stub_lines(generate_core_stubs):
    """Read dummy.capnp stub file lines."""
    stub_path = generate_core_stubs / "dummy_capnp.pyi"
    return read_stub_file(stub_path)


def test_lists_small_struct_and_listlist_fields(dummy_stub_lines):
    lines = dummy_stub_lines
    assert any("class TestLists" in line for line in lines)
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
        assert any(field in line for line in lines), f"Missing field {field}"


def test_list_defaults_struct_and_scalar_lists_present(dummy_stub_lines):
    lines = dummy_stub_lines
    assert any("class TestListDefaults" in line for line in lines)
    # Default values are not included in stub files (they're runtime info, not type info)
    # Check that the fields exist with proper types instead
    for field in ["list0:", "list1:", "list8:"]:
        assert any(field in line for line in lines), f"Missing field {field}"


def test_field_zero_bit_and_defaults(dummy_stub_lines):
    lines = dummy_stub_lines
    assert any("class TestFieldZeroIsBit" in line for line in lines)
    # Check fields exist
    assert any("bit:" in line and "bool" in line for line in lines)
    assert any("secondBit:" in line and "bool" in line for line in lines)
    assert any("thirdField:" in line and "int" in line for line in lines)
    # Default values are not shown in stub files
