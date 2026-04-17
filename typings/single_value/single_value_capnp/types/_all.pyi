"""This is an automatically generated stub for `single_value.capnp`."""

from collections.abc import Awaitable, Callable, Iterator, Sequence
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, NamedTuple, Protocol, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityClient,
    _DynamicCapabilityServer,
    _DynamicListBuilder,
    _DynamicListReader,
    _DynamicObjectBuilder,
    _DynamicObjectReader,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _InterfaceModule,
    _StructModule,
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

class _SingleValueInterfaceModule(_InterfaceModule):
    @override
    def _new_client(self, server: _DynamicCapabilityServer) -> SingleValueClient: ...
    class Server(_DynamicCapabilityServer):
        def getBool(
            self,
            _context: GetboolCallContext,
            **kwargs: object,
        ) -> Awaitable[bool | GetboolResultTuple | None]: ...
        def getBool_context(self, context: GetboolCallContext) -> Awaitable[None]: ...
        def getInt(
            self,
            _context: GetintCallContext,
            **kwargs: object,
        ) -> Awaitable[int | GetintResultTuple | None]: ...
        def getInt_context(self, context: GetintCallContext) -> Awaitable[None]: ...
        def getFloat(
            self,
            _context: GetfloatCallContext,
            **kwargs: object,
        ) -> Awaitable[float | GetfloatResultTuple | None]: ...
        def getFloat_context(self, context: GetfloatCallContext) -> Awaitable[None]: ...
        def getText(
            self,
            _context: GettextCallContext,
            **kwargs: object,
        ) -> Awaitable[str | GettextResultTuple | None]: ...
        def getText_context(self, context: GettextCallContext) -> Awaitable[None]: ...
        def getData(
            self,
            _context: GetdataCallContext,
            **kwargs: object,
        ) -> Awaitable[bytes | GetdataResultTuple | None]: ...
        def getData_context(self, context: GetdataCallContext) -> Awaitable[None]: ...
        def getList(
            self,
            _context: GetlistCallContext,
            **kwargs: object,
        ) -> Awaitable[Int32ListBuilder | Int32ListReader | Sequence[Any] | GetlistResultTuple | None]: ...
        def getList_context(self, context: GetlistCallContext) -> Awaitable[None]: ...
        def getStruct(
            self,
            _context: GetstructCallContext,
            **kwargs: object,
        ) -> Awaitable[MyStructBuilder | MyStructReader | dict[str, Any] | GetstructResultTuple | None]: ...
        def getStruct_context(self, context: GetstructCallContext) -> Awaitable[None]: ...
        def getInterface(
            self,
            _context: GetinterfaceCallContext,
            **kwargs: object,
        ) -> Awaitable[_SingleValueInterfaceModule.Server | SingleValueClient | GetinterfaceResultTuple | None]: ...
        def getInterface_context(self, context: GetinterfaceCallContext) -> Awaitable[None]: ...
        def getAny(
            self,
            _context: GetanyCallContext,
            **kwargs: object,
        ) -> Awaitable[AnyPointer | GetanyResultTuple | None]: ...
        def getAny_context(self, context: GetanyCallContext) -> Awaitable[None]: ...
        def getListStruct(
            self,
            _context: GetliststructCallContext,
            **kwargs: object,
        ) -> Awaitable[MyStructListBuilder | MyStructListReader | Sequence[Any] | GetliststructResultTuple | None]: ...
        def getListStruct_context(self, context: GetliststructCallContext) -> Awaitable[None]: ...

class GetboolRequest(Protocol):
    def send(self) -> GetboolResult: ...

class GetboolResult(Awaitable[GetboolResult], Protocol):
    val: bool

class GetboolServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> bool: ...
    @val.setter
    def val(self, value: bool) -> None: ...

class GetboolParams(Protocol): ...

class GetboolCallContext(Protocol):
    params: GetboolParams
    @property
    def results(self) -> GetboolServerResult: ...

class GetboolResultTuple(NamedTuple):
    val: bool

class GetintRequest(Protocol):
    def send(self) -> GetintResult: ...

class GetintResult(Awaitable[GetintResult], Protocol):
    val: int

class GetintServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> int: ...
    @val.setter
    def val(self, value: int) -> None: ...

class GetintParams(Protocol): ...

class GetintCallContext(Protocol):
    params: GetintParams
    @property
    def results(self) -> GetintServerResult: ...

class GetintResultTuple(NamedTuple):
    val: int

class GetfloatRequest(Protocol):
    def send(self) -> GetfloatResult: ...

class GetfloatResult(Awaitable[GetfloatResult], Protocol):
    val: float

class GetfloatServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> float: ...
    @val.setter
    def val(self, value: float) -> None: ...

class GetfloatParams(Protocol): ...

class GetfloatCallContext(Protocol):
    params: GetfloatParams
    @property
    def results(self) -> GetfloatServerResult: ...

class GetfloatResultTuple(NamedTuple):
    val: float

class GettextRequest(Protocol):
    def send(self) -> GettextResult: ...

class GettextResult(Awaitable[GettextResult], Protocol):
    val: str

class GettextServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> str: ...
    @val.setter
    def val(self, value: str) -> None: ...

class GettextParams(Protocol): ...

class GettextCallContext(Protocol):
    params: GettextParams
    @property
    def results(self) -> GettextServerResult: ...

class GettextResultTuple(NamedTuple):
    val: str

class GetdataRequest(Protocol):
    def send(self) -> GetdataResult: ...

class GetdataResult(Awaitable[GetdataResult], Protocol):
    val: bytes

class GetdataServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> bytes: ...
    @val.setter
    def val(self, value: bytes) -> None: ...

class GetdataParams(Protocol): ...

class GetdataCallContext(Protocol):
    params: GetdataParams
    @property
    def results(self) -> GetdataServerResult: ...

class GetdataResultTuple(NamedTuple):
    val: bytes

class GetlistRequest(Protocol):
    def send(self) -> GetlistResult: ...

class _Int32List:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> int: ...
        @override
        def __iter__(self) -> Iterator[int]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> int: ...
        @override
        def __setitem__(self, key: int, value: int) -> None: ...
        @override
        def __iter__(self) -> Iterator[int]: ...

class GetlistResult(Awaitable[GetlistResult], Protocol):
    val: Int32ListReader

class GetlistServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> Int32ListBuilder: ...
    @val.setter
    def val(self, value: Int32ListBuilder | Int32ListReader | Sequence[Any]) -> None: ...
    @overload
    def init(self, field: Literal["val"], size: int | None = None) -> Int32ListBuilder: ...
    @overload
    def init(self, field: str, size: int | None = None) -> Any: ...

class GetlistParams(Protocol): ...

class GetlistCallContext(Protocol):
    params: GetlistParams
    @property
    def results(self) -> GetlistServerResult: ...

class GetlistResultTuple(NamedTuple):
    val: Int32ListBuilder | Int32ListReader | Sequence[Any]

