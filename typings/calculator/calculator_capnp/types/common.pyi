"""Common typing aliases for `calculator.capnp`."""

from typing import Literal, override

from capnp.lib.capnp import _DynamicEnumField, _StructModuleWhich

class _ExpressionModuleWhich(_StructModuleWhich):
    Literal: _ExpressionModuleWhich
    PreviousResult: _ExpressionModuleWhich
    Parameter: _ExpressionModuleWhich
    Call: _ExpressionModuleWhich

class _ExpressionWhich(_DynamicEnumField):
    @override
    def __call__(self) -> Literal["literal", "previousResult", "parameter", "call"]: ...
