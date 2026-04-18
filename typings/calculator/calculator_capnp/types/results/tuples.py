"""Runtime placeholder module for result tuple helpers of `calculator.capnp`."""

# pyright: reportUnusedClass=none

from typing import NamedTuple


class DeffunctionResultTuple(NamedTuple):
    func: object


class EvaluateResultTuple(NamedTuple):
    value: object


class GetoperatorResultTuple(NamedTuple):
    func: object


class CallResultTuple(NamedTuple):
    value: object


class ReadResultTuple(NamedTuple):
    value: object


__all__ = [
    "CallResultTuple",
    "DeffunctionResultTuple",
    "EvaluateResultTuple",
    "GetoperatorResultTuple",
    "ReadResultTuple",
]
