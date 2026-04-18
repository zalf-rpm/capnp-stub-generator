"""This is an automatically generated stub for `restorer.capnp`."""

from collections.abc import Awaitable, Callable
from contextlib import AbstractContextManager
from typing import IO, Literal, NamedTuple, Protocol, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityClient,
    _DynamicCapabilityServer,
    _DynamicListBuilder,
    _DynamicListReader,
    _DynamicObjectBuilder,
    _DynamicObjectReader,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _InterfaceMethod,
    _InterfaceModule,
    _InterfaceSchema,
    _StructModule,
    _StructSchema,
    _StructSchemaField,
)

# Type alias for AnyPointer parameters (accepts all Cap'n Proto pointer types)
type AnyPointer = (
    str
    | bytes
    | _DynamicStructBuilder
    | _DynamicStructReader
    | _DynamicCapabilityClient
    | _DynamicCapabilityServer
    | _DynamicListBuilder
    | _DynamicListReader
    | _DynamicObjectReader
    | _DynamicObjectBuilder
)

# Type alias for Capability parameters
type Capability = _DynamicCapabilityClient | _DynamicCapabilityServer | _DynamicObjectReader | _DynamicObjectBuilder

# Type alias for AnyStruct parameters
type AnyStruct = _DynamicStructBuilder | _DynamicStructReader | _DynamicObjectReader | _DynamicObjectBuilder

# Type alias for AnyList parameters
type AnyList = _DynamicListBuilder | _DynamicListReader | _DynamicObjectReader | _DynamicObjectBuilder

