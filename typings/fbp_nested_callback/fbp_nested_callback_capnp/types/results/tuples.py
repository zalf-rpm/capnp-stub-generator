"""Runtime placeholder module for result tuple helpers of `fbp_nested_callback.capnp`."""

from typing import NamedTuple


class RegisterstatscallbackResultTuple(NamedTuple):
    unregisterCallback: object


class UnregResultTuple(NamedTuple):
    success: object


__all__ = ["RegisterstatscallbackResultTuple", "UnregResultTuple"]
