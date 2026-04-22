"""Context helper types for `restorer.capnp`."""

from typing import Protocol

from . import common as common
from . import readers as readers
from .results import server as results_server

class GetvalueParams(Protocol): ...

class GetvalueCallContext(Protocol):
    params: GetvalueParams
    @property
    def results(self) -> results_server.GetvalueServerResult: ...

class SetvalueParams(Protocol):
    value: str

class SetvalueCallContext(Protocol):
    params: SetvalueParams

class GetanystructParams(Protocol): ...

class GetanystructCallContext(Protocol):
    params: GetanystructParams
    @property
    def results(self) -> results_server.GetanystructServerResult: ...

class GetanylistParams(Protocol): ...

class GetanylistCallContext(Protocol):
    params: GetanylistParams
    @property
    def results(self) -> results_server.GetanylistServerResult: ...

class GetanypointerParams(Protocol): ...

class GetanypointerCallContext(Protocol):
    params: GetanypointerParams
    @property
    def results(self) -> results_server.GetanypointerServerResult: ...

class SetanypointerParams(Protocol):
    p: common.AnyPointer

class SetanypointerCallContext(Protocol):
    params: SetanypointerParams

class RestoreCallContext(Protocol):
    params: readers.RestoreParamsReader
    @property
    def results(self) -> results_server.RestoreServerResult: ...

class GetanytesterParams(Protocol): ...

class GetanytesterCallContext(Protocol):
    params: GetanytesterParams
    @property
    def results(self) -> results_server.GetanytesterServerResult: ...
