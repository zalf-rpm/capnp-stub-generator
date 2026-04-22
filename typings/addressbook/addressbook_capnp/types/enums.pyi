"""Enum helper aliases for `addressbook.capnp`."""

from typing import Literal

type PersonPhoneNumberTypeEnum = int | Literal["mobile", "home", "work"]
