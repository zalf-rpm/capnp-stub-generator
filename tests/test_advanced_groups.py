"""Tests for groups and nested unions in advanced_features.capnp."""

from __future__ import annotations

import os

from capnp_stub_generator.cli import main

here = os.path.dirname(__file__)
out_dir = os.path.join(here, "_generated")


def _generate() -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    # Need to load dummy.capnp too since advanced_features imports it
    main(
        [
            "-p",
            os.path.join(here, "schemas", "dummy.capnp"),
            os.path.join(here, "schemas", "advanced_features.capnp"),
            "-o",
            out_dir,
        ]
    )
    path = os.path.join(out_dir, "advanced_features_capnp.pyi")
    with open(path, encoding="utf8") as f:
        return f.readlines()


def test_complex_group_presence_and_nested_union_symbols():
    lines = _generate()
    for token in ["complexGroup", "head:", "tail:", "g1", "deep", "deeper", "deepest"]:
        assert any(token in line for line in lines)
