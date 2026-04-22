"""Tests for assignment-friendly ResultTuple typing."""

from __future__ import annotations

import asyncio
import importlib
import re
import sys
from typing import TYPE_CHECKING

import capnp

from tests.test_helpers import read_generated_types_combined, run_pyright

if TYPE_CHECKING:
    from pathlib import Path


async def _invoke_none_result_method(
    server_impl: object,
    interface_module: capnp.lib.capnp._InterfaceModule,
    method_name: str,
) -> capnp.KjException:
    async def new_connection(stream: capnp.lib.capnp.AsyncIoStream) -> None:
        await capnp.TwoPartyServer(stream, bootstrap=server_impl).on_disconnect()

    server = await capnp.AsyncIoStream.create_server(new_connection, "localhost", 0)
    port = server.sockets[0].getsockname()[1]

    try:
        async with server:
            connection = await capnp.AsyncIoStream.create_connection(host="localhost", port=port)
            client = capnp.TwoPartyClient(connection)
            bootstrap = client.bootstrap().cast_as(interface_module)

            try:
                await getattr(bootstrap, method_name)()
            except capnp.KjException as error:
                return error
            finally:
                connection.close()
    finally:
        server.close()
        await server.wait_closed()

    msg = f"{method_name} unexpectedly accepted None in a ResultTuple"
    raise AssertionError(msg)


def test_struct_result_tuple_accepts_struct_assignment_shapes(basic_stubs: Path) -> None:
    """Struct-valued ResultTuple fields should accept the same shapes as server result setters."""
    content = read_generated_types_combined(basic_stubs / "runtime_test_capnp")

    assert "class GetstructResultTuple(NamedTuple):" in content
    assert "info: builders.InfoBuilder | readers.InfoReader | dict[str, Any]" in content
    assert re.search(
        r"def getStruct\(.*?Awaitable\[\s*builders\.InfoBuilder\s*\|\s*readers\.InfoReader\s*\|\s*dict\[str, Any\]\s*\|\s*results_tuples\.GetstructResultTuple\s*\|\s*None\s*\]",
        content,
        re.DOTALL,
    )


def test_list_result_tuple_accepts_sequence_assignment_shapes(basic_stubs: Path) -> None:
    """List-valued ResultTuple fields should accept the same shapes as server result setters."""
    content = read_generated_types_combined(basic_stubs / "list_result_capnp")

    assert "class GetitemsResultTuple(NamedTuple):" in content
    assert "items: builders.ItemListBuilder | readers.ItemListReader | Sequence[Any]" in content
    assert re.search(
        r"def getItems\(.*?Awaitable\[\s*builders\.ItemListBuilder\s*\|\s*readers\.ItemListReader\s*\|\s*Sequence\[Any\]\s*\|\s*results_tuples\.GetitemsResultTuple\s*\|\s*None\s*\]",
        content,
        re.DOTALL,
    )


def test_interface_result_tuple_accepts_forwarded_clients(basic_stubs: Path) -> None:
    """Interface-valued ResultTuple fields should accept forwarded clients as well as servers."""
    content = read_generated_types_combined(basic_stubs / "runtime_test_capnp")

    assert "class GetinterfaceResultTuple(NamedTuple):" in content
    assert "service: _TestServiceInterfaceModule._SubServiceInterfaceModule.Server | SubServiceClient" in content

    match = re.search(r"def getInterface\(.*?-> Awaitable\[(.*?)\]", content, re.DOTALL)
    assert match, "getInterface server signature not found"
    assert "_TestServiceInterfaceModule._SubServiceInterfaceModule.Server" in match.group(1)
    assert "SubServiceClient" in match.group(1)


def test_result_tuple_type_checking(basic_stubs: Path) -> None:
    """Pyright should accept ResultTuple construction with assignment-friendly field types."""
    test_code = """
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
    async def getStruct(self, _context: GetstructCallContext, **kwargs: object):
        return {"name": "demo", "value": 1}


class ItemServiceImpl(list_result_capnp.ItemService.Server):
    async def getItems(self, _context: GetitemsCallContext, **kwargs: object):
        return [{"name": "demo", "value": 1}]
"""

    test_file = basic_stubs / "test_result_tuple_usage.py"
    test_file.write_text(test_code)

    result = run_pyright(test_file)
    assert result.returncode == 0, f"Type checking failed: {result.stdout}"


