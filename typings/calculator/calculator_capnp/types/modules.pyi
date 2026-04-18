"""Module helper types for `calculator.capnp`."""

from collections.abc import Awaitable, Callable
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityServer,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _EnumSchema,
    _InterfaceMethod,
    _InterfaceModule,
    _InterfaceSchema,
    _ListSchema,
    _StructModule,
    _StructSchema,
    _StructSchemaField,
)

from . import _all as _all

class _CalculatorInterfaceModule(_InterfaceModule):
    class _ValueInterfaceModule(_InterfaceModule):
        class _ValueSchema(_InterfaceSchema):
            class _ValueInterfaceModuleReadParamSchema(_StructSchema):
                class _Fields(dict[str, _StructSchemaField]): ...

                @property
                @override
                def fields(
                    self,
                ) -> _CalculatorInterfaceModule._ValueInterfaceModule._ValueSchema._ValueInterfaceModuleReadParamSchema._Fields: ...

            class _ValueInterfaceModuleReadResultSchema(_StructSchema):
                class _Fields(dict[str, _StructSchemaField]):
                    @overload
                    def __getitem__(self, key: Literal["value"]) -> _StructSchemaField: ...
                    @overload
                    def __getitem__(self, key: str) -> _StructSchemaField: ...

                @property
                @override
                def fields(
                    self,
                ) -> _CalculatorInterfaceModule._ValueInterfaceModule._ValueSchema._ValueInterfaceModuleReadResultSchema._Fields: ...

            class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["read"],
                ) -> _InterfaceMethod[
                    _CalculatorInterfaceModule._ValueInterfaceModule._ValueSchema._ValueInterfaceModuleReadParamSchema,
                    _CalculatorInterfaceModule._ValueInterfaceModule._ValueSchema._ValueInterfaceModuleReadResultSchema,
                ]: ...
                @overload
                def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

            @property
            @override
            def methods(self) -> _CalculatorInterfaceModule._ValueInterfaceModule._ValueSchema._Methods: ...

        @property
        @override
        def schema(self) -> _CalculatorInterfaceModule._ValueInterfaceModule._ValueSchema: ...
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
        class _FunctionSchema(_InterfaceSchema):
            class _FunctionInterfaceModuleCallParamSchema(_StructSchema):
                class _ParamsField(_StructSchemaField):
                    @property
                    @override
                    def schema(self) -> _ListSchema: ...

                class _Fields(dict[str, _StructSchemaField]):
                    @overload
                    def __getitem__(
                        self,
                        key: Literal["params"],
                    ) -> _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema._FunctionInterfaceModuleCallParamSchema._ParamsField: ...
                    @overload
                    def __getitem__(self, key: str) -> _StructSchemaField: ...

                @property
                @override
                def fields(
                    self,
                ) -> _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema._FunctionInterfaceModuleCallParamSchema._Fields: ...

            class _FunctionInterfaceModuleCallResultSchema(_StructSchema):
                class _Fields(dict[str, _StructSchemaField]):
                    @overload
                    def __getitem__(self, key: Literal["value"]) -> _StructSchemaField: ...
                    @overload
                    def __getitem__(self, key: str) -> _StructSchemaField: ...

                @property
                @override
                def fields(
                    self,
                ) -> _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema._FunctionInterfaceModuleCallResultSchema._Fields: ...

            class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["call"],
                ) -> _InterfaceMethod[
                    _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema._FunctionInterfaceModuleCallParamSchema,
                    _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema._FunctionInterfaceModuleCallResultSchema,
                ]: ...
                @overload
                def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

            @property
            @override
            def methods(self) -> _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema._Methods: ...

        @property
        @override
        def schema(self) -> _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema: ...
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

            class _ExpressionCallSchema(_StructSchema):
                class _FunctionField(_StructSchemaField):
                    @property
                    @override
                    def schema(self) -> _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema: ...

                class _ParamsField(_StructSchemaField):
                    class _Schema(_ListSchema):
                        @property
                        @override
                        def elementType(
                            self,
                        ) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionSchema: ...

                    @property
                    @override
                    def schema(
                        self,
                    ) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionCallStructModule._ExpressionCallSchema._ParamsField._Schema: ...

                class _Fields(dict[str, _StructSchemaField]):
                    @overload
                    def __getitem__(
                        self,
                        key: Literal["function"],
                    ) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionCallStructModule._ExpressionCallSchema._FunctionField: ...
                    @overload
                    def __getitem__(
                        self,
                        key: Literal["params"],
                    ) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionCallStructModule._ExpressionCallSchema._ParamsField: ...
                    @overload
                    def __getitem__(self, key: str) -> _StructSchemaField: ...

                @property
                @override
                def fields(
                    self,
                ) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionCallStructModule._ExpressionCallSchema._Fields: ...

            @property
            @override
            def schema(
                self,
            ) -> (
                _CalculatorInterfaceModule._ExpressionStructModule._ExpressionCallStructModule._ExpressionCallSchema
            ): ...
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

        class _ExpressionSchema(_StructSchema):
            class _PreviousResultField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _CalculatorInterfaceModule._ValueInterfaceModule._ValueSchema: ...

            class _CallField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _StructSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["literal"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(
                    self,
                    key: Literal["previousResult"],
                ) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionSchema._PreviousResultField: ...
                @overload
                def __getitem__(self, key: Literal["parameter"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(
                    self,
                    key: Literal["call"],
                ) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionSchema._CallField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(self) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionSchema._Fields: ...

        @property
        @override
        def schema(self) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionSchema: ...
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

    class _CalculatorSchema(_InterfaceSchema):
        class _CalculatorInterfaceModuleEvaluateParamSchema(_StructSchema):
            class _ExpressionField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["expression"],
                ) -> _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleEvaluateParamSchema._ExpressionField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleEvaluateParamSchema._Fields: ...

        class _CalculatorInterfaceModuleEvaluateResultSchema(_StructSchema):
            class _ValueField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _CalculatorInterfaceModule._ValueInterfaceModule._ValueSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["value"],
                ) -> _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleEvaluateResultSchema._ValueField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleEvaluateResultSchema._Fields
            ): ...

        class _CalculatorInterfaceModuleDefFunctionParamSchema(_StructSchema):
            class _BodyField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _CalculatorInterfaceModule._ExpressionStructModule._ExpressionSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["paramCount"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(
                    self,
                    key: Literal["body"],
                ) -> _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleDefFunctionParamSchema._BodyField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleDefFunctionParamSchema._Fields
            ): ...

        class _CalculatorInterfaceModuleDefFunctionResultSchema(_StructSchema):
            class _FuncField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["func"],
                ) -> _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleDefFunctionResultSchema._FuncField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleDefFunctionResultSchema._Fields
            ): ...

        class _CalculatorInterfaceModuleGetOperatorParamSchema(_StructSchema):
            class _OpField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _EnumSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["op"],
                ) -> _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleGetOperatorParamSchema._OpField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleGetOperatorParamSchema._Fields
            ): ...

        class _CalculatorInterfaceModuleGetOperatorResultSchema(_StructSchema):
            class _FuncField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["func"],
                ) -> _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleGetOperatorResultSchema._FuncField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleGetOperatorResultSchema._Fields
            ): ...

        class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
            @overload
            def __getitem__(
                self,
                key: Literal["evaluate"],
            ) -> _InterfaceMethod[
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleEvaluateParamSchema,
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleEvaluateResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["defFunction"],
            ) -> _InterfaceMethod[
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleDefFunctionParamSchema,
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleDefFunctionResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getOperator"],
            ) -> _InterfaceMethod[
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleGetOperatorParamSchema,
                _CalculatorInterfaceModule._CalculatorSchema._CalculatorInterfaceModuleGetOperatorResultSchema,
            ]: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

        @property
        @override
        def methods(self) -> _CalculatorInterfaceModule._CalculatorSchema._Methods: ...

    @property
    @override
    def schema(self) -> _CalculatorInterfaceModule._CalculatorSchema: ...
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
