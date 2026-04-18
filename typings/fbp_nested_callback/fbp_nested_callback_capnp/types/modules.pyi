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

from . import _all as _all

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
            def schema(
                self,
            ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsStructModule._StatsSchema: ...
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
            ) -> _all.StatsBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[_all.StatsReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[_all.StatsReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[_all.StatsBuilder]: ...
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
            ) -> _all.StatsReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> _all.StatsReader: ...

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

                class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
                    @overload
                    def __getitem__(
                        self,
                        key: Literal["unreg"],
                    ) -> _InterfaceMethod[
                        _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema._UnregisterInterfaceModuleUnregParamSchema,
                        _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema._UnregisterInterfaceModuleUnregResultSchema,
                    ]: ...
                    @overload
                    def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

                @property
                @override
                def methods(
                    self,
                ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema._Methods: ...

            @property
            @override
            def schema(
                self,
            ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema: ...
            @override
            def _new_client(self, server: _DynamicCapabilityServer) -> _all.UnregisterClient: ...
            class Server(_DynamicCapabilityServer):
                def unreg(
                    self,
                    _context: _all.UnregCallContext,
                    **kwargs: object,
                ) -> Awaitable[bool | _all.UnregResultTuple | None]: ...
                def unreg_context(self, context: _all.UnregCallContext) -> Awaitable[None]: ...

        Unregister: _UnregisterInterfaceModule
        type UnregisterServer = _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server

        class _StatsCallbackSchema(_InterfaceSchema):
            class _StatsCallbackInterfaceModuleStatusParamSchema(_StructSchema):
                class _StatsField(_StructSchemaField):
                    @property
                    @override
                    def schema(
                        self,
                    ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsStructModule._StatsSchema: ...

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

            class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
                @overload
                def __getitem__(
                    self,
                    key: Literal["status"],
                ) -> _InterfaceMethod[
                    _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._StatsCallbackInterfaceModuleStatusParamSchema,
                    _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._StatsCallbackInterfaceModuleStatusResultSchema,
                ]: ...
                @overload
                def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

            @property
            @override
            def methods(
                self,
            ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema._Methods: ...

        @property
        @override
        def schema(self) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema: ...
        @override
        def _new_client(self, server: _DynamicCapabilityServer) -> _all.StatsCallbackClient: ...
        class Server(_DynamicCapabilityServer):
            def status(
                self,
                stats: _all.StatsReader,
                _context: _all.StatusCallContext,
                **kwargs: object,
            ) -> Awaitable[None]: ...
            def status_context(self, context: _all.StatusCallContext) -> Awaitable[None]: ...

    StatsCallback: _StatsCallbackInterfaceModule
    type StatsCallbackServer = _ChannelInterfaceModule._StatsCallbackInterfaceModule.Server

    class _ChannelSchema(_InterfaceSchema):
        class _ChannelInterfaceModuleRegisterStatsCallbackParamSchema(_StructSchema):
            class _CallbackField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._StatsCallbackSchema: ...

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
                def schema(
                    self,
                ) -> (
                    _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule._UnregisterSchema
                ): ...

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

        class _Methods(dict[str, _InterfaceMethod[_StructSchema, _StructSchema]]):
            @overload
            def __getitem__(
                self,
                key: Literal["registerStatsCallback"],
            ) -> _InterfaceMethod[
                _ChannelInterfaceModule._ChannelSchema._ChannelInterfaceModuleRegisterStatsCallbackParamSchema,
                _ChannelInterfaceModule._ChannelSchema._ChannelInterfaceModuleRegisterStatsCallbackResultSchema,
            ]: ...
            @overload
            def __getitem__(self, key: str) -> _InterfaceMethod[_StructSchema, _StructSchema]: ...

        @property
        @override
        def methods(self) -> _ChannelInterfaceModule._ChannelSchema._Methods: ...

    @property
    @override
    def schema(self) -> _ChannelInterfaceModule._ChannelSchema: ...
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> _all.ChannelClient: ...
    class Server(_DynamicCapabilityServer):
        def registerStatsCallback(
            self,
            callback: _all.StatsCallbackClient,
            updateIntervalInMs: int,
            _context: _all.RegisterstatscallbackCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
            | _all.UnregisterClient
            | _all.RegisterstatscallbackResultTuple
            | None
        ]: ...
        def registerStatsCallback_context(self, context: _all.RegisterstatscallbackCallContext) -> Awaitable[None]: ...
