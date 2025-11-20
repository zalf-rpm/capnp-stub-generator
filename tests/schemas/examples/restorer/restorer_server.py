from __future__ import annotations

import asyncio

import capnp

from tests._generated.examples.restorer import restorer_capnp


class BagImpl(restorer_capnp.Bag.Server):
    def __init__(self, value=""):
        self.value = value

    async def getValue_context(self, context):
        context.results.value = self.value

    async def setValue_context(self, context):
        self.value = context.params.value


class RestorerImpl(restorer_capnp.Restorer.Server):
    def __init__(self):
        self.bags = {}

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
