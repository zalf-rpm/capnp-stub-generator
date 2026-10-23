"""This is an automatically generated stub for `fbp_nested_callback.capnp`."""

from collections.abc import Sequence
from types import ModuleType as _ModuleType

from capnp.lib.capnp import _Schema

from . import types as types

def get_schema_by_id(schema_id: int) -> _Schema: ...
def load_capnp_file(path: str, imports: Sequence[str] = ...) -> _ModuleType: ...

Channel: types.modules._ChannelInterfaceModule

__all__ = ["Channel", "get_schema_by_id", "load_capnp_file", "types"]
