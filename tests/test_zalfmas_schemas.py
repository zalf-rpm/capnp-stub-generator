"""Test zalfmas capnp schemas with stub generation.

This module tests the generation of stubs for the zalfmas schemas,
which include:
- Absolute imports (e.g., /capnp/c++.capnp)
- Relative imports (e.g., import "common.capnp")
- Complex nested schema structures
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from test_helpers import run_generator

# Test directories
TESTS_DIR = Path(__file__).parent
ZALFMAS_DIR = TESTS_DIR / "schemas" / "zalfmas"
GENERATED_ZALFMAS_DIR = TESTS_DIR / "_generated" / "zalfmas"


@pytest.fixture(scope="module")
def generated_zalfmas_dir():
    """Ensure the generated zalfmas directory exists and is clean."""
    if GENERATED_ZALFMAS_DIR.exists():
        shutil.rmtree(GENERATED_ZALFMAS_DIR)

    GENERATED_ZALFMAS_DIR.mkdir(parents=True, exist_ok=True)

    return GENERATED_ZALFMAS_DIR

    # Keep generated files for inspection
    # shutil.rmtree(GENERATED_ZALFMAS_DIR)


def test_generate_zalfmas_stubs(generated_zalfmas_dir):
    """Test generating stubs for zalfmas schemas using recursive discovery.

    This test uses recursive search and excludes to generate stubs
    for all valid zalfmas schemas, excluding known problematic files.
    """
    # Define files to exclude (problematic schemas that exist)
    # Note: Only a.capnp exists; the others are mentioned for documentation
    excludes = [str(ZALFMAS_DIR / "a.capnp")]

    # Build arguments for the CLI
    args = ["-p", str(ZALFMAS_DIR), "-o", str(generated_zalfmas_dir), "-I", str(ZALFMAS_DIR), "-r", "-e"] + excludes

    print(f"\nGenerating stubs with args: {' '.join(args)}")

    # Call the CLI main function directly
    try:
        run_generator(args)
    except Exception as e:
        pytest.fail(f"Stub generation failed: {e}")

    # Verify stubs were generated
    generated_stubs = list(generated_zalfmas_dir.glob("**/*_capnp.pyi"))

    print(f"\n✓ Successfully generated {len(generated_stubs)} stub files")

    # Show generated files organized by directory
    root_stubs = [s for s in generated_stubs if s.parent == generated_zalfmas_dir]
    subdir_stubs = [s for s in generated_stubs if s.parent != generated_zalfmas_dir]

    print(f"  - {len(root_stubs)} in root directory")
    if subdir_stubs:
        subdirs = set(s.relative_to(generated_zalfmas_dir).parent for s in subdir_stubs)
        for subdir in sorted(subdirs):
            count = len([s for s in subdir_stubs if s.relative_to(generated_zalfmas_dir).parent == subdir])
            print(f"  - {count} in {subdir}/")

    assert len(generated_stubs) > 0, "No stub files were generated"
