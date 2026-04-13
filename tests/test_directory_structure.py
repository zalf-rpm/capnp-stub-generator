"""Tests for directory structure preservation in output."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from tests.test_helpers import run_generator

EXPECTED_GENERATED_PACKAGE_COUNT = 3


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


def test_directory_structure_preserved(temp_schema_dir, temp_output_dir) -> None:
    """Test that input directory structure is preserved in output."""
    # Get all schema files
    schema_files = [str(f) for f in temp_schema_dir.rglob("*.capnp")]

    # Generate stubs
    args = ["-p", *schema_files, "-o", str(temp_output_dir), "--no-pyright"]
    run_generator(args)

    # Verify structure is preserved
    assert (temp_output_dir / "root_capnp" / "__init__.pyi").exists()
    assert (temp_output_dir / "subdir1" / "sub1_capnp" / "__init__.pyi").exists()
    assert (temp_output_dir / "subdir2" / "nested" / "deep_capnp" / "__init__.pyi").exists()

    # Verify files are not flattened
    assert not (temp_output_dir / "sub1_capnp" / "__init__.pyi").exists()
    assert not (temp_output_dir / "deep_capnp" / "__init__.pyi").exists()


def test_directory_structure_with_glob(temp_schema_dir, temp_output_dir) -> None:
    """Test directory structure preservation with glob patterns."""
    # Use glob pattern
    pattern = str(temp_schema_dir / "**" / "*.capnp")
    args = ["-p", pattern, "-o", str(temp_output_dir), "-r", "--no-pyright"]
    run_generator(args)

    # Count generated packages (directories with __init__.pyi files)
    generated_packages = [
        f.parent
        for f in temp_output_dir.rglob("*_capnp/__init__.pyi")
        if "capnp-stubs" not in str(f) and "schema_capnp" not in str(f)
    ]
    assert len(generated_packages) == EXPECTED_GENERATED_PACKAGE_COUNT  # root, sub1, deep

    # Verify structure
    package_names = [str(p.relative_to(temp_output_dir)) for p in generated_packages]
    assert any("subdir1" in name for name in package_names)
    assert any("subdir2" in name for name in package_names)


def test_single_file_no_nested_structure(temp_schema_dir, temp_output_dir) -> None:
    """Test that single file doesn't create unnecessary nesting."""
    # Generate stub for single file
    schema_file = str(temp_schema_dir / "root.capnp")
    args = ["-p", schema_file, "-o", str(temp_output_dir), "--no-pyright"]
    run_generator(args)

    # Should be directly in output dir (as package)
    assert (temp_output_dir / "root_capnp" / "__init__.pyi").exists()
    assert not any((temp_output_dir / d).exists() for d in ["subdir1", "subdir2"])


@pytest.mark.skip(
    reason="Plugin-based generation requires output directory; generating next to source is not currently supported",
)
def test_no_output_dir_places_next_to_source(temp_schema_dir) -> None:
    """Test that without -o flag, stubs are placed next to source files."""
    schema_file = str(temp_schema_dir / "root.capnp")
    args = ["-p", schema_file]
    run_generator(args)

    # Stub should be next to source
    assert (temp_schema_dir / "root_capnp" / "__init__.pyi").exists()


def test_mixed_directory_levels(temp_schema_dir, temp_output_dir) -> None:
    """Test with schemas at different directory levels."""
    # Get all schemas
    schema_files = [str(f) for f in temp_schema_dir.rglob("*.capnp")]

    args = ["-p", *schema_files, "-o", str(temp_output_dir), "--no-pyright"]
    run_generator(args)

    # All should be generated - check for package directories with __init__.pyi
    all_packages = [
        f.parent
        for f in temp_output_dir.rglob("*_capnp/__init__.pyi")
        if "capnp-stubs" not in str(f) and "schema_capnp" not in str(f)
    ]
    assert len(all_packages) == EXPECTED_GENERATED_PACKAGE_COUNT

    # Structure should match input - check for __init__.pyi in packages
    assert (temp_output_dir / "root_capnp" / "__init__.pyi").exists()
    assert (temp_output_dir / "subdir1" / "sub1_capnp" / "__init__.pyi").exists()
    assert (temp_output_dir / "subdir2" / "nested" / "deep_capnp" / "__init__.pyi").exists()
