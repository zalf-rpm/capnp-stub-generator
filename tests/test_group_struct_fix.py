import argparse
from pathlib import Path

from capnp_stub_generator.run import run


def test_group_struct_naming(tmp_path):
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

    stub_file = output_dir / "repro_group_struct_capnp.pyi"
    assert stub_file.exists()

    content = stub_file.read_text()

    # Check that Struct is used with parent scoping
    # Parent is TestGroupStruct, so group name should be TestGroupStructStruct
    assert "class _TestGroupStructStructStructModule(_StructModule):" in content
    assert "type TestGroupStructStructReader = _TestGroupStructStructStructModule.Reader" in content
    assert "type TestGroupStructStructBuilder = _TestGroupStructStructStructModule.Builder" in content

    # Check that generic Struct is NOT used (to avoid collisions)
    assert "class _StructStructModule" not in content

    # Check that GroupStruct is NOT used
    assert "class _GroupStructStructModule" not in content

    # Check that Enum is used with parent scoping
    # Parent is TestGroupEnum, so group name should be TestGroupEnumEnum
    assert "class _TestGroupEnumEnumStructModule(_StructModule):" in content
    assert "type TestGroupEnumEnumReader = _TestGroupEnumEnumStructModule.Reader" in content
    assert "type TestGroupEnumEnumBuilder = _TestGroupEnumEnumStructModule.Builder" in content

    # Check that generic Enum is NOT used (to avoid collisions)
    assert "class _EnumStructModule" not in content
