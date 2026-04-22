"""Client helper types for `fbp_nested_callback.capnp`."""

from typing import Any

from capnp.lib.capnp import (
    _DynamicCapabilityClient,
)

from . import builders as builders
from . import modules as modules
from . import readers as readers
from . import requests as requests
from .results import client as results_client

class UnregisterClient(_DynamicCapabilityClient):
    def unreg(self) -> results_client.UnregResult: ...
    def unreg_request(self) -> requests.UnregRequest: ...

class StatsCallbackClient(_DynamicCapabilityClient):
    def status(
        self,
        stats: builders.StatsBuilder | readers.StatsReader | dict[str, Any] | None = None,
    ) -> results_client.StatusResult: ...
    def status_request(self, stats: builders.StatsBuilder | None = None) -> requests.StatusRequest: ...

class ChannelClient(_DynamicCapabilityClient):
    def registerStatsCallback(
        self,
        callback: StatsCallbackClient
        | modules._ChannelInterfaceModule._StatsCallbackInterfaceModule.Server
        | None = None,
        updateIntervalInMs: int | None = None,
    ) -> results_client.RegisterstatscallbackResult: ...
    def registerStatsCallback_request(
        self,
        callback: StatsCallbackClient
        | modules._ChannelInterfaceModule._StatsCallbackInterfaceModule.Server
        | None = None,
        updateIntervalInMs: int | None = None,
    ) -> requests.RegisterstatscallbackRequest: ...
