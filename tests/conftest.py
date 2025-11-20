"""Pytest configuration and fixtures for capnp stub generator tests."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

import pytest

# Test directory structure
TESTS_DIR = Path(__file__).parent
SCHEMAS_DIR = TESTS_DIR / "schemas"
GENERATED_DIR = TESTS_DIR / "_generated"

# Schema subdirectories
BASIC_SCHEMAS_DIR = SCHEMAS_DIR / "basic"
EXAMPLES_SCHEMAS_DIR = SCHEMAS_DIR / "examples"
ZALFMAS_SCHEMAS_DIR = SCHEMAS_DIR / "zalfmas"

# Generated output subdirectories
BASIC_GENERATED_DIR = GENERATED_DIR / "basic"
EXAMPLES_GENERATED_DIR = GENERATED_DIR / "examples"
ZALFMAS_GENERATED_DIR = GENERATED_DIR / "zalfmas"


@pytest.fixture(scope="session", autouse=True)
def generate_all_stubs():
    """Generate all test stubs once at the beginning of the test session.

    This fixture runs automatically before any tests and generates stubs for:
    - Basic test schemas
    - Example schemas (calculator, addressbook, etc.)
    - Zalfmas schemas

    All other tests should use the generated stubs from this fixture.
    """
    logger = logging.getLogger(__name__)
    logger.info("Generating all test stubs...")

    # Clean generated directory
    if GENERATED_DIR.exists():
        import shutil

        shutil.rmtree(GENERATED_DIR)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    # Generate basic schemas
    logger.info(f"Generating basic schemas from {BASIC_SCHEMAS_DIR}")
    result = subprocess.run(
        [
            "capnp-stub-generator",
            "-p",
            str(BASIC_SCHEMAS_DIR),
            "-o",
            str(BASIC_GENERATED_DIR),
            "-r",  # Recursive to find all schemas
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error(f"Failed to generate basic schemas:\n{result.stderr}")
        pytest.fail(f"Basic schema generation failed: {result.stderr}")

    # Generate example schemas (recursive to get subdirectories)
    logger.info(f"Generating example schemas from {EXAMPLES_SCHEMAS_DIR}")
    result = subprocess.run(
        [
            "capnp-stub-generator",
            "-p",
            str(EXAMPLES_SCHEMAS_DIR),
            "-o",
            str(EXAMPLES_GENERATED_DIR),
            "-r",  # Recursive
            "--augment-capnp-stubs",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error(f"Failed to generate example schemas:\n{result.stderr}")
        pytest.fail(f"Example schema generation failed: {result.stderr}")

    # Generate zalfmas schemas (recursive, with exclusions)
    logger.info(f"Generating zalfmas schemas from {ZALFMAS_SCHEMAS_DIR}")
    result = subprocess.run(
        [
            "capnp-stub-generator",
            "-p",
            str(ZALFMAS_SCHEMAS_DIR),
            "-o",
            str(ZALFMAS_GENERATED_DIR),
            "-r",
            "-e",
            str(ZALFMAS_SCHEMAS_DIR / "a.capnp"),  # Exclude problematic file
            "-I",
            str(ZALFMAS_SCHEMAS_DIR),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error(f"Failed to generate zalfmas schemas:\n{result.stderr}")
        pytest.fail(f"Zalfmas schema generation failed: {result.stderr}")

    logger.info("✓ All test stubs generated successfully")

    # Return paths for tests to use
    return {
        "basic": BASIC_GENERATED_DIR,
        "examples": EXAMPLES_GENERATED_DIR,
        "zalfmas": ZALFMAS_GENERATED_DIR,
    }


@pytest.fixture(scope="session")
def generated_stubs(generate_all_stubs):
    """Provide access to generated stub directories.

    Returns:
        dict: Dictionary with keys "basic", "examples", "zalfmas"
              pointing to generated stub directories.
    """
    return generate_all_stubs


@pytest.fixture(scope="session")
def calculator_stubs(generated_stubs):
    """Provide path to generated calculator stubs."""
    return generated_stubs["examples"] / "calculator"


@pytest.fixture(scope="session")
def addressbook_stubs(generated_stubs):
    """Provide path to generated addressbook stubs."""
    return generated_stubs["examples"] / "addressbook"


@pytest.fixture(scope="session")
def basic_stubs(generated_stubs):
    """Provide path to generated basic test stubs."""
    return generated_stubs["basic"]


@pytest.fixture(scope="session")
def zalfmas_stubs(generated_stubs):
    """Provide path to generated zalfmas stubs."""
    return generated_stubs["zalfmas"]


# Legacy fixtures for backward compatibility (deprecated)
@pytest.fixture
def generate_calculator_stubs(calculator_stubs):
    """Deprecated: Use calculator_stubs fixture instead."""
    return calculator_stubs


@pytest.fixture
def calculator_stub_lines(calculator_stubs):
    """Read calculator stub file lines."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    with open(stub_file) as f:
        return f.readlines()


# Constants for backward compatibility
SCHEMAS_DIR_OLD = BASIC_SCHEMAS_DIR  # For tests that reference SCHEMAS_DIR


# Helper functions for tests
def read_stub_file(stub_path: Path) -> list[str]:
    """Read a stub file and return its lines.

    Args:
        stub_path: Path to the .pyi stub file

    Returns:
        List of lines from the stub file
    """
    with open(stub_path) as f:
        return f.readlines()


def generate_stub_from_schema(schema_name: str, output_dir: Path) -> Path:
    """Generate a stub from a schema file (for temporary test generation).

    This should only be used for CLI tests or temporary validation.
    Most tests should use the pre-generated stubs from generate_all_stubs fixture.

    Args:
        schema_name: Name of the schema file (e.g., "calculator.capnp")
        output_dir: Directory to write the generated stub

    Returns:
        Path to the generated .pyi file
    """
    # Find the schema file in any of the schema directories
    schema_path = None
    for schema_dir in [BASIC_SCHEMAS_DIR, EXAMPLES_SCHEMAS_DIR, ZALFMAS_SCHEMAS_DIR]:
        candidate = schema_dir / schema_name
        if candidate.exists():
            schema_path = candidate
            break
        # Also check subdirectories
        for subdir in schema_dir.rglob("*"):
            if subdir.is_dir():
                candidate = subdir / schema_name
                if candidate.exists():
                    schema_path = candidate
                    break
        if schema_path:
            break

    if not schema_path:
        pytest.fail(f"Schema {schema_name} not found in schema directories")

    # Generate the stub
    result = subprocess.run(
        [
            "capnp-stub-generator",
            "-p",
            str(schema_path),
            "-o",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        pytest.fail(f"Failed to generate stub: {result.stderr}")

    # Return path to generated .pyi file
    stub_name = schema_path.stem + "_capnp.pyi"
    return output_dir / stub_name


# Specific stub fixtures for individual files
@pytest.fixture(scope="session")
def dummy_stub_file(basic_stubs):
    """Provide path to dummy_capnp.pyi."""
    return basic_stubs / "dummy_capnp.pyi"


@pytest.fixture(scope="session")
def dummy_stub_lines(dummy_stub_file):
    """Read dummy stub file lines."""
    return read_stub_file(dummy_stub_file)
