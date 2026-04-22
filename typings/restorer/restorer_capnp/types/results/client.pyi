"""Client result helper types for `restorer.capnp`."""

from collections.abc import Awaitable
from typing import Protocol

from capnp.lib.capnp import (
    _DynamicObjectReader,
)

from .. import clients as clients

class GetvalueResult(Awaitable[GetvalueResult], Protocol):
    value: str

class SetvalueResult(Awaitable[None], Protocol): ...

class GetanystructResult(Awaitable[GetanystructResult], Protocol):
    s: _DynamicObjectReader

class GetanylistResult(Awaitable[GetanylistResult], Protocol):
    l: _DynamicObjectReader

class GetanypointerResult(Awaitable[GetanypointerResult], Protocol):
    p: _DynamicObjectReader

class SetanypointerResult(Awaitable[None], Protocol): ...

class RestoreResult(Awaitable[RestoreResult], Protocol):
    cap: _DynamicObjectReader

class GetanytesterResult(Awaitable[GetanytesterResult], Protocol):
    tester: clients.AnyTesterClient
