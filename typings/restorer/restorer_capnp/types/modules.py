"""Runtime placeholder module for module helper types of `restorer.capnp`."""

# pyright: reportUnusedClass=none

from __future__ import annotations

from capnp.lib.capnp import _InterfaceModule, _StructModule


class _BagInterfaceModule(_InterfaceModule):
    pass


class _RestorerInterfaceModule(_InterfaceModule):
    class _RestoreParamsStructModule(_StructModule):
        pass


class _AnyTesterInterfaceModule(_InterfaceModule):
    pass
