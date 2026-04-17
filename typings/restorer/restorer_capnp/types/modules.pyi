"""Module helper types for `restorer.capnp`."""

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

class _BagInterfaceModule(_InterfaceModule):
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
