"""This is an automatically generated stub for `calculator.capnp`."""

from collections.abc import Sequence

from capnp.lib.capnp import _Schema

from . import types as types

def get_schema_by_id(schema_id: int) -> _Schema: ...
def load_capnp_file(path: str, imports: Sequence[str] = ...) -> object: ...

Calculator: types.modules._CalculatorInterfaceModule

__all__ = ["Calculator", "get_schema_by_id", "load_capnp_file", "types"]
