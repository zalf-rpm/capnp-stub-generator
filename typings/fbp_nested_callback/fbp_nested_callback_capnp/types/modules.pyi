"""Module helper types for `fbp_nested_callback.capnp`."""

from collections.abc import Awaitable, Callable
from contextlib import AbstractContextManager
from typing import IO, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityServer,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _InterfaceModule,
    _StructModule,
)

from . import _all as _all

class _ChannelInterfaceModule(_InterfaceModule):
    class _StatsCallbackInterfaceModule(_InterfaceModule):
        class _StatsStructModule(_StructModule):
            class Reader(_DynamicStructReader): ...
            class Builder(_DynamicStructBuilder): ...

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