def test_result_tuple_runtime_helpers_live_under_tuple_module(basic_stubs: Path) -> None:
    """Runtime ResultTuple helpers should live in types.results.tuples, not the top-level module."""
    runtime_content = (basic_stubs / "runtime_test_capnp" / "__init__.py").read_text()
    tuple_module_content = (basic_stubs / "runtime_test_capnp" / "types" / "results" / "tuples.py").read_text()

    assert "GetstructResultTuple" not in runtime_content
    assert "GetinterfaceResultTuple" not in runtime_content
    assert "GetstructResultTuple" in tuple_module_content
    assert "GetinterfaceResultTuple" in tuple_module_content


def test_result_tuple_runtime_module_is_importable_and_instantiable(basic_stubs: Path) -> None:
    """Generated runtime tuple helpers should be importable and constructible from types.results.tuples."""
    sys.path.insert(0, str(basic_stubs))

    try:
        runtime_test_capnp = importlib.import_module("runtime_test_capnp")
        tuples_module = importlib.import_module("runtime_test_capnp.types.results.tuples")

        result_tuple = tuples_module.GetstructResultTuple(info={"name": "demo", "value": 1})

        assert result_tuple.info == {"name": "demo", "value": 1}
        assert not hasattr(runtime_test_capnp, "GetstructResultTuple")
    finally:
        for module_name in (
            "runtime_test_capnp.types.results.tuples",
            "runtime_test_capnp.types.results",
            "runtime_test_capnp.types",
            "runtime_test_capnp",
        ):
            sys.modules.pop(module_name, None)
        sys.path.remove(str(basic_stubs))


def test_result_tuple_none_values_are_rejected_at_runtime(basic_stubs: Path) -> None:
    """ResultTuple field types should stay non-optional because pycapnp rejects None during result serialization."""
    sys.path.insert(0, str(basic_stubs))

    try:
        runtime_test_capnp = importlib.import_module("runtime_test_capnp")
        list_result_capnp = importlib.import_module("list_result_capnp")
        runtime_tuple_module = importlib.import_module("runtime_test_capnp.types.results.tuples")
        list_tuple_module = importlib.import_module("list_result_capnp.types.results.tuples")

        async def invoke_method(
            server_impl: object,
            interface_module: capnp.lib.capnp._InterfaceModule,
            method_name: str,
        ) -> capnp.KjException:
            return await _invoke_none_result_method(server_impl, interface_module, method_name)

        async def run_checks() -> dict[str, capnp.KjException]:
            class TestServiceImpl(runtime_test_capnp.TestService.Server):
                async def getPrimitive(self, _context: object, **_kwargs: object) -> object:
                    return runtime_tuple_module.GetprimitiveResultTuple(result=None)

                async def getStruct(self, _context: object, **_kwargs: object) -> object:
                    return runtime_tuple_module.GetstructResultTuple(info=None)

                async def getInterface(self, _context: object, **_kwargs: object) -> object:
                    return runtime_tuple_module.GetinterfaceResultTuple(service=None)

            class ItemServiceImpl(list_result_capnp.ItemService.Server):
                async def getItems(self, _context: object, **_kwargs: object) -> object:
                    return list_tuple_module.GetitemsResultTuple(items=None)

            return {
                "getPrimitive": await invoke_method(TestServiceImpl(), runtime_test_capnp.TestService, "getPrimitive"),
                "getStruct": await invoke_method(TestServiceImpl(), runtime_test_capnp.TestService, "getStruct"),
                "getInterface": await invoke_method(TestServiceImpl(), runtime_test_capnp.TestService, "getInterface"),
                "getItems": await invoke_method(ItemServiceImpl(), list_result_capnp.ItemService, "getItems"),
            }

        errors = asyncio.run(capnp.run(run_checks()))
        for method_name, error in errors.items():
            assert "Value type mismatch" in str(error), f"{method_name} should reject None, got: {error}"
    finally:
        for module_name in (
            "runtime_test_capnp.types.results.tuples",
            "runtime_test_capnp.types.results",
            "runtime_test_capnp.types",
            "runtime_test_capnp",
            "list_result_capnp.types.results.tuples",
            "list_result_capnp.types.results",
            "list_result_capnp.types",
            "list_result_capnp",
        ):
            sys.modules.pop(module_name, None)
        sys.path.remove(str(basic_stubs))
