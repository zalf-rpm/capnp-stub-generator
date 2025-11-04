"""Tests for groups and nested type handling in dummy.capnp."""

from __future__ import annotations

import os
import re

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


def test_group_field_members_materialized():
    lines = _generate()
    # Ensure TestGroups appears and group members appear flattened or via nested classes
    assert any("class TestGroups" in line for line in lines)
    # Look for group-specific field names (corge/grault/garply) multiple times (now as properties)
    count_corge = sum(1 for line in lines if "def corge(self)" in line)
    assert count_corge >= 3  # across foo/bar/baz groups


def test_interleaved_groups_union_and_nested_group_fields():
    lines = _generate()
    assert any("class TestInterleavedGroups" in line for line in lines)
    # Expect nested group names or fields plugh/xyzzy/fred across two groups (now as properties)
    found = {name: False for name in ["plugh", "xyzzy", "fred", "waldo"]}
    for line in lines:
        for k in found:
            if f"def {k}(self)" in line:
                found[k] = True
    assert all(found.values())


def test_nested_types_enums_and_lists():
    lines = _generate()
    # Nested enums are under their parent struct, not flattened
    assert any(re.match(r"^\s*class NestedEnum1\(Enum\):", line) for line in lines)
    assert any(re.match(r"^\s*class NestedEnum2\(Enum\):", line) for line in lines)
    # Using declarations produce aliases or reexports
    assert any("class TestUsing" in line for line in lines)
    # Fields referencing nested enums use dotted names (not flattened, now as properties)
    assert any(
        "def outerNestedEnum(self)" in line and "TestNestedTypes" in line and "NestedEnum1" in line for line in lines
    )
    assert any(
        "def innerNestedEnum(self)" in line and "TestNestedTypes" in line and "NestedEnum2" in line for line in lines
    )


def test_using_type_aliases_resolved():
    lines = _generate()
    # OuterNestedEnum alias should result in field typing referencing original enum builder/reader variants
    assert any("OuterNestedEnum" in line and "Literal" not in line for line in lines)
    # Ensure the Using struct fields appear
    assert any("class TestUsing" in line for line in lines)
