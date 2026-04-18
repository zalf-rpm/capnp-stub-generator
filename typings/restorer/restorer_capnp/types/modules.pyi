"""Module helper types for `restorer.capnp`."""

from collections.abc import Awaitable, Callable
from contextlib import AbstractContextManager
from typing import IO, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityServer,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _InterfaceMethod,
    _InterfaceModule,
    _InterfaceSchema,
    _StructModule,
    _StructSchema,
    _StructSchemaField,
)

from . import _all as _all

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
    def _new_client(self, server: _DynamicCapabilityServer) -> _all.BagClient: ...
    class Server(_DynamicCapabilityServer):
        def getValue(
            self,
            _context: _all.GetvalueCallContext,
            **kwargs: object,
        ) -> Awaitable[str | _all.GetvalueResultTuple | None]: ...
        def getValue_context(self, context: _all.GetvalueCallContext) -> Awaitable[None]: ...
        def setValue(self, value: str, _context: _all.SetvalueCallContext, **kwargs: object) -> Awaitable[None]: ...
        def setValue_context(self, context: _all.SetvalueCallContext) -> Awaitable[None]: ...

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
        ) -> _all.RestoreParamsBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[_all.RestoreParamsReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[_all.RestoreParamsReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[_all.RestoreParamsBuilder]: ...
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
        ) -> _all.RestoreParamsReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _all.RestoreParamsReader: ...

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
    def _new_client(self, server: _DynamicCapabilityServer) -> _all.RestorerClient: ...
    class Server(_DynamicCapabilityServer):
        def restore(
            self,
            localRef: str,
            _context: _all.RestoreCallContext,
            **kwargs: object,
        ) -> Awaitable[_all.Capability | _all.RestoreResultTuple | None]: ...
        def restore_context(self, context: _all.RestoreCallContext) -> Awaitable[None]: ...
        def getAnyTester(
            self,
            _context: _all.GetanytesterCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _AnyTesterInterfaceModule.Server | _all.AnyTesterClient | _all.GetanytesterResultTuple | None
        ]: ...
        def getAnyTester_context(self, context: _all.GetanytesterCallContext) -> Awaitable[None]: ...

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
    def _new_client(self, server: _DynamicCapabilityServer) -> _all.AnyTesterClient: ...
    class Server(_DynamicCapabilityServer):
        def getAnyStruct(
            self,
            _context: _all.GetanystructCallContext,
            **kwargs: object,
        ) -> Awaitable[_all.AnyStruct | _all.GetanystructResultTuple | None]: ...
        def getAnyStruct_context(self, context: _all.GetanystructCallContext) -> Awaitable[None]: ...
        def getAnyList(
            self,
            _context: _all.GetanylistCallContext,
            **kwargs: object,
        ) -> Awaitable[_all.AnyList | _all.GetanylistResultTuple | None]: ...
        def getAnyList_context(self, context: _all.GetanylistCallContext) -> Awaitable[None]: ...
        def getAnyPointer(
            self,
            _context: _all.GetanypointerCallContext,
            **kwargs: object,
        ) -> Awaitable[_all.AnyPointer | _all.GetanypointerResultTuple | None]: ...
        def getAnyPointer_context(self, context: _all.GetanypointerCallContext) -> Awaitable[None]: ...
        def setAnyPointer(
            self,
            p: _all.AnyPointer,
            _context: _all.SetanypointerCallContext,
            **kwargs: object,
        ) -> Awaitable[None]: ...
        def setAnyPointer_context(self, context: _all.SetanypointerCallContext) -> Awaitable[None]: ...
