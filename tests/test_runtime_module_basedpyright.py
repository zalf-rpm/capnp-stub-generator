"""Regression tests for basedpyright against generated runtime modules."""

from __future__ import annotations

from pathlib import Path

from tests.test_helpers import run_command

REPO_ROOT = Path(__file__).parent.parent


def test_generated_runtime_modules_type_check_with_basedpyright(
    basic_stubs: Path,
    generated_stubs: dict[str, Path],
    zalfmas_stubs: Path,
    zalfmas_no_annotations_stubs: Path,
) -> None:
    """Generated runtime `__init__.py` files should keep schema/elementType chains strict-clean."""
    runtime_files = [
        basic_stubs / "dummy_capnp" / "__init__.py",
        basic_stubs / "fbp_channel_capnp" / "__init__.py",
        generated_stubs["examples"] / "fbp_nested_callback" / "fbp_nested_callback_capnp" / "__init__.py",
        zalfmas_stubs / "mas" / "schema" / "climate" / "climate_capnp" / "__init__.py",
        zalfmas_stubs / "mas" / "schema" / "fbp" / "fbp_capnp" / "__init__.py",
        zalfmas_no_annotations_stubs / "fbp_capnp" / "__init__.py",
    ]
    result = run_command(["basedpyright", *(str(path) for path in runtime_files)], cwd=REPO_ROOT)
    assert result.returncode == 0, result.stdout or result.stderr
