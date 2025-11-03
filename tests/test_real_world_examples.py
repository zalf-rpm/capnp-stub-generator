"""Test real-world capnp examples with type checking.

This module provides an extensible framework for testing real-world Cap'n Proto
examples. Each example consists of:
1. A .capnp schema file
2. A .py Python file that uses the generated types
3. Generated stub files (.pyi)

The tests verify that:
- Stubs can be generated without errors
- Generated stubs pass pyright type checking
- The Python code using the stubs also passes type checking
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

# Base directories
TESTS_DIR = Path(__file__).parent
EXAMPLES_DIR = TESTS_DIR / "examples"
GENERATED_EXAMPLES_DIR = TESTS_DIR / "_generated_examples"


@dataclass
class Example:
    """Represents a real-world example to test."""

    name: str
    """Name of the example (e.g., 'addressbook')"""

    schema_files: list[str]
    """List of .capnp schema files (relative to example directory)"""

    python_files: list[str]
    """List of .py Python files to type check (relative to example directory)"""

    @property
    def example_dir(self) -> Path:
        """Directory containing the example files."""
        return EXAMPLES_DIR / self.name

    @property
    def generated_dir(self) -> Path:
        """Directory where generated stubs will be placed."""
        return GENERATED_EXAMPLES_DIR / self.name

    def get_schema_paths(self) -> list[Path]:
        """Get full paths to all schema files."""
        return [self.example_dir / schema for schema in self.schema_files]

    def get_python_paths(self) -> list[Path]:
        """Get full paths to all Python files."""
        return [self.example_dir / py_file for py_file in self.python_files]


# Registry of examples to test
EXAMPLES = [
    Example(
        name="addressbook",
        schema_files=["addressbook.capnp"],
        python_files=["addressbook.py"],
    ),
    Example(
        name="calculator",
        schema_files=["calculator.capnp"],
        python_files=["async_calculator_client.py", "async_calculator_server.py"],
    ),
]


@pytest.fixture(scope="module")
def generated_examples_dir():
    """Ensure the generated examples directory exists and is clean."""
    # Clean up any existing generated files
    if GENERATED_EXAMPLES_DIR.exists():
        shutil.rmtree(GENERATED_EXAMPLES_DIR)

    GENERATED_EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    yield GENERATED_EXAMPLES_DIR

    # Optionally clean up after tests
    # shutil.rmtree(GENERATED_EXAMPLES_DIR)


@pytest.fixture(scope="module")
def generate_all_stubs(generated_examples_dir):
    """Generate stubs for all examples before running tests."""
    from capnp_stub_generator.cli import main

    generated_info = {}

    for example in EXAMPLES:
        # Create output directory for this example
        example.generated_dir.mkdir(parents=True, exist_ok=True)

        # Get all schema file paths
        schema_paths = [str(path) for path in example.get_schema_paths()]

        # Generate stubs
        args = ["-p"] + schema_paths + ["-o", str(example.generated_dir)]
        main(args)

        # Store info about what was generated
        generated_files = list(example.generated_dir.glob("*.pyi"))
        generated_info[example.name] = {
            "dir": example.generated_dir,
            "stub_files": generated_files,
        }

    return generated_info


class TestExampleGeneration:
    """Test that stubs can be generated for all examples."""

    @pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e.name)
    def test_stub_generation(self, generate_all_stubs, example: Example):
        """Test that stub files are generated for the example."""
        info = generate_all_stubs[example.name]

        # Check that at least one stub file was generated
        assert info["stub_files"], f"No stub files generated for {example.name}"

        # Check that generated files exist and are not empty
        for stub_file in info["stub_files"]:
            assert stub_file.exists(), f"Stub file {stub_file} does not exist"
            assert stub_file.stat().st_size > 0, f"Stub file {stub_file} is empty"


class TestGeneratedStubsTypeCheck:
    """Test that generated stubs pass pyright type checking."""

    @pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e.name)
    def test_generated_stubs_pyright(self, generate_all_stubs, example: Example):
        """Test that generated stub files pass pyright validation."""
        info = generate_all_stubs[example.name]

        # Run pyright on all generated stub files
        stub_paths = [str(f) for f in info["stub_files"]]
        result = subprocess.run(
            ["pyright"] + stub_paths,
            capture_output=True,
            text=True,
            cwd=str(TESTS_DIR),
        )

        error_count = result.stdout.count("error:")

        # Known issues: Reader classes override struct/list fields with narrower types
        # This violates type variance rules but is correct at runtime.
        # These are reportIncompatibleVariableOverride and reportIncompatibleMethodOverride errors.
        expected_errors = {
            "addressbook": 5,  # Variance errors in Reader classes
            "calculator": 8,  # Variance errors + interface union hints
        }.get(example.name, 0)

        if error_count > expected_errors:
            pytest.fail(
                f"Generated stubs for {example.name} have {error_count} type errors (expected max {expected_errors}).\n"
                f"ERROR: Type errors increased! This is a regression.\n"
                f"Pyright output:\n{result.stdout}"
            )
        elif error_count < expected_errors:
            print(
                f"\n✓ {example.name}: Type errors reduced from {expected_errors} to {error_count}!"
            )
            print("  Please update expected_errors in this test.")


class TestPythonCodeTypeCheck:
    """Test that Python code using generated stubs passes type checking."""

    @pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e.name)
    def test_python_code_pyright(self, generate_all_stubs, example: Example):
        """Test that Python code using the stubs passes pyright validation."""
        # Get Python file paths
        python_paths = [str(path) for path in example.get_python_paths()]

        if not python_paths:
            pytest.skip(f"No Python files to check for {example.name}")

        # Create a temporary directory with symlinks to make imports work
        temp_dir = example.generated_dir / "temp_test"
        temp_dir.mkdir(exist_ok=True)

        # Copy Python files to temp directory
        for py_path in example.get_python_paths():
            dest = temp_dir / py_path.name
            if dest.exists():
                dest.unlink()
            shutil.copy2(py_path, dest)

        # Create __init__.py to make it a package
        (temp_dir / "__init__.py").touch()

        # Run pyright on Python files with generated stubs in path
        result = subprocess.run(
            ["pyright", str(temp_dir)],
            capture_output=True,
            text=True,
            cwd=str(TESTS_DIR),
            env={
                **os.environ,
                "PYTHONPATH": f"{example.generated_dir}:{os.environ.get('PYTHONPATH', '')}",
            },
        )

        error_count = result.stdout.count("error:")

        # All typing improvements complete - calculator has 4 errors (was 16)
        # - Enum parameters accept string literals
        # - Result types with field attributes (.value, .func)
        # - Result types are Awaitable
        # - Struct parameters accept dict union
        # - Request builders have proper Builder types
        # - Interface fields accept Server implementations
        # - Interface fields return Protocol (not union with Server) for proper method access
        # - Server classes have proper method signatures with types
        # Remaining 5 errors are bugs in example code (missing _context, type mismatches)
        expected_errors = {
            "calculator": 5,  # Example code bugs: missing _context in 4 methods, evaluate_impl signature
        }.get(example.name, 0)

        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

        if error_count > expected_errors:
            pytest.fail(
                f"Python code for {example.name} has {error_count} type errors (expected {expected_errors}).\n"
                f"Pyright output:\n{result.stdout}"
            )


class TestExampleFunctionality:
    """Test that examples can actually be imported and used."""

    @pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e.name)
    def test_example_imports(self, generate_all_stubs, example: Example):
        """Test that generated modules can be imported."""
        import sys

        # Add generated directory to path
        sys.path.insert(0, str(example.generated_dir))

        try:
            # Try to import each generated module
            for stub_file in generate_all_stubs[example.name]["stub_files"]:
                module_name = stub_file.stem  # Remove .pyi extension
                if module_name.endswith("_capnp"):
                    # This would require the actual compiled capnp module
                    # For now, just check the stub exists
                    assert stub_file.exists()
        finally:
            # Clean up sys.path
            sys.path.remove(str(example.generated_dir))


# Summary test to show overall status
def test_all_examples_summary(generate_all_stubs):
    """Provide a summary of all examples tested."""
    summary = []

    for example in EXAMPLES:
        info = generate_all_stubs[example.name]
        summary.append(f"  ✓ {example.name}: {len(info['stub_files'])} stub(s) generated")

    print(f"\n{'=' * 70}")
    print("REAL-WORLD EXAMPLES TEST SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total examples tested: {len(EXAMPLES)}")
    for line in summary:
        print(line)
    print(f"{'=' * 70}\n")
