"""Module helper types for `restorer.capnp`."""

from collections.abc import Awaitable, Callable
from contextlib import AbstractContextManager
from typing import IO, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityServer,
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

from . import builders as builders
from . import clients as clients
from . import common as common
from . import contexts as contexts
from . import readers as readers
from . import schemas as schemas
from .results import tuples as results_tuples

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

        class _BagInterfaceModuleGetValueMethod(_InterfaceMethod):
            @property
            @override
            def param_type(self) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleGetValueParamSchema: ...
            @property
            @override
            def result_type(self) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleGetValueResultSchema: ...

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

        class _BagInterfaceModuleSetValueMethod(_InterfaceMethod):
            @property
            @override
            def param_type(self) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleSetValueParamSchema: ...
            @property
            @override
            def result_type(self) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleSetValueResultSchema: ...

        class _Methods(dict[str, _InterfaceMethod]):
            @overload
            def __getitem__(
                self,
                key: Literal["getValue"],
            ) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleGetValueMethod: ...
            @overload
            def __getitem__(
                self,
                key: Literal["setValue"],
            ) -> _BagInterfaceModule._BagSchema._BagInterfaceModuleSetValueMethod: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod: ...

        @property
        @override
        def methods(self) -> _BagInterfaceModule._BagSchema._Methods: ...

    @property
    @override
    def schema(self) -> schemas._BagSchema: ...
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> clients.BagClient: ...
    class Server(_DynamicCapabilityServer):
        def getValue(
            self,
            _context: contexts.GetvalueCallContext,
            **kwargs: object,
        ) -> Awaitable[str | results_tuples.GetvalueResultTuple | None]: ...
        def getValue_context(self, context: contexts.GetvalueCallContext) -> Awaitable[None]: ...
        def setValue(self, value: str, _context: contexts.SetvalueCallContext, **kwargs: object) -> Awaitable[None]: ...
        def setValue_context(self, context: contexts.SetvalueCallContext) -> Awaitable[None]: ...

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
        def schema(self) -> schemas._RestorerRestoreParamsSchema: ...
        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            localRef: str | None = None,
            **kwargs: object,
        ) -> builders.RestoreParamsBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[readers.RestoreParamsReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[readers.RestoreParamsReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[builders.RestoreParamsBuilder]: ...
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
        ) -> readers.RestoreParamsReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> readers.RestoreParamsReader: ...

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

        class _RestorerInterfaceModuleRestoreMethod(_InterfaceMethod):
            @property
            @override
            def param_type(
                self,
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleRestoreParamSchema: ...
            @property
            @override
            def result_type(
                self,
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleRestoreResultSchema: ...

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
                def schema(self) -> schemas._AnyTesterSchema: ...

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

        class _RestorerInterfaceModuleGetAnyTesterMethod(_InterfaceMethod):
            @property
            @override
            def param_type(
                self,
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleGetAnyTesterParamSchema: ...
            @property
            @override
            def result_type(
                self,
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleGetAnyTesterResultSchema: ...

        class _Methods(dict[str, _InterfaceMethod]):
            @overload
            def __getitem__(
                self,
                key: Literal["restore"],
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleRestoreMethod: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getAnyTester"],
            ) -> _RestorerInterfaceModule._RestorerSchema._RestorerInterfaceModuleGetAnyTesterMethod: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod: ...

        @property
        @override
        def methods(self) -> _RestorerInterfaceModule._RestorerSchema._Methods: ...

    @property
    @override
    def schema(self) -> schemas._RestorerSchema: ...
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> clients.RestorerClient: ...
    class Server(_DynamicCapabilityServer):
        def restore(
            self,
            localRef: str,
            _context: contexts.RestoreCallContext,
            **kwargs: object,
        ) -> Awaitable[common.Capability | results_tuples.RestoreResultTuple | None]: ...
        def restore_context(self, context: contexts.RestoreCallContext) -> Awaitable[None]: ...
        def getAnyTester(
            self,
            _context: contexts.GetanytesterCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _AnyTesterInterfaceModule.Server | clients.AnyTesterClient | results_tuples.GetanytesterResultTuple | None
        ]: ...
        def getAnyTester_context(self, context: contexts.GetanytesterCallContext) -> Awaitable[None]: ...

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

        class _AnyTesterInterfaceModuleGetAnyStructMethod(_InterfaceMethod):
            @property
            @override
            def param_type(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyStructParamSchema: ...
            @property
            @override
            def result_type(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyStructResultSchema: ...

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

        class _AnyTesterInterfaceModuleGetAnyListMethod(_InterfaceMethod):
            @property
            @override
            def param_type(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyListParamSchema: ...
            @property
            @override
            def result_type(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyListResultSchema: ...

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

        class _AnyTesterInterfaceModuleGetAnyPointerMethod(_InterfaceMethod):
            @property
            @override
            def param_type(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyPointerParamSchema: ...
            @property
            @override
            def result_type(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyPointerResultSchema: ...

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

        class _AnyTesterInterfaceModuleSetAnyPointerMethod(_InterfaceMethod):
            @property
            @override
            def param_type(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleSetAnyPointerParamSchema: ...
            @property
            @override
            def result_type(
                self,
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleSetAnyPointerResultSchema: ...

        class _Methods(dict[str, _InterfaceMethod]):
            @overload
            def __getitem__(
                self,
                key: Literal["getAnyStruct"],
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyStructMethod: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getAnyList"],
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyListMethod: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getAnyPointer"],
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleGetAnyPointerMethod: ...
            @overload
            def __getitem__(
                self,
                key: Literal["setAnyPointer"],
            ) -> _AnyTesterInterfaceModule._AnyTesterSchema._AnyTesterInterfaceModuleSetAnyPointerMethod: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod: ...

        @property
        @override
        def methods(self) -> _AnyTesterInterfaceModule._AnyTesterSchema._Methods: ...

    @property
    @override
    def schema(self) -> schemas._AnyTesterSchema: ...
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> clients.AnyTesterClient: ...
    class Server(_DynamicCapabilityServer):
        def getAnyStruct(
            self,
            _context: contexts.GetanystructCallContext,
            **kwargs: object,
        ) -> Awaitable[common.AnyStruct | results_tuples.GetanystructResultTuple | None]: ...
        def getAnyStruct_context(self, context: contexts.GetanystructCallContext) -> Awaitable[None]: ...
        def getAnyList(
            self,
            _context: contexts.GetanylistCallContext,
            **kwargs: object,
        ) -> Awaitable[common.AnyList | results_tuples.GetanylistResultTuple | None]: ...
        def getAnyList_context(self, context: contexts.GetanylistCallContext) -> Awaitable[None]: ...
        def getAnyPointer(
            self,
            _context: contexts.GetanypointerCallContext,
            **kwargs: object,
        ) -> Awaitable[common.AnyPointer | results_tuples.GetanypointerResultTuple | None]: ...
        def getAnyPointer_context(self, context: contexts.GetanypointerCallContext) -> Awaitable[None]: ...
        def setAnyPointer(
            self,
            p: _DynamicObjectReader,
            _context: contexts.SetanypointerCallContext,
            **kwargs: object,
        ) -> Awaitable[None]: ...
        def setAnyPointer_context(self, context: contexts.SetanypointerCallContext) -> Awaitable[None]: ...
