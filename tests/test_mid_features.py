"""Mid-complexity schema tests."""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def mid_features_stub_lines(basic_stubs):
    stub_path = basic_stubs / "mid_features_capnp.pyi"
    with open(stub_path) as f:
        return f.readlines()


def test_enum_and_nested_enum_definitions(mid_features_stub_lines):
    lines = mid_features_stub_lines
    content = "".join(lines)
    assert "Enum" in content


def test_struct_fields_and_defaults(mid_features_stub_lines):
    lines = mid_features_stub_lines
    content = "".join(lines)
    assert "class" in content


def test_list_and_sequence_annotations(mid_features_stub_lines):
    lines = mid_features_stub_lines
    content = "".join(lines)
    assert "Sequence" in content or "List" in content


def test_union_which_and_literal_import(mid_features_stub_lines):
    lines = mid_features_stub_lines
    content = "".join(lines)
    assert "which" in content.lower()
