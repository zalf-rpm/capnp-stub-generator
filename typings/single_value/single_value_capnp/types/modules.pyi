"""Module helper types for `single_value.capnp`."""

from collections.abc import Awaitable, Callable, Sequence
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityServer,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _InterfaceModule,
    _StructModule,
)

from . import _all as _all

class _SingleValueInterfaceModule(_InterfaceModule):
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> _all.SingleValueClient: ...
    class Server(_DynamicCapabilityServer):
        def getBool(
            self,
            _context: _all.GetboolCallContext,
            **kwargs: object,
        ) -> Awaitable[bool | _all.GetboolResultTuple | None]: ...
        def getBool_context(self, context: _all.GetboolCallContext) -> Awaitable[None]: ...
        def getInt(
            self,
            _context: _all.GetintCallContext,
            **kwargs: object,
        ) -> Awaitable[int | _all.GetintResultTuple | None]: ...
        def getInt_context(self, context: _all.GetintCallContext) -> Awaitable[None]: ...
        def getFloat(
            self,
            _context: _all.GetfloatCallContext,
            **kwargs: object,
        ) -> Awaitable[float | _all.GetfloatResultTuple | None]: ...
        def getFloat_context(self, context: _all.GetfloatCallContext) -> Awaitable[None]: ...
        def getText(
            self,
            _context: _all.GettextCallContext,
            **kwargs: object,
        ) -> Awaitable[str | _all.GettextResultTuple | None]: ...
        def getText_context(self, context: _all.GettextCallContext) -> Awaitable[None]: ...
        def getData(
            self,
            _context: _all.GetdataCallContext,
            **kwargs: object,
        ) -> Awaitable[bytes | _all.GetdataResultTuple | None]: ...
        def getData_context(self, context: _all.GetdataCallContext) -> Awaitable[None]: ...
        def getList(
            self,
            _context: _all.GetlistCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _all.Int32ListBuilder | _all.Int32ListReader | Sequence[Any] | _all.GetlistResultTuple | None
        ]: ...
        def getList_context(self, context: _all.GetlistCallContext) -> Awaitable[None]: ...
        def getStruct(
            self,
            _context: _all.GetstructCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _all.MyStructBuilder | _all.MyStructReader | dict[str, Any] | _all.GetstructResultTuple | None
        ]: ...
        def getStruct_context(self, context: _all.GetstructCallContext) -> Awaitable[None]: ...
        def getInterface(
            self,
            _context: _all.GetinterfaceCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _SingleValueInterfaceModule.Server | _all.SingleValueClient | _all.GetinterfaceResultTuple | None
        ]: ...
        def getInterface_context(self, context: _all.GetinterfaceCallContext) -> Awaitable[None]: ...
        def getAny(
            self,
            _context: _all.GetanyCallContext,
            **kwargs: object,
        ) -> Awaitable[_all.AnyPointer | _all.GetanyResultTuple | None]: ...
        def getAny_context(self, context: _all.GetanyCallContext) -> Awaitable[None]: ...
        def getListStruct(
            self,
            _context: _all.GetliststructCallContext,
            **kwargs: object,
        ) -> Awaitable[
            _all.MyStructListBuilder | _all.MyStructListReader | Sequence[Any] | _all.GetliststructResultTuple | None
        ]: ...
        def getListStruct_context(self, context: _all.GetliststructCallContext) -> Awaitable[None]: ...

class _MyStructStructModule(_StructModule):
    class Reader(_DynamicStructReader): ...
    class Builder(_DynamicStructBuilder): ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        id: int | None = None,
        **kwargs: object,
    ) -> _all.MyStructBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[_all.MyStructReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[_all.MyStructReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[_all.MyStructBuilder]: ...
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
    ) -> _all.MyStructReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> _all.MyStructReader: ...
