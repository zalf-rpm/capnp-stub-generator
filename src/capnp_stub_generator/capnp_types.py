"""Types definitions that are common in capnproto schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from capnp.lib.capnp import (
        _EnumSchema,
        _InterfaceSchema,
        _ParsedSchema,
        _StructSchema,
    )

CAPNP_TYPE_TO_PYTHON = {
    "void": "None",
    "bool": "bool",
    "int8": "int",
    "int16": "int",
    "int32": "int",
    "int64": "int",
    "uint8": "int",
    "uint16": "int",
    "uint32": "int",
    "uint64": "int",
    "float32": "float",
    "float64": "float",
    "text": "str",
    "data": "bytes",
}


class CapnpFieldType:
    """Types of capnproto fields."""

    GROUP = "group"
    SLOT = "slot"


class CapnpElementType:
    """Types of capnproto elements."""

    ENUM = "enum"
    STRUCT = "struct"
    CONST = "const"
    LIST = "list"
    ANY_POINTER = "anyPointer"
    INTERFACE = "interface"


type SchemaRegistryType = dict[int, tuple[str, "_ParsedSchema"]]
type SchemaType = _ParsedSchema | _StructSchema | _EnumSchema | _InterfaceSchema
