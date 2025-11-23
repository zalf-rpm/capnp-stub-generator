def test_advanced_constants_and_version_fields(basic_stubs):
    """Test that constants and versioned struct fields are properly generated."""
    stub_file = basic_stubs / "advanced_features_capnp.pyi"
    assert stub_file.exists(), "Expected stub file for advanced features"

    content = stub_file.read_text()

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
