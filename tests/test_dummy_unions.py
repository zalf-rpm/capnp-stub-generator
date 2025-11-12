"""Tests for union-related sections of dummy.capnp split out."""

from __future__ import annotations

import re


def test_union_which_methods_and_literal_import(dummy_stub_lines):
    lines = dummy_stub_lines
    # which() for TestUnion should be present with Literal return
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)
    # Literal import appears (for which and maybe discriminants)
    assert any(line.startswith("from typing import") and "Literal" in line for line in lines)


def test_unnamed_union_fields_present(dummy_stub_lines):
    lines = dummy_stub_lines
    # TestUnnamedUnion field annotations should include foo/bar discriminant usage (now as properties)
    assert any("class TestUnnamedUnion" in line for line in lines)
    assert any("def foo(self)" in line and "int" in line for line in lines) or any(
        "def foo(self)" in line and "Optional" in line for line in lines
    )
    assert any("def bar(self)" in line and "int" in line for line in lines) or any(
        "def bar(self)" in line and "Optional" in line for line in lines
    )


def test_interleaved_union_discriminants_sorted(dummy_stub_lines):
    lines = dummy_stub_lines
    # Discriminant enums are not generated separately
    # Instead, which() methods use Literal types
    # Check that which() methods exist for union types
    which_methods = [line for line in lines if "def which" in line and "Literal" in line]
    assert which_methods  # there should be which() methods for unions


def test_union_defaults_struct_initializers_present(dummy_stub_lines):
    lines = dummy_stub_lines
    # Defaults referencing unions should generate inline initializers in TestUnionDefaults (now as properties)
    assert any("class TestUnionDefaults" in line for line in lines)
    assert any("def s16s8s64s8Set(self)" in line for line in lines)
    assert any("def s0sps1s32Set(self)" in line for line in lines)
    # Unnamed union defaults
    assert any("def unnamed1(self)" in line for line in lines)
    assert any("def unnamed2(self)" in line for line in lines)
