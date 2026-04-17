"""Runtime placeholder module for server helpers of `fbp_nested_callback.capnp`."""

from .. import Channel

ChannelServer = Channel.Server
StatsCallbackServer = Channel.StatsCallback.Server
UnregisterServer = Channel.StatsCallback.Unregister.Server
