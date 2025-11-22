"""Internal types for pycapnp stubs - NOT part of public API.

This module contains internal type definitions including:
- Protocol classes for schema nodes that exist in the pycapnp runtime
- TypeVars used in generic types
- Helper types for type annotations

These are imported by lib/capnp.pyi for type annotations but NOT re-exported.
"""

from __future__ import annotations

import asyncio
import types

from .lib.capnp import SchemaParser, _NodeReader, _ParsedSchema, _SchemaType

# Protocol classes for types imported from capnp runtime

class CapnpTypesModule:
    Void: _SchemaType
    Bool: _SchemaType
    Int8: _SchemaType
    Int16: _SchemaType
    Int32: _SchemaType
    Int64: _SchemaType
    UInt8: _SchemaType
    UInt16: _SchemaType
    UInt32: _SchemaType
    UInt64: _SchemaType
    Float32: _SchemaType
    Float64: _SchemaType
    Text: _SchemaType
    Data: _SchemaType
    AnyPointer: _SchemaType

class CapnpModule(types.ModuleType):
    schema: _ParsedSchema
    _nodeSchema: _ParsedSchema
    _nodeProto: _NodeReader
    _parser: SchemaParser

# Re-export commonly used types
Server = asyncio.Server
