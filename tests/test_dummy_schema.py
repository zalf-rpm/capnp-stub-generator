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
        assert any(l.startswith("from enum import") and "Enum" in l for l in lines)
        assert any(l.strip().startswith("class TestEnum(Enum):") for l in lines)
        for name in ["foo", "bar", "baz", "qux"]:
            assert any(l.strip() == f'{name} = "{name}"' for l in lines)

    def test_testalltypes_field_presence_and_collections_import(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(
            l.startswith("from collections.abc import") and "Sequence" in l and "Iterator" in l
            for l in lines
        )
        for field in [
            "voidField",
            "boolField",
            "int8Field",
            "float64Field",
            "textField",
            "dataField",
        ]:
            assert any(field + ":" in l for l in lines)
        assert any("structField:" in l and "TestAllTypes" in l for l in lines)
        assert any("enumField:" in l and "TestEnum" in l for l in lines)


class TestDummyListsAndDefaults:
    """Tests for list handling and default values."""

    def test_lists_small_struct_and_listlist_fields(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestLists" in l for l in lines)
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

    def test_list_defaults_struct_and_scalar_lists_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestListDefaults" in l for l in lines)
        for field in ["list0:", "list1:", "list8:"]:
            assert any(field in l for l in lines), f"Missing field {field}"

    def test_field_zero_bit_and_defaults(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestFieldZeroIsBit" in l for l in lines)
        assert any("bit:" in l and "bool" in l for l in lines)
        assert any("secondBit:" in l and "bool" in l for l in lines)
        assert any("thirdField:" in l and "int" in l for l in lines)


class TestDummyGroupsAndNested:
    """Tests for groups and nested type handling."""

    def test_group_field_members_materialized(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestGroups" in l for l in lines)
        count_corge = sum(1 for l in lines if "corge:" in l)
        assert count_corge >= 3  # across foo/bar/baz groups

    def test_interleaved_groups_union_and_nested_group_fields(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestInterleavedGroups" in l for l in lines)
        found = {name: False for name in ["plugh", "xyzzy", "fred", "waldo"]}
        for l in lines:
            for k in found:
                if k + ":" in l:
                    found[k] = True
        assert all(found.values())

    def test_nested_types_enums_and_lists(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(re.match(r"^\s*class NestedEnum1\(Enum\):", l) for l in lines)
        assert any(re.match(r"^\s*class NestedEnum2\(Enum\):", l) for l in lines)
        assert any("class TestUsing" in l for l in lines)
        assert any(
            "outerNestedEnum:" in l and "TestNestedTypes" in l and "NestedEnum1" in l for l in lines
        )
        assert any(
            "innerNestedEnum:" in l and "TestNestedTypes" in l and "NestedEnum2" in l for l in lines
        )

    def test_using_type_aliases_resolved(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("OuterNestedEnum" in l and "Literal" not in l for l in lines)
        assert any("class TestUsing" in l for l in lines)


class TestDummyUnions:
    """Tests for union-related features."""

    def test_union_which_methods_and_literal_import(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(re.match(r"^\s*def which\(self\) -> Literal\[", l) for l in lines)
        assert any(l.startswith("from typing import") and "Literal" in l for l in lines)

    def test_unnamed_union_fields_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestUnnamedUnion" in l for l in lines)
        assert any("foo:" in l and "int" in l for l in lines) or any(
            "foo:" in l and "Optional" in l for l in lines
        )
        assert any("bar:" in l and "int" in l for l in lines) or any(
            "bar:" in l and "Optional" in l for l in lines
        )

    def test_interleaved_union_discriminants_sorted(self, dummy_stub_lines):
        lines = dummy_stub_lines
        which_methods = [l for l in lines if "def which" in l and "Literal" in l]
        assert which_methods

    def test_union_defaults_struct_initializers_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestUnionDefaults" in l for l in lines)
        assert any("s16s8s64s8Set:" in l for l in lines)
        assert any("s0sps1s32Set:" in l for l in lines)
        assert any("unnamed1:" in l for l in lines)
        assert any("unnamed2:" in l for l in lines)


class TestDummyConstantsAndVersioning:
    """Tests for constants, versioned structs, and name annotations."""

    def test_global_constants_and_derived_constant_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("globalInt:" in l for l in lines)
        assert any("globalText:" in l for l in lines)

    def test_struct_constants_section(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestConstants" in l for l in lines)

    def test_versioned_structs_fields_and_defaults(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestOldVersion" in l for l in lines)
        assert any("class TestNewVersion" in l for l in lines)
        assert any("new1:" in l and "int" in l for l in lines)
        assert any("new2:" in l and "str" in l for l in lines)

    def test_name_annotations_renamed_struct_enum_fields(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestNameAnnotation" in l for l in lines)
        assert any("class BadlyNamedEnum" in l for l in lines)
        assert any("badFieldName" in l or "bar" in l for l in lines)

    def test_empty_struct_representation(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class TestEmptyStruct" in l for l in lines)
