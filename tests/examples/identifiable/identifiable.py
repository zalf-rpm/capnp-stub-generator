import asyncio
import uuid

import capnp
from _generated_zalfmas import common_capnp

# import common_capnp


class Identifiable(common_capnp.Identifiable.Server):
    def __init__(
        self,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        self._id: str = id if id else str(uuid.uuid4())
        self._name: str = name if name else f"Unnamed_{self._id}"
        self._description: str = description if description else ""
        self._init_info_func = None

    @property
    def init_info_func(self):
        return self._init_info_func

    @init_info_func.setter
    def init_info_func(self, f):
        self._init_info_func = f

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, i):
        self._id = i

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, d):
        self._description = d

    async def info(self, **kwargs):  # () -> IdInformation;
        if self._init_info_func:
            self._init_info_func()

        id_infomation = common_capnp.IdInformation.new_message(id=self.id, name=self.name, description=self.description)
        return id_infomation


async def main():
    identifiable = Identifiable(name="TestObject", description="This is a test object.")
    print(f"Info: {await identifiable.info()}")
    # Inspect the type of the object
    print(f"Type: {type(await identifiable.info())}")


if __name__ == "__main__":
    asyncio.run(capnp.run(main()))