class _BagInterfaceModule(_InterfaceModule):
    class _BagSchema(_InterfaceSchema):
        class _BagInterfaceModuleGetValueParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(self) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleGetValueParamSchema._Fields: ...

        class _BagInterfaceModuleGetValueResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["value"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(self) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleGetValueResultSchema._Fields: ...

        class _BagInterfaceModuleSetValueParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["value"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(self) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleSetValueParamSchema._Fields: ...

        class _BagInterfaceModuleSetValueResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(self) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleSetValueResultSchema._Fields: ...

        class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
            @overload
            def __getitem__(
                self,
                key: Literal["getValue"],
            ) -> _InterfaceMethod[
                _BagInterfaceModule._BagSchema._BagInterfaceModuleGetValueParamSchema,
                _BagInterfaceModule._BagSchema._BagInterfaceModuleGetValueResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["setValue"],
            ) -> _InterfaceMethod[
                _BagInterfaceModule._BagSchema._BagInterfaceModuleSetValueParamSchema,
                _BagInterfaceModule._BagSchema._BagInterfaceModuleSetValueResultSchema,
            ]: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

        @property
        @override
        def methods(self) -> _BagInterfaceModule._BagSchema._Methods: ...

    @property
    @override
    def schema(self) -> _BagInterfaceModule._BagSchema: ...
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> BagClient: ...
    class Server(_DynamicCapabilityServer):
        def getValue(
            self,
            _context: GetvalueCallContext,
            **kwargs: object,
        ) -> Awaitable[str | GetvalueResultTuple | None]: ...
        def getValue_context(self, context: GetvalueCallContext) -> Awaitable[None]: ...
        def setValue(self, value: str, _context: SetvalueCallContext, **kwargs: object) -> Awaitable[None]: ...
        def setValue_context(self, context: SetvalueCallContext) -> Awaitable[None]: ...

class GetvalueRequest(Protocol):
    def send(self) -> GetvalueResult: ...

class GetvalueResult(Awaitable[GetvalueResult], Protocol):
    value: str

class GetvalueServerResult(_DynamicStructBuilder):
    @property
    def value(self) -> str: ...
    @value.setter
    def value(self, value: str) -> None: ...

class GetvalueParams(Protocol): ...

class GetvalueCallContext(Protocol):
    params: GetvalueParams
    @property
    def results(self) -> GetvalueServerResult: ...

class GetvalueResultTuple(NamedTuple):
    value: str

class SetvalueRequest(Protocol):
    value: str
    def send(self) -> SetvalueResult: ...

class SetvalueResult(Awaitable[None], Protocol): ...

class SetvalueParams(Protocol):
    value: str

class SetvalueCallContext(Protocol):
    params: SetvalueParams

class BagClient(_DynamicCapabilityClient):
    def getValue(self) -> GetvalueResult: ...
    def setValue(self, value: str | None = None) -> SetvalueResult: ...
    def getValue_request(self) -> GetvalueRequest: ...
    def setValue_request(self, value: str | None = None) -> SetvalueRequest: ...

Bag: _BagInterfaceModule

class _RestorerInterfaceModule(_InterfaceModule):
    class _RestoreParamsStructModule(_StructModule):
        class Reader(_DynamicStructReader): ...
        class Builder(_DynamicStructBuilder): ...

        class _RestoreParamsSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["localRef"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(self) -> _RestorerInterfaceModule._RestoreParamsStructModule._RestoreParamsSchema._Fields: ...

        @property
        @override
        def schema(self) -> _RestorerInterfaceModule._RestoreParamsStructModule._RestoreParamsSchema: ...
        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            localRef: str | None = None,
            **kwargs: object,
        ) -> RestoreParamsBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[RestoreParamsReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[RestoreParamsReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[RestoreParamsBuilder]: ...
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
        ) -> RestoreParamsReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> RestoreParamsReader: ...

    RestoreParams: _RestoreParamsStructModule

    class _RestorerSchema(_InterfaceSchema):
        class _RestorerInterfaceModuleRestoreParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["localRef"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleRestoreParamSchema._Fields: ...

        class _RestorerInterfaceModuleRestoreResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["cap"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleRestoreResultSchema._Fields: ...

        class _RestorerInterfaceModuleGetAnyTesterParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleGetAnyTesterParamSchema._Fields: ...

        class _RestorerInterfaceModuleGetAnyTesterResultSchema(_StructSchema):
            class _TesterField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _AnyTesterInterfaceModule._AnyTesterSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["tester"],
                ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleGetAnyTesterResultSchema._TesterField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleGetAnyTesterResultSchema._Fields: ...

        class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
            @overload
            def __getitem__(
                self,
                key: Literal["restore"],
            ) -> _InterfaceMethod[
                _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleRestoreParamSchema,
                _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleRestoreResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getAnyTester"],
            ) -> _InterfaceMethod[
                _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleGetAnyTesterParamSchema,
                _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleGetAnyTesterResultSchema,
            ]: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

        @property
        @override
        def methods(self) -> _RestorerInterfaceModule._RestorerSchema._Methods: ...

    @property
    @override
    def schema(self) -> _RestorerInterfaceModule._RestorerSchema: ...
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> RestorerClient: ...
    class Server(_DynamicCapabilityServer):
        def restore(
            self,
            localRef: str,
            _context: RestoreCallContext,
            **kwargs: object,
        ) -> Awaitable[Capability | RestoreResultTuple | None]: ...
        def restore_context(self, context: RestoreCallContext) -> Awaitable[None]: ...
        def getAnyTester(
            self,
            _context: GetanytesterCallContext,
            **kwargs: object,
        ) -> Awaitable[_AnyTesterInterfaceModule.Server | AnyTesterClient | GetanytesterResultTuple | None]: ...
        def getAnyTester_context(self, context: GetanytesterCallContext) -> Awaitable[None]: ...

class RestoreParamsReader(_DynamicStructReader):
    @property
    def localRef(self) -> str: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> RestoreParamsBuilder: ...

class RestoreParamsBuilder(_DynamicStructBuilder):
    @property
    def localRef(self) -> str: ...
    @localRef.setter
    def localRef(self, value: str) -> None: ...
    @override
    def as_reader(self) -> RestoreParamsReader: ...

class _AnyTesterInterfaceModule(_InterfaceModule):
    class _AnyTesterSchema(_InterfaceSchema):
        class _AnyTesterInterfaceModuleGetAnyStructParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyStructParamSchema._Fields
            ): ...

        class _AnyTesterInterfaceModuleGetAnyStructResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["s"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyStructResultSchema._Fields
            ): ...

        class _AnyTesterInterfaceModuleGetAnyListParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyListParamSchema._Fields: ...

        class _AnyTesterInterfaceModuleGetAnyListResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["l"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyListResultSchema._Fields: ...

        class _AnyTesterInterfaceModuleGetAnyPointerParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyPointerParamSchema._Fields
            ): ...

        class _AnyTesterInterfaceModuleGetAnyPointerResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["p"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyPointerResultSchema._Fields
            ): ...

        class _AnyTesterInterfaceModuleSetAnyPointerParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["p"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleSetAnyPointerParamSchema._Fields
            ): ...

        class _AnyTesterInterfaceModuleSetAnyPointerResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleSetAnyPointerResultSchema._Fields
            ): ...

        class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
            @overload
            def __getitem__(
                self,
                key: Literal["getAnyStruct"],
            ) -> _InterfaceMethod[
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyStructParamSchema,
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyStructResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getAnyList"],
            ) -> _InterfaceMethod[
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyListParamSchema,
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyListResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getAnyPointer"],
            ) -> _InterfaceMethod[
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyPointerParamSchema,
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyPointerResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["setAnyPointer"],
            ) -> _InterfaceMethod[
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleSetAnyPointerParamSchema,
                _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleSetAnyPointerResultSchema,
            ]: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

        @property
        @override
        def methods(self) -> _AnyTesterInterfaceModule._AnyTesterSchema._Methods: ...

    @property
    @override
    def schema(self) -> _AnyTesterInterfaceModule._AnyTesterSchema: ...
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> AnyTesterClient: ...
    class Server(_DynamicCapabilityServer):
        def getAnyStruct(
            self,
            _context: GetanystructCallContext,
            **kwargs: object,
        ) -> Awaitable[AnyStruct | GetanystructResultTuple | None]: ...
        def getAnyStruct_context(self, context: GetanystructCallContext) -> Awaitable[None]: ...
        def getAnyList(
            self,
            _context: GetanylistCallContext,
            **kwargs: object,
        ) -> Awaitable[AnyList | GetanylistResultTuple | None]: ...
        def getAnyList_context(self, context: GetanylistCallContext) -> Awaitable[None]: ...
        def getAnyPointer(
            self,
            _context: GetanypointerCallContext,
            **kwargs: object,
        ) -> Awaitable[AnyPointer | GetanypointerResultTuple | None]: ...
        def getAnyPointer_context(self, context: GetanypointerCallContext) -> Awaitable[None]: ...
        def setAnyPointer(
            self,
            p: AnyPointer,
            _context: SetanypointerCallContext,
            **kwargs: object,
        ) -> Awaitable[None]: ...
        def setAnyPointer_context(self, context: SetanypointerCallContext) -> Awaitable[None]: ...

class GetanystructRequest(Protocol):
    def send(self) -> GetanystructResult: ...

class GetanystructResult(Awaitable[GetanystructResult], Protocol):
    s: _DynamicObjectReader

class GetanystructServerResult(_DynamicStructBuilder):
    @property
    def s(self) -> AnyStruct: ...
    @s.setter
    def s(self, value: AnyStruct) -> None: ...

class GetanystructParams(Protocol): ...

class GetanystructCallContext(Protocol):
    params: GetanystructParams
    @property
    def results(self) -> GetanystructServerResult: ...

class GetanystructResultTuple(NamedTuple):
    s: AnyStruct

class GetanylistRequest(Protocol):
    def send(self) -> GetanylistResult: ...

class GetanylistResult(Awaitable[GetanylistResult], Protocol):
    l: _DynamicObjectReader

class GetanylistServerResult(_DynamicStructBuilder):
    @property
    def l(self) -> AnyList: ...
    @l.setter
    def l(self, value: AnyList) -> None: ...

class GetanylistParams(Protocol): ...

class GetanylistCallContext(Protocol):
    params: GetanylistParams
    @property
    def results(self) -> GetanylistServerResult: ...

class GetanylistResultTuple(NamedTuple):
    l: AnyList

class GetanypointerRequest(Protocol):
    def send(self) -> GetanypointerResult: ...

class GetanypointerResult(Awaitable[GetanypointerResult], Protocol):
    p: _DynamicObjectReader

class GetanypointerServerResult(_DynamicStructBuilder):
    @property
    def p(self) -> AnyPointer: ...
    @p.setter
    def p(self, value: AnyPointer) -> None: ...

class GetanypointerParams(Protocol): ...

class GetanypointerCallContext(Protocol):
    params: GetanypointerParams
    @property
    def results(self) -> GetanypointerServerResult: ...

class GetanypointerResultTuple(NamedTuple):
    p: AnyPointer

class SetanypointerRequest(Protocol):
    p: AnyPointer
    def send(self) -> SetanypointerResult: ...

class SetanypointerResult(Awaitable[None], Protocol): ...

class SetanypointerParams(Protocol):
    p: AnyPointer

class SetanypointerCallContext(Protocol):
    params: SetanypointerParams

class AnyTesterClient(_DynamicCapabilityClient):
    def getAnyStruct(self) -> GetanystructResult: ...
    def getAnyList(self) -> GetanylistResult: ...
    def getAnyPointer(self) -> GetanypointerResult: ...
    def setAnyPointer(self, p: AnyPointer | None = None) -> SetanypointerResult: ...
    def getAnyStruct_request(self) -> GetanystructRequest: ...
    def getAnyList_request(self) -> GetanylistRequest: ...
    def getAnyPointer_request(self) -> GetanypointerRequest: ...
    def setAnyPointer_request(self, p: AnyPointer | None = None) -> SetanypointerRequest: ...

AnyTester: _AnyTesterInterfaceModule

class RestoreRequest(Protocol):
    localRef: str
    def send(self) -> RestoreResult: ...

class RestoreResult(Awaitable[RestoreResult], Protocol):
    cap: _DynamicObjectReader

class RestoreServerResult(_DynamicStructBuilder):
    @property
    def cap(self) -> Capability: ...
    @cap.setter
    def cap(self, value: Capability) -> None: ...

class RestoreCallContext(Protocol):
    params: RestoreParamsReader
    @property
    def results(self) -> RestoreServerResult: ...

class RestoreResultTuple(NamedTuple):
    cap: Capability

class GetanytesterRequest(Protocol):
    def send(self) -> GetanytesterResult: ...

class GetanytesterResult(Awaitable[GetanytesterResult], Protocol):
    tester: AnyTesterClient

class GetanytesterServerResult(_DynamicStructBuilder):
    @property
    def tester(self) -> _AnyTesterInterfaceModule.Server | AnyTesterClient: ...
    @tester.setter
    def tester(self, value: _AnyTesterInterfaceModule.Server | AnyTesterClient) -> None: ...

class GetanytesterParams(Protocol): ...

class GetanytesterCallContext(Protocol):
    params: GetanytesterParams
    @property
    def results(self) -> GetanytesterServerResult: ...

class GetanytesterResultTuple(NamedTuple):
    tester: _AnyTesterInterfaceModule.Server | AnyTesterClient

class RestorerClient(_DynamicCapabilityClient):
    def restore(self, localRef: str | None = None) -> RestoreResult: ...
    def getAnyTester(self) -> GetanytesterResult: ...
    def restore_request(self, localRef: str | None = None) -> RestoreRequest: ...
    def getAnyTester_request(self) -> GetanytesterRequest: ...

Restorer: _RestorerInterfaceModule

# Top-level type aliases for use in type annotations
AnyTesterServer = _AnyTesterInterfaceModule.Server
BagServer = _BagInterfaceModule.Server
RestorerServer = _RestorerInterfaceModule.Server
