"""Tests for group struct generation fixes."""

import argparse
from pathlib import Path

from capnp_stub_generator.run import run
from tests.test_helpers import read_generated_types_combined


def test_group_struct_naming(tmp_path: Path) -> None:
    """Test that a group named 'struct' is generated as 'Struct' and not 'GroupStruct'."""
    # Use absolute path for schema
    cwd = Path.cwd()
    schema_path = cwd / "tests/schemas/repro_group_struct.capnp"
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    args = argparse.Namespace(
        paths=[str(schema_path)],
        excludes=[],
        clean=[],
        output_dir=str(output_dir),
        import_paths=[],
        recursive=False,
        skip_pyright=True,
        augment_capnp_stubs=False,
    )

    run(args, str(cwd))

    package_dir = output_dir / "repro_group_struct_capnp"
    assert (package_dir / "types" / "modules.pyi").exists()

    content = read_generated_types_combined(package_dir)

    # Check that Struct is used with parent scoping
    # Parent is TestGroupStruct, so group name should be TestGroupStructStruct
    assert "class _TestGroupStructStructStructModule(_StructModule):" in content
    assert "class TestGroupStructStructReader(" in content
    assert "class TestGroupStructStructReader(_DynamicStructReader):" in content
    assert "class TestGroupStructStructBuilder(" in content
    assert "class TestGroupStructStructBuilder(_DynamicStructBuilder):" in content

    # Check that generic Struct is NOT used (to avoid collisions)
    assert "class _StructStructModule" not in content

    # Check that GroupStruct is NOT used
    assert "class _GroupStructStructModule" not in content

    # Check that Enum is used with parent scoping
    # Parent is TestGroupEnum, so group name should be TestGroupEnumEnum
    assert "class _TestGroupEnumEnumStructModule(_StructModule):" in content
    assert "class TestGroupEnumEnumReader(" in content
    assert "class TestGroupEnumEnumReader(_DynamicStructReader):" in content
    assert "class TestGroupEnumEnumBuilder(" in content
    assert "class TestGroupEnumEnumBuilder(_DynamicStructBuilder):" in content

    # Check that generic Enum is NOT used (to avoid collisions)
    assert "class _EnumStructModule" not in content
