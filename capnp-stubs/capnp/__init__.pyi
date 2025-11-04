"""Type stubs for pycapnp.

This stub file provides type information for the pycapnp package, enabling
static type checkers to understand the Cap'n Proto Python bindings.

Version: 2.2.1
Compatible with: pycapnp >= 2.0.0
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator, Mapping, MutableMapping, Sequence
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Generic, Protocol, TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

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

class InterfaceNode(Protocol):
    """Node representing an interface schema.

    Only accessible when node.which() == 'interface'.
    """

    methods: Sequence[InterfaceMethod]
    superclasses: Sequence[SuperclassNode]

class SuperclassNode(Protocol):
    """Superclass reference in interface inheritance."""

    id: int

class SchemaNode(Protocol):
    """Schema node - a union type.

    This is a union! You must check which() before accessing union fields:
    - node.struct (when which() == 'struct')
    - node.enum (when which() == 'enum')
    - node.interface (when which() == 'interface')
    - node.const (when which() == 'const')
    - node.file (when which() == 'file')
    """

    # Always available fields
    id: int
    scopeId: int
    displayName: str
    displayNamePrefixLength: int
    nestedNodes: Sequence[NestedNode]
    parameters: Sequence[ParameterNode]
    isGeneric: bool

    # Union fields - only ONE is valid at a time based on which()
    struct: StructNode
    enum: EnumNode
    const: ConstNode
    interface: InterfaceNode
    # Note: file, annotation also exist but are less commonly used
    def which(self) -> str:
        """Return which union field is currently set.

        Returns one of: 'file', 'struct', 'enum', 'interface', 'const', 'annotation'
        """
        ...

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
    """Reader for Cap'n Proto structs.

    This class wraps the Cap'n Proto C++ DynamicStruct::Reader.
    Provides read-only access to struct fields.
    """

    name: str
    slot: SlotRuntime
    schema: StructSchema
    list: DynamicListReader
    struct: StructType
    enum: EnumType
    interface: InterfaceType

    def which(self) -> str:
        """Return the name of the currently set union field."""
        ...

    def as_builder(
        self, num_first_segment_words: int | None = None, allocate_seg_callable: Callable[..., Any] | None = None
    ) -> _DynamicStructBuilder:
        """Convert this reader to a builder (creates a copy).

        Args:
            num_first_segment_words: Size of first segment
            allocate_seg_callable: Custom allocator function

        Returns:
            A builder containing a copy of this struct
        """
        ...

    def to_dict(
        self, verbose: bool = False, ordered: bool = False, encode_bytes_as_base64: bool = False
    ) -> dict[str, Any]:
        """Convert the struct to a Python dictionary.

        Args:
            verbose: Include more details
            ordered: Use OrderedDict for output
            encode_bytes_as_base64: Encode bytes fields as base64 strings

        Returns:
            Dictionary representation of the struct
        """
        ...

class _DynamicStructBuilder(Protocol):
    """Builder for Cap'n Proto structs.

    This class wraps the Cap'n Proto C++ DynamicStruct::Builder.
    Provides read-write access to struct fields.
    """

    name: str
    schema: StructSchema

    def which(self) -> str:
        """Return the name of the currently set union field."""
        ...

    def as_reader(self) -> _DynamicStructReader:
        """Convert this builder to a reader (read-only view).

        Returns:
            A reader view of this struct
        """
        ...

    def adopt(self, field: str, orphan: Any) -> None:
        """Adopt an orphaned message into a field.

        Args:
            field: Field name
            orphan: Orphaned message to adopt
        """
        ...

    def disown(self, field: str) -> Any:
        """Disown a field, returning an orphan.

        Args:
            field: Field name

        Returns:
            Orphaned message
        """
        ...

    def init(self, field: str, size: int | None = None) -> Any:
        """Initialize a struct or list field.

        Args:
            field: Field name
            size: Size for list fields

        Returns:
            The initialized field (builder for structs, list builder for lists)
        """
        ...

    def init_resizable_list(self, field: str) -> _DynamicListBuilder[Any]:
        """Initialize a resizable list field.

        Args:
            field: Field name

        Returns:
            Resizable list builder
        """
        ...

    def from_dict(self, d: dict[str, Any]) -> None:
        """Populate the struct from a dictionary.

        Args:
            d: Dictionary with field values
        """
        ...

    def to_dict(
        self, verbose: bool = False, ordered: bool = False, encode_bytes_as_base64: bool = False
    ) -> dict[str, Any]:
        """Convert the struct to a Python dictionary.

        Args:
            verbose: Include more details
            ordered: Use OrderedDict for output
            encode_bytes_as_base64: Encode bytes fields as base64 strings

        Returns:
            Dictionary representation of the struct
        """
        ...

    def copy(
        self, num_first_segment_words: int | None = None, allocate_seg_callable: Callable[..., Any] | None = None
    ) -> _DynamicStructBuilder:
        """Create a deep copy of this struct.

        Args:
            num_first_segment_words: Size of first segment
            allocate_seg_callable: Custom allocator function

        Returns:
            A new builder containing a copy
        """
        ...

    def clear_write_flag(self) -> None:
        """Clear the write flag for this struct."""
        ...

    def to_bytes(self) -> bytes:
        """Serialize the struct to bytes.

        Returns:
            Serialized message bytes
        """
        ...

    def to_bytes_packed(self) -> bytes:
        """Serialize the struct to packed bytes.

        Returns:
            Serialized message bytes (packed format)
        """
        ...

    def to_segments(self) -> list[bytes]:
        """Serialize the struct to a list of segment bytes.

        Returns:
            List of segment byte arrays
        """
        ...

    def write(self, file: Any) -> None:
        """Write the struct to a file.

        Args:
            file: File-like object to write to
        """
        ...

    def write_packed(self, file: Any) -> None:
        """Write the struct to a file in packed format.

        Args:
            file: File-like object to write to
        """
        ...

    async def write_async(self, stream: AsyncIoStream) -> None:
        """Asynchronously write the struct to a stream.

        Args:
            stream: AsyncIoStream to write to
        """
        ...

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

# RPC Request/Response Types
class _Request(_DynamicStructBuilder, Protocol):
    """RPC request builder.

    Extends DynamicStructBuilder with RPC-specific send() method.
    """
    def send(self) -> _Response:
        """Send the RPC request and return a promise for the response.

        Returns:
            Response promise
        """
        ...

class _Response(_DynamicStructReader, Protocol):
    """RPC response reader.

    Extends DynamicStructReader for reading RPC responses.
    Response objects are also awaitable promises.
    """

    pass

class _CallContext(Protocol):
    """Context for an RPC call on the server side.

    Provides methods for handling server-side RPC calls.
    """
    def release_params(self) -> None:
        """Release the parameter struct.

        Call this when you're done reading the parameters to allow
        the message memory to be freed.
        """
        ...

    def tail_call(self, tailRequest: _Request) -> None:
        """Perform a tail call to another capability.

        Args:
            tailRequest: Request to tail call
        """
        ...

# Capability Types
class _DynamicCapabilityClient(Protocol):
    """Dynamic capability client.

    Represents a reference to a remote capability.
    """
    def cast_as(self, schema: type[T]) -> T:
        """Cast this capability to a specific interface type.

        Args:
            schema: Interface type to cast to

        Returns:
            Capability cast to the specified interface
        """
        ...

    def upcast(self, schema: type[T]) -> T:
        """Upcast this capability to a parent interface type.

        Args:
            schema: Parent interface type

        Returns:
            Capability upcast to the parent interface
        """
        ...

class _DynamicCapabilityServer(Protocol):
    """Dynamic capability server base class.

    Implement this to create server-side capability implementations.
    """

    pass

class GeneratedModule(ModuleType):
    schema: StructSchema
    __file__: str | None

class SchemaParser:
    """Parser for loading Cap'n Proto schema files.

    Do not use this class unless you're sure you know what you're doing.
    Use the convenience method :func:`load` instead.
    """

    modules_by_id: MutableMapping[int, GeneratedModule]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def load(
        self,
        file_name: str,
        display_name: str | None = None,
        imports: Sequence[str] = [],
    ) -> GeneratedModule:
        """Load a Cap'n Proto schema file.

        Args:
            file_name: Path to the .capnp file
            display_name: Optional display name for the module
            imports: List of import paths for resolving imports

        Returns:
            Loaded GeneratedModule
        """
        ...

class SchemaLoader:
    """Class for constructing Schema objects from schema::Nodes.

    Wraps capnproto/c++/src/capnp/schema-loader.h directly.
    """
    def __init__(self) -> None: ...
    def get(self, id_: int) -> StructSchema:
        """Get a schema by its ID.

        Args:
            id_: Schema node ID

        Returns:
            The schema with the given ID
        """
        ...
    def load(self, reader: _DynamicStructReader) -> StructSchema:
        """Load a schema from a reader.

        Args:
            reader: DynamicStructReader containing schema data

        Returns:
            Loaded schema
        """
        ...
    def load_dynamic(self, reader: _DynamicStructReader) -> StructSchema:
        """Load a schema dynamically from a reader.

        Args:
            reader: DynamicStructReader containing schema data

        Returns:
            Loaded schema
        """
        ...

# Module loading and import hooks
def add_import_hook() -> None:
    """Add a hook to the Python import system.

    After calling this, Cap'n Proto modules can be directly imported
    like regular Python modules.
    """
    ...

def remove_import_hook() -> None:
    """Remove the import hook and return Python's import to normal."""
    ...

