"""Tests for import path generation in .py files."""

import re


def test_import_path_includes_schema_directory(zalfmas_stubs):
    """Test that the schema's own directory is included in import_path."""
    # Check monica_management_capnp.py
    # It is located in tests/_generated/zalfmas/model/monica/monica_management_capnp.py
    # The schema is in tests/schemas/zalfmas/model/monica/monica_management.capnp

    stub_file = zalfmas_stubs / "model/monica/monica_management_capnp.py"
    content = stub_file.read_text()

    # Extract import_path list
    match = re.search(r"import_path = \[(.*?)\]", content, re.DOTALL)
    assert match, "import_path not found in generated file"
    import_path_str = match.group(1)

    # Should contain the schema directory
    # Since we are using abspath and join, we look for the relative path part
    # The relative path from generated file to schema dir is "../../../../schemas/zalfmas/model/monica"
    # But wait, the test environment might have different paths.
    # The key is that we expect to see the path to the schema directory added.

    # In the user's example:
    # module_file = .../schemas/zalfmas/model/monica/monica_management.capnp
    # import_path should contain .../schemas/zalfmas/model/monica

    # Let's check for the presence of the path component
    assert "model/monica" in import_path_str, "Schema directory should be in import_path"

    # Also check that abspath is used
    assert "os.path.abspath" in import_path_str, "import_path should use abspath"


def test_import_path_no_duplicates(zalfmas_stubs):
    """Test that import_path does not contain duplicates."""
    stub_file = zalfmas_stubs / "model/monica/monica_params_capnp.py"
    content = stub_file.read_text()

    match = re.search(r"import_path = \[(.*?)\]", content, re.DOTALL)
    assert match
    import_path_str = match.group(1)

    # Split by comma and clean up
    # The string is like: here, os.path.abspath(os.path.join(here, "path")), ...
    # Simple split by comma might split inside function calls if not careful, but here paths are simple strings
    # However, the regex captured the content inside [], which might be multiline or have spaces

    # Let's use a smarter way to parse or just check for specific duplicates
    # If we see the same path component twice, it's a duplicate

    # Normalize whitespace
    import_path_str = " ".join(import_path_str.split())

    # Check if any path appears twice
    # We can extract the paths inside quotes
    quoted_paths = re.findall(r'"([^"]*)"', import_path_str)
    unique_quoted = set(quoted_paths)

    assert len(quoted_paths) == len(unique_quoted), f"Duplicate paths found: {quoted_paths}"


def test_import_path_uses_abspath(zalfmas_stubs):
    """Test that all paths in import_path are wrapped in abspath."""
    stub_file = zalfmas_stubs / "model/monica/monica_management_capnp.py"
    content = stub_file.read_text()

    match = re.search(r"import_path = \[(.*?)\]", content, re.DOTALL)
    assert match
    import_path_str = match.group(1)

    # Check that every os.path.join is wrapped in os.path.abspath
    # We can check this by ensuring "os.path.join" is always preceded by "os.path.abspath("

    # Find all occurrences of os.path.join
    indices = [m.start() for m in re.finditer(r"os\.path\.join", import_path_str)]

    for idx in indices:
        # Check preceding characters
        # Should be "os.path.abspath("
        preceding = import_path_str[max(0, idx - 16) : idx]
        assert "os.path.abspath(" in preceding, f"os.path.join at index {idx} not wrapped in abspath"
