"""Reader helper types for `fbp_nested_callback.capnp`."""

from collections.abc import Callable
from typing import override

from capnp.lib.capnp import (
    _DynamicStructReader,
)

from . import builders as builders

class StatsReader(_DynamicStructReader):
    @property
    def noOfWaitingWriters(self) -> int: ...
    @property
    def noOfWaitingReaders(self) -> int: ...
    @property
    def noOfIpsInQueue(self) -> int: ...
    @property
    def totalNoOfIpsReceived(self) -> int: ...
    @property
    def timestamp(self) -> str: ...
    @property
    def updateIntervalInMs(self) -> int: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> builders.StatsBuilder: ...
