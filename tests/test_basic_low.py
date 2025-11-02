"""Low complexity schema generation tests for basic_low.capnp."""

from __future__ import annotations

import os

from capnp_stub_generator.cli import main

here = os.path.dirname(__file__)
_out_dir = os.path.join(here, "_generated")


def _generate() -> list[str]:
    os.makedirs(_out_dir, exist_ok=True)
    main(
        [
            "-p",
            os.path.join(here, "schemas", "basic_low.capnp"),
            "-o",
            _out_dir,
        ]
    )
    path = os.path.join(_out_dir, "basic_low_capnp.pyi")
    with open(path, encoding="utf8") as f:
        return f.readlines()


def test_enum_color_defined():
    lines = _generate()
    assert any(l.startswith("from enum import") for l in lines)
    assert any(l.strip().startswith("class Color(Enum):") for l in lines)
    for member in ["red", "green", "blue"]:
        assert any(l.strip() == f'{member} = "{member}"' for l in lines)


def test_basiclow_struct_and_fields():
    lines = _generate()
    assert any("class BasicLow" in l for l in lines)
    for field in ["id:", "name:", "isActive:", "favoriteColor:"]:
        assert any(field in l for l in lines)
    # List fields should be annotated with Sequence
    assert any("scores:" in l and "Sequence" in l for l in lines)
    assert any("tags:" in l and "Sequence" in l for l in lines)


def test_builder_reader_presence():
    lines = _generate()
    # BasicLowReader and BasicLowBuilder classes
    assert any(l.strip().startswith("class BasicLowReader(BasicLow):") for l in lines)
    assert any(l.strip().startswith("class BasicLowBuilder(BasicLow):") for l in lines)
