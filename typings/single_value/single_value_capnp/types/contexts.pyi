"""Context helper types for `single_value.capnp`."""

from typing import Protocol

from .results import server as results_server

class GetboolParams(Protocol): ...

class GetboolCallContext(Protocol):
    params: GetboolParams
    @property
    def results(self) -> results_server.GetboolServerResult: ...

class GetintParams(Protocol): ...

class GetintCallContext(Protocol):
    params: GetintParams
    @property
    def results(self) -> results_server.GetintServerResult: ...

class GetfloatParams(Protocol): ...

class GetfloatCallContext(Protocol):
    params: GetfloatParams
    @property
    def results(self) -> results_server.GetfloatServerResult: ...

class GettextParams(Protocol): ...

class GettextCallContext(Protocol):
    params: GettextParams
    @property
    def results(self) -> results_server.GettextServerResult: ...

class GetdataParams(Protocol): ...

class GetdataCallContext(Protocol):
    params: GetdataParams
    @property
    def results(self) -> results_server.GetdataServerResult: ...

class GetlistParams(Protocol): ...

class GetlistCallContext(Protocol):
    params: GetlistParams
    @property
    def results(self) -> results_server.GetlistServerResult: ...

class GetstructParams(Protocol): ...

class GetstructCallContext(Protocol):
    params: GetstructParams
    @property
    def results(self) -> results_server.GetstructServerResult: ...

class GetinterfaceParams(Protocol): ...

class GetinterfaceCallContext(Protocol):
    params: GetinterfaceParams
    @property
    def results(self) -> results_server.GetinterfaceServerResult: ...

class GetanyParams(Protocol): ...

class GetanyCallContext(Protocol):
    params: GetanyParams
    @property
    def results(self) -> results_server.GetanyServerResult: ...

class GetliststructParams(Protocol): ...

class GetliststructCallContext(Protocol):
    params: GetliststructParams
    @property
    def results(self) -> results_server.GetliststructServerResult: ...
