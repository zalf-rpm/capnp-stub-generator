"""Server helper types for `calculator.capnp`."""

from . import modules as modules

CalculatorServer = modules._CalculatorInterfaceModule.Server

FunctionServer = modules._CalculatorInterfaceModule._FunctionInterfaceModule.Server

ValueServer = modules._CalculatorInterfaceModule._ValueInterfaceModule.Server
