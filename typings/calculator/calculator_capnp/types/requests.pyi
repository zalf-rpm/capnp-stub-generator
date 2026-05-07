"""Request helper types for `calculator.capnp`."""

from collections.abc import Sequence
from typing import Any, Literal, Protocol, overload

from . import builders as builders
from . import enums as enums
from . import readers as readers
from .results import client as results_client

class ReadRequest(Protocol):
    def send(self) -> results_client.ReadResult: ...

class CallRequest(Protocol):
    params: builders.Float64ListBuilder | readers.Float64ListReader | Sequence[float]
    @overload
    def init(self, name: Literal["params"], size: int = ...) -> builders.Float64ListBuilder: ...
    @overload
    def init(self, name: str, size: int = ...) -> Any: ...
    def send(self) -> results_client.CallResult: ...

class EvaluateRequest(Protocol):
    expression: builders.ExpressionBuilder
    @overload
    def init(self, name: Literal["expression"]) -> builders.ExpressionBuilder: ...
    @overload
    def init(self, name: str, size: int = ...) -> Any: ...
    def send(self) -> results_client.EvaluateResult: ...

class DeffunctionRequest(Protocol):
    paramCount: int
    body: builders.ExpressionBuilder
    @overload
    def init(self, name: Literal["body"]) -> builders.ExpressionBuilder: ...
    @overload
    def init(self, name: str, size: int = ...) -> Any: ...
    def send(self) -> results_client.DeffunctionResult: ...

class GetoperatorRequest(Protocol):
    op: enums.CalculatorOperatorEnum
    def send(self) -> results_client.GetoperatorResult: ...
