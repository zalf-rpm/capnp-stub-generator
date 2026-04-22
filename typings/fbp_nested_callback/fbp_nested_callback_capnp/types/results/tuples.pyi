"""Result tuple helper types for `fbp_nested_callback.capnp`."""

from typing import NamedTuple

from .. import clients as clients
from .. import modules as modules

class UnregResultTuple(NamedTuple):
    success: bool

class RegisterstatscallbackResultTuple(NamedTuple):
    unregisterCallback: (
        modules._ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
        | clients.UnregisterClient
    )
