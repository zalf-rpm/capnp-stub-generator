"""Request helper types for `fbp_nested_callback.capnp`."""

from typing import Any, Literal, Protocol, overload

from . import builders as builders
from . import clients as clients
from . import modules as modules
from .results import client as results_client

class UnregRequest(Protocol):
    def send(self) -> results_client.UnregResult: ...

class StatusRequest(Protocol):
    stats: builders.StatsBuilder
    @overload
    def init(self, name: Literal["stats"]) -> builders.StatsBuilder: ...
    @overload
    def init(self, name: str, size: int = ...) -> Any: ...
    def send(self) -> results_client.StatusResult: ...

class RegisterstatscallbackRequest(Protocol):
    callback: clients.StatsCallbackClient | modules._ChannelInterfaceModule._StatsCallbackInterfaceModule.Server
    updateIntervalInMs: int
    def send(self) -> results_client.RegisterstatscallbackResult: ...
