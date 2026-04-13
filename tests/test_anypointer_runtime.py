"""Runtime tests for AnyPointer behavior against generated stubs."""

import asyncio
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
    async def new_connection(stream: "capnp.lib.capnp.AsyncIoStream") -> None:
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
        # await connection.wait_closed() # if available


def test_anypointer_runtime_wrapper() -> None:
    asyncio.run(capnp.run(_test_anypointer_runtime_behavior()))
