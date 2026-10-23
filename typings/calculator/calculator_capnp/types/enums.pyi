"""Enum helper aliases for `calculator.capnp`."""

from typing import Literal, override

from capnp.lib.capnp import _DynamicEnum

class CalculatorOperatorValue(_DynamicEnum):
    @override
    def __str__(self) -> Literal["add", "subtract", "multiply", "divide"]: ...

type CalculatorOperatorEnum = int | Literal["add", "subtract", "multiply", "divide"]
