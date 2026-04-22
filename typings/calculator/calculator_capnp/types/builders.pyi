"""Builder helper types for `calculator.capnp`."""

from typing import Any, Literal, override

from capnp.lib.capnp import (
    _DynamicStructBuilder,
)

from . import clients as clients
from . import lists as lists
from . import modules as modules
from . import readers as readers

class ExpressionCallBuilder(_DynamicStructBuilder):
    @property
    def function(self) -> clients.FunctionClient: ...
    @function.setter
    def function(
        self,
        value: clients.FunctionClient | modules._CalculatorInterfaceModule._FunctionInterfaceModule.Server,
    ) -> None: ...
    @property
    def params(self) -> ExpressionListBuilder: ...
    @params.setter
    def params(self, value: ExpressionListBuilder | readers.ExpressionListReader | dict[str, Any]) -> None: ...
    @override
    def init(self, field: Literal["params"], size: int | None = None) -> ExpressionListBuilder: ...
    @override
    def as_reader(self) -> readers.ExpressionCallReader: ...

class ExpressionBuilder(_DynamicStructBuilder):
    @property
    def literal(self) -> float: ...
    @literal.setter
    def literal(self, value: float) -> None: ...
    @property
    def previousResult(self) -> clients.ValueClient: ...
    @previousResult.setter
    def previousResult(
        self,
        value: clients.ValueClient | modules._CalculatorInterfaceModule._ValueInterfaceModule.Server,
    ) -> None: ...
    @property
    def parameter(self) -> int: ...
    @parameter.setter
    def parameter(self, value: int) -> None: ...
    @property
    def call(self) -> ExpressionCallBuilder: ...
    @call.setter
    def call(self, value: ExpressionCallBuilder | readers.ExpressionCallReader | dict[str, Any]) -> None: ...
    @override
    def which(self) -> Literal["literal", "previousResult", "parameter", "call"]: ...
    @override
    def init(self, field: Literal["call"], size: int | None = None) -> ExpressionCallBuilder: ...
    @override
    def as_reader(self) -> readers.ExpressionReader: ...

type ExpressionListBuilder = lists._ExpressionList.Builder

type Float64ListBuilder = lists._Float64List.Builder
