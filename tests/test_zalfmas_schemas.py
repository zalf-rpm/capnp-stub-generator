"""Test zalfmas capnp schemas with stub generation.

This module tests the generation of stubs for the zalfmas schemas,
which include:
- Absolute imports (e.g., /capnp/c++.capnp)
- Relative imports (e.g., import "common.capnp")
- Complex nested schema structures
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import capnp
import pytest

from capnp_stub_generator.cli import main

# Test directories
TESTS_DIR = Path(__file__).parent
ZALFMAS_DIR = TESTS_DIR / "zalfmas_capnp_schemas"
GENERATED_ZALFMAS_DIR = TESTS_DIR / "_generated_zalfmas"


@pytest.fixture(scope="module")
def generated_zalfmas_dir():
    """Ensure the generated zalfmas directory exists and is clean."""
    if GENERATED_ZALFMAS_DIR.exists():
        shutil.rmtree(GENERATED_ZALFMAS_DIR)

    GENERATED_ZALFMAS_DIR.mkdir(parents=True, exist_ok=True)

    yield GENERATED_ZALFMAS_DIR

    # Keep generated files for inspection
    # shutil.rmtree(GENERATED_ZALFMAS_DIR)


def test_zalfmas_schemas_exist():
    """Test that zalfmas schemas are present."""
    assert ZALFMAS_DIR.exists(), "zalfmas_capnp_schemas directory not found"
    
    schema_files = list(ZALFMAS_DIR.glob("*.capnp"))
    assert len(schema_files) > 0, "No capnp schema files found in zalfmas_capnp_schemas"
    
    print(f"\nFound {len(schema_files)} zalfmas schema files:")
    for schema in sorted(schema_files):
        print(f"  - {schema.name}")


def test_absolute_imports_handling(generated_zalfmas_dir):
    """Test handling of absolute imports like /capnp/c++.capnp.
    
    This test verifies that schemas with absolute imports can be loaded
    when proper import paths are provided.
    """
    # Try to load a schema with absolute imports
    common_schema = ZALFMAS_DIR / "common.capnp"
    
    assert common_schema.exists(), "common.capnp not found"
    
    # Read and check for absolute imports
    content = common_schema.read_text()
    assert '/capnp/c++.capnp' in content, "Expected absolute import not found"
    
    # Try to load with SchemaParser and import path
    parser = capnp.SchemaParser()
    
    try:
        # Load with import path - absolute imports like /capnp/c++.capnp 
        # will be resolved relative to the import path
        module = parser.load(str(common_schema), imports=[str(ZALFMAS_DIR)])
        print(f"\n✓ Successfully loaded {common_schema.name}")
        print(f"  Display name: {module.schema.node.displayName}")
        print(f"  Nested nodes: {len(module.schema.node.nestedNodes)}")
        for node in module.schema.node.nestedNodes:
            print(f"    - {node.name}")
    except Exception as e:
        print(f"\n✗ Failed to load {common_schema.name}: {e}")
        pytest.fail(f"Failed to load schema with absolute imports: {e}")


def test_generate_simple_zalfmas_stub(generated_zalfmas_dir):
    """Test generating a stub for a simple zalfmas schema with absolute imports.
    
    This test uses the -I flag to specify import paths for resolving absolute imports.
    """
    # Look for schemas with minimal dependencies
    date_schema = ZALFMAS_DIR / "date.capnp"
    
    if not date_schema.exists():
        pytest.skip("date.capnp not found")
    
    # Check what imports it has
    content = date_schema.read_text()
    print(f"\ndate.capnp content (first 500 chars):\n{content[:500]}")
    
    # Try to generate stubs with import path
    try:
        # Add the zalfmas directory as an import path so /capnp/c++.capnp can be found
        args = ["-p", str(date_schema), "-o", str(generated_zalfmas_dir), "-I", str(ZALFMAS_DIR)]
        main(args)
        
        # Check if stub was generated
        stub_file = generated_zalfmas_dir / "date_capnp.pyi"
        assert stub_file.exists(), f"Stub file {stub_file} was not generated"
        assert stub_file.stat().st_size > 0, f"Stub file {stub_file} is empty"
        
        print(f"\n✓ Successfully generated stub for date.capnp")
        print(f"  Stub file: {stub_file}")
        print(f"  Size: {stub_file.stat().st_size} bytes")
        
    except Exception as e:
        print(f"\n✗ Failed to generate stub: {e}")
        pytest.fail(f"Stub generation failed: {e}")


def test_list_zalfmas_schemas_by_imports():
    """List all zalfmas schemas organized by their import types.
    
    This helps us understand which schemas can be tested first.
    """
    schemas_by_type = {
        "absolute_only": [],
        "relative_only": [],
        "both": [],
        "none": []
    }
    
    for schema_file in sorted(ZALFMAS_DIR.glob("*.capnp")):
        if schema_file.is_file():
            content = schema_file.read_text()
            
            has_absolute = 'import "/' in content
            has_relative = 'import "' in content and 'import "./' not in content and 'import "/' not in content or 'import "./' in content
            
            # More precise check for relative imports
            has_relative = False
            for line in content.split('\n'):
                if 'import "' in line and 'import "/' not in line and '.capnp"' in line:
                    has_relative = True
                    break
            
            if has_absolute and has_relative:
                schemas_by_type["both"].append(schema_file.name)
            elif has_absolute:
                schemas_by_type["absolute_only"].append(schema_file.name)
            elif has_relative:
                schemas_by_type["relative_only"].append(schema_file.name)
            else:
                schemas_by_type["none"].append(schema_file.name)
    
    print("\n" + "=" * 70)
    print("ZALFMAS SCHEMAS BY IMPORT TYPE")
    print("=" * 70)
    
    for import_type, schemas in schemas_by_type.items():
        print(f"\n{import_type.upper()} ({len(schemas)} schemas):")
        for schema in schemas:
            print(f"  - {schema}")
    
    print("=" * 70)


def test_generate_all_zalfmas_stubs(generated_zalfmas_dir):
    """Test generating stubs for all zalfmas schemas at once.
    
    This tests that all schemas can be processed together with proper import resolution.
    Note: Excludes schemas with known errors in the schema files themselves.
    """
    # Get all capnp files in the zalfmas directory (not in subdirectories)
    all_schema_files = list(ZALFMAS_DIR.glob("*.capnp"))
    
    # Skip known problematic schemas that have errors in the schema files themselves
    skip_schemas = {
        "climate_data_old.capnp",  # Has invalid import
        "vr.capnp",  # Missing import: functions.capnp
        "x.capnp",  # Likely also has missing imports: 'import "common.capnp"' has no member named 'Common'
    }
    
    schema_files = [f for f in all_schema_files if f.name not in skip_schemas]
    
    if not schema_files:
        pytest.skip("No schema files found")
    
    print(f"\nGenerating stubs for {len(schema_files)} zalfmas schemas (excluding {len(skip_schemas)} problematic schemas)...")
    
    # Generate stubs for all schemas at once with import path
    try:
        schema_paths = [str(f) for f in schema_files]
        args = ["-p"] + schema_paths + ["-o", str(generated_zalfmas_dir), "-I", str(ZALFMAS_DIR)]
        main(args)
        
        # Check that stubs were generated
        generated_stubs = list(generated_zalfmas_dir.glob("*_capnp.pyi"))
        
        print(f"\n✓ Successfully generated {len(generated_stubs)} stub files:")
        for stub in sorted(generated_stubs):
            print(f"  - {stub.name} ({stub.stat().st_size} bytes)")
        
        assert len(generated_stubs) > 0, "No stub files were generated"
        assert len(generated_stubs) == len(schema_files), \
            f"Expected {len(schema_files)} stubs, but got {len(generated_stubs)}"
        
    except Exception as e:
        print(f"\n✗ Failed to generate stubs: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"Stub generation failed: {e}")


def test_generate_zalfmas_stubs_individually(generated_zalfmas_dir):
    """Test generating stubs for zalfmas schemas one by one.
    
    This helps identify which specific schemas might have issues.
    Note: Some schemas may have errors due to incorrect imports in the schema files themselves.
    """
    schema_files = list(ZALFMAS_DIR.glob("*.capnp"))
    
    if not schema_files:
        pytest.skip("No schema files found")
    
    print(f"\nTesting individual stub generation for {len(schema_files)} schemas...")
    
    success_count = 0
    failed_schemas = []
    
    # Skip known problematic schemas that have errors in the schema files themselves
    skip_schemas = {
        "climate_data_old.capnp",  # Has invalid import
        "vr.capnp",  # Missing import: functions.capnp
        "x.capnp",  # Likely also has missing imports: 'import "common.capnp"' has no member named 'Common'
    }
    
    for schema_file in sorted(schema_files):
        if schema_file.name in skip_schemas:
            print(f"  ⊘ {schema_file.name} (skipped - known schema error)")
            continue
            
        try:
            # Use a separate subdirectory for each schema to avoid conflicts
            schema_output_dir = generated_zalfmas_dir / "individual" / schema_file.stem
            schema_output_dir.mkdir(parents=True, exist_ok=True)
            
            args = ["-p", str(schema_file), "-o", str(schema_output_dir), "-I", str(ZALFMAS_DIR)]
            main(args)
            
            stub_file = schema_output_dir / f"{schema_file.stem}_capnp.pyi"
            if stub_file.exists() and stub_file.stat().st_size > 0:
                print(f"  ✓ {schema_file.name}")
                success_count += 1
            else:
                print(f"  ✗ {schema_file.name} (stub not created or empty)")
                failed_schemas.append(schema_file.name)
                
        except Exception as e:
            print(f"  ✗ {schema_file.name}: {str(e)[:100]}")
            failed_schemas.append(schema_file.name)
    
    print(f"\nResults: {success_count}/{len(schema_files) - len(skip_schemas)} successful (excluding skipped schemas)")
    if failed_schemas:
        print(f"Failed schemas: {', '.join(failed_schemas)}")
    
    assert success_count > 0, "No schemas were successfully processed"
