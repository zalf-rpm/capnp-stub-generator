"""Runtime placeholder module for server helpers of `calculator.capnp`."""

# pyright: reportUnusedClass=none

from .. import Calculator

CalculatorServer = Calculator.Server
FunctionServer = Calculator.Function.Server
ValueServer = Calculator.Value.Server
