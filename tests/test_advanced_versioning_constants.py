"""Tests for constants and versioned fields in generated stubs."""

from pathlib import Path

from tests.test_helpers import read_generated_types_combined


def test_advanced_constants_and_version_fields(basic_stubs: Path) -> None:
    """Test that constants and versioned struct fields are properly generated."""
    package_dir = basic_stubs / "advanced_features_capnp"
    assert (package_dir / "types" / "modules.pyi").exists(), "Expected helper stubs for advanced features"

    content = read_generated_types_combined(package_dir)

    # Check for constants
    assert "baseInt: int" in content, "baseInt constant should be declared"
    assert "baseText: str" in content, "baseText constant should be declared"

    # Check for versioned structs with Protocol structure
    assert "class _OldVersionStructModule(_StructModule):" in content, "OldVersion Protocol should exist"
    assert "class _NewVersionStructModule(_StructModule):" in content, "NewVersion Protocol should exist"

    # Check that NewVersion has additional fields
    assert "def old1(self) -> int:" in content, "old1 field should be in NewVersion"

    # With nested Reader/Builder classes, just check that the fields exist in the file
    # (they will be in Reader/Builder classes inside NewVersion)
    assert "def new1(self)" in content, "NewVersion should have new1 field"
    assert "def newText(self)" in content, "NewVersion should have newText field"
