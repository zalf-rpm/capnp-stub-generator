# Import submodules
from capnp import lib, version

# Import the types module from lib.capnp where it's actually defined
from capnp.lib.capnp import (
    # Public classes
    AsyncIoStream,
    # Exception classes
    KjException,
    SchemaLoader,
    SchemaParser,
    TwoPartyClient,
    TwoPartyServer,
    # Internal classes and functions that are re-exported
    _CapabilityClient,
    _DynamicCapabilityClient,
    _DynamicListBuilder,
    _DynamicListReader,
    _DynamicOrphan,
    _DynamicResizableListBuilder,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _EventLoop,
    _init_capnp_api,
    _InterfaceModule,
    _ListSchema,
    _MallocMessageBuilder,
    _PackedFdMessageReader,
    _PyCustomMessageBuilder,
    _StreamFdMessageReader,
    _StructModule,
    _write_message_to_fd,
    _write_packed_message_to_fd,
    # Public functions
    add_import_hook,
    cleanup_global_schema_parser,
    deregister_all_types,
    fill_context,
    kj_loop,
    load,
    read_multiple_bytes_packed,
    register_type,
    remove_import_hook,
    run,
    types,
    void_task_done_callback,
)

# Re-export everything from lib.capnp that's part of the public API
# Version string
from capnp.version import version as __version__

# Shared schema loader for embedded schema modules
# This is set dynamically when embedded schema modules are imported
_embedded_schema_loader: SchemaLoader

__all__ = [
    # Public classes
    "AsyncIoStream",
    # Exception class
    "KjException",
    "SchemaLoader",
    "SchemaParser",
    "TwoPartyClient",
    "TwoPartyServer",
    # Internal classes that are exposed but prefixed with underscore
    "_CapabilityClient",
    "_DynamicCapabilityClient",
    "_DynamicListBuilder",
    "_DynamicListReader",
    "_DynamicOrphan",
    "_DynamicResizableListBuilder",
    "_DynamicStructBuilder",
    "_DynamicStructReader",
    "_EventLoop",
    "_InterfaceModule",
    "_ListSchema",
    "_MallocMessageBuilder",
    "_PackedFdMessageReader",
    "_PyCustomMessageBuilder",
    "_StreamFdMessageReader",
    "_StructModule",
    # Version string
    "__version__",
    "_init_capnp_api",
    "_write_message_to_fd",
    "_write_packed_message_to_fd",
    # Public functions
    "add_import_hook",
    "cleanup_global_schema_parser",
    "deregister_all_types",
    "fill_context",
    "kj_loop",
    # Modules
    "lib",
    "load",
    "read_multiple_bytes_packed",
    "register_type",
    "remove_import_hook",
    "run",
    "types",
    "version",
    "void_task_done_callback",
]
