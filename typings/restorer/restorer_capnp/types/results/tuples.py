"""Runtime placeholder module for result tuple helpers of `restorer.capnp`."""

# pyright: reportUnusedClass=none

from typing import NamedTuple


class GetanylistResultTuple(NamedTuple):
    l: object


class GetanypointerResultTuple(NamedTuple):
    p: object


class GetanystructResultTuple(NamedTuple):
    s: object


class GetvalueResultTuple(NamedTuple):
    value: object


class GetanytesterResultTuple(NamedTuple):
    tester: object


class RestoreResultTuple(NamedTuple):
    cap: object


__all__ = [
    "GetanylistResultTuple",
    "GetanypointerResultTuple",
    "GetanystructResultTuple",
    "GetanytesterResultTuple",
    "GetvalueResultTuple",
    "RestoreResultTuple",
]
