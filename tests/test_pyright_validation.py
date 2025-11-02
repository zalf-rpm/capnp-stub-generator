"""Test that generated stub files pass pyright type checking."""

from __future__ import annotations

import os
import subprocess

import pytest

here = os.path.dirname(__file__)
_out_dir = os.path.join(here, "_generated")


@pytest.fixture(scope="module")
def generated_stubs():
    """Generate all stub files before running tests."""
    from capnp_stub_generator.cli import main

    os.makedirs(_out_dir, exist_ok=True)

    # Generate all the schema files
    schemas = [
        "basic_low.capnp",
        "dummy.capnp",
        "mid_features.capnp",
        "primitives.capnp",
        "nested.capnp",
        "unions.capnp",
        "interfaces.capnp",
        "import_base.capnp",
        "import_user.capnp",
        "advanced_features.capnp",
    ]

    schema_paths = [os.path.join(here, "schemas", s) for s in schemas]
    main(["-p"] + schema_paths + ["-o", _out_dir])

    return _out_dir


def test_generated_stubs_type_check(generated_stubs):
    """Run pyright on all generated stub files."""
    # Run pyright on the generated directory
    result = subprocess.run(
        ["pyright", f"{generated_stubs}/*.pyi"],
        capture_output=True,
        text=True,
        cwd=here,
    )

    # For now, we'll allow some errors but track them
    # This test documents the current state and prevents regressions
    errors = result.stdout.count("error:")

    # Almost all errors fixed! Remaining 0 are overload incompatibility
    # in classes with both union/group inits and list inits
    EXPECTED_ERROR_COUNT = 0

    if errors != EXPECTED_ERROR_COUNT:
        pytest.fail(
            f"Generated stubs have {errors} type errors (expected {EXPECTED_ERROR_COUNT}).\n"
            f"Pyright output:\n{result.stdout}"
        )

    print("\n✓ All generated stubs pass pyright validation with 0 errors!")
