"""Low complexity schema generation tests for basic_low.capnp."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.test_helpers import read_generated_types_lines

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(scope="module")
def basic_low_stub_lines(basic_stubs: Path) -> list[str]:
    """Read basic_low.capnp stub lines."""
    return read_generated_types_lines(basic_stubs / "basic_low_capnp")


def test_enum_color_defined(basic_low_stub_lines: list[str]) -> None:
    """Test enum color defined."""
    lines = basic_low_stub_lines
    # Enums are generated as _EnumModule-typed helper classes with int attributes.
    assert any("class _ColorEnumModule(_EnumModule):" in line for line in lines)
    # Enum values are int annotations
    assert any("red: int" in line for line in lines)
    assert any("green: int" in line for line in lines)
    assert any("blue: int" in line for line in lines)
    # Type alias at top level with Literal values
    assert any('type ColorEnum = int | Literal["red", "green", "blue"]' in line for line in lines)


def test_basiclow_struct_and_fields(basic_low_stub_lines: list[str]) -> None:
    """Test basiclow struct and fields."""
    lines = basic_low_stub_lines
    assert any("class _BasicLowStructModule(_StructModule):" in line for line in lines)
    content = "".join(lines)
    assert "name" in content
    assert "id" in content


def test_builder_reader_presence(basic_low_stub_lines: list[str]) -> None:
    """Test builder reader presence."""
    lines = basic_low_stub_lines
    content = "".join(lines)
    assert "BasicLowBuilder" in content
    assert "BasicLowReader" in content
