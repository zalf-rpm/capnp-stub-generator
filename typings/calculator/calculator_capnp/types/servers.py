"""Runtime placeholder module for server helpers of `calculator.capnp`."""

from .. import Calculator

CalculatorServer = Calculator.Server
FunctionServer = Calculator.Function.Server
ValueServer = Calculator.Value.Server