class GetstructRequest(Protocol):
    def send(self) -> GetstructResult: ...

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
    ) -> MyStructBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[MyStructReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[MyStructReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[MyStructBuilder]: ...
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
    ) -> MyStructReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> MyStructReader: ...

class MyStructReader(_DynamicStructReader):
    @property
    def id(self) -> int: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> MyStructBuilder: ...

class MyStructBuilder(_DynamicStructBuilder):
    @property
    def id(self) -> int: ...
    @id.setter
    def id(self, value: int) -> None: ...
    @override
    def as_reader(self) -> MyStructReader: ...

MyStruct: _MyStructStructModule

class GetstructResult(Awaitable[GetstructResult], Protocol):
    val: MyStructReader

class GetstructServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> MyStructBuilder: ...
    @val.setter
    def val(self, value: MyStructBuilder | MyStructReader | dict[str, Any]) -> None: ...
    @overload
    def init(self, field: Literal["val"], size: int | None = None) -> MyStructBuilder: ...
    @overload
    def init(self, field: str, size: int | None = None) -> Any: ...

class GetstructParams(Protocol): ...

class GetstructCallContext(Protocol):
    params: GetstructParams
    @property
    def results(self) -> GetstructServerResult: ...

class GetstructResultTuple(NamedTuple):
    val: MyStructBuilder | MyStructReader | dict[str, Any]

class GetinterfaceRequest(Protocol):
    def send(self) -> GetinterfaceResult: ...

class GetinterfaceResult(Awaitable[GetinterfaceResult], Protocol):
    val: SingleValueClient

class GetinterfaceServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> _SingleValueInterfaceModule.Server | SingleValueClient: ...
    @val.setter
    def val(self, value: _SingleValueInterfaceModule.Server | SingleValueClient) -> None: ...

class GetinterfaceParams(Protocol): ...

class GetinterfaceCallContext(Protocol):
    params: GetinterfaceParams
    @property
    def results(self) -> GetinterfaceServerResult: ...

class GetinterfaceResultTuple(NamedTuple):
    val: _SingleValueInterfaceModule.Server | SingleValueClient

class GetanyRequest(Protocol):
    def send(self) -> GetanyResult: ...

class GetanyResult(Awaitable[GetanyResult], Protocol):
    val: _DynamicObjectReader

class GetanyServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> AnyPointer: ...
    @val.setter
    def val(self, value: AnyPointer) -> None: ...

class GetanyParams(Protocol): ...

class GetanyCallContext(Protocol):
    params: GetanyParams
    @property
    def results(self) -> GetanyServerResult: ...

class GetanyResultTuple(NamedTuple):
    val: AnyPointer

class GetliststructRequest(Protocol):
    def send(self) -> GetliststructResult: ...

class _MyStructList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> MyStructReader: ...
        @override
        def __iter__(self) -> Iterator[MyStructReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> MyStructBuilder: ...
        @override
        def __setitem__(self, key: int, value: MyStructReader | MyStructBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[MyStructBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> MyStructBuilder: ...

class GetliststructResult(Awaitable[GetliststructResult], Protocol):
    val: MyStructListReader

class GetliststructServerResult(_DynamicStructBuilder):
    @property
    def val(self) -> MyStructListBuilder: ...
    @val.setter
    def val(self, value: MyStructListBuilder | MyStructListReader | Sequence[Any]) -> None: ...
    @overload
    def init(self, field: Literal["val"], size: int | None = None) -> MyStructListBuilder: ...
    @overload
    def init(self, field: str, size: int | None = None) -> Any: ...

class GetliststructParams(Protocol): ...

class GetliststructCallContext(Protocol):
    params: GetliststructParams
    @property
    def results(self) -> GetliststructServerResult: ...

class GetliststructResultTuple(NamedTuple):
    val: MyStructListBuilder | MyStructListReader | Sequence[Any]

class SingleValueClient(_DynamicCapabilityClient):
    def getBool(self) -> GetboolResult: ...
    def getInt(self) -> GetintResult: ...
    def getFloat(self) -> GetfloatResult: ...
    def getText(self) -> GettextResult: ...
    def getData(self) -> GetdataResult: ...
    def getList(self) -> GetlistResult: ...
    def getStruct(self) -> GetstructResult: ...
    def getInterface(self) -> GetinterfaceResult: ...
    def getAny(self) -> GetanyResult: ...
    def getListStruct(self) -> GetliststructResult: ...
    def getBool_request(self) -> GetboolRequest: ...
    def getInt_request(self) -> GetintRequest: ...
    def getFloat_request(self) -> GetfloatRequest: ...
    def getText_request(self) -> GettextRequest: ...
    def getData_request(self) -> GetdataRequest: ...
    def getList_request(self) -> GetlistRequest: ...
    def getStruct_request(self) -> GetstructRequest: ...
    def getInterface_request(self) -> GetinterfaceRequest: ...
    def getAny_request(self) -> GetanyRequest: ...
    def getListStruct_request(self) -> GetliststructRequest: ...

SingleValue: _SingleValueInterfaceModule

# Top-level type aliases for use in type annotations
type Int32ListBuilder = _Int32List.Builder
type Int32ListReader = _Int32List.Reader
type MyStructListBuilder = _MyStructList.Builder
type MyStructListReader = _MyStructList.Reader
SingleValueServer = _SingleValueInterfaceModule.Server
