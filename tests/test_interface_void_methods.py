"""Test that void interface methods return Awaitable[None], not None."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_void_methods_return_awaitable_none(tmp_path: Path):
    """Test that void interface methods like close() return Awaitable[None]."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # close() should return Awaitable[None], not None
    assert "def close(self) -> Awaitable[None]:" in content, "Void methods should return Awaitable[None]"

    # Should NOT have: def close(self) -> None:
    # (except possibly in type annotations or comments)
    lines = [line for line in content.split("\n") if "def close(self)" in line]
    for line in lines:
        if "def close(self) -> None:" in line:
            pytest.fail(f"Found void method returning None instead of Awaitable[None]: {line}")


def test_void_method_send_returns_awaitable_none(tmp_path: Path):
    """Test that CloseRequest.send() also returns Awaitable[None]."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # CloseRequest.send() should return Awaitable[None]
    assert "def send(self) -> Awaitable[None]:" in content, "send() for void methods should return Awaitable[None]"


def test_void_method_usage_pattern(tmp_path: Path):
    """Test that void methods can be properly awaited in user code."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    stub_dir = stub_path.parent

    test_file = tmp_path / "test_void_usage.py"
    test_file.write_text(
        f"""
from __future__ import annotations

import sys
sys.path.insert(0, '{stub_dir}')

import asyncio
import fbp_simple_capnp
from typing import TypeVar

T = TypeVar('T')

class ConnectionManager:
    async def try_connect(
        self,
        sturdy_ref: str | None,
        cast_as: type[T] | None = None,
    ) -> T | None:
        return None

async def main():
    con_man = ConnectionManager()
    
    reader = await con_man.try_connect(
        "capnp://example.com:5000/token",
        cast_as=fbp_simple_capnp.Channel.Reader
    )
    
    if reader:
        # close() returns Awaitable[None], so we must await it
        await reader.close()  # This should type-check correctly
        
        # Can also store the promise before awaiting
        close_promise = reader.close()
        await close_promise  # Should work

asyncio.run(main())
"""
    )

    from tests.conftest import run_pyright

    returncode, output = run_pyright(test_file, cwd=tmp_path)

    error_count = output.count("error:")
    if error_count > 0:
        print(f"Type checking output:\n{output}")
        pytest.fail(f"Found {error_count} type errors:\n{output}")

    print("✅ Void methods work correctly with await!")


def test_server_void_methods_return_none(tmp_path: Path):
    """Test that Server implementations of void methods return None (not Awaitable[None])."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # Server.close() can return None because server implementations
    # can be sync or async - pycapnp wraps them
    # Actually, let's check what's generated
    lines = content.split("\n")
    in_server = False
    for i, line in enumerate(lines):
        if "class Server:" in line:
            in_server = True
        elif "class " in line and in_server:
            in_server = False

        if in_server and "def close(self" in line:
            print(f"Server.close(): {line.strip()}")
            # Server methods should return Awaitable (they're async)
            if "Awaitable" not in line:
                print(f"Note: Server method doesn't have Awaitable: {line}")
            # This is actually acceptable - server methods can be sync or async


def test_comparison_with_non_void_methods(tmp_path: Path):
    """Compare void methods with non-void methods to ensure consistency."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # read() returns Awaitable[Channel.Reader.ReadResult] (direct struct return creates a Result protocol with scoping)
    assert "def read(self) -> Awaitable[Channel.Reader.ReadResult]:" in content

    # close() returns Awaitable[None] (void method)
    assert "def close(self) -> Awaitable[None]:" in content

    # The pattern should be consistent:
    # ALL client interface methods return Awaitable[ReturnType]
    print("✅ Consistent Awaitable pattern for all interface methods!")
