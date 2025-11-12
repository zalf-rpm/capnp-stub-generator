"""Tests for unions in advanced_features.capnp."""

from __future__ import annotations

import re


def test_top_level_union_which_literal(basic_stubs):
    path = basic_stubs / "advanced_features_capnp.pyi"
    with open(path, encoding="utf8") as f:
        lines = f.readlines()
    # Expect which() function for discriminant unions.
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)


def test_union_field_names_present(basic_stubs):
    path = basic_stubs / "advanced_features_capnp.pyi"
    with open(path, encoding="utf8") as f:
        lines = f.readlines()
    # Check representative union member names appear somewhere (future enhancement: in Literal).
    for name in ["a", "b", "c", "x", "y", "z", "u", "v", "g1", "deep", "deeper", "deepest"]:
        assert any(name in line for line in lines)
