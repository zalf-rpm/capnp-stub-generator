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
    assert any("class TestGroups" in l for l in lines)
    # Look for group-specific field names (corge/grault/garply) multiple times
    count_corge = sum(1 for l in lines if "corge:" in l)
    assert count_corge >= 3  # across foo/bar/baz groups


def test_interleaved_groups_union_and_nested_group_fields():
    lines = _generate()
    assert any("class TestInterleavedGroups" in l for l in lines)
    # Expect nested group names or fields plugh/xyzzy/fred across two groups
    found = {name: False for name in ["plugh", "xyzzy", "fred", "waldo"]}
    for l in lines:
        for k in found:
            if k + ":" in l:
                found[k] = True
    assert all(found.values())


def test_nested_types_enums_and_lists():
    lines = _generate()
    # Nested enums are under their parent struct, not flattened
    assert any(re.match(r"^\s*class NestedEnum1\(Enum\):", l) for l in lines)
    assert any(re.match(r"^\s*class NestedEnum2\(Enum\):", l) for l in lines)
    # Using declarations produce aliases or reexports
    assert any("class TestUsing" in l for l in lines)
    # Fields referencing nested enums use dotted names (not flattened)
    assert any(
        "outerNestedEnum:" in l and "TestNestedTypes" in l and "NestedEnum1" in l for l in lines
    )
    assert any(
        "innerNestedEnum:" in l and "TestNestedTypes" in l and "NestedEnum2" in l for l in lines
    )


def test_using_type_aliases_resolved():
    lines = _generate()
    # OuterNestedEnum alias should result in field typing referencing original enum builder/reader variants
    assert any("OuterNestedEnum" in l and "Literal" not in l for l in lines)
    # Ensure the Using struct fields appear
    assert any("class TestUsing" in l for l in lines)
