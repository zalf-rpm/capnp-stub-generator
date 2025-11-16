"""Low complexity schema generation tests for basic_low.capnp."""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def basic_low_stub_lines(basic_stubs):
    """Read basic_low.capnp stub lines."""
    stub_path = basic_stubs / "basic_low_capnp.pyi"
    with open(stub_path, encoding="utf8") as f:
        return f.readlines()


def test_enum_color_defined(basic_low_stub_lines):
    lines = basic_low_stub_lines
    # Enums are now generated as simple classes with int attributes
    assert any("class _ColorModule:" in line for line in lines)
    # Enum values are int annotations
    assert any("red: int" in line for line in lines)
    assert any("green: int" in line for line in lines)
    assert any("blue: int" in line for line in lines)
    # Type alias at top level with Literal values
    assert any('type Color = int | Literal["red", "green", "blue"]' in line for line in lines)


def test_basiclow_struct_and_fields(basic_low_stub_lines):
    lines = basic_low_stub_lines
    assert any("class _BasicLowModule(_StructModule):" in line for line in lines)
    content = "".join(lines)
    assert "name" in content and "id" in content


def test_builder_reader_presence(basic_low_stub_lines):
    lines = basic_low_stub_lines
    content = "".join(lines)
    assert "BasicLowBuilder" in content
    assert "BasicLowReader" in content
