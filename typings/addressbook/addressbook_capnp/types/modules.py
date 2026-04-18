"""Runtime placeholder module for module helper types of `addressbook.capnp`."""

# pyright: reportUnusedClass=none

from __future__ import annotations

from capnp.lib.capnp import _StructModule


class _PersonStructModule(_StructModule):
    class _PhoneNumberStructModule(_StructModule):
        pass


class _AddressBookStructModule(_StructModule):
    pass
