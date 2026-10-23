"""Common typing aliases for `addressbook.capnp`."""

from typing import Literal, override

from capnp.lib.capnp import _DynamicEnumField, _StructModuleWhich

class _PersonEmploymentModuleWhich(_StructModuleWhich):
    unemployed: _PersonEmploymentModuleWhich
    employer: _PersonEmploymentModuleWhich
    school: _PersonEmploymentModuleWhich
    selfEmployed: _PersonEmploymentModuleWhich

class _PersonEmploymentWhich(_DynamicEnumField):
    @override
    def __call__(self) -> Literal["unemployed", "employer", "school", "selfEmployed"]: ...
