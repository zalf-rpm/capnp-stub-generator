from __future__ import annotations

import asyncio
from typing import cast

import capnp

from tests._generated.examples.restorer import restorer_capnp


async def main():
    # Connect to server
    # Note: In a real scenario we'd use argparse for host/port
    connection = await capnp.AsyncIoStream.create_connection(host="localhost", port=60000)
    client = capnp.TwoPartyClient(connection)

    # Bootstrap the restorer
    restorer = client.bootstrap().cast_as(restorer_capnp.Restorer)

    # Restore a bag
    print("Restoring 'bag1'...")
    result = await restorer.restore(localRef="bag1")

    # The result.cap should now be typed as _DynamicCapabilityClient (or Capability)
    # which has cast_as method.
    bag1 = result.cap.cast_as(restorer_capnp.Bag)

    # Use the bag
    val = await bag1.getValue()
    print(f"Bag1 value: {val.value}")

    # Set new value
    print("Setting bag1 value to 'Hello World'...")
    await bag1.setValue("Hello World")

    # Verify value
    val = await bag1.getValue()
    print(f"Bag1 new value: {val.value}")

    # Restore same bag again (should persist state in memory)
    print("Restoring 'bag1' again...")
    result = await restorer.restore(localRef="bag1")
    bag1_again = result.cap.cast_as(restorer_capnp.Bag)

    val = await bag1_again.getValue()
    print(f"Bag1 value again: {val.value}")
    assert val.value == "Hello World"

    print("Success!")


if __name__ == "__main__":
    asyncio.run(capnp.run(main()))
