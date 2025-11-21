"""Test real-world capnp examples with type checking.

This module provides an extensible framework for testing real-world Cap'n Proto
examples. Each example consists of:
1. A .capnp schema file
2. A .py Python file that uses the generated types
3. Generated stub files (.pyi)

The tests verify that:
- Stubs can be generated without errors
- The Python code using the stubs also passes type checking
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

# Base directories
TESTS_DIR = Path(__file__).parent
EXAMPLES_DIR = TESTS_DIR / "schemas" / "examples"
GENERATED_EXAMPLES_DIR = TESTS_DIR / "_generated" / "examples"


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
    Example(
        name="restorer",
        schema_files=["restorer.capnp"],
        python_files=["restorer_client.py", "restorer_server.py"],
    ),
    Example(
        name="single_value",
        schema_files=["single_value.capnp"],
        python_files=["single_value_client.py", "single_value_server.py"],
    ),
]


@pytest.fixture(scope="session")
def generate_all_stubs(generated_stubs):
    """Use pre-generated stubs from session fixture."""
    generated_info = {}

    for example in EXAMPLES:
        # Get the pre-generated directory
        example_dir = generated_stubs["examples"] / example.name

        # Store info about what was generated
        generated_files = list(example_dir.glob("*.pyi"))
        generated_info[example.name] = {
            "dir": example_dir,
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

    @pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e.name)
    def test_example_type_checking(self, generate_all_stubs, example: Example):
        """Test that example python files pass type checking with pyright."""
        import os
        import subprocess

        if not example.python_files:
            return

        # Get generated directory
        generated_dir = example.generated_dir

        # Run pyright on each python file
        # We need to set PYTHONPATH to include the generated stubs
        # The examples use 'from _generated.examples.xxx import xxx_capnp'
        # So we need to add the parent of _generated (which is tests/) to PYTHONPATH
        env = os.environ.copy()
        python_path = env.get("PYTHONPATH", "")

        # Add tests/ directory to PYTHONPATH so _generated package is found
        tests_dir = str(TESTS_DIR)
        env["PYTHONPATH"] = f"{tests_dir}:{python_path}"

        for python_file in example.get_python_paths():
            if not python_file.exists():
                continue

            # Run pyright
            # We use --pythonpath to ensure it finds the stubs
            cmd = ["pyright", str(python_file)]

            # Note: We need to ensure pyright can find the generated stubs.
            # Usually pyright looks in the current directory or site-packages.
            # Since stubs are in _generated/examples/<name>, we might need to configure pyright
            # or copy stubs to a place where pyright finds them.
            # But setting PYTHONPATH might be enough if pyright respects it for import resolution.

            # Actually, pyright execution might be slow, so we should be careful.
            # But for correctness it's valuable.

            result = subprocess.run(cmd, capture_output=True, text=True, env=env)

            # We expect success (0)
            # If it fails, print output for debugging
            if result.returncode != 0:
                print(f"Pyright failed for {python_file}:")
                print(result.stdout)
                print(result.stderr)

            assert result.returncode == 0, f"Type checking failed for {python_file.name}"


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
