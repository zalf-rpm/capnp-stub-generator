"""This is an automatically generated stub for `addressbook.capnp`."""

from collections.abc import Sequence
from types import ModuleType as _ModuleType

from capnp.lib.capnp import _Schema

from . import types as types

def get_schema_by_id(schema_id: int) -> _Schema: ...
def load_capnp_file(path: str, imports: Sequence[str] = ...) -> _ModuleType: ...

qux: int
Person: types.modules._PersonStructModule
AddressBook: types.modules._AddressBookStructModule

__all__ = ["AddressBook", "Person", "get_schema_by_id", "load_capnp_file", "qux", "types"]
