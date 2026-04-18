"""Runtime placeholder module for module helper types of `calculator.capnp`."""

# pyright: reportUnusedClass=none

from __future__ import annotations

from capnp.lib.capnp import _InterfaceModule, _StructModule


class _CalculatorInterfaceModule(_InterfaceModule):
    class _ExpressionStructModule(_StructModule):
        pass

    class _ValueInterfaceModule(_InterfaceModule):
        pass

    class _FunctionInterfaceModule(_InterfaceModule):
        pass
