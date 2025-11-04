from pathlib import Path

from capnp_stub_generator.cli import main

SCHEMAS_DIR = Path(__file__).parent / "schemas"
SCHEMA = SCHEMAS_DIR / "advanced_features.capnp"
DUMMY_SCHEMA = SCHEMAS_DIR / "dummy.capnp"


def test_name_annotations(tmp_path):
    """Test that Cap'n Proto name annotations ($Cxx.name) are handled.

    Note: The generator currently uses the original schema names rather than
    the annotated names. This is intentional as Python stubs should match
    the Python API, which uses the original names. The annotations are
    primarily for C++ code generation.
    """
    # Need to load dummy.capnp as well since advanced_features imports it
    main(["-p", str(DUMMY_SCHEMA), str(SCHEMA), "-o", str(tmp_path)])
    stub = tmp_path / "advanced_features_capnp.pyi"
    assert stub.exists(), "Stub should be generated"

    content = stub.read_text()

    # The Python API uses the original names from the schema, not the C++ annotations
    # This is correct behavior - name annotations are for other language bindings
    assert "class BadName:" in content, "BadName struct should use original name"

    # Check that the struct has the expected fields (using original names)
    assert "union {" in content or "def badField(self)" in content or "def alt(self)" in content, (
        "BadName should have union fields"
    )

    # Check for nested enum (original name)
    lines = content.split("\n")
    in_badname = False
    found_oops_enum = False

    for line in lines:
        if "class BadName:" in line:
            in_badname = True
        elif in_badname and line.startswith("class ") and "BadName" not in line and "Oops" not in line:
            in_badname = False

        if in_badname and "class Oops(Enum):" in line:
            found_oops_enum = True
            break

    assert found_oops_enum, "BadName should have nested Oops enum"
