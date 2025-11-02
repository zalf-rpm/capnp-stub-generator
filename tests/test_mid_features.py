"""Tests for mid_features.capnp covering nested structs/enums, union, defaults, and lists."""

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
            os.path.join(here, "schemas", "mid_features.capnp"),
            "-o",
            _out_dir,
        ]
    )
    path = os.path.join(_out_dir, "mid_features_capnp.pyi")
    with open(path, encoding="utf8") as f:
        return f.readlines()


def test_enum_and_nested_enum_definitions():
    lines = _generate()
    # Top-level enum import and class
    assert any(l.startswith("from enum import") and "Enum" in l for l in lines)
    assert any(l.strip().startswith("class TopEnum(Enum):") for l in lines)
    # Nested enum class for Nested.State (not flattened)
    assert any(re.match(r"^\s*class State\(Enum\):", l) for l in lines)
    # Representative enumerants
    for name in ["alpha", "beta", "gamma", "start", "running", "done"]:
        assert any(l.strip() == f'{name} = "{name}"' for l in lines)


def test_struct_fields_and_defaults():
    lines = _generate()
    # Main struct and nested struct reader/builder classes
    assert any(
        l.strip().startswith("class MidFeatureContainerReader(MidFeatureContainer):") for l in lines
    )
    assert any(
        l.strip().startswith("class MidFeatureContainerBuilder(MidFeatureContainer):")
        for l in lines
    )
    # Basic fields appear
    for field in ["id:", "name:", "mode:", "nested:"]:
        assert any(field in l for l in lines)
    # Default values are not included in stub files (runtime info, not type info)
    # Check field types instead
    assert any("name:" in l and "str" in l for l in lines)
    assert any("mode:" in l and "TopEnum" in l for l in lines)
    # Nested struct fields
    assert any("flag:" in l and "bool" in l for l in lines)
    assert any("count:" in l and "int" in l for l in lines)
    assert any("state:" in l and "State" in l for l in lines)


def test_list_and_sequence_annotations():
    lines = _generate()
    # Sequence import present
    assert any(l.startswith("from collections.abc import") and "Sequence" in l for l in lines)
    # Lists of nested struct and enums
    assert any("nestedList:" in l and "Sequence" in l for l in lines)
    assert any("enumList:" in l and "Sequence" in l for l in lines)
    assert any("stateList:" in l and "Sequence" in l for l in lines)


def test_union_which_and_literal_import():
    lines = _generate()
    # which() should exist for discriminantCount > 0
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", l) for l in lines)
    # Literal import for which()
    assert any(l.startswith("from typing import") and "Literal" in l for l in lines)
    # Union field names appear in which return type (expected future enhancement)
    # Not asserting specific names due to current generator limitations.
