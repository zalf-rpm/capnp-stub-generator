"""Request helper types for `restorer.capnp`."""

from typing import Protocol

from capnp.lib.capnp import (
    _DynamicObjectBuilder,
)

from . import common as common
from .results import client as results_client

class GetvalueRequest(Protocol):
    def send(self) -> results_client.GetvalueResult: ...

class SetvalueRequest(Protocol):
    value: str
    def send(self) -> results_client.SetvalueResult: ...

class GetanystructRequest(Protocol):
    def send(self) -> results_client.GetanystructResult: ...

class GetanylistRequest(Protocol):
    def send(self) -> results_client.GetanylistResult: ...

class GetanypointerRequest(Protocol):
    def send(self) -> results_client.GetanypointerResult: ...

class SetanypointerRequest(Protocol):
    @property
    def p(self) -> _DynamicObjectBuilder: ...
    @p.setter
    def p(self, value: common.AnyPointer) -> None: ...
    def send(self) -> results_client.SetanypointerResult: ...

class RestoreRequest(Protocol):
    localRef: str
    def send(self) -> results_client.RestoreResult: ...

class GetanytesterRequest(Protocol):
    def send(self) -> results_client.GetanytesterResult: ...
