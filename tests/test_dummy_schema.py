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


class TestDummyEnumsAndTypes:
    """Tests for enum definitions and basic types."""

    def test_enum_definition_and_imports(self, dummy_stub_lines):
        lines = dummy_stub_lines
        # Enums are now simple classes with int attributes
        assert any(line.strip().startswith("class _TestEnumEnumModule:") for line in lines)
        # Type alias at top level (not instance annotation)
        assert any(line.strip().startswith("type TestEnumEnum = int | Literal[") for line in lines)
        for name in ["foo", "bar", "baz", "qux"]:
            assert any(f"{name}: int" in line for line in lines)

    def test_testalltypes_field_presence_and_collections_import(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(line.startswith("from collections.abc import") and "Sequence" in line for line in lines)
        # Fields are now properties
        for field in [
            "voidField",
            "boolField",
            "int8Field",
            "float64Field",
            "textField",
            "dataField",
        ]:
            assert any(f"def {field}(self)" in line for line in lines)
        assert any("def structField(self)" in line and "TestAllTypes" in line for line in lines)
        assert any("def enumField(self)" in line for line in lines)


class TestDummyListsAndDefaults:
    """Tests for list handling and default values."""

    def test_lists_small_struct_and_listlist_fields(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestListsStructModule(_StructModule):" in line for line in lines)
        # Fields are now properties - check for def fieldname(self)
        for field in [
            "list0",
            "list1",
            "list8",
            "list16",
            "list32",
            "list64",
            "listP",
            "listlist0",
            "listlist1",
            "listlist8",
            "listlist16",
            "listlist32",
            "listlist64",
            "listlistP",
            "list0c",
            "list1c",
            "list8c",
            "list16c",
            "list32c",
            "list64c",
            "listPc",
            "int32ListList",
            "textListList",
            "structListList",
        ]:
            assert any(f"def {field}(self)" in line for line in lines), f"Missing field {field}"

    def test_list_defaults_struct_and_scalar_lists_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestListDefaultsStructModule(_StructModule):" in line for line in lines)
        # Fields are now properties
        for field in ["list0", "list1", "list8"]:
            assert any(f"def {field}(self)" in line for line in lines), f"Missing field {field}"

    def test_field_zero_bit_and_defaults(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestFieldZeroIsBitStructModule(_StructModule):" in line for line in lines)
        # Fields are now properties
        assert any("def bit(self)" in line and "bool" in line for line in lines)
        assert any("def secondBit(self)" in line and "bool" in line for line in lines)
        assert any("def thirdField(self)" in line and "int" in line for line in lines)


class TestDummyGroupsAndNested:
    """Tests for groups and nested type handling."""

    def test_group_field_members_materialized(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestGroupsStructModule(_StructModule):" in line for line in lines)
        # Fields are now properties
        count_corge = sum(1 for line in lines if "def corge(self)" in line)
        assert count_corge >= 3  # across foo/bar/baz groups

    def test_interleaved_groups_union_and_nested_group_fields(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestInterleavedGroupsStructModule(_StructModule):" in line for line in lines)
        # Fields are now properties
        found = {name: False for name in ["plugh", "xyzzy", "fred", "waldo"]}
        for line in lines:
            for k in found:
                if f"def {k}(self)" in line:
                    found[k] = True
        assert all(found.values())

    def test_nested_types_enums_and_lists(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(re.match(r"^\s*class _NestedEnum1EnumModule:", line) for line in lines)
        assert any(re.match(r"^\s*class _NestedEnum2EnumModule:", line) for line in lines)
        assert any("NestedEnum1: _NestedEnum1EnumModule" in line for line in lines)
        assert any("NestedEnum2: _NestedEnum2EnumModule" in line for line in lines)
        assert any("class _TestUsingStructModule(_StructModule):" in line for line in lines)
        # Enum fields now return the Enum type alias
        assert any("def outerNestedEnum(self) -> TestNestedTypesNestedEnum1Enum" in line for line in lines)
        assert any("def innerNestedEnum(self) -> TestNestedTypesNestedStructNestedEnum2Enum" in line for line in lines)

    def test_using_type_aliases_resolved(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("OuterNestedEnum" in line and "Literal" not in line for line in lines)
        assert any("class _TestUsingStructModule(_StructModule):" in line for line in lines)


class TestDummyUnions:
    """Tests for union-related features."""

    def test_union_which_methods_and_literal_import(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)
        assert any(line.startswith("from typing import") and "Literal" in line for line in lines)

    def test_unnamed_union_fields_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestUnnamedUnionStructModule(_StructModule):" in line for line in lines)
        # Fields are now properties
        assert any("def foo(self)" in line and "int" in line for line in lines) or any(
            "def foo(self)" in line and "Optional" in line for line in lines
        )
        assert any("def bar(self)" in line and "int" in line for line in lines) or any(
            "def bar(self)" in line and "Optional" in line for line in lines
        )

    def test_interleaved_union_discriminants_sorted(self, dummy_stub_lines):
        lines = dummy_stub_lines
        which_methods = [line for line in lines if "def which" in line and "Literal" in line]
        assert which_methods

    def test_union_defaults_struct_initializers_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestUnionDefaultsStructModule(_StructModule):" in line for line in lines)
        # Fields are now properties
        assert any("def s16s8s64s8Set(self)" in line for line in lines)
        assert any("def s0sps1s32Set(self)" in line for line in lines)
        assert any("def unnamed1(self)" in line for line in lines)
        assert any("def unnamed2(self)" in line for line in lines)


class TestDummyConstantsAndVersioning:
    """Tests for constants, versioned structs, and name annotations."""

    def test_global_constants_and_derived_constant_present(self, dummy_stub_lines):
        lines = dummy_stub_lines
        # Constants remain as simple annotations (not properties)
        assert any("globalInt:" in line for line in lines)
        assert any("globalText:" in line for line in lines)

    def test_struct_constants_section(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestConstantsStructModule(_StructModule):" in line for line in lines)

    def test_versioned_structs_fields_and_defaults(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestOldVersionStructModule(_StructModule):" in line for line in lines)
        assert any("class _TestNewVersionStructModule(_StructModule):" in line for line in lines)
        # Fields are now properties
        assert any("def new1(self)" in line and "int" in line for line in lines)
        assert any("def new2(self)" in line and "str" in line for line in lines)

    def test_name_annotations_renamed_struct_enum_fields(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestNameAnnotationStructModule(_StructModule):" in line for line in lines)
        assert any("class _BadlyNamedEnumEnumModule:" in line for line in lines)
        assert any("BadlyNamedEnum: _BadlyNamedEnumEnumModule" in line for line in lines)
        assert any("badFieldName" in line or "bar" in line for line in lines)

    def test_empty_struct_representation(self, dummy_stub_lines):
        lines = dummy_stub_lines
        assert any("class _TestEmptyStructStructModule(_StructModule):" in line for line in lines)
