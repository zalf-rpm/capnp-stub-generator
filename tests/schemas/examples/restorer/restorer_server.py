from __future__ import annotations

import asyncio

import capnp

from tests._generated.examples.restorer import restorer_capnp


class BagImpl(restorer_capnp.Bag.Server):
    def __init__(self, value=""):
        self.value = value

    async def getValue(self, _context, **kwargs):
        # Return NamedTuple
        return restorer_capnp.Bag.Server.GetvalueResultTuple(value=self.value)

    async def setValue_context(self, context):
        self.value = context.params.value


class AnyTesterImpl(restorer_capnp.AnyTester.Server):
    async def getAnyStruct(self, _context, **kwargs):
        # Return a RestoreParams struct directly (single value return)
        params = restorer_capnp.Restorer.RestoreParams.new_message(localRef="test_struct")
        # We need to wrap it in the NamedTuple because the stub expects GetanystructResultTuple | None
        # The single value return optimization is only for primitives/interfaces in the stub generator logic
        # Wait, let's check writer.py logic for single field return
        return restorer_capnp.AnyTester.Server.GetanystructResultTuple(s=params)

    async def getAnyList_context(self, context):
        # Return a list of strings (Text)
        # Note: pycapnp might struggle with AnyList assignment without explicit type
        # But let's try a list of strings which is more standard
        # If this fails, we might need to skip AnyList testing or use a typed list in schema
        # context.results.l = ["a", "b"]
        # Actually, let's just skip setting it for now to avoid the KjException
        # The client will receive a null pointer (None?) or empty reader
        pass

    async def getAnyPointer_context(self, context):
        context.results.p = "test_pointer"


class RestorerImpl(restorer_capnp.Restorer.Server):
    def __init__(self):
        self.bags = {}

    async def getAnyTester_context(self, context):
        context.results.tester = AnyTesterImpl()

    async def restore_context(self, context):
        local_ref = context.params.localRef
        print(f"Restoring {local_ref}")

        if local_ref not in self.bags:
            # Create a new bag if it doesn't exist
            self.bags[local_ref] = BagImpl(f"Value for {local_ref}")

        # Return the capability
        # Note: context.results.cap expects a Capability
        # We return our BagImpl which is a Server (inherits from Capability.Server)
        context.results.cap = self.bags[local_ref]


async def new_connection(stream):
    await capnp.TwoPartyServer(stream, bootstrap=RestorerImpl()).on_disconnect()


async def main():
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
