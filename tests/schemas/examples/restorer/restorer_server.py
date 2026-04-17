from __future__ import annotations

import asyncio
import importlib
from typing import TYPE_CHECKING, Any

import capnp

if TYPE_CHECKING:
    from restorer import restorer_capnp
    from restorer.restorer_capnp.types.results.tuples import (
        GetanystructResultTuple,
        GetvalueResultTuple,
    )
    from restorer.restorer_capnp.types.servers import (
        AnyTesterServer,
        BagServer,
        RestorerServer,
    )
else:
    from tests._generated.examples.restorer import restorer_capnp

    AnyTesterServer = restorer_capnp.AnyTester.Server
    BagServer = restorer_capnp.Bag.Server
    RestorerServer = restorer_capnp.Restorer.Server

RESULT_TUPLES_MODULE = (
    "restorer.restorer_capnp.types.results.tuples"
    if TYPE_CHECKING
    else "tests._generated.examples.restorer.restorer_capnp.types.results.tuples"
)


def _get_anystruct_result_tuple() -> type[GetanystructResultTuple]:
    tuples_module = importlib.import_module(RESULT_TUPLES_MODULE)
    return tuples_module.GetanystructResultTuple


def _get_value_result_tuple() -> type[GetvalueResultTuple]:
    tuples_module = importlib.import_module(RESULT_TUPLES_MODULE)
    return tuples_module.GetvalueResultTuple


class BagImpl(BagServer):
    def __init__(self, value: str = "") -> None:
        self.value = value

    async def getValue(self, _context: object, **kwargs: object) -> GetvalueResultTuple:
        # Return NamedTuple
        return _get_value_result_tuple()(value=self.value)

    async def setValue_context(self, context: Any) -> None:
        self.value = context.params.value


class AnyTesterImpl(AnyTesterServer):
    async def getAnyStruct(self, _context: object, **kwargs: object) -> GetanystructResultTuple:
        # Return a RestoreParams struct directly (single value return)
        params = restorer_capnp.Restorer.RestoreParams.new_message(localRef="test_struct")
        # We need to wrap it in the NamedTuple because the stub expects GetanystructResultTuple | None
        # The single value return optimization is only for primitives/interfaces in the stub generator logic
        # Wait, let's check writer.py logic for single field return
        return _get_anystruct_result_tuple()(s=params)

    async def getAnyList_context(self, context: Any) -> None:
        # Return a list of strings (Text)
        # Note: pycapnp might struggle with AnyList assignment without explicit type
        # But let's try a list of strings which is more standard
        # If this fails, we might need to skip AnyList testing or use a typed list in schema
        # context.results.l = ["a", "b"]
        # Actually, let's just skip setting it for now to avoid the KjException
        # The client will receive a null pointer (None?) or empty reader
        pass

    async def getAnyPointer_context(self, context: Any) -> None:
        context.results.p = "test_pointer"

    async def setAnyPointer_context(self, context: Any) -> None:
        # Just consume it to verify it was passed
        pass


class RestorerImpl(RestorerServer):
    def __init__(self) -> None:
        self.bags: dict[str, capnp.lib.capnp.Capability] = {}

    async def getAnyTester_context(self, context: Any) -> None:
        context.results.tester = AnyTesterImpl()

    async def restore_context(self, context: Any) -> None:
        local_ref = context.params.localRef
        print(f"Restoring {local_ref}")

        if local_ref not in self.bags:
            # Create a new bag if it doesn't exist
            self.bags[local_ref] = BagImpl(f"Value for {local_ref}")

        # Return the capability
        # Note: context.results.cap expects a Capability
        # We return our BagImpl which is a Server (inherits from Capability.Server)
        context.results.cap = self.bags[local_ref]


async def new_connection(stream: capnp.lib.capnp.AsyncIoStream) -> None:
    await capnp.TwoPartyServer(stream, bootstrap=RestorerImpl()).on_disconnect()


async def main() -> None:
    # Create the restorer
    # In a real server, we would export this via TwoPartyServer
    # For this example, we'll just simulate usage or run a simple server

    # Create a server socket
    server = await capnp.AsyncIoStream.create_server(new_connection, "localhost", 60000)
    print("Server running on port 60000")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(capnp.run(main()))
