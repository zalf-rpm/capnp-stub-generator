"""Runtime placeholder module for result tuple helpers of `single_value.capnp`."""

from typing import NamedTuple


class GetanyResultTuple(NamedTuple):
    val: object


class GetboolResultTuple(NamedTuple):
    val: object


class GetdataResultTuple(NamedTuple):
    val: object


class GetfloatResultTuple(NamedTuple):
    val: object


class GetintResultTuple(NamedTuple):
    val: object


class GetinterfaceResultTuple(NamedTuple):
    val: object


class GetlistResultTuple(NamedTuple):
    val: object


class GetliststructResultTuple(NamedTuple):
    val: object


class GetstructResultTuple(NamedTuple):
    val: object


class GettextResultTuple(NamedTuple):
    val: object


__all__ = [
    "GetanyResultTuple",
    "GetboolResultTuple",
    "GetdataResultTuple",
    "GetfloatResultTuple",
    "GetintResultTuple",
    "GetinterfaceResultTuple",
    "GetlistResultTuple",
    "GetliststructResultTuple",
    "GetstructResultTuple",
    "GettextResultTuple",
]
