"""Type stubs for pycapnp.

This stub file provides type information for the pycapnp package, enabling
static type checkers to understand the Cap'n Proto Python bindings.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from types import ModuleType
from typing import Any, Generic, Protocol, TypeVar

T = TypeVar("T")

class KjException(Exception):
    """Exception raised by Cap'n Proto operations."""

class NestedNode(Protocol):
    name: str
    id: int

class ParameterNode(Protocol):
    name: str

class Enumerant(Protocol):
    name: str

class EnumNode(Protocol):
    enumerants: Sequence[Enumerant]

class AnyPointerParameter(Protocol):
    parameterIndex: int
    scopeId: int

class AnyPointerType(Protocol):
    def which(self) -> str: ...
    parameter: AnyPointerParameter

class BrandBinding(Protocol):
    type: TypeReader

class BrandScope(Protocol):
    def which(self) -> str: ...
    scopeId: int
    bind: Sequence[BrandBinding]

class Brand(Protocol):
    scopes: Sequence[BrandScope]

class ListElementType(Protocol):
    elementType: TypeReader

class ListType(ListElementType, Protocol): ...

class EnumType(Protocol):
    typeId: int

class StructType(Protocol):
    typeId: int
    brand: Brand

class InterfaceType(Protocol):
    typeId: int

class TypeReader(Protocol):
    def which(self) -> str: ...
    list: ListType
    enum: EnumType
    struct: StructType
    interface: InterfaceType
    anyPointer: AnyPointerType
    elementType: TypeReader

class SlotNode(Protocol):
    type: TypeReader

class FieldNode(Protocol):
    name: str
    slot: SlotNode
    discriminantValue: int
    def which(self) -> str: ...

class StructNode(Protocol):
    fields: Sequence[FieldNode]
    discriminantCount: int

class ConstNode(Protocol):
    type: TypeReader

class SchemaNode(Protocol):
    id: int
    scopeId: int
    displayName: str
    nestedNodes: Sequence[NestedNode]
    parameters: Sequence[ParameterNode]
    struct: StructNode
    enum: EnumNode
    const: ConstNode
    isGeneric: bool
    def which(self) -> str: ...

class DefaultValueReader(Protocol):
    def as_bool(self) -> bool: ...
    def __str__(self) -> str: ...

class StructRuntime(Protocol):
    fields_list: Sequence[_DynamicStructReader]

class StructSchema(Protocol):
    node: SchemaNode
    elementType: TypeReader
    def as_struct(self) -> StructRuntime: ...
    def get_nested(self, name: str) -> StructSchema: ...

class ListSchema(Protocol):
    node: SchemaNode
    elementType: TypeReader

    def as_struct(self) -> StructRuntime: ...
    def get_nested(self, name: str) -> StructSchema: ...

class DynamicListReader(Protocol):
    elementType: TypeReader
    list: DynamicListReader

class SlotRuntime(Protocol):
    type: TypeReader

class _DynamicStructReader(Protocol):
    name: str
    slot: SlotRuntime
    schema: StructSchema
    list: DynamicListReader
    struct: StructType
    enum: EnumType
    interface: InterfaceType
    def which(self) -> str: ...

class _ListSchema(Protocol):
    node: SchemaNode
    elementType: TypeReader

    def as_struct(self) -> StructRuntime: ...
    def get_nested(self, name: str) -> StructSchema: ...

class _StructSchema(Protocol):
    node: SchemaNode
    def as_struct(self) -> StructRuntime: ...
    def get_nested(self, name: str) -> StructSchema: ...

class InterfaceMethod(Protocol):
    param_type: StructSchema
    result_type: StructSchema

class InterfaceSchema(Protocol):
    methods: Mapping[str, InterfaceMethod]

class InterfaceRuntime(Protocol):
    schema: InterfaceSchema

class GeneratedModule(ModuleType):
    schema: StructSchema
    __file__: str | None

class SchemaParser:
    modules_by_id: MutableMapping[int, GeneratedModule]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def load(
        self,
        file_name: str,
        display_name: str | None = ...,
        imports: Sequence[str] | None = ...,
    ) -> GeneratedModule: ...

def remove_import_hook() -> None: ...
def load(
    file_name: str,
    imports: Sequence[str] | None = ...,
    *,
    runtime: bool | None = ...,
) -> GeneratedModule: ...

class _CapnpLibCapnpModule:
    """The capnp.lib.capnp submodule containing implementation classes."""

    _DynamicStructReader: type[_DynamicStructReader]
    _ListSchema: type[_ListSchema]
    _StructSchema: type[_StructSchema]
    KjException: type[KjException]
    SchemaParser: type[SchemaParser]

class _CapnpLibModule:
    """The capnp.lib submodule."""

    capnp: _CapnpLibCapnpModule

class _CapnpLib:
    """The capnp.lib namespace."""

    capnp: _CapnpLibCapnpModule

lib: _CapnpLib

class _DynamicListBuilder(Generic[T]):
    """Generic list builder type returned by init() for list fields."""
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> T: ...
    def __setitem__(self, index: int, value: T) -> None: ...

# RPC Classes
I_co = TypeVar("I_co")

class CastableBootstrap(Protocol):
    def cast_as(self, interface: type[I_co]) -> I_co: ...

class TwoPartyClient:
    """Two-party RPC client for Cap'n Proto."""
    def __init__(self, connection: Any) -> None: ...
    def bootstrap(self) -> CastableBootstrap: ...
    async def on_disconnect(self) -> None: ...

class TwoPartyServer:
    """Two-party RPC server for Cap'n Proto."""
    def __init__(self, connection: Any, bootstrap: Any) -> None: ...
    async def on_disconnect(self) -> None: ...

class Server:
    """Server returned by AsyncIoStream.create_server."""
    async def serve_forever(self) -> None:
        """Run the server until cancelled."""
        ...
    async def wait_closed(self) -> None:
        """Wait until the server is closed."""
        ...
    def close(self) -> None:
        """Close the server."""
        ...
    def is_serving(self) -> bool:
        """Return True if the server is actively serving."""
        ...
    async def __aenter__(self) -> Server: ...
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

class AsyncIoStream:
    """Async I/O stream wrapper for Cap'n Proto RPC."""
    @staticmethod
    async def create_connection(host: str, port: int) -> AsyncIoStream: ...
    @staticmethod
    async def create_server(callback: Any, host: str, port: int | None = None, **kwargs: Any) -> Server: ...

# Async utilities
async def run(coro: Any) -> Any:
    """Run an async coroutine with Cap'n Proto event loop."""
    ...

__all__ = [
    "AnyPointerParameter",
    "AnyPointerType",
    "Brand",
    "BrandBinding",
    "BrandScope",
    "ConstNode",
    "DefaultValueReader",
    "DynamicListReader",
    "Enumerant",
    "EnumNode",
    "EnumType",
    "GeneratedModule",
    "InterfaceMethod",
    "InterfaceRuntime",
    "InterfaceSchema",
    "KjException",
    "ListSchema",
    "ListType",
    "ListElementType",
    "NestedNode",
    "ParameterNode",
    "SchemaNode",
    "SchemaParser",
    "StructNode",
    "StructRuntime",
    "StructSchema",
    "StructType",
    "TypeReader",
    "SlotNode",
    "SlotRuntime",
    "FieldNode",
    "lib",
    "_DynamicListBuilder",
    "_DynamicStructReader",
    "_ListSchema",
    "_StructSchema",
    "load",
    "remove_import_hook",
    "CastableBootstrap",
    "TwoPartyClient",
    "TwoPartyServer",
    "Server",
    "AsyncIoStream",
    "run",
]
