"""Regression tests for embedded nested callback interfaces."""

from __future__ import annotations

import asyncio
import sys
from importlib import import_module
from pathlib import Path
from typing import Any

import capnp

TESTS_DIR = Path(__file__).parent
REPO_ROOT = TESTS_DIR.parent
SCHEMA_PATH = TESTS_DIR / "schemas" / "examples" / "fbp_nested_callback" / "fbp_nested_callback.capnp"

if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))


def _load_generated_module() -> Any:
    """Import the generated example module after fixtures created it."""
    return import_module("tests._generated.examples.fbp_nested_callback.fbp_nested_callback_capnp")


async def _exercise_direct_load() -> None:
    direct_schema = capnp.load(str(SCHEMA_PATH))

    class StatsCallback(direct_schema.Channel.StatsCallback.Server):
        async def status_context(self, context: Any) -> None:
            _ = context.params.stats

    class Channel(direct_schema.Channel.Server):
        async def registerStatsCallback_context(self, context: Any) -> None:
            _ = context.params.updateIntervalInMs

    channel_client = direct_schema.Channel._new_client(Channel())
    _ = channel_client.registerStatsCallback(StatsCallback(), 1000)


async def _exercise_generated_embedded_schema() -> None:
    fbp_nested_callback_capnp = _load_generated_module()

    class StatsCallback(fbp_nested_callback_capnp.Channel.StatsCallback.Server):
        async def status_context(self, context: Any) -> None:
            _ = context.params.stats

    class Channel(fbp_nested_callback_capnp.Channel.Server):
        async def registerStatsCallback_context(self, context: Any) -> None:
            _ = context.params.updateIntervalInMs

    channel_client = fbp_nested_callback_capnp.Channel._new_client(Channel())
    _ = channel_client.registerStatsCallback(StatsCallback(), 1000)


def test_direct_loaded_schema_accepts_branded_nested_callback_server() -> None:
    """Direct pycapnp loads should accept the nongeneric nested callback server."""
    asyncio.run(capnp.run(_exercise_direct_load()))


def test_generated_embedded_schema_accepts_nested_callback_server() -> None:
    """Generated runtime modules should expose a usable branded nested callback."""
    asyncio.run(capnp.run(_exercise_generated_embedded_schema()))


def test_generated_runtime_uses_typed_schema_helpers() -> None:
    """Generated runtime files should use typed schema helpers for nested schema access."""
    runtime_file = (
        TESTS_DIR / "_generated" / "examples" / "fbp_nested_callback" / "fbp_nested_callback_capnp" / "__init__.py"
    )
    content = runtime_file.read_text()
    assert "from typing import cast" in content
    assert "def _as_struct_schema(schema: object) -> _StructSchema:" in content
    assert "def _struct_field(schema: _StructSchema, name: str) -> _StructSchemaField:" in content
    assert "def _interface_method(schema: _InterfaceSchema, name: str) -> _InterfaceMethod:" in content
    assert content.splitlines()[0] == "# pyright: reportAttributeAccessIssue=false, reportArgumentType=false"
    assert "_require_" not in content
    assert "import schema_capnp" in content
    assert "capnp.schema_capnp" not in content
    assert "sys.modules.get" not in content
    assert "capnp.add_import_hook()" not in content
    assert "_field_schema(" in content
    assert "_method_param_type(" in content
    assert "_method_result_type(" in content
    assert 'Channel.schema.methods["registerStatsCallback"].param_type.fields["callback"].schema' not in content
    assert 'Channel.StatsCallback.schema.methods["status"].param_type.fields["stats"].schema' not in content
    assert (
        'Channel.schema.methods["registerStatsCallback"].result_type.fields["unregisterCallback"].schema' not in content
    )
