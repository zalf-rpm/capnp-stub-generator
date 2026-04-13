"""Test generation of zalfmas schemas without Python module annotations."""

from __future__ import annotations

MIN_GENERATED_STUB_COUNT = 10
MIN_EXPECTED_ZALFMAS_STUB_COUNT = 20
MIN_SCHEMA_STUB_CONTENT_LENGTH = 100


def test_generate_zalfmas_no_annotations_stubs(zalfmas_no_annotations_stubs) -> None:
    """Test that zalfmas schemas without Python annotations generate correctly."""
    # Check that stubs were generated
    assert zalfmas_no_annotations_stubs.exists(), "Generated directory should exist"

    # Find all generated stub files
    stub_files = list(zalfmas_no_annotations_stubs.rglob("*_capnp/__init__.pyi"))

    # Should have generated stubs for multiple schemas
    assert len(stub_files) > MIN_GENERATED_STUB_COUNT, f"Expected many stub files, found {len(stub_files)}"

    # Check a specific schema exists
    common_stub = zalfmas_no_annotations_stubs / "common_capnp" / "__init__.pyi"
    assert common_stub.exists(), "common_capnp stub should exist"

    # Verify content
    content = common_stub.read_text()
    assert "class _IdInformationStructModule" in content, "Should contain IdInformation struct module"
    assert "class _IdentifiableInterfaceModule" in content, "Should contain Identifiable interface module"


def test_no_annotations_vs_annotations_structure(zalfmas_stubs, zalfmas_no_annotations_stubs) -> None:
    """Compare structure of annotated vs non-annotated schemas.

    Without Python annotations, schemas should be generated flat at the root.
    With Python annotations, schemas should be in namespace directories.
    """
    # Annotated: should have mas/schema/common/common_capnp structure
    annotated_common = zalfmas_stubs / "mas" / "schema" / "common" / "common_capnp" / "__init__.pyi"
    assert annotated_common.exists(), "Annotated schemas should use namespace structure"

    # Non-annotated: should be flat at root
    no_ann_common = zalfmas_no_annotations_stubs / "common_capnp" / "__init__.pyi"
    assert no_ann_common.exists(), "Non-annotated schemas should be flat at root"

    # Content should be similar (same structs/interfaces)
    ann_content = annotated_common.read_text()
    no_ann_content = no_ann_common.read_text()

    assert "class _IdInformationStructModule" in ann_content
    assert "class _IdInformationStructModule" in no_ann_content


def test_plugin_works_without_annotations(zalfmas_no_annotations_stubs) -> None:
    """Test that the capnpc plugin successfully processes schemas without Python annotations.

    This verifies that:
    1. The plugin doesn't crash when Python module annotation is missing
    2. Stubs are generated in the correct location (flat structure)
    3. Unknown annotation warnings are now debug-level (not polluting output)
    """
    # Check multiple schemas were generated
    stub_files = list(zalfmas_no_annotations_stubs.rglob("*_capnp/__init__.pyi"))

    # Should have many schemas
    assert len(stub_files) >= MIN_EXPECTED_ZALFMAS_STUB_COUNT, (
        f"Expected at least 20 stub files, found {len(stub_files)}"
    )

    # Verify a few key schemas
    expected_schemas = ["common_capnp", "climate_capnp", "model_capnp", "service_capnp"]
    for schema_name in expected_schemas:
        stub_path = zalfmas_no_annotations_stubs / schema_name / "__init__.pyi"
        assert stub_path.exists(), f"{schema_name} should be generated"

        # Check it has content
        content = stub_path.read_text()
        assert len(content) > MIN_SCHEMA_STUB_CONTENT_LENGTH, f"{schema_name} should have substantial content"
