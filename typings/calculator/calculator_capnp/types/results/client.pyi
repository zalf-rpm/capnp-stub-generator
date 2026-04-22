"""Client result helper types for `calculator.capnp`."""

from collections.abc import Awaitable
from typing import Protocol

from .. import clients as clients

class ReadResult(Awaitable[ReadResult], Protocol):
    value: float

class CallResult(Awaitable[CallResult], Protocol):
    value: float

class EvaluateResult(Awaitable[EvaluateResult], Protocol):
    value: clients.ValueClient

class DeffunctionResult(Awaitable[DeffunctionResult], Protocol):
    func: clients.FunctionClient

class GetoperatorResult(Awaitable[GetoperatorResult], Protocol):
    func: clients.FunctionClient
