"""This is an automatically generated stub for `calculator.capnp`."""

from collections.abc import Awaitable, Callable, Iterator, Sequence
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, NamedTuple, Protocol, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityClient,
    _DynamicCapabilityServer,
    _DynamicListBuilder,
    _DynamicListReader,
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
        def _new_client(self, server: _DynamicCapabilityServer) -> ValueClient: ...
        class Server(_DynamicCapabilityServer):
            def read(
                self,
                _context: ReadCallContext,
                **kwargs: object,
            ) -> Awaitable[float | ReadResultTuple | None]: ...
            def read_context(self, context: ReadCallContext) -> Awaitable[None]: ...

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
        def _new_client(self, server: _DynamicCapabilityServer) -> FunctionClient: ...
        class Server(_DynamicCapabilityServer):
            def call(
                self,
                params: Float64ListReader,
                _context: CallCallContext,
                **kwargs: object,
            ) -> Awaitable[float | CallResultTuple | None]: ...
            def call_context(self, context: CallCallContext) -> Awaitable[None]: ...

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
                function: FunctionClient | _CalculatorInterfaceModule._FunctionInterfaceModule.Server | None = None,
                params: ExpressionListBuilder | dict[str, Any] | None = None,
                **kwargs: object,
            ) -> ExpressionCallBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[ExpressionCallReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[ExpressionCallReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[ExpressionCallBuilder]: ...
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
            ) -> ExpressionCallReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> ExpressionCallReader: ...

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
            previousResult: ValueClient | _CalculatorInterfaceModule._ValueInterfaceModule.Server | None = None,
            parameter: int | None = None,
            call: ExpressionCallBuilder | dict[str, Any] | None = None,
            **kwargs: object,
        ) -> ExpressionBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[ExpressionReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[ExpressionReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[ExpressionBuilder]: ...
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
        ) -> ExpressionReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> ExpressionReader: ...

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
    def _new_client(self, server: _DynamicCapabilityServer) -> CalculatorClient: ...
    class Server(_DynamicCapabilityServer):
        def evaluate(
            self,
            expression: ExpressionReader,
            _context: EvaluateCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _CalculatorInterfaceModule._ValueInterfaceModule.Server | ValueClient | EvaluateResultTuple | None
        ]: ...
        def evaluate_context(self, context: EvaluateCallContext) -> Awaitable[None]: ...
        def defFunction(
            self,
            paramCount: int,
            body: ExpressionReader,
            _context: DeffunctionCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _CalculatorInterfaceModule._FunctionInterfaceModule.Server | FunctionClient | DeffunctionResultTuple | None
        ]: ...
        def defFunction_context(self, context: DeffunctionCallContext) -> Awaitable[None]: ...
        def getOperator(
            self,
            op: CalculatorOperatorEnum,
            _context: GetoperatorCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _CalculatorInterfaceModule._FunctionInterfaceModule.Server | FunctionClient | GetoperatorResultTuple | None
        ]: ...
        def getOperator_context(self, context: GetoperatorCallContext) -> Awaitable[None]: ...

class ReadRequest(Protocol):
    def send(self) -> ReadResult: ...

class ReadResult(Awaitable[ReadResult], Protocol):
    value: float

class ReadServerResult(_DynamicStructBuilder):
    @property
    def value(self) -> float: ...
    @value.setter
    def value(self, value: float) -> None: ...

class ReadParams(Protocol): ...

class ReadCallContext(Protocol):
    params: ReadParams
    @property
    def results(self) -> ReadServerResult: ...

class ReadResultTuple(NamedTuple):
    value: float

class ValueClient(_DynamicCapabilityClient):
    def read(self) -> ReadResult: ...
    def read_request(self) -> ReadRequest: ...

class _Float64List:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> float: ...
        @override
        def __iter__(self) -> Iterator[float]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> float: ...
        @override
        def __setitem__(self, key: int, value: float) -> None: ...
        @override
        def __iter__(self) -> Iterator[float]: ...

class CallRequest(Protocol):
    params: Float64ListBuilder | Float64ListReader | Sequence[Any]
    @overload
    def init(self, name: Literal["params"], size: int = ...) -> Float64ListBuilder: ...
    @overload
    def init(self, name: str, size: int = ...) -> Any: ...
    def send(self) -> CallResult: ...

class CallResult(Awaitable[CallResult], Protocol):
    value: float

class CallServerResult(_DynamicStructBuilder):
    @property
    def value(self) -> float: ...
    @value.setter
    def value(self, value: float) -> None: ...

class CallParams(Protocol):
    params: Float64ListReader

class CallCallContext(Protocol):
    params: CallParams
    @property
    def results(self) -> CallServerResult: ...

class CallResultTuple(NamedTuple):
    value: float

class FunctionClient(_DynamicCapabilityClient):
    def call(self, params: Float64ListBuilder | Float64ListReader | Sequence[Any] | None = None) -> CallResult: ...
    def call_request(
        self,
        params: Float64ListBuilder | Float64ListReader | Sequence[Any] | None = None,
    ) -> CallRequest: ...

class _ExpressionList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> ExpressionReader: ...
        @override
        def __iter__(self) -> Iterator[ExpressionReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> ExpressionBuilder: ...
        @override
        def __setitem__(self, key: int, value: ExpressionReader | ExpressionBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[ExpressionBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> ExpressionBuilder: ...

class ExpressionCallReader(_DynamicStructReader):
    @property
    def function(self) -> FunctionClient: ...
    @property
    def params(self) -> ExpressionListReader: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> ExpressionCallBuilder: ...

class ExpressionCallBuilder(_DynamicStructBuilder):
    @property
    def function(self) -> FunctionClient: ...
    @function.setter
    def function(self, value: FunctionClient | _CalculatorInterfaceModule._FunctionInterfaceModule.Server) -> None: ...
    @property
    def params(self) -> ExpressionListBuilder: ...
    @params.setter
    def params(self, value: ExpressionListBuilder | ExpressionListReader | dict[str, Any]) -> None: ...
    @override
    def init(self, field: Literal["params"], size: int | None = None) -> ExpressionListBuilder: ...
    @override
    def as_reader(self) -> ExpressionCallReader: ...

class ExpressionReader(_DynamicStructReader):
    @property
    def literal(self) -> float: ...
    @property
    def previousResult(self) -> ValueClient: ...
    @property
    def parameter(self) -> int: ...
    @property
    def call(self) -> ExpressionCallReader: ...
    @override
    def which(self) -> Literal["literal", "previousResult", "parameter", "call"]: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> ExpressionBuilder: ...

class ExpressionBuilder(_DynamicStructBuilder):
    @property
    def literal(self) -> float: ...
    @literal.setter
    def literal(self, value: float) -> None: ...
    @property
    def previousResult(self) -> ValueClient: ...
    @previousResult.setter
    def previousResult(self, value: ValueClient | _CalculatorInterfaceModule._ValueInterfaceModule.Server) -> None: ...
    @property
    def parameter(self) -> int: ...
    @parameter.setter
    def parameter(self, value: int) -> None: ...
    @property
    def call(self) -> ExpressionCallBuilder: ...
    @call.setter
    def call(self, value: ExpressionCallBuilder | ExpressionCallReader | dict[str, Any]) -> None: ...
    @override
    def which(self) -> Literal["literal", "previousResult", "parameter", "call"]: ...
    @override
    def init(self, field: Literal["call"], size: int | None = None) -> ExpressionCallBuilder: ...
    @override
    def as_reader(self) -> ExpressionReader: ...

class EvaluateRequest(Protocol):
    expression: ExpressionBuilder
    @overload
    def init(self, name: Literal["expression"]) -> ExpressionBuilder: ...
    @overload
    def init(self, name: str, size: int = ...) -> Any: ...
    def send(self) -> EvaluateResult: ...

class EvaluateResult(Awaitable[EvaluateResult], Protocol):
    value: ValueClient

class EvaluateServerResult(_DynamicStructBuilder):
    @property
    def value(self) -> _CalculatorInterfaceModule._ValueInterfaceModule.Server | ValueClient: ...
    @value.setter
    def value(self, value: _CalculatorInterfaceModule._ValueInterfaceModule.Server | ValueClient) -> None: ...

class EvaluateParams(Protocol):
    expression: ExpressionReader

class EvaluateCallContext(Protocol):
    params: EvaluateParams
    @property
    def results(self) -> EvaluateServerResult: ...

class EvaluateResultTuple(NamedTuple):
    value: _CalculatorInterfaceModule._ValueInterfaceModule.Server | ValueClient

class DeffunctionRequest(Protocol):
    paramCount: int
    body: ExpressionBuilder
    @overload
    def init(self, name: Literal["body"]) -> ExpressionBuilder: ...
    @overload
    def init(self, name: str, size: int = ...) -> Any: ...
    def send(self) -> DeffunctionResult: ...

class DeffunctionResult(Awaitable[DeffunctionResult], Protocol):
    func: FunctionClient

class DeffunctionServerResult(_DynamicStructBuilder):
    @property
    def func(self) -> _CalculatorInterfaceModule._FunctionInterfaceModule.Server | FunctionClient: ...
    @func.setter
    def func(self, value: _CalculatorInterfaceModule._FunctionInterfaceModule.Server | FunctionClient) -> None: ...

class DeffunctionParams(Protocol):
    paramCount: int
    body: ExpressionReader

class DeffunctionCallContext(Protocol):
    params: DeffunctionParams
    @property
    def results(self) -> DeffunctionServerResult: ...

class DeffunctionResultTuple(NamedTuple):
    func: _CalculatorInterfaceModule._FunctionInterfaceModule.Server | FunctionClient

class GetoperatorRequest(Protocol):
    op: CalculatorOperatorEnum
    def send(self) -> GetoperatorResult: ...

class GetoperatorResult(Awaitable[GetoperatorResult], Protocol):
    func: FunctionClient

class GetoperatorServerResult(_DynamicStructBuilder):
    @property
    def func(self) -> _CalculatorInterfaceModule._FunctionInterfaceModule.Server | FunctionClient: ...
    @func.setter
    def func(self, value: _CalculatorInterfaceModule._FunctionInterfaceModule.Server | FunctionClient) -> None: ...

class GetoperatorParams(Protocol):
    op: CalculatorOperatorEnum

class GetoperatorCallContext(Protocol):
    params: GetoperatorParams
    @property
    def results(self) -> GetoperatorServerResult: ...

class GetoperatorResultTuple(NamedTuple):
    func: _CalculatorInterfaceModule._FunctionInterfaceModule.Server | FunctionClient

class CalculatorClient(_DynamicCapabilityClient):
    def evaluate(
        self,
        expression: ExpressionBuilder | ExpressionReader | dict[str, Any] | None = None,
    ) -> EvaluateResult: ...
    def defFunction(
        self,
        paramCount: int | None = None,
        body: ExpressionBuilder | ExpressionReader | dict[str, Any] | None = None,
    ) -> DeffunctionResult: ...
    def getOperator(self, op: CalculatorOperatorEnum | None = None) -> GetoperatorResult: ...
    def evaluate_request(self, expression: ExpressionBuilder | None = None) -> EvaluateRequest: ...
    def defFunction_request(
        self,
        paramCount: int | None = None,
        body: ExpressionBuilder | None = None,
    ) -> DeffunctionRequest: ...
    def getOperator_request(self, op: CalculatorOperatorEnum | None = None) -> GetoperatorRequest: ...

Calculator: _CalculatorInterfaceModule

# Top-level type aliases for use in type annotations
type CalculatorOperatorEnum = int | Literal["add", "subtract", "multiply", "divide"]
CalculatorServer = _CalculatorInterfaceModule.Server
type ExpressionListBuilder = _ExpressionList.Builder
type ExpressionListReader = _ExpressionList.Reader
type Float64ListBuilder = _Float64List.Builder
type Float64ListReader = _Float64List.Reader
FunctionServer = _CalculatorInterfaceModule._FunctionInterfaceModule.Server
ValueServer = _CalculatorInterfaceModule._ValueInterfaceModule.Server