def load(
    file_name: str,
    display_name: str | None = None,
    imports: Sequence[str] = [],
) -> GeneratedModule:
    """Load a Cap'n Proto schema from a file.

    Args:
        file_name: Path to the .capnp file
        display_name: Optional display name for the module
        imports: List of import paths for resolving imports

    Returns:
        Loaded GeneratedModule with generated types
    """
    ...

def register_type(id: int, klass: type) -> None:
    """Register a type with the given schema ID.

    Args:
        id: Schema node ID
        klass: Python class to register
    """
    ...

def cleanup_global_schema_parser() -> None:
    """Unload all schemas from the current context."""
    ...

def deregister_all_types() -> None:
    """Deregister all registered types."""
    ...

def read_multiple_bytes_packed(
    buf: bytes,
    traversal_limit_in_words: int | None = None,
    nesting_limit: int | None = None,
) -> Iterator[_DynamicStructReader]:
    """Read multiple packed Cap'n Proto messages from a buffer.

    Returns an iterable that yields Readers for AnyPointer messages.

    Args:
        buf: Buffer containing packed messages
        traversal_limit_in_words: Optional limit on pointer dereferences
        nesting_limit: Optional limit on nesting depth

    Yields:
        DynamicStructReader for each message
    """
    ...

class _CapnpLibCapnpModule:
    """The capnp.lib.capnp submodule containing implementation classes.

    This module contains the low-level C++ wrapper classes.
    """

    # Dynamic types
    _DynamicStructReader: type[_DynamicStructReader]
    _DynamicStructBuilder: type[_DynamicStructBuilder]
    _DynamicListReader: type[_DynamicListReader]
    _DynamicListBuilder: type[_DynamicListBuilder]

    # Schema types
    _ListSchema: type[_ListSchema]
    _StructSchema: type[_StructSchema]

    # RPC types
    _Request: type[_Request]
    _Response: type[_Response]
    _CallContext: type[_CallContext]
    _DynamicCapabilityClient: type[_DynamicCapabilityClient]
    _DynamicCapabilityServer: type[_DynamicCapabilityServer]

    # Exception types
    KjException: type[KjException]

    # Parser types
    SchemaParser: type[SchemaParser]
    SchemaLoader: type[SchemaLoader]

    # RPC classes
    TwoPartyClient: type[TwoPartyClient]
    TwoPartyServer: type[TwoPartyServer]
    AsyncIoStream: type[AsyncIoStream]

