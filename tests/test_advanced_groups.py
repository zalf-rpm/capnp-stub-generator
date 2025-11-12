"""Tests for groups and nested unions in advanced_features.capnp."""

from __future__ import annotations


def test_complex_group_presence_and_nested_union_symbols(basic_stubs):
    path = basic_stubs / "advanced_features_capnp.pyi"
    with open(path, encoding="utf8") as f:
        lines = f.readlines()
    # Check for class and field names (fields are now properties)
    for token in ["complexGroup", "g1", "deep", "deeper", "deepest"]:
        assert any(token in line for line in lines)
    # Check for property definitions
    for field in ["head", "tail"]:
        assert any(f"def {field}(self)" in line for line in lines)
