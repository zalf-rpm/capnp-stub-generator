"""Regression tests for pycapnp promise wait() expectations."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import capnp

from tests.test_helpers import read_generated_types_combined

if TYPE_CHECKING:
    from pathlib import Path


def test_runtime_promise_classes_do_not_expose_wait() -> None:
    """Pycapnp promise classes should expose await/cancel, not a blocking wait()."""
    assert "cancel" in dir(capnp.lib.capnp._Promise)
    assert "wait" not in dir(capnp.lib.capnp._Promise)
    assert "__await__" in dir(capnp.lib.capnp._RemotePromise)
    assert "wait" not in dir(capnp.lib.capnp._RemotePromise)


def test_generated_read_result_helper_does_not_advertise_wait(basic_stubs: Path) -> None:
    """Generated result helpers should not claim wait() support that pycapnp lacks."""
    content = read_generated_types_combined(basic_stubs / "fbp_simple_capnp")

    match = re.search(r"class ReadResult\(Awaitable\[ReadResult\], Protocol\):.*?(?=\nclass |\Z)", content, re.DOTALL)
    assert match is not None
    assert "def read(self) -> results_client.ReadResult:" in content
    assert "def wait(" not in match.group(0)
