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
        def __getitem__(self, key: int) -> int: ...
        @override
        def __iter__(self) -> Iterator[int]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> int: ...
        @override
        def __setitem__(self, key: int, value: int) -> None: ...
        @override
        def __iter__(self) -> Iterator[int]: ...

class _MyStructList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> readers.MyStructReader: ...
        @override
        def __iter__(self) -> Iterator[readers.MyStructReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> builders.MyStructBuilder: ...
        @override
        def __setitem__(
            self,
            key: int,
            value: readers.MyStructReader | builders.MyStructBuilder | dict[str, Any],
        ) -> None: ...
        @override
        def __iter__(self) -> Iterator[builders.MyStructBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> builders.MyStructBuilder: ...