class _CapnpLibModule:
    """The capnp.lib submodule."""

    capnp: _CapnpLibCapnpModule

class _CapnpLib:
    """The capnp.lib namespace.

    Provides access to low-level Cap'n Proto implementation classes.
    """

    capnp: _CapnpLibCapnpModule

lib: _CapnpLib

class _DynamicListBuilder(Generic[T]):
    """Generic list builder type returned by init() for list fields.

    This class wraps the Cap'n Proto C++ DynamicList::Builder.
    Provides list-like interface for building Cap'n Proto list fields.
    """
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> T: ...
    def __setitem__(self, index: int, value: T) -> None: ...
    def __iter__(self) -> Iterator[T]: ...
    def adopt(self, index: int, orphan: Any) -> None:
        """Adopt an orphaned message at the given index."""
        ...
    def disown(self, index: int) -> Any:
        """Disown the element at the given index, returning an orphan."""
        ...
    def init(self, index: int, size: int) -> Any:
        """Initialize a struct or list element at the given index with the given size."""
        ...

class _DynamicListReader(Generic[T_co]):
    """Generic list reader type for reading Cap'n Proto list fields.

    This class wraps the Cap'n Proto C++ DynamicList::Reader.
    Provides read-only list-like interface.
    """
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> T_co: ...
    def __iter__(self) -> Iterator[T_co]: ...

# RPC Classes
I_co = TypeVar("I_co")

class CastableBootstrap(Protocol):
    def cast_as(self, interface: type[I_co]) -> I_co: ...

