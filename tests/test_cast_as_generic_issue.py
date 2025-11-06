"""Test the specific cast_as generic issue reported by the user."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_cast_as_generic_returns_instance(tmp_path: Path):
    """
    Test that when using a generic function with cast_as pattern,
    the return type is an instance, not type[T].

    This reproduces the user's issue where:
        first_reader = await con_man.try_connect(sr, cast_as=fbp_capnp.Channel.Reader)
    Results in first_reader having type `type[Reader]` instead of `Reader`.
    """
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("interfaces.capnp", tmp_path)
    stub_dir = stub_path.parent

    test_file = tmp_path / "test_cast_as_generic.py"
    test_file.write_text(
        f"""
from __future__ import annotations

import sys
sys.path.insert(0, '{stub_dir}')

import interfaces_capnp
from typing import TypeVar

T = TypeVar('T')

class ConnectionManager:
    async def try_connect(
        self,
        sturdy_ref: str | None,
        cast_as: type[T] | None = None,
    ) -> T | None:
        '''
        Connect and cast to the specified type.
        
        Args:
            sturdy_ref: Connection string
            cast_as: Type to cast the result to (e.g., MyInterface)
            
        Returns:
            An instance of type T, or None
        '''
        # In real code, this would connect and cast
        # For testing, we return None
        return None

async def main():
    con_man = ConnectionManager()
    
    # User's pattern: pass the interface type, get an instance
    first_reader = await con_man.try_connect(
        "capnp://example.com:5000/token",
        cast_as=interfaces_capnp.Greeter  # Pass the type
    )
    
    # first_reader should be of type Greeter (instance), not type[Greeter] (class)
    # This means we should be able to call methods directly
    if first_reader:
        # This should work - calling a method on the instance
        # Should NOT complain about "Argument missing for parameter 'self'"
        result = first_reader.greet("Alice")

import asyncio
asyncio.run(main())
"""
    )

    # Run pyright to check for type errors
    from tests.conftest import run_pyright

    returncode, output = run_pyright(test_file, cwd=tmp_path)

    # The specific error the user is getting
    if "Argument missing for parameter" in output and '"self"' in output:
        pytest.fail(
            f"Type checker thinks first_reader is type[Greeter] instead of Greeter!\n"
            f"This is the user's exact issue.\n\n"
            f"Pyright output:\n{output}"
        )

    # Check for any other errors
    error_count = output.count("error:")
    if error_count > 0:
        # Print but don't fail - we want to see what errors exist
        print(f"Found {error_count} type error(s):")
        print(output)

        # Fail only if it's the specific "self" error
        if "Argument missing" in output:
            pytest.fail(f"Type errors found:\n{output}")


def test_protocol_as_type_parameter(tmp_path: Path):
    """Test if Protocol types can be used as type parameters."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("interfaces.capnp", tmp_path)
    stub_dir = stub_path.parent

    test_file = tmp_path / "test_protocol_type_param.py"
    test_file.write_text(
        f"""
from __future__ import annotations

import sys
sys.path.insert(0, '{stub_dir}')

import interfaces_capnp
from typing import TypeVar, Protocol

# Test 1: Can we use Greeter as a type parameter?
P = TypeVar('P', bound=interfaces_capnp.Greeter)

def accept_interface_type(iface_type: type[P]) -> P:
    '''Accept an interface type, return an instance.'''
    # Mock implementation
    return None  # type: ignore

# Test 2: Can we pass the interface?
result = accept_interface_type(interfaces_capnp.Greeter)

# Test 3: Can we call methods on the result?
if result:
    result.greet("test")
"""
    )

    from tests.conftest import run_pyright

    returncode, output = run_pyright(test_file, cwd=tmp_path)

    print(f"Pyright output:\n{output}")

    # Check what errors we get
    if "is not a concrete class" in output:
        print("\n⚠️  Interface Protocol cannot be used with type[Protocol]")
        print("This is the root cause of the user's issue!")

    error_count = output.count("error:")
    print(f"\nTotal errors: {error_count}")
