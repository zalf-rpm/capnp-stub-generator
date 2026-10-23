"""Reader helper types for `calculator.capnp`."""

from collections.abc import Callable
from typing import Any, override

from capnp.lib.capnp import (
    _DynamicStructReader,
)

from . import builders as builders
from . import clients as clients
from . import common as common
from . import lists as lists

class ExpressionCallReader(_DynamicStructReader):
    @property
    def function(self) -> clients.FunctionClient: ...
    @property
    def params(self) -> ExpressionListReader: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], Any] | None = None,
    ) -> builders.ExpressionCallBuilder: ...

class ExpressionReader(_DynamicStructReader):
    @property
    def literal(self) -> float: ...
    @property
    def previousResult(self) -> clients.ValueClient: ...
    @property
    def parameter(self) -> int: ...
    @property
    def call(self) -> ExpressionCallReader: ...
    @property
    @override
    def which(self) -> common._ExpressionWhich: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], Any] | None = None,
    ) -> builders.ExpressionBuilder: ...

type ExpressionListReader = lists._ExpressionList.Reader

type Float64ListReader = lists._Float64List.Reader
