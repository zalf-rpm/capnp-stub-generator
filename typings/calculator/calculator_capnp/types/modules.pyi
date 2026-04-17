"""Module helper types for `calculator.capnp`."""

from collections.abc import Awaitable, Callable
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityServer,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _InterfaceModule,
    _StructModule,
)

from . import _all as _all

class _CalculatorInterfaceModule(_InterfaceModule):
    class _ValueInterfaceModule(_InterfaceModule):
        @override
        def _new_client(self, server: _DynamicCapabilityServer) -> _all.ValueClient: ...
        class Server(_DynamicCapabilityServer):
            def read(
                self,
                _context: _all.ReadCallContext,
                **kwargs: object,
            ) -> Awaitable[float | _all.ReadResultTuple | None]: ...
            def read_context(self, context: _all.ReadCallContext) -> Awaitable[None]: ...

    Value: _ValueInterfaceModule
    type ValueServer = _CalculatorInterfaceModule._ValueInterfaceModule.Server
    class _FunctionInterfaceModule(_InterfaceModule):
        @override
        def _new_client(self, server: _DynamicCapabilityServer) -> _all.FunctionClient: ...
        class Server(_DynamicCapabilityServer):
            def call(
                self,
                params: _all.Float64ListReader,
                _context: _all.CallCallContext,
                **kwargs: object,
            ) -> Awaitable[float | _all.CallResultTuple | None]: ...
            def call_context(self, context: _all.CallCallContext) -> Awaitable[None]: ...

    Function: _FunctionInterfaceModule
    type FunctionServer = _CalculatorInterfaceModule._FunctionInterfaceModule.Server
    class _ExpressionStructModule(_StructModule):
        class _ExpressionCallStructModule(_StructModule):
            class Reader(_DynamicStructReader): ...
            class Builder(_DynamicStructBuilder): ...

            @override
            def new_message(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
                function: _all.FunctionClient
                | _CalculatorInterfaceModule._FunctionInterfaceModule.Server
                | None = None,
                params: _all.ExpressionListBuilder | dict[str, Any] | None = None,
                **kwargs: object,
            ) -> _all.ExpressionCallBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[_all.ExpressionCallReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[_all.ExpressionCallReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[_all.ExpressionCallBuilder]: ...
            @override
            def from_bytes_packed(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> _DynamicStructReader: ...
            @override
            def read(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> _all.ExpressionCallReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> _all.ExpressionCallReader: ...

        ExpressionCall: _ExpressionCallStructModule
        class Reader(_DynamicStructReader): ...
        class Builder(_DynamicStructBuilder): ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            literal: float | None = None,
            previousResult: _all.ValueClient | _CalculatorInterfaceModule._ValueInterfaceModule.Server | None = None,
            parameter: int | None = None,
            call: _all.ExpressionCallBuilder | dict[str, Any] | None = None,
            **kwargs: object,
        ) -> _all.ExpressionBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[_all.ExpressionReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[_all.ExpressionReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[_all.ExpressionBuilder]: ...
        @override
        def from_bytes_packed(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _DynamicStructReader: ...
        @override
        def read(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _all.ExpressionReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _all.ExpressionReader: ...

    Expression: _ExpressionStructModule
    class _OperatorEnumModule:
        add: int
        subtract: int
        multiply: int
        divide: int

    Operator: _OperatorEnumModule
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> _all.CalculatorClient: ...
    class Server(_DynamicCapabilityServer):
        def evaluate(
            self,
            expression: _all.ExpressionReader,
            _context: _all.EvaluateCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _CalculatorInterfaceModule._ValueInterfaceModule.Server | _all.ValueClient | _all.EvaluateResultTuple | None
        ]: ...
        def evaluate_context(self, context: _all.EvaluateCallContext) -> Awaitable[None]: ...
        def defFunction(
            self,
            paramCount: int,
            body: _all.ExpressionReader,
            _context: _all.DeffunctionCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _CalculatorInterfaceModule._FunctionInterfaceModule.Server
            | _all.FunctionClient
            | _all.DeffunctionResultTuple
            | None
        ]: ...
        def defFunction_context(self, context: _all.DeffunctionCallContext) -> Awaitable[None]: ...
        def getOperator(
            self,
            op: _all.CalculatorOperatorEnum,
            _context: _all.GetoperatorCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _CalculatorInterfaceModule._FunctionInterfaceModule.Server
            | _all.FunctionClient
            | _all.GetoperatorResultTuple
            | None
        ]: ...
        def getOperator_context(self, context: _all.GetoperatorCallContext) -> Awaitable[None]: ...
