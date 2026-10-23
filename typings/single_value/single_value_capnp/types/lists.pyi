"""List helper types for `single_value.capnp`."""

from collections.abc import Iterator
from typing import Any, override

from capnp.lib.capnp import (
    _DynamicListBuilder,
    _DynamicListReader,
)

from . import builders as builders
from . import readers as readers

class _Int32List:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, index: int) -> int: ...
        def __iter__(self) -> Iterator[int]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, index: int) -> int: ...
        @override
        def __setitem__(self, index: int, value: int) -> None: ...
        def __iter__(self) -> Iterator[int]: ...

class _MyStructList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, index: int) -> readers.MyStructReader: ...
        def __iter__(self) -> Iterator[readers.MyStructReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, index: int) -> builders.MyStructBuilder: ...
        @override
        def __setitem__(
            self,
            index: int,
            value: readers.MyStructReader | builders.MyStructBuilder | dict[str, Any],
        ) -> None: ...
        def __iter__(self) -> Iterator[builders.MyStructBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> builders.MyStructBuilder: ...
