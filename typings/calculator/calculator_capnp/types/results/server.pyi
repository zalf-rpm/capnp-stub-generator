"""Server result helper types for `calculator.capnp`."""

from capnp.lib.capnp import (
    _DynamicStructBuilder,
)

from .. import clients as clients
from .. import modules as modules

class ReadServerResult(_DynamicStructBuilder):
    @property
    def value(self) -> float: ...
    @value.setter
    def value(self, value: float) -> None: ...

class CallServerResult(_DynamicStructBuilder):
    @property
    def value(self) -> float: ...
    @value.setter
    def value(self, value: float) -> None: ...

class EvaluateServerResult(_DynamicStructBuilder):
    @property
    def value(self) -> modules._CalculatorInterfaceModule._ValueInterfaceModule.Server | clients.ValueClient: ...
    @value.setter
    def value(
        self,
        value: modules._CalculatorInterfaceModule._ValueInterfaceModule.Server | clients.ValueClient,
    ) -> None: ...

class DeffunctionServerResult(_DynamicStructBuilder):
    @property
    def func(self) -> modules._CalculatorInterfaceModule._FunctionInterfaceModule.Server | clients.FunctionClient: ...
    @func.setter
    def func(
        self,
        value: modules._CalculatorInterfaceModule._FunctionInterfaceModule.Server | clients.FunctionClient,
    ) -> None: ...

class GetoperatorServerResult(_DynamicStructBuilder):
    @property
    def func(self) -> modules._CalculatorInterfaceModule._FunctionInterfaceModule.Server | clients.FunctionClient: ...
    @func.setter
    def func(
        self,
        value: modules._CalculatorInterfaceModule._FunctionInterfaceModule.Server | clients.FunctionClient,
    ) -> None: ...
