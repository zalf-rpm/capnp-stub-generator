"""Result tuple helper types for `restorer.capnp`."""

from typing import NamedTuple

from .. import clients as clients
from .. import common as common
from .. import modules as modules

class GetvalueResultTuple(NamedTuple):
    value: str

class GetanystructResultTuple(NamedTuple):
    s: common.AnyStruct

class GetanylistResultTuple(NamedTuple):
    l: common.AnyList

class GetanypointerResultTuple(NamedTuple):
    p: common.AnyPointer

class RestoreResultTuple(NamedTuple):
    cap: common.Capability

class GetanytesterResultTuple(NamedTuple):
    tester: modules._AnyTesterInterfaceModule.Server | clients.AnyTesterClient
