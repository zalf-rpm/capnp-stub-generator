"""Test that void interface methods return None (fire-and-forget), not Awaitable."""

from __future__ import annotations

from pathlib import Path


def test_void_methods_return_none(tmp_path: Path):
    """Test that void interface methods like close() return None (fire-and-forget)."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # close() should return None (fire-and-forget)
    assert "def close(self) -> None:" in content, "Void methods should return None (fire-and-forget)"

    # CloseRequest should exist
    assert "class CloseRequest(Protocol):" in content


def test_void_method_send_returns_none(tmp_path: Path):
    """Test that CloseRequest.send() returns None."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # CloseRequest.send() should return None
    assert "def send(self) -> None:" in content, "send() for void methods should return None"


def test_server_void_methods_return_awaitable_none(tmp_path: Path):
    """Test that Server implementations of void methods return Awaitable[None]."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # Server.close() returns Awaitable[None] because server implementations are async
    assert "Awaitable[None]" in content, "Server void methods should return Awaitable[None]"


def test_comparison_with_non_void_methods(tmp_path: Path):
    """Compare void methods with non-void methods to ensure consistency."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # read() returns ReadResult (which is Awaitable) - using Protocol naming
    assert "def read(" in content
    assert ") -> _ChannelModule._ReaderModule.ReadResult:" in content

    # close() returns None (fire-and-forget)
    assert "def close(self) -> None:" in content

    print("✅ Consistent void/non-void method patterns!")
