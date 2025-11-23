"""Test that void interface methods return awaitable Result protocols."""

from __future__ import annotations

from pathlib import Path


def test_void_methods_return_result_protocol(tmp_path: Path):
    """Test that void interface methods like close() return a Result protocol (awaitable)."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # close() should return Client.CloseResult (which is Awaitable[None])
    # Results are now nested inside Client classes
    assert (
        "def close(self) -> _ChannelInterfaceModule._ReaderInterfaceModule.ReaderClient.CloseResult:" in content
        or "def close(self) -> _ChannelInterfaceModule._WriterInterfaceModule.WriterClient.CloseResult:" in content
    ), "Void methods should return nested Client.Result protocol for promise pipelining"

    # CloseRequest should exist at module level
    assert "class CloseRequest(Protocol):" in content


def test_void_method_send_returns_result(tmp_path: Path):
    """Test that CloseRequest.send() returns Client.CloseResult (awaitable)."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # CloseRequest.send() should return Client.CloseResult (consistent with non-void methods)
    assert "class CloseRequest(Protocol):" in content
    assert (
        "def send(self) -> _ChannelInterfaceModule._ReaderInterfaceModule.ReaderClient.CloseResult:" in content
        or "def send(self) -> _ChannelInterfaceModule._WriterInterfaceModule.WriterClient.CloseResult:" in content
    ), "send() for void methods should return nested Client.CloseResult (awaitable)"


def test_void_result_protocol_is_awaitable(tmp_path: Path):
    """Test that CloseResult is Awaitable[None]."""
    from tests.conftest import generate_stub_from_schema

    stub_path = generate_stub_from_schema("fbp_simple.capnp", tmp_path)
    content = stub_path.read_text()

    # CloseResult should be Awaitable[None]
    assert "class CloseResult(Awaitable[None], Protocol): ..." in content, (
        "CloseResult should be Awaitable[None] for void methods"
    )


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

    # read() returns Client.ReadResult (which is Awaitable) - using Protocol naming
    # Results are now nested inside Client classes
    assert "def read(" in content
    assert ") -> _ChannelInterfaceModule._ReaderInterfaceModule.ReaderClient.ReadResult:" in content

    # close() also returns nested Client.Result (CloseResult which is Awaitable[None])
    assert (
        "def close(self) -> _ChannelInterfaceModule._ReaderInterfaceModule.ReaderClient.CloseResult:" in content
        or "def close(self) -> _ChannelInterfaceModule._WriterInterfaceModule.WriterClient.CloseResult:" in content
    )

    print("✅ Consistent void/non-void method patterns with nested Results!")
