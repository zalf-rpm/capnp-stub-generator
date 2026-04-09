from __future__ import annotations

import asyncio

import capnp

from tests._generated.examples.fbp_nested_callback import fbp_nested_callback_capnp


class StatsCallback(fbp_nested_callback_capnp.Channel.StatsCallback.Server):
    async def status_context(self, context) -> None:
        _ = context.params.stats


class Channel(fbp_nested_callback_capnp.Channel.Server):
    async def registerStatsCallback_context(self, context) -> None:
        _ = context.params.updateIntervalInMs


async def main() -> None:
    channel = Channel()
    channel_client = fbp_nested_callback_capnp.Channel._new_client(channel)
    _ = channel_client.registerStatsCallback(StatsCallback(), 1000)


if __name__ == "__main__":
    asyncio.run(capnp.run(main()))
