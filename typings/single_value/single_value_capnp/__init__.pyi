"""This is an automatically generated stub for `single_value.capnp`."""

from collections.abc import Sequence
from types import ModuleType as _ModuleType

from capnp.lib.capnp import _Schema

from . import types as types

def get_schema_by_id(schema_id: int) -> _Schema: ...
def load_capnp_file(path: str, imports: Sequence[str] = ...) -> _ModuleType: ...

MyStruct: types.modules._MyStructStructModule

SingleValue: types.modules._SingleValueInterfaceModule

__all__ = ["MyStruct", "SingleValue", "get_schema_by_id", "load_capnp_file", "types"]
