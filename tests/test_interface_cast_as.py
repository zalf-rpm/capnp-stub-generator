"""Test that interfaces work correctly with cast_as pattern."""

from __future__ import annotations

from pathlib import Path


def test_interface_cast_as_returns_instance_not_type(tmp_path: Path):
    """Test that using an interface with cast_as returns an instance, not a type."""
    from tests.conftest import generate_stub_from_schema

    stub_dir = generate_stub_from_schema("interfaces.capnp", tmp_path)

    # Create a test file that mimics the user's ConnectionManager pattern
    test_file = tmp_path / "test_cast_as.py"
    test_file.write_text(
        f"""
from __future__ import annotations

import sys
sys.path.insert(0, '{stub_dir.parent}')

import interfaces_capnp
from typing import TypeVar

T = TypeVar('T')

class ConnectionManager:
    async def try_connect(
        self,
        sturdy_ref: str | None,
        cast_as: type[T] | None = None,
    ) -> T | None:
        '''Simulates casting to an interface type.'''
        # In real code, this would return an instance of type T
        # For testing, we just return None
        return None

async def main():
    con_man = ConnectionManager()
    
    # This should work: cast_as receives a type, returns an instance
    first_reader = await con_man.try_connect(
        "capnp://example.com:5000/token",
        cast_as=interfaces_capnp.Greeter  # Pass the interface type
    )
    
    # first_reader should be an instance of Greeter, not type[Greeter]
    # This means we can call methods on it
    if first_reader:
        # This should be valid - calling a method on the instance
        result = first_reader.greet("Alice")

import asyncio
asyncio.run(main())
"""
    )

    # Run pyright on the test file to check for type errors
    from tests.conftest import run_pyright

    returncode, output = run_pyright(test_file, cwd=tmp_path)

    # Check that there are no errors about "Argument missing for parameter 'self'"
    if "Argument missing for parameter" in output:
        import pytest

        pytest.fail(f"Type checker thinks first_reader is a type, not an instance!\nPyright output:\n{output}")

    # Check that pyright doesn't complain about calling methods
    error_count = output.count("error:")
    if error_count > 0:
        import pytest

        pytest.fail(f"Unexpected type errors:\n{output}")


def test_interface_reader_alias_not_needed(tmp_path: Path):
    """Test that InterfaceReader and InterfaceBuilder are not separate types."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("interfaces.capnp", tmp_path)

    # The stub_path is the .pyi file itself
    content = stub_path.read_text()

    # Should NOT have "class GreeterReader" or "class GreeterBuilder"
    assert "class GreeterReader" not in content, "Interfaces should not have Reader class"
    assert "class GreeterBuilder" not in content, "Interfaces should not have Builder class"

    # Should have "class Greeter(Protocol):"
    assert "class Greeter(Protocol):" in content
