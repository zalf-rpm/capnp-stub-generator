import capnp

from tests._generated.examples.single_value import single_value_capnp


class SingleValueImpl(single_value_capnp.SingleValue.Server):
    async def getBool(self, _context, **kwargs):
        return True

    async def getInt(self, _context, **kwargs):
        return 42

    async def getFloat(self, _context, **kwargs):
        return 3.14

    async def getText(self, _context, **kwargs):
        return "hello"

    async def getData(self, _context, **kwargs):
        return b"data"

    async def getList(self, _context, **kwargs):
        return [1, 2, 3]

    async def getStruct(self, _context, **kwargs):
        return single_value_capnp.MyStruct.new_message(id=123)

    async def getInterface(self, _context, **kwargs):
        return self

    async def getAny(self, _context, **kwargs):
        return None

    async def getListStruct(self, _context, **kwargs):
        # Return a list of structs (builders)
        s1 = single_value_capnp.MyStruct.new_message(id=1)
        s2 = single_value_capnp.MyStruct.new_message(id=2)
        return [s1, s2]


async def new_connection(stream: capnp.lib.capnp.AsyncIoStream):
    await capnp.TwoPartyServer(stream, bootstrap=SingleValueImpl()).on_disconnect()


async def main():
    # Create the restorer
    # In a real server, we would export this via TwoPartyServer
    # For this example, we'll just simulate usage or run a simple server

    # Create a server socket
    server = await capnp.AsyncIoStream.create_server(new_connection, "localhost", 60000)
    print("Server running on port 60000")
    async with server:
        await server.serve_forever()
