"""Regression tests for embedded nested callback interfaces."""

from __future__ import annotations

import asyncio
import re
import sys
from importlib import import_module
from pathlib import Path
from typing import Any

import capnp

from tests.test_helpers import run_command

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


def test_generated_runtime_uses_typed_schema_paths() -> None:
    """Generated runtime files should use typed module helpers instead of inline casts."""
    runtime_file = (
        TESTS_DIR / "_generated" / "examples" / "fbp_nested_callback" / "fbp_nested_callback_capnp" / "__init__.py"
    )
    content = runtime_file.read_text()
    assert content.splitlines()[0] == "# pyright: reportAttributeAccessIssue=false, reportArgumentType=false"
    assert "_require_" not in content
    assert "import schema_capnp" in content
    assert "capnp.schema_capnp" not in content
    assert "sys.modules.get" not in content
    assert "capnp.add_import_hook()" not in content
    assert "cast(" not in content
    assert "def _as_struct_schema" not in content
    assert "def _struct_field" not in content
    assert "def _interface_method" not in content
    assert "_field_schema(" not in content
    assert "_method_param_type(" not in content
    assert "_method_result_type(" not in content
    assert "from capnp.lib.capnp import _InterfaceModule" in content
    assert "from .types.modules import" not in content
    assert re.search(
        r'Channel\.schema\.methods\["registerStatsCallback"\]\.param_type\.fields\["callback"\]\.schema', content
    )
    assert re.search(
        r'Channel\.StatsCallback\.schema\.methods\["status"\]\.param_type\.fields\["stats"\]\.schema', content
    )
    assert re.search(
        r'Channel\.schema\.methods\["registerStatsCallback"\]\.result_type\.fields\["unregisterCallback"\]\.schema',
        content,
    )


def test_schema_helpers_are_separated_into_types_schemas() -> None:
    """Public schema helper aliases should live in `types.schemas` while modules keep the canonical nested classes."""
    types_dir = TESTS_DIR / "_generated" / "examples" / "fbp_nested_callback" / "fbp_nested_callback_capnp" / "types"
    modules_content = (types_dir / "modules.pyi").read_text()
    schemas_content = (types_dir / "schemas.pyi").read_text()

    assert "from . import schemas as schemas" in modules_content
    assert "def schema(self) -> schemas._ChannelSchema" in modules_content
    assert "def schema(self) -> schemas._ChannelStatsCallbackSchema" in modules_content
    assert "class _ChannelSchema(" in modules_content
    assert "class _StatsCallbackSchema(" in modules_content

    assert "from . import modules as modules" in schemas_content
    assert "type _ChannelSchema = modules._ChannelInterfaceModule._ChannelSchema" in schemas_content
    assert (
        "type _ChannelStatsCallbackSchema = modules._ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema"
        in schemas_content
    )


def test_generated_schema_chain_type_checks_without_casts(tmp_path: Path) -> None:
    """Generated schema helper types should make raw nested schema chains strict-clean."""
    sample = tmp_path / "typed_schema_chain.py"
    sample.write_text(
        """
from fbp_nested_callback import fbp_nested_callback_capnp

callback_schema = fbp_nested_callback_capnp.Channel.schema.methods["registerStatsCallback"].param_type.fields["callback"].schema
status_method = callback_schema.methods["status"]
stats_schema = callback_schema.methods["status"].param_type.fields["stats"].schema
timestamp_field = stats_schema.fields["timestamp"]
_ = (status_method, timestamp_field)
""".strip(),
    )

    result = run_command(["basedpyright", str(sample)], cwd=REPO_ROOT)
    assert result.returncode == 0, result.stdout or result.stderr
