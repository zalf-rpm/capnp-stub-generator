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

    # Known issues: Method overload ordering in some edge cases
    # Most variance issues fixed by using @property with setters
    # These are reportIncompatibleMethodOverride errors.
    EXPECTED_ERROR_COUNT = 3  # Method overload ordering issues

    if errors > EXPECTED_ERROR_COUNT:
        pytest.fail(
            f"Generated stubs have {errors} type errors (expected max {EXPECTED_ERROR_COUNT}).\n"
            f"ERROR: Type errors increased! This is a regression.\n"
            f"Pyright output:\n{result.stdout}"
        )
    elif errors < EXPECTED_ERROR_COUNT:
        print(f"\n✓ Type errors reduced from {EXPECTED_ERROR_COUNT} to {errors}!")
        print("  Please update EXPECTED_ERROR_COUNT in this test.")

    if errors == EXPECTED_ERROR_COUNT:
        print(f"\n✓ Generated stubs have {errors} known variance-related errors (acceptable).")
