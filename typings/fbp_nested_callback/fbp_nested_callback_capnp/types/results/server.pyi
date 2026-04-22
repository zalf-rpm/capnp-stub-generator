"""Server result helper types for `fbp_nested_callback.capnp`."""

from capnp.lib.capnp import (
    _DynamicStructBuilder,
)

from .. import clients as clients
from .. import modules as modules

class UnregServerResult(_DynamicStructBuilder):
    @property
    def success(self) -> bool: ...
    @success.setter
    def success(self, value: bool) -> None: ...

class RegisterstatscallbackServerResult(_DynamicStructBuilder):
    @property
    def unregisterCallback(
        self,
    ) -> (
        modules._ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
        | clients.UnregisterClient
    ): ...
    @unregisterCallback.setter
    def unregisterCallback(
        self,
        value: modules._ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
        | clients.UnregisterClient,
    ) -> None: ...
