"""Context helper types for `fbp_nested_callback.capnp`."""

from typing import Protocol

from . import clients as clients
from . import readers as readers
from .results import server as results_server

class UnregParams(Protocol): ...

class UnregCallContext(Protocol):
    params: UnregParams
    @property
    def results(self) -> results_server.UnregServerResult: ...

class StatusParams(Protocol):
    stats: readers.StatsReader

class StatusCallContext(Protocol):
    params: StatusParams

class RegisterstatscallbackParams(Protocol):
    callback: clients.StatsCallbackClient
    updateIntervalInMs: int

class RegisterstatscallbackCallContext(Protocol):
    params: RegisterstatscallbackParams
    @property
    def results(self) -> results_server.RegisterstatscallbackServerResult: ...
