"""Enum helper aliases for `addressbook.capnp`."""

from typing import Literal, override

from capnp.lib.capnp import _DynamicEnum

class PersonPhoneNumberTypeValue(_DynamicEnum):
    @override
    def __str__(self) -> Literal["mobile", "home", "work"]: ...

type PersonPhoneNumberTypeEnum = int | Literal["mobile", "home", "work"]
