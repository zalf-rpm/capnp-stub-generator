"""Tests for unions in advanced_features.capnp."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def test_top_level_union_which_literal(basic_stubs: Path) -> None:
    """Test top level union which literal."""
    path = basic_stubs / "advanced_features_capnp" / "__init__.pyi"
    with path.open(encoding="utf8") as f:
        lines = f.readlines()
    # Expect which() function for discriminant unions.
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)


def test_union_field_names_present(basic_stubs: Path) -> None:
    """Test union field names present."""
    path = basic_stubs / "advanced_features_capnp" / "__init__.pyi"
    with path.open(encoding="utf8") as f:
        lines = f.readlines()
    # Check representative union member names appear somewhere (future enhancement: in Literal).
    for name in ["a", "b", "c", "x", "y", "z", "u", "v", "g1", "deep", "deeper", "deepest"]:
        assert any(name in line for line in lines)
