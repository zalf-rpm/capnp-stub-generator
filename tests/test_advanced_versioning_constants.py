from pathlib import Path

from capnp_stub_generator.cli import main

SCHEMAS_DIR = Path(__file__).parent / "schemas"
SCHEMA = SCHEMAS_DIR / "advanced_features.capnp"
DUMMY_SCHEMA = SCHEMAS_DIR / "dummy.capnp"


def test_advanced_constants_and_version_fields(tmp_path):
    """Test that constants and versioned struct fields are properly generated."""
    # Need to load dummy.capnp as well since advanced_features imports it
    main(["-p", str(DUMMY_SCHEMA), str(SCHEMA), "-o", str(tmp_path)])

    stub_file = tmp_path / "advanced_features_capnp.pyi"
    assert stub_file.exists(), "Expected stub file for advanced features"

    content = stub_file.read_text()

    # Check for constants
    assert "baseInt: int" in content, "baseInt constant should be declared"
    assert "baseText: str" in content, "baseText constant should be declared"

    # Check for versioned structs
    assert "class OldVersion:" in content, "OldVersion struct should exist"
    assert "class NewVersion:" in content, "NewVersion struct should exist"

    # Check that NewVersion has additional fields
    assert "def old1(self) -> int:" in content, "old1 field should be in NewVersion"
    lines = content.split("\n")

    # Find NewVersion class and verify it has new1 and newText fields
    in_new_version = False
    found_new1 = False
    found_new_text = False

    for i, line in enumerate(lines):
        if "class NewVersion:" in line:
            in_new_version = True
        elif in_new_version and "class " in line and "NewVersion" not in line:
            in_new_version = False

        if in_new_version:
            if "def new1(self)" in line:
                found_new1 = True
            if "def newText(self)" in line:
                found_new_text = True

    assert found_new1, "NewVersion should have new1 field"
    assert found_new_text, "NewVersion should have newText field"
