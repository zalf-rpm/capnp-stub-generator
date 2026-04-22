"""Context helper types for `calculator.capnp`."""

from typing import Protocol

from . import enums as enums
from . import readers as readers
from .results import server as results_server

class ReadParams(Protocol): ...

class ReadCallContext(Protocol):
    params: ReadParams
    @property
    def results(self) -> results_server.ReadServerResult: ...

class CallParams(Protocol):
    params: readers.Float64ListReader

class CallCallContext(Protocol):
    params: CallParams
    @property
    def results(self) -> results_server.CallServerResult: ...

class EvaluateParams(Protocol):
    expression: readers.ExpressionReader

class EvaluateCallContext(Protocol):
    params: EvaluateParams
    @property
    def results(self) -> results_server.EvaluateServerResult: ...

class DeffunctionParams(Protocol):
    paramCount: int
    body: readers.ExpressionReader

class DeffunctionCallContext(Protocol):
    params: DeffunctionParams
    @property
    def results(self) -> results_server.DeffunctionServerResult: ...

class GetoperatorParams(Protocol):
    op: enums.CalculatorOperatorEnum

class GetoperatorCallContext(Protocol):
    params: GetoperatorParams
    @property
    def results(self) -> results_server.GetoperatorServerResult: ...
