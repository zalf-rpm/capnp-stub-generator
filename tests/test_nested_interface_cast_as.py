"""Test cast_as with nested interfaces like Channel.Reader."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_nested_interface_cast_as(tmp_path: Path):
    """
    Test the user's exact pattern with Channel.Reader.

    This reproduces:
        first_reader = await self.con_man.try_connect(
            first_reader_sr, cast_as=fbp_capnp.Channel.Reader
        )

    Where Pylance complains:
        Argument missing for parameter "self"
        (variable) first_reader: type[Reader]
    """
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("channel.capnp", tmp_path)
    stub_dir = stub_path.parent

    test_file = tmp_path / "test_user_issue.py"
    test_file.write_text(
        f"""
from __future__ import annotations

import sys
sys.path.insert(0, '{stub_dir}')

import channel_capnp
from typing import TypeVar

T = TypeVar('T')

class ConnectionManager:
    async def try_connect(
        self,
        sturdy_ref: str | None,
        cast_as: type[T] | None = None,
    ) -> T | None:
        '''Connect and cast to specified type.'''
        # In real pycapnp, this would return an instance of type T
        return None

async def main():
    con_man = ConnectionManager()
    
    # This is the user's exact pattern
    first_reader = await con_man.try_connect(
        "capnp://example.com:5000/token",
        cast_as=channel_capnp.Channel.Reader  # Nested interface
    )
    
    # first_reader should be Channel.Reader (instance), not type[Channel.Reader]
    # We should be able to call methods without "missing self" error
    if first_reader:
        # This should work fine - calling methods on the instance
        # Don't actually await since our mock returns None
        result_promise = first_reader.read()
        print(f"Got promise: {{result_promise}}")
        
        # Method calls should work
        close_promise = first_reader.close()
        print(f"Got close promise: {{close_promise}}")

import asyncio
asyncio.run(main())
"""
    )

    # Run pyright to check for the specific error
    from tests.conftest import run_pyright

    returncode, output = run_pyright(test_file, cwd=tmp_path)

    # Check for the user's specific error
    if "Argument missing for parameter" in output and '"self"' in output:
        pytest.fail(
            f"❌ REPRODUCED USER'S ISSUE!\n"
            f"Pylance thinks first_reader is type[Reader], not Reader instance.\n\n"
            f"Pyright output:\n{output}"
        )

    # Check for the type annotation issue
    if "type[Reader]" in output:
        print("⚠️  Type checker sees type[Reader] instead of Reader")
        print(output)
        pytest.fail(f"Type is incorrect:\n{output}")

    error_count = output.count("error:")
    if error_count > 0:
        print(f"Type checking produced errors:\n{output}")
        pytest.fail(f"Found {error_count} error(s):\n{output}")

    print("✅ Test passed! Nested interface cast_as works correctly.")


def test_check_if_protocol_is_the_issue(tmp_path: Path):
    """Check if Protocol types work with generic type parameters."""
    test_file = tmp_path / "test_protocol_generic.py"
    test_file.write_text(
        """
from __future__ import annotations

from typing import TypeVar, Protocol

class MyInterface(Protocol):
    def do_something(self) -> str: ...

T = TypeVar('T')

def cast_to(target_type: type[T]) -> T:
    '''Takes a type, returns an instance.'''
    return None  # type: ignore

# Test: pass Protocol type, get instance
result = cast_to(MyInterface)

# Should be able to call methods on the result
output = result.do_something()
print(output)
"""
    )

    from tests.conftest import run_pyright

    returncode, output = run_pyright(test_file, cwd=tmp_path)

    print(f"Simple Protocol test:\n{output}")

    if "error:" in output:
        print("❌ Basic Protocol with generics doesn't work")
    else:
        print("✅ Basic Protocol with generics works")
