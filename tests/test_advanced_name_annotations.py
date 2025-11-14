def test_name_annotations(basic_stubs):
    """Test that Cap'n Proto name annotations ($Cxx.name) are handled.

    Note: The generator currently uses the original schema names rather than
    the annotated names. This is intentional as Python stubs should match
    the Python API, which uses the original names. The annotations are
    primarily for C++ code generation.
    """
    stub = basic_stubs / "advanced_features_capnp.pyi"
    assert stub.exists(), "Stub should be generated"

    content = stub.read_text()

    # The Python API uses the original names from the schema, not the C++ annotations
    # With Protocol structure, check for the Protocol and annotation
    assert "class _BadNameModule(Protocol):" in content, "BadName Protocol should use original name"
    assert "BadName: _BadNameModule" in content, "BadName annotation should exist"

    # Check that the struct has the expected fields (using original names)
    assert "union {" in content or "def badField(self)" in content or "def alt(self)" in content, (
        "BadName should have union fields"
    )

    # Check for nested enum (original name)
    lines = content.split("\n")
    in_badname = False
    found_oops_enum = False

    for line in lines:
        if "class _BadNameModule(Protocol):" in line:
            in_badname = True
        elif in_badname and line.startswith("class ") and "_BadNameModule" not in line and "Oops" not in line:
            in_badname = False

        if in_badname and "class _OopsModule(Enum):" in line:
            found_oops_enum = True
            break

    assert found_oops_enum, "BadName should have nested Oops enum (as Enum class)"
