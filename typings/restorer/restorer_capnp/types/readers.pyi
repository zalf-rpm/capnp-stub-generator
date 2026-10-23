"""Reader helper types for `restorer.capnp`."""

from collections.abc import Callable
from typing import Any, override

from capnp.lib.capnp import (
    _DynamicStructReader,
)

from . import builders as builders

class RestoreParamsReader(_DynamicStructReader):
    @property
    def localRef(self) -> str: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], Any] | None = None,
    ) -> builders.RestoreParamsBuilder: ...
