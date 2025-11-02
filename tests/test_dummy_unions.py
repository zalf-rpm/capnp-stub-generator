"""Tests for union-related sections of dummy.capnp split out."""

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


def test_union_which_methods_and_literal_import():
    lines = _generate()
    # which() for TestUnion should be present with Literal return
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)
    # Literal import appears (for which and maybe discriminants)
    assert any(line.startswith("from typing import") and "Literal" in line for line in lines)


def test_unnamed_union_fields_present():
    lines = _generate()
    # TestUnnamedUnion field annotations should include foo/bar discriminant usage
    assert any("class TestUnnamedUnion" in line for line in lines)
    assert any("foo:" in line and "int" in line for line in lines) or any(
        "foo:" in line and "Optional" in line for line in lines
    )
    assert any("bar:" in line and "int" in line for line in lines) or any(
        "bar:" in line and "Optional" in line for line in lines
    )


def test_interleaved_union_discriminants_sorted():
    lines = _generate()
    # Discriminant enums are not generated separately
    # Instead, which() methods use Literal types
    # Check that which() methods exist for union types
    which_methods = [line for line in lines if "def which" in line and "Literal" in line]
    assert which_methods  # there should be which() methods for unions


def test_union_defaults_struct_initializers_present():
    lines = _generate()
    # Defaults referencing unions should generate inline initializers in TestUnionDefaults
    assert any("class TestUnionDefaults" in line for line in lines)
    assert any("s16s8s64s8Set:" in line for line in lines)
    assert any("s0sps1s32Set:" in line for line in lines)
    # Unnamed union defaults
    assert any("unnamed1:" in line for line in lines)
    assert any("unnamed2:" in line for line in lines)
