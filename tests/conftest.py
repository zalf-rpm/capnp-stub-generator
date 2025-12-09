"""Pytest configuration and fixtures for capnp stub generator tests."""

from __future__ import annotations

import logging
import subprocess
import sys
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
CAPNP_SCHEMAS_DIR = SCHEMAS_DIR / "capnp"

# Generated output subdirectories
BASIC_GENERATED_DIR = GENERATED_DIR / "basic"
EXAMPLES_GENERATED_DIR = GENERATED_DIR / "examples"
ZALFMAS_GENERATED_DIR = GENERATED_DIR / "zalfmas"
CAPNP_GENERATED_DIR = GENERATED_DIR / "capnp"


@pytest.fixture(scope="session", autouse=True)
def generate_all_stubs():
    """Generate all test stubs once at the beginning of the test session.

    This fixture runs automatically before any tests and generates stubs for:
    - Basic test schemas
    - Example schemas (calculator, addressbook, etc.)
    - Zalfmas schemas

    Uses the capnp compile plugin approach to ensure all schemas including
    groups in unions are properly handled.

    All other tests should use the generated stubs from this fixture.
    """
    logger = logging.getLogger(__name__)
    logger.info("Generating all test stubs using capnp compile plugin...")

    # Clean generated directory
    if GENERATED_DIR.exists():
        import shutil

        shutil.rmtree(GENERATED_DIR)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    # Get the capnpc-python plugin path
    plugin_path = Path(__file__).parent.parent / "src" / "capnp_stub_generator" / "capnpc_plugin.py"
    if not plugin_path.exists():
        pytest.fail(f"Plugin not found at {plugin_path}")

    # Create a temporary wrapper script for the plugin
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix="_capnpc_python", delete=False) as wrapper:
        wrapper.write(f"""#!/usr/bin/env {sys.executable}
import sys
sys.path.insert(0, {str(Path(__file__).parent.parent / "src")!r})
from capnp_stub_generator.capnpc_plugin import main
main()
""")
        wrapper_path = wrapper.name

    # Make wrapper executable
    import os as os_module

    os_module.chmod(wrapper_path, 0o755)

    try:
        # Helper function to generate stubs using capnp compile
        def compile_schemas(schema_dir: Path, output_dir: Path, import_paths: list[str] = None):
            """Compile schemas using capnp compile with our plugin."""
            # Find all .capnp files recursively
            schema_files = list(schema_dir.rglob("*.capnp"))

            if not schema_files:
                logger.warning(f"No schema files found in {schema_dir}")
                return

            logger.info(f"Compiling {len(schema_files)} schemas from {schema_dir}")

            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)

            # Build compile command with --src-prefix to strip the schema_dir prefix
            cmd = ["capnp", "compile", f"--src-prefix={schema_dir}", f"-o{wrapper_path}:{output_dir}"]

            # Add import paths
            if import_paths:
                for import_path in import_paths:
                    cmd.extend(["-I", import_path])

            # Add all schema files
            cmd.extend([str(f) for f in schema_files])

            logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.error(f"Failed to compile schemas from {schema_dir}:\n{result.stderr}")
                logger.error(f"stdout: {result.stdout}")
                pytest.fail(f"Schema compilation failed: {result.stderr}")

            logger.info(f"✓ Generated stubs in {output_dir}")

        # Generate basic schemas
        compile_schemas(BASIC_SCHEMAS_DIR, BASIC_GENERATED_DIR)

        # Generate example schemas
        compile_schemas(EXAMPLES_SCHEMAS_DIR, EXAMPLES_GENERATED_DIR)

        # Generate zalfmas schemas (with import path, excluding problematic file)
        zalfmas_files = list(ZALFMAS_SCHEMAS_DIR.rglob("*.capnp"))
        # Exclude a.capnp which has duplicate ID
        zalfmas_files = [f for f in zalfmas_files if f.name != "a.capnp"]

        if zalfmas_files:
            logger.info(f"Compiling {len(zalfmas_files)} zalfmas schemas")
            ZALFMAS_GENERATED_DIR.mkdir(parents=True, exist_ok=True)

            cmd = [
                "capnp",
                "compile",
                f"--src-prefix={ZALFMAS_SCHEMAS_DIR}",
                f"-o{wrapper_path}:{ZALFMAS_GENERATED_DIR}",
                "-I",
                str(ZALFMAS_SCHEMAS_DIR),
            ]
            cmd.extend([str(f) for f in zalfmas_files])

            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to compile zalfmas schemas:\n{result.stderr}")
                pytest.fail(f"Zalfmas schema compilation failed: {result.stderr}")

            logger.info(f"✓ Generated zalfmas stubs in {ZALFMAS_GENERATED_DIR}")

        # Generate capnp schemas
        compile_schemas(CAPNP_SCHEMAS_DIR, CAPNP_GENERATED_DIR)

        logger.info("✓ All test stubs generated successfully using capnp compile")

        # Run pyright validation on generated stubs (excluding zalfmas which has complex cross-schema imports)
        logger.info("Running pyright validation on generated stubs...")
        pyright_result = subprocess.run(
            ["pyright", str(BASIC_GENERATED_DIR), str(EXAMPLES_GENERATED_DIR), str(CAPNP_GENERATED_DIR)],
            check=False,
            capture_output=True,
            text=True,
        )

        if pyright_result.returncode != 0:
            # Count actual errors (not warnings)
            error_lines = [line for line in pyright_result.stdout.split("\n") if " error:" in line]
            if error_lines:
                logger.error(f"Pyright validation failed:\n{pyright_result.stdout}")
                pytest.fail(f"Pyright validation failed with {len(error_lines)} error(s)")

        logger.info("✓ Pyright validation passed")

    finally:
        # Clean up wrapper script
        try:
            os_module.unlink(wrapper_path)
        except Exception:
            pass

    # Return paths for tests to use
    return {
        "basic": BASIC_GENERATED_DIR,
        "examples": EXAMPLES_GENERATED_DIR,
        "zalfmas": ZALFMAS_GENERATED_DIR,
    }

    logger.info("✓ All test stubs generated successfully using capnp compile")

    # Run pyright validation on the whole repository
    logger.info("Running pyright validation...")
    pyright_result = subprocess.run(
        ["pyright", "."],
        check=False,
        capture_output=True,
        text=True,
    )

    if pyright_result.returncode != 0:
        logger.error(f"Pyright validation failed:\n{pyright_result.stdout}")
        pytest.fail(f"Pyright validation failed:\n{pyright_result.stdout}")

    logger.info("✓ Pyright validation passed")

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
        check=False,
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
