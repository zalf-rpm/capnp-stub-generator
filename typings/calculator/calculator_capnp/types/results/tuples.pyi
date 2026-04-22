"""Result tuple helper types for `calculator.capnp`."""

from typing import NamedTuple

from .. import clients as clients
from .. import modules as modules

class ReadResultTuple(NamedTuple):
    value: float

class CallResultTuple(NamedTuple):
    value: float

class EvaluateResultTuple(NamedTuple):
    value: modules._CalculatorInterfaceModule._ValueInterfaceModule.Server | clients.ValueClient

class DeffunctionResultTuple(NamedTuple):
    func: modules._CalculatorInterfaceModule._FunctionInterfaceModule.Server | clients.FunctionClient

class GetoperatorResultTuple(NamedTuple):
    func: modules._CalculatorInterfaceModule._FunctionInterfaceModule.Server | clients.FunctionClient
