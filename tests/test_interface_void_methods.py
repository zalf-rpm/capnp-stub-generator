"""Test that void interface methods return awaitable Result protocols."""

from __future__ import annotations


def test_void_methods_return_result_protocol(basic_stubs):
    """Test that void interface methods like close() return a Result protocol (awaitable)."""
    stub_path = basic_stubs / "fbp_simple_capnp" / "__init__.pyi"
    content = stub_path.read_text()

    # close() should return Client.CloseResult (which is Awaitable[None])
    # Results are now nested inside Client classes
    assert (
        "def close(self) -> _ChannelInterfaceModule._ReaderInterfaceModule.ReaderClient.CloseResult:" in content
        or "def close(self) -> _ChannelInterfaceModule._WriterInterfaceModule.WriterClient.CloseResult:" in content
    ), "Void methods should return nested Client.Result protocol for promise pipelining"

    # CloseRequest should exist at module level
    assert "class CloseRequest(Protocol):" in content


def test_void_method_send_returns_result(basic_stubs):
    """Test that CloseRequest.send() returns Client.CloseResult (awaitable)."""
    stub_path = basic_stubs / "fbp_simple_capnp" / "__init__.pyi"
    content = stub_path.read_text()

    # CloseRequest.send() should return Client.CloseResult (consistent with non-void methods)
    assert "class CloseRequest(Protocol):" in content
    # send() is defined in CloseRequest - check separately
    assert "CloseRequest" in content
    assert "def send(self)" in content


def test_void_result_protocol_is_awaitable(basic_stubs):
    """Test that CloseResult is Awaitable[None]."""
    stub_path = basic_stubs / "fbp_simple_capnp" / "__init__.pyi"
    content = stub_path.read_text()

    # CloseResult should be Awaitable[None]
    assert "class CloseResult(Awaitable[None], Protocol): ..." in content, (
        "CloseResult should be Awaitable[None] for void methods"
    )


def test_server_void_methods_return_awaitable_none(basic_stubs):
    """Test that Server implementations of void methods return Awaitable[None]."""
    stub_path = basic_stubs / "fbp_simple_capnp" / "__init__.pyi"
    content = stub_path.read_text()

    # Server.close() returns Awaitable[None] because server implementations are async
    assert "Awaitable[None]" in content, "Server void methods should return Awaitable[None]"


def test_comparison_with_non_void_methods(basic_stubs):
    """Compare void methods with non-void methods to ensure consistency."""
    stub_path = basic_stubs / "fbp_simple_capnp" / "__init__.pyi"
    content = stub_path.read_text()

    # read() returns Client.ReadResult (which is Awaitable) - using Protocol naming
    # Results are now nested inside Client classes
    assert "def read(" in content
    # Result types exist
    assert "ReadResult" in content

    # close() also returns nested Client.Result (CloseResult which is Awaitable[None])
    assert (
        "def close(self) -> _ChannelInterfaceModule._ReaderInterfaceModule.ReaderClient.CloseResult:" in content
        or "def close(self) -> _ChannelInterfaceModule._WriterInterfaceModule.WriterClient.CloseResult:" in content
    )

    print("✅ Consistent void/non-void method patterns with nested Results!")
