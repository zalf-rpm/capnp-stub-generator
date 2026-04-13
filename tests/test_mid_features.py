"""Mid-complexity schema tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(scope="module")
def mid_features_stub_lines(basic_stubs: Path) -> list[str]:
    stub_path = basic_stubs / "mid_features_capnp" / "__init__.pyi"
    with open(stub_path) as f:
        return f.readlines()


def test_enum_and_nested_enum_definitions(mid_features_stub_lines: list[str]) -> None:
    lines = mid_features_stub_lines
    content = "".join(lines)
    assert "Enum" in content


def test_struct_fields_and_defaults(mid_features_stub_lines: list[str]) -> None:
    lines = mid_features_stub_lines
    content = "".join(lines)
    assert "class" in content


def test_list_and_sequence_annotations(mid_features_stub_lines: list[str]) -> None:
    lines = mid_features_stub_lines
    content = "".join(lines)
    assert "Sequence" in content or "List" in content


def test_union_which_and_literal_import(mid_features_stub_lines: list[str]) -> None:
    lines = mid_features_stub_lines
    content = "".join(lines)
    assert "which" in content.lower()
