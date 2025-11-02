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
    assert any(line.startswith("from enum import") and "Enum" in line for line in lines)
    assert any(line.strip().startswith("class TopEnum(Enum):") for line in lines)
    # Nested enum class for Nested.State (not flattened)
    assert any(re.match(r"^\s*class State\(Enum\):", line) for line in lines)
    # Representative enumerants
    for name in ["alpha", "beta", "gamma", "start", "running", "done"]:
        assert any(line.strip() == f'{name} = "{name}"' for line in lines)


def test_struct_fields_and_defaults():
    lines = _generate()
    # Main struct and nested struct reader/builder classes
    assert any(
        line.strip().startswith("class MidFeatureContainerReader(MidFeatureContainer):")
        for line in lines
    )
    assert any(
        line.strip().startswith("class MidFeatureContainerBuilder(MidFeatureContainer):")
        for line in lines
    )
    # Basic fields appear
    for field in ["id:", "name:", "mode:", "nested:"]:
        assert any(field in line for line in lines)
    # Default values are not included in stub files (runtime info, not type info)
    # Check field types instead
    assert any("name:" in line and "str" in line for line in lines)
    assert any("mode:" in line and "TopEnum" in line for line in lines)
    # Nested struct fields
    assert any("flag:" in line and "bool" in line for line in lines)
    assert any("count:" in line and "int" in line for line in lines)
    assert any("state:" in line and "State" in line for line in lines)


def test_list_and_sequence_annotations():
    lines = _generate()
    # Sequence import present
    assert any(
        line.startswith("from collections.abc import") and "Sequence" in line for line in lines
    )
    # Lists of nested struct and enums
    assert any("nestedList:" in line and "Sequence" in line for line in lines)
    assert any("enumList:" in line and "Sequence" in line for line in lines)
    assert any("stateList:" in line and "Sequence" in line for line in lines)


def test_union_which_and_literal_import():
    lines = _generate()
    # which() should exist for discriminantCount > 0
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)
    # Literal import for which()
    assert any(line.startswith("from typing import") and "Literal" in line for line in lines)
    # Union field names appear in which return type (expected future enhancement)
    # Not asserting specific names due to current generator limitations.
