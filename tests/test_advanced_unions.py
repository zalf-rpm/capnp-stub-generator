"""Tests for unions in advanced_features.capnp."""

from __future__ import annotations

import os
import re

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


def test_top_level_union_which_literal():
    lines = _generate()
    # Expect which() function for discriminant unions.
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)


def test_union_field_names_present():
    lines = _generate()
    # Check representative union member names appear somewhere (future enhancement: in Literal).
    for name in ["a", "b", "c", "x", "y", "z", "u", "v", "g1", "deep", "deeper", "deepest"]:
        assert any(name in line for line in lines)
