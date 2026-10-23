"""Tests for union-related sections of dummy.capnp split out."""

from __future__ import annotations


def test_union_refines_runtime_which_descriptor(dummy_stub_lines: list[str]) -> None:
    """Union types narrow the real callable ``which`` descriptor."""
    lines = dummy_stub_lines
    assert any("class _TestStructUnionUnWhich(_DynamicEnumField):" in line for line in lines)
    assert any('def __call__(self) -> Literal["struct", "object"]:' in line for line in lines)
    which_lines = [index for index, line in enumerate(lines) if "def which(" in line]
    assert which_lines
    assert any(
        any("@property" in prior_line for prior_line in lines[max(0, index - 2) : index]) for index in which_lines
    )


def test_unnamed_union_fields_present(dummy_stub_lines: list[str]) -> None:
    """Test unnamed union fields present."""
    lines = dummy_stub_lines
    # TestUnnamedUnion field annotations should include foo/bar discriminant usage (now as properties)
    assert any("class _TestUnnamedUnionStructModule(_StructModule):" in line for line in lines)
    assert any("def foo(self)" in line and "int" in line for line in lines) or any(
        "def foo(self)" in line and "Optional" in line for line in lines
    )
    assert any("def bar(self)" in line and "int" in line for line in lines) or any(
        "def bar(self)" in line and "Optional" in line for line in lines
    )


def test_interleaved_union_discriminants_sorted(dummy_stub_lines: list[str]) -> None:
    """Interleaved union discriminants retain their runtime field order."""
    lines = dummy_stub_lines
    assert any("class _TestInterleavedGroupsGroup1Which(_DynamicEnumField):" in line for line in lines)
    assert any('def __call__(self) -> Literal["qux", "corge", "fred"]:' in line for line in lines)


def test_union_defaults_struct_initializers_present(dummy_stub_lines: list[str]) -> None:
    """Test union defaults struct initializers present."""
    lines = dummy_stub_lines
    # Defaults referencing unions should generate inline initializers in TestUnionDefaults (now as properties)
    assert any("class _TestUnionDefaultsStructModule(_StructModule):" in line for line in lines)
    assert any("def s16s8s64s8Set(self)" in line for line in lines)
    assert any("def s0sps1s32Set(self)" in line for line in lines)
    # Unnamed union defaults
    assert any("def unnamed1(self)" in line for line in lines)
    assert any("def unnamed2(self)" in line for line in lines)
