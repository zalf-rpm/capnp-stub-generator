"""Tests for direct-struct interface parameters in server CallContext helpers."""

from __future__ import annotations

import asyncio
import importlib
import re
import sys
from typing import TYPE_CHECKING, Any

import capnp

if TYPE_CHECKING:
    from pathlib import Path


async def _capture_direct_union_write_context(fbp_capnp: Any) -> dict[str, object]:
    future: asyncio.Future[dict[str, object]] = asyncio.get_running_loop().create_future()

    class WriterImpl(fbp_capnp.Channel.Writer.Server):
        async def write_context(self, context: Any) -> None:
            future.set_result(
                {
                    "params_type": type(context.params).__name__,
                    "which": context.params.which(),
                    "done": context.params.done,
                },
            )

    writer = fbp_capnp.Channel.Writer._new_client(WriterImpl())
    await writer.write(done=None)
    return await asyncio.wait_for(future, timeout=5)


def test_direct_union_params_use_reader_in_callcontext(zalfmas_stubs: Path) -> None:
    """Direct-struct union params should expose the union reader on CallContext.params."""
    content = (zalfmas_stubs / "mas" / "schema" / "fbp" / "fbp_capnp" / "types" / "_all.pyi").read_text()

    assert re.search(r"class WriteCallContext\(Protocol\):\n\s+params: MsgReader", content)
    assert re.search(r"class WriteifspaceCallContext\(Protocol\):\n\s+params: MsgReader", content)
    assert "class WriteParams(Protocol):" not in content
    assert "class WriteifspaceParams(Protocol):" not in content


def test_direct_union_params_only_advertise_context_server_variant(zalfmas_stubs: Path) -> None:
    """Direct union params should only advertise the _context server variant."""
    content = (zalfmas_stubs / "mas" / "schema" / "fbp" / "fbp_capnp" / "types" / "_all.pyi").read_text()
    writer_server = re.search(
        r"class _WriterInterfaceModule.*?class Server\([^\)]*\):(?P<body>.*?)\n\s*Writer: _WriterInterfaceModule",
        content,
        re.DOTALL,
    )
    assert writer_server, "Writer.Server block not found"

    body = writer_server.group("body")
    assert "def write_context(self, context: WriteCallContext) -> Awaitable[None]: ..." in body
    assert "def writeIfSpace_context(self, context: WriteifspaceCallContext) -> Awaitable[None]: ..." in body
    assert "def write(" not in body
    assert "def writeIfSpace(" not in body


def test_direct_non_union_params_use_reader_but_keep_regular_server_method(zalfmas_stubs: Path) -> None:
    """Direct non-union params should still use the struct reader in CallContext.params."""
    content = (zalfmas_stubs / "mas" / "schema" / "fbp" / "fbp_capnp" / "types" / "_all.pyi").read_text()

    assert re.search(r"class SetconfigentryCallContext\(Protocol\):\n\s+params: ConfigEntryReader", content)
    assert "class SetconfigentryParams(Protocol):" not in content
    assert re.search(r"def setConfigEntry\([^)]*_context:\s*SetconfigentryCallContext", content, re.DOTALL)


def test_explicit_wrapper_params_keep_params_protocol(basic_stubs: Path) -> None:
    """Explicit `(msg :Msg)` params should keep the synthetic Params wrapper."""
    content = (basic_stubs / "fbp_channel_capnp" / "types" / "_all.pyi").read_text()

    assert re.search(r"class WriteParams\(Protocol\):\n\s+msg: MsgReader", content)
    assert re.search(r"class WriteCallContext\(Protocol\):\n\s+params: WriteParams", content)


def test_direct_union_context_params_which_works_at_runtime(zalfmas_stubs: Path) -> None:
    """Runtime CallContext.params should support which() for direct union params."""
    had_loader = hasattr(capnp, "_embedded_schema_loader")
    previous_loader = getattr(capnp, "_embedded_schema_loader", None)
    sys.path.insert(0, str(zalfmas_stubs))

    try:
        capnp._embedded_schema_loader = capnp.SchemaLoader()
        fbp_capnp = importlib.import_module("mas.schema.fbp.fbp_capnp")
        result = asyncio.run(capnp.run(_capture_direct_union_write_context(fbp_capnp)))
    finally:
        for module_name in ("mas.schema.fbp.fbp_capnp", "mas.schema.fbp", "mas.schema", "mas"):
            sys.modules.pop(module_name, None)
        if had_loader:
            capnp._embedded_schema_loader = previous_loader
        elif hasattr(capnp, "_embedded_schema_loader"):
            delattr(capnp, "_embedded_schema_loader")
        sys.path.remove(str(zalfmas_stubs))

    assert result["params_type"] == "_DynamicStructReader"
    assert result["which"] == "done"
    assert result["done"] is None
