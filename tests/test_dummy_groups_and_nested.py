"""Tests for groups and nested type handling in dummy.capnp."""

from __future__ import annotations

import re


def test_group_field_members_materialized(dummy_stub_lines):
    lines = dummy_stub_lines
    # Ensure TestGroups appears and group members appear flattened or via nested classes
    assert any("class _TestGroupsModule(Protocol):" in line for line in lines)
    # Look for group-specific field names (corge/grault/garply) multiple times (now as properties)
    count_corge = sum(1 for line in lines if "def corge(self)" in line)
    assert count_corge >= 3  # across foo/bar/baz groups


def test_interleaved_groups_union_and_nested_group_fields(dummy_stub_lines):
    lines = dummy_stub_lines
    assert any("class _TestInterleavedGroupsModule(Protocol):" in line for line in lines)
    # Expect nested group names or fields plugh/xyzzy/fred across two groups (now as properties)
    found = {name: False for name in ["plugh", "xyzzy", "fred", "waldo"]}
    for line in lines:
        for k in found:
            if f"def {k}(self)" in line:
                found[k] = True
    assert all(found.values())


def test_nested_types_enums_and_lists(dummy_stub_lines):
    lines = dummy_stub_lines
    # Nested enums are now Enum classes under their parent struct with TypeAliases
    assert any(re.match(r"^\s*class _NestedEnum1Module\(Enum\):", line) for line in lines)
    assert any(re.match(r"^\s*class _NestedEnum2Module\(Enum\):", line) for line in lines)
    assert any("NestedEnum1: TypeAlias = _NestedEnum1Module" in line for line in lines)
    assert any("NestedEnum2: TypeAlias = _NestedEnum2Module" in line for line in lines)
    # Using declarations produce aliases or reexports
    assert any("class _TestUsingModule(Protocol):" in line for line in lines)
    # Fields referencing nested enums use dotted names with module alias (not flattened, now as properties)
    assert any(
        "def outerNestedEnum(self)" in line and "_TestNestedTypesModule._NestedEnum1Module" in line for line in lines
    )
    assert any(
        "def innerNestedEnum(self)" in line and "_TestNestedTypesModule._NestedStructModule._NestedEnum2Module" in line
        for line in lines
    )


def test_using_type_aliases_resolved(dummy_stub_lines):
    lines = dummy_stub_lines
    # OuterNestedEnum alias should result in field typing referencing original enum builder/reader variants
    assert any("OuterNestedEnum" in line and "Literal" not in line for line in lines)
    # Ensure the Using struct fields appear
    assert any("class _TestUsingModule(Protocol):" in line for line in lines)
