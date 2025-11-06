"""Test that interface methods returning structs directly are typed correctly."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_direct_struct_return_generates_awaitable(tmp_path: Path):
    """Test that `read() -> Msg` generates `Awaitable[ReadResult]` with a Result Protocol."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # Should have: class ReadResult(Protocol): with struct fields
    assert "class ReadResult(Protocol):" in content, "Direct struct return should create a Result Protocol"

    # Client method should return Awaitable[Channel.Reader.ReadResult] (properly scoped)
    assert "def read(self) -> Awaitable[Channel.Reader.ReadResult]:" in content, (
        "Direct struct return should be Awaitable[Channel.Reader.ReadResult]"
    )

    assert "class ReadCallContext(Protocol)" in content, "Should have CallContext for server _context"
    assert "results: Channel.Reader.ReadResult" in content, (
        "CallContext should have results: Channel.Reader.ReadResult for direct struct returns"
    )


def test_named_result_fields_still_create_protocol(tmp_path: Path):
    """Test that `reader() -> (r :Reader)` still creates a Result Protocol."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # Should have: class ReaderResult(Awaitable[ReaderResult], Protocol):
    assert "class ReaderResult(Awaitable[ReaderResult], Protocol):" in content, (
        "Named result fields should create Result Protocol"
    )

    # Should have the named field
    assert "r: Channel.Reader" in content, "Result Protocol should have the named field"


def test_direct_struct_return_usage_pattern(tmp_path: Path):
    """Test that the usage pattern works correctly with direct struct returns."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    stub_dir = stub_path.parent

    test_file = tmp_path / "test_usage.py"
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
    
    # Get a reader interface
    reader = await con_man.try_connect(
        "capnp://example.com:5000/token",
        cast_as=fbp_simple_capnp.Channel.Reader
    )
    
    if reader:
        # Call read() - returns Awaitable[ReadResult]
        msg_awaitable = reader.read()
        
        # Await to get the ReadResult
        msg = await msg_awaitable
        
        # msg is ReadResult - access its fields
        # For unions, check which() to see which field is set
        which = msg.which()
        
        if which == 'value':
            content = msg.value  # Should work
            print(f"Value: {{content}}")
        elif which == 'done':
            print("Done message")
        elif which == 'noMsg':
            print("No message")

asyncio.run(main())
"""
    )

    from tests.conftest import run_pyright

    returncode, output = run_pyright(test_file, cwd=tmp_path)

    error_count = output.count("error:")
    if error_count > 0:
        print(f"Type checking output:\n{output}")
        pytest.fail(f"Found {error_count} type errors:\n{output}")

    print("✅ Direct struct return usage works correctly!")


def test_request_send_method_returns_awaitable(tmp_path: Path):
    """Test that ReadRequest.send() also returns Awaitable[ReadResult]."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # The ReadRequest Protocol should have send() returning Awaitable[Channel.Reader.ReadResult] (properly scoped)
    assert "def send(self) -> Awaitable[Channel.Reader.ReadResult]:" in content, (
        "send() method should return Awaitable[Channel.Reader.ReadResult]"
    )


def test_server_method_returns_result_for_direct_struct(tmp_path: Path):
    """Test that Server.read() returns Awaitable[Server.ReadResult] (NamedTuple) for direct struct returns."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # Server implementation returns Awaitable[Channel.Reader.Server.ReadResult] (NamedTuple)
    # Check for the key parts (may span multiple lines)
    assert "def read(" in content, "Should have read method"
    assert "_context: Channel.Reader.ReadCallContext" in content, "Should have ReadCallContext parameter"
    assert "Awaitable[Channel.Reader.Server.ReadResult]" in content, (
        "Server method should return Awaitable[Channel.Reader.Server.ReadResult]"
    )
    assert "class ReadResult(NamedTuple):" in content, "Should have Server.ReadResult as NamedTuple"


def test_channel_capnp_like_schema(tmp_path: Path):
    """Test with a more complex schema similar to the real Channel interface."""
    # Create a more realistic test schema
    from tests.conftest import SCHEMAS_DIR

    schema_file = SCHEMAS_DIR / "fbp_channel.capnp"
    schema_file.write_text(
        """
@0xbf602c4868dbb231;

struct IP {
    content @0 :AnyPointer;
}

interface Channel {
    struct Msg {
        union {
            value @0 :IP;
            done  @1 :Void;
        }
    }
    
    interface Reader {
        read        @0 () -> Msg;
        readIfMsg   @1 () -> Msg;
        close       @2 ();
    }
    
    interface Writer {
        write @0 (msg :Msg);
        close @1 ();
    }
    
    reader  @0 () -> (r :Reader);
    writer  @1 () -> (w :Writer);
}
"""
    )

    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_channel.capnp", tmp_path)
    content = stub_path.read_text()

    # Both read and readIfMsg should return properly scoped results
    # Note: capitalize() converts "readIfMsg" to "Readifmsg"
    assert "def read(self) -> Awaitable[Channel.Reader.ReadResult]:" in content, (
        "read() should return Awaitable[Channel.Reader.ReadResult]"
    )

    assert "def readIfMsg(self) -> Awaitable[Channel.Reader.ReadifmsgResult]:" in content, (
        "readIfMsg() should return Awaitable[Channel.Reader.ReadifmsgResult]"
    )

    # Named result fields should still work
    assert "class ReaderResult" in content
    assert "class WriterResult" in content

    print("✅ Complex FBP-like schema generates correct types!")
