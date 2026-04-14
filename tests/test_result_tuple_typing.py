"""Tests for assignment-friendly ResultTuple typing."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tests.test_helpers import run_pyright

if TYPE_CHECKING:
    from pathlib import Path


def test_struct_result_tuple_accepts_struct_assignment_shapes(basic_stubs: Path) -> None:
    """Struct-valued ResultTuple fields should accept the same shapes as server result setters."""
    stub_file = basic_stubs / "runtime_test_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    assert "class GetstructResultTuple(NamedTuple):" in content
    assert "info: InfoBuilder | InfoReader | dict[str, Any]" in content
    assert re.search(
        r"def getStruct\(.*?-> Awaitable\[InfoBuilder \| InfoReader \| dict\[str, Any\] \| GetstructResultTuple \| None\]",
        content,
        re.DOTALL,
    )


def test_list_result_tuple_accepts_sequence_assignment_shapes(basic_stubs: Path) -> None:
    """List-valued ResultTuple fields should accept the same shapes as server result setters."""
    stub_file = basic_stubs / "list_result_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    assert "class GetitemsResultTuple(NamedTuple):" in content
    assert "items: ItemListBuilder | ItemListReader | Sequence[Any]" in content
    assert re.search(
        r"def getItems\(.*?-> Awaitable\[ItemListBuilder \| ItemListReader \| Sequence\[Any\] \| GetitemsResultTuple \| None\]",
        content,
        re.DOTALL,
    )


def test_interface_result_tuple_accepts_forwarded_clients(basic_stubs: Path) -> None:
    """Interface-valued ResultTuple fields should accept forwarded clients as well as servers."""
    stub_file = basic_stubs / "runtime_test_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    assert "class GetinterfaceResultTuple(NamedTuple):" in content
    assert "service: _TestServiceInterfaceModule._SubServiceInterfaceModule.Server | SubServiceClient" in content

    match = re.search(r"def getInterface\(.*?-> Awaitable\[(.*?)\]", content, re.DOTALL)
    assert match, "getInterface server signature not found"
    assert "_TestServiceInterfaceModule._SubServiceInterfaceModule.Server" in match.group(1)
    assert "SubServiceClient" in match.group(1)


def test_result_tuple_type_checking(basic_stubs: Path) -> None:
    """Pyright should accept ResultTuple construction with assignment-friendly field types."""
    test_code = """
from typing import Any

import list_result_capnp
import runtime_test_capnp
from list_result_capnp.types.contexts import GetitemsCallContext
from list_result_capnp.types.results.tuples import GetitemsResultTuple
from runtime_test_capnp.types.contexts import GetstructCallContext
from runtime_test_capnp.types.clients import SubServiceClient
from runtime_test_capnp.types.results.tuples import GetinterfaceResultTuple, GetstructResultTuple


def build_struct_tuple() -> GetstructResultTuple:
    return GetstructResultTuple(info={"name": "demo", "value": 1})


def build_list_tuple() -> GetitemsResultTuple:
    return GetitemsResultTuple(items=[{"name": "demo", "value": 1}])


def build_interface_tuple(forwarded: SubServiceClient) -> GetinterfaceResultTuple:
    return GetinterfaceResultTuple(service=forwarded)


class RuntimeTestServiceImpl(runtime_test_capnp.TestService.Server):
    async def getStruct(self, _context: GetstructCallContext, **kwargs: Any):
        return {"name": "demo", "value": 1}


class ItemServiceImpl(list_result_capnp.ItemService.Server):
    async def getItems(self, _context: GetitemsCallContext, **kwargs: Any):
        return [{"name": "demo", "value": 1}]
"""

    test_file = basic_stubs / "test_result_tuple_usage.py"
    test_file.write_text(test_code)

    result = run_pyright(test_file)
    assert result.returncode == 0, f"Type checking failed: {result.stdout}"
