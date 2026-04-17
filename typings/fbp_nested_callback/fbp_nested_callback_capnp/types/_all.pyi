"""This is an automatically generated stub for `fbp_nested_callback.capnp`."""

from collections.abc import Awaitable, Callable
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, NamedTuple, Protocol, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityClient,
    _DynamicCapabilityServer,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _InterfaceModule,
    _StructModule,
)

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
            ) -> StatsBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[StatsReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[StatsReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[StatsBuilder]: ...
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
            ) -> StatsReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> StatsReader: ...

        Stats: _StatsStructModule
        class _UnregisterInterfaceModule(_InterfaceModule):
            @override
            def _new_client(self, server: _DynamicCapabilityServer) -> UnregisterClient: ...
            class Server(_DynamicCapabilityServer):
                def unreg(
                    self,
                    _context: UnregCallContext,
                    **kwargs: object,
                ) -> Awaitable[bool | UnregResultTuple | None]: ...
                def unreg_context(self, context: UnregCallContext) -> Awaitable[None]: ...

        Unregister: _UnregisterInterfaceModule
        type UnregisterServer = _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
        @override
        def _new_client(self, server: _DynamicCapabilityServer) -> StatsCallbackClient: ...
        class Server(_DynamicCapabilityServer):
            def status(self, stats: StatsReader, _context: StatusCallContext, **kwargs: object) -> Awaitable[None]: ...
            def status_context(self, context: StatusCallContext) -> Awaitable[None]: ...

    StatsCallback: _StatsCallbackInterfaceModule
    type StatsCallbackServer = _ChannelInterfaceModule._StatsCallbackInterfaceModule.Server
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> ChannelClient: ...
    class Server(_DynamicCapabilityServer):
        def registerStatsCallback(
            self,
            callback: StatsCallbackClient,
            updateIntervalInMs: int,
            _context: RegisterstatscallbackCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
            | UnregisterClient
            | RegisterstatscallbackResultTuple
            | None
        ]: ...
        def registerStatsCallback_context(self, context: RegisterstatscallbackCallContext) -> Awaitable[None]: ...

class StatsReader(_DynamicStructReader):
    @property
    def noOfWaitingWriters(self) -> int: ...
    @property
    def noOfWaitingReaders(self) -> int: ...
    @property
    def noOfIpsInQueue(self) -> int: ...
    @property
    def totalNoOfIpsReceived(self) -> int: ...
    @property
    def timestamp(self) -> str: ...
    @property
    def updateIntervalInMs(self) -> int: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> StatsBuilder: ...

class StatsBuilder(_DynamicStructBuilder):
    @property
    def noOfWaitingWriters(self) -> int: ...
    @noOfWaitingWriters.setter
    def noOfWaitingWriters(self, value: int) -> None: ...
    @property
    def noOfWaitingReaders(self) -> int: ...
    @noOfWaitingReaders.setter
    def noOfWaitingReaders(self, value: int) -> None: ...
    @property
    def noOfIpsInQueue(self) -> int: ...
    @noOfIpsInQueue.setter
    def noOfIpsInQueue(self, value: int) -> None: ...
    @property
    def totalNoOfIpsReceived(self) -> int: ...
    @totalNoOfIpsReceived.setter
    def totalNoOfIpsReceived(self, value: int) -> None: ...
    @property
    def timestamp(self) -> str: ...
    @timestamp.setter
    def timestamp(self, value: str) -> None: ...
    @property
    def updateIntervalInMs(self) -> int: ...
    @updateIntervalInMs.setter
    def updateIntervalInMs(self, value: int) -> None: ...
    @override
    def as_reader(self) -> StatsReader: ...

class UnregRequest(Protocol):
    def send(self) -> UnregResult: ...

class UnregResult(Awaitable[UnregResult], Protocol):
    success: bool

class UnregServerResult(_DynamicStructBuilder):
    @property
    def success(self) -> bool: ...
    @success.setter
    def success(self, value: bool) -> None: ...

class UnregParams(Protocol): ...

class UnregCallContext(Protocol):
    params: UnregParams
    @property
    def results(self) -> UnregServerResult: ...

class UnregResultTuple(NamedTuple):
    success: bool

class UnregisterClient(_DynamicCapabilityClient):
    def unreg(self) -> UnregResult: ...
    def unreg_request(self) -> UnregRequest: ...

class StatusRequest(Protocol):
    stats: StatsBuilder
    @overload
    def init(self, name: Literal["stats"]) -> StatsBuilder: ...
    @overload
    def init(self, name: str, size: int = ...) -> Any: ...
    def send(self) -> StatusResult: ...

class StatusResult(Awaitable[None], Protocol): ...

class StatusParams(Protocol):
    stats: StatsReader

class StatusCallContext(Protocol):
    params: StatusParams

class StatsCallbackClient(_DynamicCapabilityClient):
    def status(self, stats: StatsBuilder | StatsReader | dict[str, Any] | None = None) -> StatusResult: ...
    def status_request(self, stats: StatsBuilder | None = None) -> StatusRequest: ...

class RegisterstatscallbackRequest(Protocol):
    callback: StatsCallbackClient | _ChannelInterfaceModule._StatsCallbackInterfaceModule.Server
    updateIntervalInMs: int
    def send(self) -> RegisterstatscallbackResult: ...

class RegisterstatscallbackResult(Awaitable[RegisterstatscallbackResult], Protocol):
    unregisterCallback: UnregisterClient

class RegisterstatscallbackServerResult(_DynamicStructBuilder):
    @property
    def unregisterCallback(
        self,
    ) -> _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server | UnregisterClient: ...
    @unregisterCallback.setter
    def unregisterCallback(
        self,
        value: _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
        | UnregisterClient,
    ) -> None: ...

class RegisterstatscallbackParams(Protocol):
    callback: StatsCallbackClient
    updateIntervalInMs: int

class RegisterstatscallbackCallContext(Protocol):
    params: RegisterstatscallbackParams
    @property
    def results(self) -> RegisterstatscallbackServerResult: ...

class RegisterstatscallbackResultTuple(NamedTuple):
    unregisterCallback: (
        _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server | UnregisterClient
    )

class ChannelClient(_DynamicCapabilityClient):
    def registerStatsCallback(
        self,
        callback: StatsCallbackClient | _ChannelInterfaceModule._StatsCallbackInterfaceModule.Server | None = None,
        updateIntervalInMs: int | None = None,
    ) -> RegisterstatscallbackResult: ...
    def registerStatsCallback_request(
        self,
        callback: StatsCallbackClient | _ChannelInterfaceModule._StatsCallbackInterfaceModule.Server | None = None,
        updateIntervalInMs: int | None = None,
    ) -> RegisterstatscallbackRequest: ...

Channel: _ChannelInterfaceModule

# Top-level type aliases for use in type annotations
ChannelServer = _ChannelInterfaceModule.Server
StatsCallbackServer = _ChannelInterfaceModule._StatsCallbackInterfaceModule.Server
UnregisterServer = _ChannelInterfaceModule._StatsCallbackInterfaceModule._UnregisterInterfaceModule.Server
