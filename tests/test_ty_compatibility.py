"""Regression tests for type-checker compatibility details."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def test_generated_stubs_avoid_ty_shadowing_and_override_errors(basic_stubs: Path) -> None:
    """Generated stubs should avoid ty's builtin shadowing and override-name diagnostics."""
    type_dir = basic_stubs / "ty_compat_capnp" / "types"
    readers = (type_dir / "readers.pyi").read_text(encoding="utf8")
    builders = (type_dir / "builders.pyi").read_text(encoding="utf8")
    lists = (type_dir / "lists.pyi").read_text(encoding="utf8")

    assert "import builtins" in readers
    assert "def bool(self) -> builtins.bool: ..." in readers

    assert "import builtins" in builders
    assert "def bool(self) -> builtins.bool: ..." in builders
    assert "def bool(self, value: builtins.bool) -> None: ..." in builders

    assert "def __getitem__(self, index: int) -> float: ..." in lists
    assert "def __setitem__(self, index: int, value: float) -> None: ..." in lists
    assert "key: int" not in lists
