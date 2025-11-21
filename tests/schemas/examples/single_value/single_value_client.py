import asyncio

import capnp

from tests._generated.examples.single_value import single_value_capnp


async def main():
    # Connect to server
    # Note: In a real scenario we'd use argparse for host/port
    connection = await capnp.AsyncIoStream.create_connection(host="localhost", port=60000)
    client = capnp.TwoPartyClient(connection)

    # Bootstrap the restorer
    client = client.bootstrap().cast_as(single_value_capnp.SingleValue)

    # Bool
    res_bool = await client.getBool()
    val_bool: bool = res_bool.val
    assert val_bool is True

    # Int
    res_int = await client.getInt()
    val_int: int = res_int.val
    assert val_int == 42

    # Float
    res_float = await client.getFloat()
    val_float: float = res_float.val
    assert abs(val_float - 3.14) < 0.001

    # Text
    res_text = await client.getText()
    val_text: str = res_text.val
    assert val_text == "hello"

    # Data
    res_data = await client.getData()
    val_data: bytes = res_data.val
    assert val_data == b"data"

    # List
    res_list = await client.getList()
    # val_list is a Sequence[int] (Reader)
    val_list = res_list.val
    assert len(val_list) == 3
    assert val_list[0] == 1

    # Struct
    res_struct = await client.getStruct()
    val_struct = res_struct.val
    assert val_struct.id == 123

    # Interface
    res_interface = await client.getInterface()
    val_interface = res_interface.val
    # val_interface should be a SingleValue client
    # We can call methods on it
    res_bool_2 = await val_interface.getBool()
    assert res_bool_2.val is True

    # AnyPointer
    # res_any = await client.getAny()
    # val_any = res_any.val
    # AnyPointer handling depends on what was sent.

    # List of Structs
    res_list_struct = await client.getListStruct()
    val_list_struct = res_list_struct.val
    assert len(val_list_struct) == 2
    assert val_list_struct[0].id == 1
    assert val_list_struct[1].id == 2


if __name__ == "__main__":
    asyncio.run(capnp.run(main()))
