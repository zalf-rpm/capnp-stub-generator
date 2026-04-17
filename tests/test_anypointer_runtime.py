"""Runtime tests for AnyPointer behavior against generated stubs."""

from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path
from typing import Any, cast

import capnp
import pytest

# Ensure we can import from tests directory
sys.path.append(str(Path(__file__).parent.parent))

from tests._generated.examples.restorer import restorer_capnp
from tests.schemas.examples.restorer.restorer_server import RestorerImpl


async def _test_anypointer_runtime_behavior() -> None:
    # Start server on random port
    async def new_connection(stream: capnp.lib.capnp.AsyncIoStream) -> None:
        await capnp.TwoPartyServer(stream, bootstrap=RestorerImpl()).on_disconnect()

    server = await capnp.AsyncIoStream.create_server(new_connection, "localhost", 0)
    port = server.sockets[0].getsockname()[1]

    async with server:
        # Start client
        connection = await capnp.AsyncIoStream.create_connection(host="localhost", port=port)
        client = capnp.TwoPartyClient(connection)
        bootstrap = client.bootstrap()
        restorer = bootstrap.cast_as(restorer_capnp.Restorer)

        # Get AnyTester
        tester_result = await restorer.getAnyTester()
        tester = tester_result.tester

        # Test 1: Passing a list to AnyPointer (Expected Failure)
        # This is the core issue: type hint says it's allowed (list[Any]), but runtime fails
        with pytest.raises(capnp.KjException) as excinfo:
            await tester.setAnyPointer(cast("Any", [1, 2, 3]))

        # Verify the error message is about init() or similar
        # The exact message might vary but "init() with size is only valid for list" is typical
        assert "init() with size is only valid for list" in str(excinfo.value) or "failed" in str(excinfo.value)

        # Test 2: Passing a string (Text) to AnyPointer (Should work)
        await tester.setAnyPointer("valid string")

        # Test 3: Passing a struct to AnyPointer (Should work)
        params = restorer_capnp.Restorer.RestoreParams.new_message(localRef="test")
        await tester.setAnyPointer(params)

        # Test 4: Passing a Capability to AnyPointer (Should work)
        # We can pass the tester itself
        await tester.setAnyPointer(tester)

        # Close connection to allow server to shut down
        connection.close()


def test_anypointer_runtime_wrapper() -> None:
    """Test anypointer runtime wrapper."""
    asyncio.run(capnp.run(_test_anypointer_runtime_behavior()))


async def _test_anypointer_result_none_behavior() -> None:
    tuples_module = importlib.import_module("tests._generated.examples.restorer.restorer_capnp.types.results.tuples")

    class AnyTesterImpl(restorer_capnp.AnyTester.Server):
        async def getAnyStruct(
            self,
            _context: object,
            **_kwargs: object,
        ) -> restorer_capnp.types.common.AnyStruct | restorer_capnp.types.results.tuples.GetanystructResultTuple | None:
            return tuples_module.GetanystructResultTuple(s=None)

        async def getAnyList(
            self,
            _context: object,
            **_kwargs: object,
        ) -> restorer_capnp.types.common.AnyList | restorer_capnp.types.results.tuples.GetanylistResultTuple | None:
            return tuples_module.GetanylistResultTuple(l=None)

        async def getAnyPointer(
            self,
            _context: object,
            **_kwargs: object,
        ) -> (
            restorer_capnp.types.common.AnyPointer | restorer_capnp.types.results.tuples.GetanypointerResultTuple | None
        ):
            return tuples_module.GetanypointerResultTuple(p=None)

    async def new_connection(stream: capnp.lib.capnp.AsyncIoStream) -> None:
        await capnp.TwoPartyServer(stream, bootstrap=AnyTesterImpl()).on_disconnect()

    server = await capnp.AsyncIoStream.create_server(new_connection, "localhost", 0)
    port = server.sockets[0].getsockname()[1]

    async with server:
        connection = await capnp.AsyncIoStream.create_connection(host="localhost", port=port)
        client = capnp.TwoPartyClient(connection)
        tester = client.bootstrap().cast_as(restorer_capnp.AnyTester)

        try:
            for method_name in ("getAnyStruct", "getAnyList", "getAnyPointer"):
                with pytest.raises(capnp.KjException) as excinfo:
                    await getattr(tester, method_name)()
                assert "Value type mismatch" in str(excinfo.value)
        finally:
            connection.close()


def test_anypointer_result_none_wrapper() -> None:
    """AnyPointer-style ResultTuple fields should stay non-optional because None is rejected at runtime."""
    asyncio.run(capnp.run(_test_anypointer_result_none_behavior()))
