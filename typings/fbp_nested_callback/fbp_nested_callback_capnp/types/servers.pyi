"""Server helper types for `fbp_nested_callback.capnp`."""

from . import modules as modules

ChannelServer = modules._ChannelInterfaceModule.Server

StatsCallbackServer = modules._ChannelInterfaceModule._StatsCallbackInterfaceModule.Server

UnregisterServer = modules._ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
