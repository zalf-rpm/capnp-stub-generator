"""Client helper types for `calculator.capnp`."""

from collections.abc import Sequence
from typing import Any

from capnp.lib.capnp import (
    _DynamicCapabilityClient,
)

from . import builders as builders
from . import enums as enums
from . import readers as readers
from . import requests as requests
from .results import client as results_client

class ValueClient(_DynamicCapabilityClient):
    def read(self) -> results_client.ReadResult: ...
    def read_request(self) -> requests.ReadRequest: ...

class FunctionClient(_DynamicCapabilityClient):
    def call(
        self,
        params: builders.Float64ListBuilder | readers.Float64ListReader | Sequence[float] | None = None,
    ) -> results_client.CallResult: ...
    def call_request(
        self,
        params: builders.Float64ListBuilder | readers.Float64ListReader | Sequence[float] | None = None,
    ) -> requests.CallRequest: ...

class CalculatorClient(_DynamicCapabilityClient):
    def evaluate(
        self,
        expression: builders.ExpressionBuilder | readers.ExpressionReader | dict[str, Any] | None = None,
    ) -> results_client.EvaluateResult: ...
    def defFunction(
        self,
        paramCount: int | None = None,
        body: builders.ExpressionBuilder | readers.ExpressionReader | dict[str, Any] | None = None,
    ) -> results_client.DeffunctionResult: ...
    def getOperator(self, op: enums.CalculatorOperatorEnum | None = None) -> results_client.GetoperatorResult: ...
    def evaluate_request(self, expression: builders.ExpressionBuilder | None = None) -> requests.EvaluateRequest: ...
    def defFunction_request(
        self,
        paramCount: int | None = None,
        body: builders.ExpressionBuilder | None = None,
    ) -> requests.DeffunctionRequest: ...
    def getOperator_request(self, op: enums.CalculatorOperatorEnum | None = None) -> requests.GetoperatorRequest: ...
