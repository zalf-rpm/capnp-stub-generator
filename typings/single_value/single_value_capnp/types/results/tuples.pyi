"""Result tuple helper types for `single_value.capnp`."""

from collections.abc import Sequence
from typing import Any, NamedTuple

from .. import builders as builders
from .. import clients as clients
from .. import common as common
from .. import modules as modules
from .. import readers as readers

class GetboolResultTuple(NamedTuple):
    val: bool

class GetintResultTuple(NamedTuple):
    val: int

class GetfloatResultTuple(NamedTuple):
    val: float

class GettextResultTuple(NamedTuple):
    val: str

class GetdataResultTuple(NamedTuple):
    val: bytes

class GetlistResultTuple(NamedTuple):
    val: builders.Int32ListBuilder | readers.Int32ListReader | Sequence[int]

class GetstructResultTuple(NamedTuple):
    val: builders.MyStructBuilder | readers.MyStructReader | dict[str, Any]

class GetinterfaceResultTuple(NamedTuple):
    val: modules._SingleValueInterfaceModule.Server | clients.SingleValueClient

class GetanyResultTuple(NamedTuple):
    val: common.AnyPointer

class GetliststructResultTuple(NamedTuple):
    val: (
        builders.MyStructListBuilder
        | readers.MyStructListReader
        | Sequence[readers.MyStructReader | builders.MyStructBuilder | dict[str, Any]]
    )
