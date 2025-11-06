"""Tests to ensure generated stubs pass pyright validation with proper scoping."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def test_direct_struct_return_pyright_validation(tmp_path: Path):
    """Test that direct struct return stubs pass pyright validation."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("struct_return.capnp", tmp_path)
    
    # Run pyright
    result = subprocess.run(['pyright', str(stub_path)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Pyright output:\n{result.stdout}")
        pytest.fail(f"Pyright validation failed for struct_return.capnp stubs")
    
    assert "0 errors" in result.stdout, "Should have no errors"
    print("✅ Direct struct return stubs pass pyright validation")


def test_nested_interface_pyright_validation(tmp_path: Path):
    """Test that nested interface stubs pass pyright validation."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    
    # Run pyright
    result = subprocess.run(['pyright', str(stub_path)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Pyright output:\n{result.stdout}")
        pytest.fail(f"Pyright validation failed for fbp_simple.capnp stubs")
    
    assert "0 errors" in result.stdout, "Should have no errors"
    print("✅ Nested interface stubs pass pyright validation")


def test_complex_nested_interface_pyright_validation(tmp_path: Path):
    """Test that complex nested interface stubs pass pyright validation."""
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
    
    # Run pyright
    result = subprocess.run(['pyright', str(stub_path)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Pyright output:\n{result.stdout}")
        pytest.fail(f"Pyright validation failed for fbp_channel.capnp stubs")
    
    assert "0 errors" in result.stdout, "Should have no errors"
    print("✅ Complex nested interface stubs pass pyright validation")


def test_scoping_in_result_protocols(tmp_path: Path):
    """Test that Result protocols reference nested types with proper scoping."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("struct_return.capnp", tmp_path)
    content = stub_path.read_text()
    
    # Check that InfoResult is properly referenced with full scope
    assert "results: Identifiable.InfoResult" in content, (
        "CallContext.results should reference InfoResult with full scope"
    )
    assert "def info(self) -> Awaitable[Identifiable.InfoResult]:" in content, (
        "Method should reference InfoResult with full scope"
    )
    assert "def send(self) -> Awaitable[Identifiable.InfoResult]:" in content, (
        "Request.send() should reference InfoResult with full scope"
    )
    
    print("✅ Result protocols use proper scoping")


def test_scoping_in_nested_interfaces(tmp_path: Path):
    """Test that nested interface Result protocols use proper scoping."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()
    
    # Check that ReadResult is properly referenced with full scope (Channel.Reader.ReadResult)
    assert "results: Channel.Reader.ReadResult" in content, (
        "CallContext.results should reference ReadResult with full scope"
    )
    assert "def read(self) -> Awaitable[Channel.Reader.ReadResult]:" in content, (
        "Method should reference ReadResult with full scope"
    )
    assert "def send(self) -> Awaitable[Channel.Reader.ReadResult]:" in content, (
        "Request.send() should reference ReadResult with full scope"
    )
    
    print("✅ Nested interface Result protocols use proper scoping")
