"""This is an automatically generated stub for `restorer.capnp`."""

from collections.abc import Sequence

from capnp.lib.capnp import _Schema

from . import types as types

def get_schema_by_id(schema_id: int) -> _Schema: ...
def load_capnp_file(path: str, imports: Sequence[str] = ...) -> object: ...

Bag: types.modules._BagInterfaceModule
AnyTester: types.modules._AnyTesterInterfaceModule

Restorer: types.modules._RestorerInterfaceModule

__all__ = ["AnyTester", "Bag", "Restorer", "get_schema_by_id", "load_capnp_file", "types"]
