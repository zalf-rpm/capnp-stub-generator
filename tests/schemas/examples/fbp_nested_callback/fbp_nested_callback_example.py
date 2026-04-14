from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import capnp

from tests._generated.examples.fbp_nested_callback import fbp_nested_callback_capnp

if TYPE_CHECKING:
    from tests._generated.examples.fbp_nested_callback.fbp_nested_callback_capnp.types.servers import (
        ChannelServer,
        StatsCallbackServer,
    )
else:
    ChannelServer = fbp_nested_callback_capnp.Channel.Server
    StatsCallbackServer = fbp_nested_callback_capnp.Channel.StatsCallback.Server


class StatsCallback(StatsCallbackServer):
    async def status_context(self, context) -> None:
        _ = context.params.stats


class Channel(ChannelServer):
    async def registerStatsCallback_context(self, context) -> None:
        _ = context.params.updateIntervalInMs


async def main() -> None:
    channel = Channel()
    channel_client = fbp_nested_callback_capnp.Channel._new_client(channel)
    _ = channel_client.registerStatsCallback(StatsCallback(), 1000)


if __name__ == "__main__":
    asyncio.run(capnp.run(main()))
