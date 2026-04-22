"""Builder helper types for `single_value.capnp`."""

from typing import override

from capnp.lib.capnp import (
    _DynamicStructBuilder,
)

from . import lists as lists
from . import readers as readers

class MyStructBuilder(_DynamicStructBuilder):
    @property
    def id(self) -> int: ...
    @id.setter
    def id(self, value: int) -> None: ...
    @override
    def as_reader(self) -> readers.MyStructReader: ...

type Int32ListBuilder = lists._Int32List.Builder

type MyStructListBuilder = lists._MyStructList.Builder
