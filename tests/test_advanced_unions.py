"""Tests for unions in advanced_features.capnp."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.test_helpers import read_generated_types_lines

if TYPE_CHECKING:
    from pathlib import Path


def test_top_level_union_refines_runtime_which_descriptor(basic_stubs: Path) -> None:
    """Refine the runtime callable property without replacing it with a method."""
    lines = read_generated_types_lines(basic_stubs / "advanced_features_capnp")
    assert any("class _AdvancedContainerFirstUnionWhich(_DynamicEnumField):" in line for line in lines)
    assert any('def __call__(self) -> Literal["a", "b", "c"]:' in line for line in lines)
    which_lines = [index for index, line in enumerate(lines) if "def which(" in line]
    assert which_lines
    assert any(
        any("@property" in prior_line for prior_line in lines[max(0, index - 2) : index]) for index in which_lines
    )


def test_union_field_names_present(basic_stubs: Path) -> None:
    """Test union field names present."""
    lines = read_generated_types_lines(basic_stubs / "advanced_features_capnp")
    # Check representative union member names appear somewhere (future enhancement: in Literal).
    for name in ["a", "b", "c", "x", "y", "z", "u", "v", "g1", "deep", "deeper", "deepest"]:
        assert any(name in line for line in lines)
