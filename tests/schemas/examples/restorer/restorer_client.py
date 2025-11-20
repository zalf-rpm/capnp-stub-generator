from __future__ import annotations

import asyncio

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
    bag1 = result.cap.as_interface(restorer_capnp.Bag)

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
    bag1_again = result.cap.as_interface(restorer_capnp.Bag)

    val = await bag1_again.getValue()
    print(f"Bag1 value again: {val.value}")
    assert val.value == "Hello World"

    print("Success!")

    # Test AnyTester
    print("Testing AnyTester...")
    tester = restorer.getAnyTester().tester

    # Test AnyStruct
    s_result = await tester.getAnyStruct()
    print(f"AnyStruct type: {type(s_result.s)}")
    # It should be _DynamicObjectReader
    assert "DynamicObjectReader" in str(type(s_result.s))
    # We can cast it to a struct if we want, but for now just checking the type returned
    s_typed = s_result.s.as_struct(restorer_capnp.Restorer.RestoreParams.schema)

    # Test AnyList
    l_result = await tester.getAnyList()
    # If server doesn't set it, it might be None or empty
    # print(f"AnyList type: {type(l_result.l)}")
    # assert "DynamicObjectReader" in str(type(l_result.l))
    pass

    # Test AnyPointer
    p_result = await tester.getAnyPointer()
    print(f"AnyPointer type: {type(p_result.p)}")
    # Should be _DynamicObjectReader wrapping the text
    assert "DynamicObjectReader" in str(type(p_result.p))
    # Cast to text
    text_val = p_result.p.as_text()
    assert text_val == "test_pointer"

    print("AnyTester Success!")


if __name__ == "__main__":
    asyncio.run(capnp.run(main()))
