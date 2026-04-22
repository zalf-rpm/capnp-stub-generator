"""Tests for groups and nested unions in advanced_features.capnp."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.test_helpers import read_generated_types_lines

if TYPE_CHECKING:
    from pathlib import Path


def test_complex_group_presence_and_nested_union_symbols(basic_stubs: Path) -> None:
    """Test complex group presence and nested union symbols."""
    lines = read_generated_types_lines(basic_stubs / "advanced_features_capnp")
    # Check for class and field names (fields are now properties)
    for token in ["complexGroup", "g1", "deep", "deeper", "deepest"]:
        assert any(token in line for line in lines)
    # Check for property definitions
    for field in ["head", "tail"]:
        assert any(f"def {field}(self)" in line for line in lines)
