"""Tests for Python module annotation support ($Python.module())."""

from pathlib import Path

from test_helpers import run_generator


def test_module_annotation_creates_directory_structure(tmp_path):
    """Test that $Python.module() creates the correct directory structure."""
    # Use zalfmas climate schema which has $Python.module("mas.schema.climate")
    schema_path = Path("tests/schemas/zalfmas/climate.capnp")
    output_dir = tmp_path / "output"

    run_generator(["-p", str(schema_path), "-I", "tests/schemas/zalfmas", "-o", str(output_dir), "--no-pyright"])

    # Check that the directory structure was created according to the annotation
    expected_path = output_dir / "mas" / "schema" / "climate" / "climate_capnp" / "__init__.pyi"
    assert expected_path.exists(), f"Expected stub at {expected_path}"

    # Check that __init__.py was also created
    expected_py = expected_path.parent / "__init__.py"
    assert expected_py.exists(), f"Expected __init__.py at {expected_py}"

    # Check that parent package __init__ files were created
    assert (output_dir / "mas" / "__init__.py").exists()
    assert (output_dir / "mas" / "__init__.pyi").exists()
    assert (output_dir / "mas" / "schema" / "__init__.py").exists()
    assert (output_dir / "mas" / "schema" / "__init__.pyi").exists()
    assert (output_dir / "mas" / "schema" / "climate" / "__init__.py").exists()
    assert (output_dir / "mas" / "schema" / "climate" / "__init__.pyi").exists()


def test_module_annotation_uses_absolute_imports(tmp_path):
    """Test that stubs with $Python.module() use absolute imports."""
    schema_path = Path("tests/schemas/zalfmas/climate.capnp")
    output_dir = tmp_path / "output"

    run_generator(["-p", str(schema_path), "-I", "tests/schemas/zalfmas", "-o", str(output_dir), "--no-pyright"])

    stub_path = output_dir / "mas" / "schema" / "climate" / "climate_capnp" / "__init__.pyi"
    content = stub_path.read_text()

    # Check for absolute imports (not relative with .)
    assert "from mas.schema.common.date_capnp import" in content, "Should use absolute import for date_capnp"
    assert "from mas.schema.geo.geo_capnp import" in content, "Should use absolute import for geo_capnp"
    assert "from mas.schema.persistence.persistence_capnp import" in content, (
        "Should use absolute import for persistence_capnp"
    )

    # Make sure there are no relative imports to these modules
    assert "from .date_capnp import" not in content, "Should not use relative import for date_capnp"
    assert "from .geo_capnp import" not in content, "Should not use relative import for geo_capnp"


def test_schema_without_annotation_still_works(tmp_path):
    """Test that schemas without $Python.module() still work with relative imports."""
    # Use addressbook schema which doesn't have Python module annotations
    schema_path = Path("tests/schemas/examples/addressbook/addressbook.capnp")
    output_dir = tmp_path / "output"

    run_generator(["-p", str(schema_path), "-o", str(output_dir), "--no-pyright"])

    # Without annotation, should create flat structure
    expected_path = output_dir / "addressbook_capnp" / "__init__.pyi"
    assert expected_path.exists(), f"Expected stub at {expected_path}"


def test_mixed_annotated_and_non_annotated_schemas(tmp_path):
    """Test that annotated and non-annotated schemas can coexist."""
    # Generate both types of schemas, but use different import paths to avoid conflicts
    annotated_schema = Path("tests/schemas/zalfmas/date.capnp")
    non_annotated_schema = Path("tests/schemas/examples/addressbook/addressbook.capnp")
    output_dir = tmp_path / "output"

    run_generator(["-p", str(annotated_schema), "-I", "tests/schemas/zalfmas", "-o", str(output_dir), "--no-pyright"])

    run_generator(["-p", str(non_annotated_schema), "-o", str(output_dir), "--no-pyright"])

    # Annotated schema should have module structure
    annotated_path = output_dir / "mas" / "schema" / "common" / "date_capnp" / "__init__.pyi"
    assert annotated_path.exists(), "Annotated schema should use module structure"

    # Non-annotated schema should have flat structure
    non_annotated_path = output_dir / "addressbook_capnp" / "__init__.pyi"
    assert non_annotated_path.exists(), "Non-annotated schema should use flat structure"


def test_nested_module_paths(tmp_path):
    """Test that deeply nested module paths work correctly."""
    # date.capnp has $Python.module("mas.schema.common")
    schema_path = Path("tests/schemas/zalfmas/date.capnp")
    output_dir = tmp_path / "output"

    run_generator(["-p", str(schema_path), "-I", "tests/schemas/zalfmas", "-o", str(output_dir), "--no-pyright"])

    expected_path = output_dir / "mas" / "schema" / "common" / "date_capnp" / "__init__.pyi"
    assert expected_path.exists(), f"Expected stub at {expected_path}"

    # Verify all parent directories have __init__ files
    current = expected_path.parent
    while current != output_dir:
        assert (current / "__init__.py").exists(), f"Missing __init__.py in {current}"
        assert (current / "__init__.pyi").exists(), f"Missing __init__.pyi in {current}"
        current = current.parent
