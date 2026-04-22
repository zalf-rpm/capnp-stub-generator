"""Test that void interface methods return awaitable Result protocols."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.test_helpers import log_summary, read_generated_types_combined

if TYPE_CHECKING:
    from pathlib import Path


def test_void_methods_return_result_protocol(basic_stubs: Path) -> None:
    """Test that void interface methods like close() return a Result protocol (awaitable)."""
    content = read_generated_types_combined(basic_stubs / "fbp_simple_capnp")

    # close() should return a flattened top-level helper Result (which is Awaitable[None])
    assert "def close(self) -> ReaderCloseResult:" in content or "def close(self) -> WriterCloseResult:" in content, (
        "Void methods should return flattened top-level Result helpers for promise pipelining"
    )

    # CloseRequest helpers should exist at module level
    assert "class ReaderCloseRequest(Protocol):" in content
    assert "class WriterCloseRequest(Protocol):" in content


def test_void_method_send_returns_result(basic_stubs: Path) -> None:
    """Test that the flattened CloseRequest helpers return top-level Result helpers."""
    content = read_generated_types_combined(basic_stubs / "fbp_simple_capnp")

    assert "class ReaderCloseRequest(Protocol):" in content
    assert "def send(self) -> ReaderCloseResult: ..." in content
    assert "class WriterCloseRequest(Protocol):" in content
    assert "def send(self) -> WriterCloseResult: ..." in content


def test_void_result_protocol_is_awaitable(basic_stubs: Path) -> None:
    """Test that CloseResult is Awaitable[None]."""
    content = read_generated_types_combined(basic_stubs / "fbp_simple_capnp")

    assert "class ReaderCloseResult(Awaitable[None], Protocol): ..." in content
    assert "class WriterCloseResult(Awaitable[None], Protocol): ..." in content


def test_server_void_methods_return_awaitable_none(basic_stubs: Path) -> None:
    """Test that Server implementations of void methods return Awaitable[None]."""
    content = read_generated_types_combined(basic_stubs / "fbp_simple_capnp")

    # Server.close() returns Awaitable[None] because server implementations are async
    assert "Awaitable[None]" in content, "Server void methods should return Awaitable[None]"


def test_comparison_with_non_void_methods(basic_stubs: Path) -> None:
    """Compare void methods with non-void methods to ensure consistency."""
    content = read_generated_types_combined(basic_stubs / "fbp_simple_capnp")

    # read() returns a flattened top-level Result helper (which is Awaitable)
    assert "def read(" in content
    # Result types exist
    assert "ReadResult" in content

    # close() also returns flattened top-level Result helpers
    assert "def close(self) -> ReaderCloseResult:" in content or "def close(self) -> WriterCloseResult:" in content

    log_summary(
        "VOID METHOD RESULT SUMMARY",
        ["✅ Consistent void/non-void method patterns with flattened top-level helpers!"],
    )
