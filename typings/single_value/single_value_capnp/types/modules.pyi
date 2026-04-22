"""Module helper types for `single_value.capnp`."""

from collections.abc import Awaitable, Callable, Sequence
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityServer,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _InterfaceMethod,
    _InterfaceModule,
    _InterfaceSchema,
    _ListSchema,
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

class _SingleValueInterfaceModule(_InterfaceModule):
    class _SingleValueSchema(_InterfaceSchema):
        class _SingleValueInterfaceModuleGetBoolParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetBoolParamSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetBoolResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["val"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetBoolResultSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetIntParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetIntParamSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetIntResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["val"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetIntResultSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetFloatParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetFloatParamSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetFloatResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["val"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetFloatResultSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetTextParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetTextParamSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetTextResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["val"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetTextResultSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetDataParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetDataParamSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetDataResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["val"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetDataResultSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetListParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListParamSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetListResultSchema(_StructSchema):
            class _ValField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _ListSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["val"],
                ) -> _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListResultSchema._ValField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListResultSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetStructParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetStructParamSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetStructResultSchema(_StructSchema):
            class _ValField(_StructSchemaField):
                @property
                @override
                def schema(self) -> schemas._MyStructSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["val"],
                ) -> _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetStructResultSchema._ValField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetStructResultSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetInterfaceParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetInterfaceParamSchema._Fields: ...

        class _SingleValueInterfaceModuleGetInterfaceResultSchema(_StructSchema):
            class _ValField(_StructSchemaField):
                @property
                @override
                def schema(self) -> schemas._SingleValueSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["val"],
                ) -> _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetInterfaceResultSchema._ValField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetInterfaceResultSchema._Fields: ...

        class _SingleValueInterfaceModuleGetAnyParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetAnyParamSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetAnyResultSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["val"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetAnyResultSchema._Fields
            ): ...

        class _SingleValueInterfaceModuleGetListStructParamSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]): ...

            @property
            @override
            def fields(
                self,
            ) -> _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListStructParamSchema._Fields: ...

        class _SingleValueInterfaceModuleGetListStructResultSchema(_StructSchema):
            class _ValField(_StructSchemaField):
                class _Schema(_ListSchema):
                    @property
                    @override
                    def elementType(self) -> schemas._MyStructSchema: ...

                @property
                @override
                def schema(
                    self,
                ) -> _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListStructResultSchema._ValField._Schema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["val"],
                ) -> _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListStructResultSchema._ValField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListStructResultSchema._Fields: ...

        class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
            @overload
            def __getitem__(
                self,
                key: Literal["getBool"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetBoolParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetBoolResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getInt"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetIntParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetIntResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getFloat"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetFloatParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetFloatResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getText"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetTextParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetTextResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getData"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetDataParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetDataResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getList"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getStruct"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetStructParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetStructResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getInterface"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetInterfaceParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetInterfaceResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getAny"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetAnyParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetAnyResultSchema,
            ]: ...
            @overload
            def __getitem__(
                self,
                key: Literal["getListStruct"],
            ) -> _InterfaceMethod[
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListStructParamSchema,
                _SingleValueInterfaceModule._SingleValueSchema._SingleValueInterfaceModuleGetListStructResultSchema,
            ]: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

        @property
        @override
        def methods(self) -> _SingleValueInterfaceModule._SingleValueSchema._Methods: ...

    @property
    @override
    def schema(self) -> schemas._SingleValueSchema: ...
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> clients.SingleValueClient: ...
    class Server(_DynamicCapabilityServer):
        def getBool(
            self,
            _context: contexts.GetboolCallContext,
            **kwargs: object,
        ) -> Awaitable[bool | results_tuples.GetboolResultTuple | None]: ...
        def getBool_context(self, context: contexts.GetboolCallContext) -> Awaitable[None]: ...
        def getInt(
            self,
            _context: contexts.GetintCallContext,
            **kwargs: object,
        ) -> Awaitable[int | results_tuples.GetintResultTuple | None]: ...
        def getInt_context(self, context: contexts.GetintCallContext) -> Awaitable[None]: ...
        def getFloat(
            self,
            _context: contexts.GetfloatCallContext,
            **kwargs: object,
        ) -> Awaitable[float | results_tuples.GetfloatResultTuple | None]: ...
        def getFloat_context(self, context: contexts.GetfloatCallContext) -> Awaitable[None]: ...
        def getText(
            self,
            _context: contexts.GettextCallContext,
            **kwargs: object,
        ) -> Awaitable[str | results_tuples.GettextResultTuple | None]: ...
        def getText_context(self, context: contexts.GettextCallContext) -> Awaitable[None]: ...
        def getData(
            self,
            _context: contexts.GetdataCallContext,
            **kwargs: object,
        ) -> Awaitable[bytes | results_tuples.GetdataResultTuple | None]: ...
        def getData_context(self, context: contexts.GetdataCallContext) -> Awaitable[None]: ...
        def getList(
            self,
            _context: contexts.GetlistCallContext,
            **kwargs: object,
        ) -> Awaitable[
            builders.Int32ListBuilder
            | readers.Int32ListReader
            | Sequence[Any]
            | results_tuples.GetlistResultTuple
            | None
        ]: ...
        def getList_context(self, context: contexts.GetlistCallContext) -> Awaitable[None]: ...
        def getStruct(
            self,
            _context: contexts.GetstructCallContext,
            **kwargs: object,
        ) -> Awaitable[
            builders.MyStructBuilder
            | readers.MyStructReader
            | dict[str, Any]
            | results_tuples.GetstructResultTuple
            | None
        ]: ...
        def getStruct_context(self, context: contexts.GetstructCallContext) -> Awaitable[None]: ...
        def getInterface(
            self,
            _context: contexts.GetinterfaceCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _SingleValueInterfaceModule.Server
            | clients.SingleValueClient
            | results_tuples.GetinterfaceResultTuple
            | None
        ]: ...
        def getInterface_context(self, context: contexts.GetinterfaceCallContext) -> Awaitable[None]: ...
        def getAny(
            self,
            _context: contexts.GetanyCallContext,
            **kwargs: object,
        ) -> Awaitable[common.AnyPointer | results_tuples.GetanyResultTuple | None]: ...
        def getAny_context(self, context: contexts.GetanyCallContext) -> Awaitable[None]: ...
        def getListStruct(
            self,
            _context: contexts.GetliststructCallContext,
            **kwargs: object,
        ) -> Awaitable[
            builders.MyStructListBuilder
            | readers.MyStructListReader
            | Sequence[Any]
            | results_tuples.GetliststructResultTuple
            | None
        ]: ...
        def getListStruct_context(self, context: contexts.GetliststructCallContext) -> Awaitable[None]: ...

class _MyStructStructModule(_StructModule):
    class Reader(_DynamicStructReader): ...
    class Builder(_DynamicStructBuilder): ...

    class _MyStructSchema(_StructSchema):
        class _Fields(dict[str, _StructSchemaField]):
            @overload
            def __getitem__(self, key: Literal["id"]) -> _StructSchemaField: ...
            @overload
            def __getitem__(self, key: str) -> _StructSchemaField: ...

        @property
        @override
        def fields(self) -> _MyStructStructModule._MyStructSchema._Fields: ...

    @property
    @override
    def schema(self) -> schemas._MyStructSchema: ...
    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        id: int | None = None,
        **kwargs: object,
    ) -> builders.MyStructBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[readers.MyStructReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[readers.MyStructReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[builders.MyStructBuilder]: ...
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
    ) -> readers.MyStructReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> readers.MyStructReader: ...
