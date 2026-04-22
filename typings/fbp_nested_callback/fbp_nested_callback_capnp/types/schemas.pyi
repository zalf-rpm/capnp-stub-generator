"""Schema helper types for `fbp_nested_callback.capnp`."""

from . import modules as modules

type _ChannelSchema = modules._ChannelInterfaceModule._ChannelSchema

type _ChannelStatsCallbackSchema = modules._ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema

type _ChannelStatsCallbackStatsSchema = (
    modules._ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsStructModule._StatsSchema
)

type _ChannelStatsCallbackUnregisterSchema = (
    modules._ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema
)
