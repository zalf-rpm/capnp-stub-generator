"""Client result helper types for `single_value.capnp`."""

from collections.abc import Awaitable
from typing import Protocol

from capnp.lib.capnp import (
    _DynamicObjectReader,
)

from .. import clients as clients
from .. import readers as readers

class GetboolResult(Awaitable[GetboolResult], Protocol):
    val: bool

class GetintResult(Awaitable[GetintResult], Protocol):
    val: int

class GetfloatResult(Awaitable[GetfloatResult], Protocol):
    val: float

class GettextResult(Awaitable[GettextResult], Protocol):
    val: str

class GetdataResult(Awaitable[GetdataResult], Protocol):
    val: bytes

class GetlistResult(Awaitable[GetlistResult], Protocol):
    val: readers.Int32ListReader

class GetstructResult(Awaitable[GetstructResult], Protocol):
    val: readers.MyStructReader

class GetinterfaceResult(Awaitable[GetinterfaceResult], Protocol):
    val: clients.SingleValueClient

class GetanyResult(Awaitable[GetanyResult], Protocol):
    val: _DynamicObjectReader

class GetliststructResult(Awaitable[GetliststructResult], Protocol):
    val: readers.MyStructListReader
