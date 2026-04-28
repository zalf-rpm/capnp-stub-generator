"""Module helper types for `fbp_nested_callback.capnp`."""

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

from . import builders as builders
from . import clients as clients
from . import contexts as contexts
from . import readers as readers
from . import schemas as schemas
from . import servers as servers
from .results import tuples as results_tuples

class _ChannelInterfaceModule(_InterfaceModule):
    class _StatsCallbackInterfaceModule(_InterfaceModule):
        class _StatsStructModule(_StructModule):
            class Reader(_DynamicStructReader): ...
            class Builder(_DynamicStructBuilder): ...

            class _StatsSchema(_StructSchema):
                class _Fields(dict[str, _StructSchemaField]):
                    @overload
                    def __getitem__(self, key: Literal["noOfWaitingWriters"]) -> _StructSchemaField: ...
                    @overload
                    def __getitem__(self, key: Literal["noOfWaitingReaders"]) -> _StructSchemaField: ...
                    @overload
                    def __getitem__(self, key: Literal["noOfIpsInQueue"]) -> _StructSchemaField: ...
                    @overload
                    def __getitem__(self, key: Literal["totalNoOfIpsReceived"]) -> _StructSchemaField: ...
                    @overload
                    def __getitem__(self, key: Literal["timestamp"]) -> _StructSchemaField: ...
                    @overload
                    def __getitem__(self, key: Literal["updateIntervalInMs"]) -> _StructSchemaField: ...
                    @overload
                    def __getitem__(self, key: str) -> _StructSchemaField: ...

                @property
                @override
                def fields(
                    self,
                ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsStructModule._StatsSchema._Fields: ...

            @property
            @override
            def schema(self) -> schemas._ChannelStatsCallbackStatsSchema: ...
            @override
            def new_message(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
                noOfWaitingWriters: int | None = None,
                noOfWaitingReaders: int | None = None,
                noOfIpsInQueue: int | None = None,
                totalNoOfIpsReceived: int | None = None,
                timestamp: str | None = None,
                updateIntervalInMs: int | None = None,
                **kwargs: object,
            ) -> builders.StatsBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[readers.StatsReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[readers.StatsReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[builders.StatsBuilder]: ...
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
            ) -> readers.StatsReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> readers.StatsReader: ...

        Stats: _StatsStructModule
        class _UnregisterInterfaceModule(_InterfaceModule):
            class _UnregisterSchema(_InterfaceSchema):
                class _UnregisterInterfaceModuleUnregParamSchema(_StructSchema):
                    class _Fields(dict[str, _StructSchemaField]): ...

                    @property
                    @override
                    def fields(
                        self,
                    ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema._UnregisterInterfaceModuleUnregParamSchema._Fields: ...

                class _UnregisterInterfaceModuleUnregResultSchema(_StructSchema):
                    class _Fields(dict[str, _StructSchemaField]):
                        @overload
                        def __getitem__(self, key: Literal["success"]) -> _StructSchemaField: ...
                        @overload
                        def __getitem__(self, key: str) -> _StructSchemaField: ...

                    @property
                    @override
                    def fields(
                        self,
                    ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema._UnregisterInterfaceModuleUnregResultSchema._Fields: ...

                class _UnregisterInterfaceModuleUnregMethod(_InterfaceMethod):
                    @property
                    @override
                    def param_type(
                        self,
                    ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema._UnregisterInterfaceModuleUnregParamSchema: ...
                    @property
                    @override
                    def result_type(
                        self,
                    ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema._UnregisterInterfaceModuleUnregResultSchema: ...

                class _Methods(dict[str, _InterfaceMethod]):
                    @overload
                    def __getitem__(
                        self,
                        key: Literal["unreg"],
                    ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema._UnregisterInterfaceModuleUnregMethod: ...
                    @overload
                    def __getitem__(self, key: str) -> _InterfaceMethod: ...

                @property
                @override
                def methods(
                    self,
                ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema._Methods: ...

            @property
            @override
            def schema(self) -> schemas._ChannelStatsCallbackUnregisterSchema: ...
            @override
            def _new_client(self, server: _DynamicCapabilityServer) -> clients.UnregisterClient: ...
            class Server(_DynamicCapabilityServer):
                def unreg(
                    self,
                    _context: contexts.UnregCallContext,
                    **kwargs: object,
                ) -> Awaitable[bool | results_tuples.UnregResultTuple | None]: ...
                def unreg_context(self, context: contexts.UnregCallContext) -> Awaitable[None]: ...

        Unregister: _UnregisterInterfaceModule
        type UnregisterServer = _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server

        class _StatsCallbackSchema(_InterfaceSchema):
            class _StatsCallbackInterfaceModuleStatusParamSchema(_StructSchema):
                class _StatsField(_StructSchemaField):
                    @property
                    @override
                    def schema(self) -> schemas._ChannelStatsCallbackStatsSchema: ...

                class _Fields(dict[str, _StructSchemaField]):
                    @overload
                    def __getitem__(
                        self,
                        key: Literal["stats"],
                    ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._StatsCallbackInterfaceModuleStatusParamSchema._StatsField: ...
                    @overload
                    def __getitem__(self, key: str) -> _StructSchemaField: ...

                @property
                @override
                def fields(
                    self,
                ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._StatsCallbackInterfaceModuleStatusParamSchema._Fields: ...

            class _StatsCallbackInterfaceModuleStatusResultSchema(_StructSchema):
                class _Fields(dict[str, _StructSchemaField]): ...

                @property
                @override
                def fields(
                    self,
                ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._StatsCallbackInterfaceModuleStatusResultSchema._Fields: ...

            class _StatsCallbackInterfaceModuleStatusMethod(_InterfaceMethod):
                @property
                @override
                def param_type(
                    self,
                ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._StatsCallbackInterfaceModuleStatusParamSchema: ...
                @property
                @override
                def result_type(
                    self,
                ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._StatsCallbackInterfaceModuleStatusResultSchema: ...

            class _Methods(dict[str, _InterfaceMethod]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["status"],
                ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._StatsCallbackInterfaceModuleStatusMethod: ...
                @overload
                def __getitem__(self, key: str) -> _InterfaceMethod: ...

            @property
            @override
            def methods(
                self,
            ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._Methods: ...

        @property
        @override
        def schema(self) -> schemas._ChannelStatsCallbackSchema: ...
        @override
        def _new_client(self, server: _DynamicCapabilityServer) -> clients.StatsCallbackClient: ...
        class Server(_DynamicCapabilityServer):
            def status(
                self,
                stats: readers.StatsReader,
                _context: contexts.StatusCallContext,
                **kwargs: object,
            ) -> Awaitable[None]: ...
            def status_context(self, context: contexts.StatusCallContext) -> Awaitable[None]: ...

    StatsCallback: _StatsCallbackInterfaceModule
    type StatsCallbackServer = _ChannelInterfaceModule._StatsCallbackInterfaceModule.Server

    class _ChannelSchema(_InterfaceSchema):
        class _ChannelInterfaceModuleRegisterStatsCallbackParamSchema(_StructSchema):
            class _CallbackField(_StructSchemaField):
                @property
                @override
                def schema(self) -> schemas._ChannelStatsCallbackSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["callback"],
                ) -> _ChannelInterfaceModule._ChannelSchema._ChannelInterfaceModuleRegisterStatsCallbackParamSchema._CallbackField: ...
                @overload
                def __getitem__(self, key: Literal["updateIntervalInMs"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _ChannelInterfaceModule._ChannelSchema._ChannelInterfaceModuleRegisterStatsCallbackParamSchema._Fields
            ): ...

        class _ChannelInterfaceModuleRegisterStatsCallbackResultSchema(_StructSchema):
            class _UnregisterCallbackField(_StructSchemaField):
                @property
                @override
                def schema(self) -> schemas._ChannelStatsCallbackUnregisterSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["unregisterCallback"],
                ) -> _ChannelInterfaceModule._ChannelSchema._ChannelInterfaceModuleRegisterStatsCallbackResultSchema._UnregisterCallbackField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(
                self,
            ) -> (
                _ChannelInterfaceModule._ChannelSchema._ChannelInterfaceModuleRegisterStatsCallbackResultSchema._Fields
            ): ...

        class _ChannelInterfaceModuleRegisterStatsCallbackMethod(_InterfaceMethod):
            @property
            @override
            def param_type(
                self,
            ) -> _ChannelInterfaceModule._ChannelSchema._ChannelInterfaceModuleRegisterStatsCallbackParamSchema: ...
            @property
            @override
            def result_type(
                self,
            ) -> _ChannelInterfaceModule._ChannelSchema._ChannelInterfaceModuleRegisterStatsCallbackResultSchema: ...

        class _Methods(dict[str, _InterfaceMethod]):
            @overload
            def __getitem__(
                self,
                key: Literal["registerStatsCallback"],
            ) -> _ChannelInterfaceModule._ChannelSchema._ChannelInterfaceModuleRegisterStatsCallbackMethod: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod: ...

        @property
        @override
        def methods(self) -> _ChannelInterfaceModule._ChannelSchema._Methods: ...

    @property
    @override
    def schema(self) -> schemas._ChannelSchema: ...
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> clients.ChannelClient: ...
    class Server(_DynamicCapabilityServer):
        def registerStatsCallback(
            self,
            callback: clients.StatsCallbackClient,
            updateIntervalInMs: int,
            _context: contexts.RegisterstatscallbackCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
            | clients.UnregisterClient
            | results_tuples.RegisterstatscallbackResultTuple
            | None
        ]: ...
        def registerStatsCallback_context(
            self,
            context: contexts.RegisterstatscallbackCallContext,
        ) -> Awaitable[None]: ...
