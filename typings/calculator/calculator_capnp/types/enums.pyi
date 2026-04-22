"""Enum helper aliases for `calculator.capnp`."""

from typing import Literal

type CalculatorOperatorEnum = int | Literal["add", "subtract", "multiply", "divide"]
