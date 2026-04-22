"""Tests for handling Cap'n Proto name annotations in generated stubs."""

from pathlib import Path

from tests.test_helpers import read_generated_types_combined


def test_name_annotations(basic_stubs: Path) -> None:
    """Test that Cap'n Proto name annotations ($Cxx.name) are handled.

    Note: The generator currently uses the original schema names rather than
    the annotated names. This is intentional as Python stubs should match
    the Python API, which uses the original names. The annotations are
    primarily for C++ code generation.
    """
    package_dir = basic_stubs / "advanced_features_capnp"
    assert (package_dir / "types" / "modules.pyi").exists(), "Stub should be generated"

    content = read_generated_types_combined(package_dir)

    # The Python API uses the original names from the schema, not the C++ annotations
    # With _StructModule structure, check for the module and annotation
    assert "class _BadNameStructModule(_StructModule):" in content, "BadName _StructModule should use original name"
    assert "BadName: _BadNameStructModule" in content, "BadName annotation should exist"

    # Check that the struct has the expected fields (using original names)
    assert "union {" in content or "def badField(self)" in content or "def alt(self)" in content, (
        "BadName should have union fields"
    )

    # Check for nested enum (original name)
    lines = content.split("\n")
    in_badname = False
    found_oops_enum = False

    for line in lines:
        if "class _BadNameStructModule(_StructModule):" in line:
            in_badname = True
        elif in_badname and line.startswith("class ") and "_BadNameStructModule" not in line and "Oops" not in line:
            in_badname = False

        if in_badname and "class _OopsEnumModule(_EnumModule):" in line:
            found_oops_enum = True
            break

    assert found_oops_enum, "BadName should have nested Oops enum helper"
