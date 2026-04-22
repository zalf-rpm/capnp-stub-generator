"""Client result helper types for `fbp_nested_callback.capnp`."""

from collections.abc import Awaitable
from typing import Protocol

from .. import clients as clients

class UnregResult(Awaitable[UnregResult], Protocol):
    success: bool

class StatusResult(Awaitable[None], Protocol): ...

class RegisterstatscallbackResult(Awaitable[RegisterstatscallbackResult], Protocol):
    unregisterCallback: clients.UnregisterClient
