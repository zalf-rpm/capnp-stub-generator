"""Reader helper types for `single_value.capnp`."""

from collections.abc import Callable
from typing import override

from capnp.lib.capnp import (
    _DynamicStructReader,
)

from . import builders as builders
from . import lists as lists

class MyStructReader(_DynamicStructReader):
    @property
    def id(self) -> int: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> builders.MyStructBuilder: ...

type Int32ListReader = lists._Int32List.Reader

type MyStructListReader = lists._MyStructList.Reader
