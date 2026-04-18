"""Runtime placeholder module for module helper types of `fbp_nested_callback.capnp`."""

# pyright: reportUnusedClass=none

from __future__ import annotations

from capnp.lib.capnp import _InterfaceModule, _StructModule


class _ChannelInterfaceModule(_InterfaceModule):
    class _StatsCallbackInterfaceModule(_InterfaceModule):
        class _StatsStructModule(_StructModule):
            pass

        class _UnregisterInterfaceModule(_InterfaceModule):
            pass