class TwoPartyClient:
    """Two-party RPC client for Cap'n Proto.

    Args:
        socket: AsyncIoStream connection
        traversal_limit_in_words: Optional limit on pointer dereferences
        nesting_limit: Optional limit on nesting depth
    """
    def __init__(
        self,
        socket: AsyncIoStream | None = None,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> None: ...
    def bootstrap(self) -> CastableBootstrap:
        """Get the bootstrap interface for this client."""
        ...
    def close(self) -> None:
        """Close the client connection."""
        ...
    async def on_disconnect(self) -> None:
        """Wait until the connection is disconnected."""
        ...

class TwoPartyServer:
    """Two-party RPC server for Cap'n Proto.

    Args:
        socket: AsyncIoStream connection
        bootstrap: Bootstrap interface implementation
        traversal_limit_in_words: Optional limit on pointer dereferences
        nesting_limit: Optional limit on nesting depth
    """
    def __init__(
        self,
        socket: AsyncIoStream | None = None,
        bootstrap: Any = None,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> None: ...
    def close(self) -> None:
        """Close the server connection."""
        ...
    async def on_disconnect(self) -> None:
        """Wait until the connection is disconnected."""
        ...

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
    """Async I/O stream wrapper for Cap'n Proto RPC.

    Provides async I/O operations for Cap'n Proto RPC over TCP and Unix domain sockets.
    """
    @staticmethod
    async def create_connection(host: str | None = None, port: int | None = None, **kwargs: Any) -> AsyncIoStream:
        """Create an async TCP connection.

        Args:
            host: Hostname to connect to
            port: Port number to connect to
            **kwargs: Additional connection options

        Returns:
            AsyncIoStream connected to the server
        """
        ...

    @staticmethod
    async def create_unix_connection(path: str | None = None, **kwargs: Any) -> AsyncIoStream:
        """Create an async Unix domain socket connection.

        Args:
            path: Path to Unix domain socket
            **kwargs: Additional connection options

        Returns:
            AsyncIoStream connected to the server
        """
        ...

    @staticmethod
    async def create_server(
        callback: Callable[[AsyncIoStream], Awaitable[None]],
        host: str | None = None,
        port: int | None = None,
        **kwargs: Any,
    ) -> Server:
        """Create an async TCP server.

        Args:
            callback: Async callback function for each new connection
            host: Hostname to bind to
            port: Port number to bind to
            **kwargs: Additional server options

        Returns:
            Server instance
        """
        ...

    @staticmethod
    async def create_unix_server(
        callback: Callable[[AsyncIoStream], Awaitable[None]], path: str | None = None, **kwargs: Any
    ) -> Server:
        """Create an async Unix domain socket server.

        Args:
            callback: Async callback function for each new connection
            path: Path for Unix domain socket
            **kwargs: Additional server options

        Returns:
            Server instance
        """
        ...

    def close(self) -> None:
        """Close the stream."""
        ...

    async def wait_closed(self) -> None:
        """Wait until the stream is closed."""
        ...

# Async utilities
async def run(coro: Awaitable[T]) -> T:
    """Run an async coroutine with Cap'n Proto event loop.

    Ensures that the coroutine runs while the KJ event loop is running.

    Args:
        coro: Coroutine to run

    Returns:
        The result of the coroutine
    """
    ...

@contextmanager
def kj_loop() -> Iterator[None]:
    """Context manager for running the KJ event loop.

    Usage:
        with capnp.kj_loop():
            # Run async code
            pass
    """
    ...

__all__ = [
    # Schema types
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
    "FieldNode",
    "GeneratedModule",
    "InterfaceMethod",
    "InterfaceRuntime",
    "InterfaceSchema",
    "ListElementType",
    "ListSchema",
    "ListType",
    "NestedNode",
    "ParameterNode",
    "SchemaNode",
    "SchemaParser",
    "SchemaLoader",
    "SlotNode",
    "SlotRuntime",
    "StructNode",
    "StructRuntime",
    "StructSchema",
    "StructType",
    "TypeReader",
    # Dynamic types
    "_DynamicListBuilder",
    "_DynamicListReader",
    "_DynamicStructBuilder",
    "_DynamicStructReader",
    "_ListSchema",
    "_StructSchema",
    # RPC types
    "_Request",
    "_Response",
    "_CallContext",
    "_DynamicCapabilityClient",
    "_DynamicCapabilityServer",
    "CastableBootstrap",
    "TwoPartyClient",
    "TwoPartyServer",
    "Server",
    "AsyncIoStream",
    # Exceptions
    "KjException",
    # Functions
    "add_import_hook",
    "cleanup_global_schema_parser",
    "deregister_all_types",
    "kj_loop",
    "load",
    "read_multiple_bytes_packed",
    "register_type",
    "remove_import_hook",
    "run",
    # Module
    "lib",
]
