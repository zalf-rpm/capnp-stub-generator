"""Server result helper types for `restorer.capnp`."""

from capnp.lib.capnp import (
    _DynamicStructBuilder,
)

from .. import clients as clients
from .. import common as common
from .. import modules as modules

class GetvalueServerResult(_DynamicStructBuilder):
    @property
    def value(self) -> str: ...
    @value.setter
    def value(self, value: str) -> None: ...

class GetanystructServerResult(_DynamicStructBuilder):
    @property
    def s(self) -> common.AnyStruct: ...
    @s.setter
    def s(self, value: common.AnyStruct) -> None: ...

class GetanylistServerResult(_DynamicStructBuilder):
    @property
    def l(self) -> common.AnyList: ...
    @l.setter
    def l(self, value: common.AnyList) -> None: ...

class GetanypointerServerResult(_DynamicStructBuilder):
    @property
    def p(self) -> common.AnyPointer: ...
    @p.setter
    def p(self, value: common.AnyPointer) -> None: ...

class RestoreServerResult(_DynamicStructBuilder):
    @property
    def cap(self) -> common.Capability: ...
    @cap.setter
    def cap(self, value: common.Capability) -> None: ...

class GetanytesterServerResult(_DynamicStructBuilder):
    @property
    def tester(self) -> modules._AnyTesterInterfaceModule.Server | clients.AnyTesterClient: ...
    @tester.setter
    def tester(self, value: modules._AnyTesterInterfaceModule.Server | clients.AnyTesterClient) -> None: ...
