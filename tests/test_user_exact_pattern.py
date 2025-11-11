"""Test the user's EXACT code pattern to reproduce their issue."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_issue_is_not_with_stubs(tmp_path: Path):
    """
    Test to confirm the issue is NOT with the generated stubs,
    but with how type[T] works in the user's function signature.
    """
    test_file = tmp_path / "test_generic_issue.py"
    test_file.write_text(
        """
from __future__ import annotations

from typing import TypeVar, Protocol

T = TypeVar('T')

class MyProto(Protocol):
    def do_something(self) -> str: ...

# Signature similar to user's try_connect
async def generic_cast(cast_as: T | None = None) -> T | None:
    return None

async def main():
    # Pass a Protocol type, get back an instance
    result = await generic_cast(cast_as=MyProto)
    
    # Is result an instance or a type?
    if result:
        result.do_something()  # Should work if result is MyProto instance

import asyncio
asyncio.run(main())
"""
    )

    from tests.conftest import run_pyright

    returncode, output = run_pyright(test_file, cwd=tmp_path)

    print(f"\nGeneric test output:\n{output}\n")

    if "type[MyProto]" in output or "Argument missing" in output:
        print(
            "❌ The issue is with how TypeVar works with `cast_as: T | None`!\n"
            "When you pass a type (like MyProto), Python infers T = type[MyProto],\n"
            "not T = MyProto.\n\n"
            "The fix is to use `cast_as: type[T] | None` instead!"
        )
    else:
        print("Hmm, this simpler case works...")


def test_correct_signature_with_type_t(tmp_path: Path):
    """Test the CORRECT signature using type[T]."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("channel.capnp", tmp_path)
    stub_dir = stub_path.parent

    test_file = tmp_path / "test_correct_signature.py"
    test_file.write_text(
        f"""
from __future__ import annotations

import sys
sys.path.insert(0, '{stub_dir}')

import asyncio
import channel_capnp
from typing import TypeVar

T = TypeVar('T')

class ConnectionManager:
    # CORRECT signature: cast_as takes type[T], returns T
    async def try_connect(
        self,
        sturdy_ref: str | None,
        cast_as: type[T] | None = None,  # ← type[T], not T
    ) -> T | None:
        return None

async def main():
    con_man = ConnectionManager()
    
    # Pass the type
    first_reader = await con_man.try_connect(
        "capnp://example.com:5000/token",
        cast_as=channel_capnp.Channel.Reader
    )
    
    # first_reader should be Reader instance
    if first_reader:
        promise = first_reader.read()  # Should work!

asyncio.run(main())
"""
    )

    from tests.conftest import run_pyright

    returncode, output = run_pyright(test_file, cwd=tmp_path)

    print(f"\nCorrect signature test:\n{output}\n")

    error_count = output.count("error:")
    if error_count > 0:
        pytest.fail(f"Even correct signature has errors:\n{output}")

    print("✅ With `type[T]` signature, everything works correctly!")
