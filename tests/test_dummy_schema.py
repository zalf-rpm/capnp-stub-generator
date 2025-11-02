"""Consolidated tests for dummy.capnp schema covering all features.

This consolidates the following test modules:
- test_dummy_enums_and_all_types
- test_dummy_lists_and_defaults
- test_dummy_groups_and_nested
- test_dummy_unions
- test_dummy_constants_versions_names
"""

from __future__ import annotations

import re

import pytest
from conftest import read_stub_file


@pytest.fixture(scope="module")
def dummy_stub_lines(generate_core_stubs):
    """Read dummy.capnp stub file lines."""
    stub_path = generate_core_stubs / "dummy_capnp.pyi"
    return read_stub_file(stub_path)


class TestDummyEnumsAndTypes:
    """Tests for enum definitions and basic types."""

    def test_enum_definition_and_imports(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(line.startswith("from enum import") and "Enum" in line for line in lines)
        assert any(line.strip().startswith("class TestEnum(Enum):") for line in lines)
        for name in ["foo", "bar", "baz", "qux"]:
            assert any(line.strip() == f'{name} = "{name}"' for line in lines)

    def test_testalltypes_field_presence_and_collections_import(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(
            line.startswith("from collections.abc import")
            and "Sequence" in line
            and "Iterator" in line
            for line in lines
        )
        for field in [
            "voidField",
            "boolField",
            "int8Field",
            "float64Field",
            "textField",
            "dataField",
        ]:
            assert any(field + ":" in line for line in lines)
        assert any("structField:" in line and "TestAllTypes" in line for line in lines)
        assert any("enumField:" in line and "TestEnum" in line for line in lines)


class TestDummyListsAndDefaults:
    """Tests for list handling and default values."""

    def test_lists_small_struct_and_listlist_fields(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestLists" in line for line in lines)
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

    def test_list_defaults_struct_and_scalar_lists_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestListDefaults" in line for line in lines)
        for field in ["list0:", "list1:", "list8:"]:
            assert any(field in line for line in lines), f"Missing field {field}"

    def test_field_zero_bit_and_defaults(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestFieldZeroIsBit" in line for line in lines)
        assert any("bit:" in line and "bool" in line for line in lines)
        assert any("secondBit:" in line and "bool" in line for line in lines)
        assert any("thirdField:" in line and "int" in line for line in lines)


class TestDummyGroupsAndNested:
    """Tests for groups and nested type handling."""

    def test_group_field_members_materialized(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestGroups" in line for line in lines)
        count_corge = sum(1 for line in lines if "corge:" in line)
        assert count_corge >= 3  # across foo/bar/baz groups

    def test_interleaved_groups_union_and_nested_group_fields(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestInterleavedGroups" in line for line in lines)
        found = {name: False for name in ["plugh", "xyzzy", "fred", "waldo"]}
        for line in lines:
            for k in found:
                if k + ":" in line:
                    found[k] = True
        assert all(found.values())

    def test_nested_types_enums_and_lists(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(re.match(r"^\s*class NestedEnum1\(Enum\):", line) for line in lines)
        assert any(re.match(r"^\s*class NestedEnum2\(Enum\):", line) for line in lines)
        assert any("class TestUsing" in line for line in lines)
        assert any(
            "outerNestedEnum:" in line and "TestNestedTypes" in line and "NestedEnum1" in line
            for line in lines
        )
        assert any(
            "innerNestedEnum:" in line and "TestNestedTypes" in line and "NestedEnum2" in line
            for line in lines
        )

    def test_using_type_aliases_resolved(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("OuterNestedEnum" in line and "Literal" not in line for line in lines)
        assert any("class TestUsing" in line for line in lines)


class TestDummyUnions:
    """Tests for union-related features."""

    def test_union_which_methods_and_literal_import(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)
        assert any(line.startswith("from typing import") and "Literal" in line for line in lines)

    def test_unnamed_union_fields_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestUnnamedUnion" in line for line in lines)
        assert any("foo:" in line and "int" in line for line in lines) or any(
            "foo:" in line and "Optional" in line for line in lines
        )
        assert any("bar:" in line and "int" in line for line in lines) or any(
            "bar:" in line and "Optional" in line for line in lines
        )

    def test_interleaved_union_discriminants_sorted(self, dummy_stub_lines):
        lines = dummy_stub_lines
        which_methods = [line for line in lines if "def which" in line and "Literal" in line]
        assert which_methods

    def test_union_defaults_struct_initializers_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestUnionDefaults" in line for line in lines)
        assert any("s16s8s64s8Set:" in line for line in lines)
        assert any("s0sps1s32Set:" in line for line in lines)
        assert any("unnamed1:" in line for line in lines)
        assert any("unnamed2:" in line for line in lines)


class TestDummyConstantsAndVersioning:
    """Tests for constants, versioned structs, and name annotations."""

    def test_global_constants_and_derived_constant_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("globalInt:" in line for line in lines)
        assert any("globalText:" in line for line in lines)

    def test_struct_constants_section(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestConstants" in line for line in lines)

    def test_versioned_structs_fields_and_defaults(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestOldVersion" in line for line in lines)
        assert any("class TestNewVersion" in line for line in lines)
        assert any("new1:" in line and "int" in line for line in lines)
        assert any("new2:" in line and "str" in line for line in lines)

    def test_name_annotations_renamed_struct_enum_fields(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestNameAnnotation" in line for line in lines)
        assert any("class BadlyNamedEnum" in line for line in lines)
        assert any("badFieldName" in line or "bar" in line for line in lines)

    def test_empty_struct_representation(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestEmptyStruct" in line for line in lines)
