"""Builder helper types for `restorer.capnp`."""

from typing import override

from capnp.lib.capnp import (
    _DynamicStructBuilder,
)

from . import readers as readers

class RestoreParamsBuilder(_DynamicStructBuilder):
    @property
    def localRef(self) -> str: ...
    @localRef.setter
    def localRef(self, value: str) -> None: ...
    @override
    def as_reader(self) -> readers.RestoreParamsReader: ...
