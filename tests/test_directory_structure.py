"""Tests for directory structure preservation in output."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from capnp_stub_generator.cli import main


@pytest.fixture
def temp_schema_dir():
    """Create a temporary directory with nested schema structure."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create directory structure
        (temp_dir / "subdir1").mkdir()
        (temp_dir / "subdir2" / "nested").mkdir(parents=True)

        # Create simple schemas with unique IDs
        (temp_dir / "root.capnp").write_text("""
@0xaabbccdd11223344;

struct RootStruct {
    value @0 :Int32;
}
""")

        (temp_dir / "subdir1" / "sub1.capnp").write_text("""
@0xbbccddee22334455;

struct Sub1Struct {
    name @0 :Text;
}
""")

        (temp_dir / "subdir2" / "nested" / "deep.capnp").write_text("""
@0xccddff3344556677;

struct DeepStruct {
    id @0 :UInt64;
}
""")

        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def test_directory_structure_preserved(temp_schema_dir, temp_output_dir):
    """Test that input directory structure is preserved in output."""
    # Get all schema files
    schema_files = [str(f) for f in temp_schema_dir.rglob("*.capnp")]

    # Generate stubs
    args = ["-p"] + schema_files + ["-o", str(temp_output_dir)]
    main(args)

    # Verify structure is preserved
    assert (temp_output_dir / "root_capnp.pyi").exists()
    assert (temp_output_dir / "subdir1" / "sub1_capnp.pyi").exists()
    assert (temp_output_dir / "subdir2" / "nested" / "deep_capnp.pyi").exists()

    # Verify files are not flattened
    assert not (temp_output_dir / "sub1_capnp.pyi").exists()
    assert not (temp_output_dir / "deep_capnp.pyi").exists()


def test_directory_structure_with_glob(temp_schema_dir, temp_output_dir):
    """Test directory structure preservation with glob patterns."""
    # Use glob pattern
    pattern = str(temp_schema_dir / "**" / "*.capnp")
    args = ["-p", pattern, "-o", str(temp_output_dir), "-r"]
    main(args)

    # Count generated files
    generated = list(temp_output_dir.rglob("*.pyi"))
    assert len(generated) == 3  # root, sub1, deep

    # Verify structure
    assert any("subdir1" in str(f) for f in generated)
    assert any("subdir2" in str(f) for f in generated)


def test_single_file_no_nested_structure(temp_schema_dir, temp_output_dir):
    """Test that single file doesn't create unnecessary nesting."""
    # Generate stub for single file
    schema_file = str(temp_schema_dir / "root.capnp")
    args = ["-p", schema_file, "-o", str(temp_output_dir)]
    main(args)

    # Should be directly in output dir
    assert (temp_output_dir / "root_capnp.pyi").exists()
    assert not any((temp_output_dir / d).exists() for d in ["subdir1", "subdir2"])


def test_no_output_dir_places_next_to_source(temp_schema_dir):
    """Test that without -o flag, stubs are placed next to source files."""
    schema_file = str(temp_schema_dir / "root.capnp")
    args = ["-p", schema_file]
    main(args)

    # Stub should be next to source
    assert (temp_schema_dir / "root_capnp.pyi").exists()


def test_mixed_directory_levels(temp_schema_dir, temp_output_dir):
    """Test with schemas at different directory levels."""
    # Get all schemas
    schema_files = [str(f) for f in temp_schema_dir.rglob("*.capnp")]

    args = ["-p"] + schema_files + ["-o", str(temp_output_dir)]
    main(args)

    # All should be generated
    all_pyi = list(temp_output_dir.rglob("*.pyi"))
    assert len(all_pyi) == 3

    # Structure should match input
    rel_paths_input = {
        str(f.relative_to(temp_schema_dir).with_suffix(""))
        for f in temp_schema_dir.rglob("*.capnp")
    }
    rel_paths_output = {str(f.relative_to(temp_output_dir).with_suffix("")) for f in all_pyi}

    # Transform _capnp suffix
    rel_paths_output_normalized = {p.replace("_capnp", "") for p in rel_paths_output}

    assert rel_paths_input == rel_paths_output_normalized
