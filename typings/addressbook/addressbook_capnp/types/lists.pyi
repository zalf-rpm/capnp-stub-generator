"""List helper types for `addressbook.capnp`."""

from collections.abc import Iterator
from typing import Any, override

from capnp.lib.capnp import (
    _DynamicListBuilder,
    _DynamicListReader,
)

from . import builders as builders
from . import readers as readers

class _PhoneNumberList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> readers.PhoneNumberReader: ...
        @override
        def __iter__(self) -> Iterator[readers.PhoneNumberReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> builders.PhoneNumberBuilder: ...
        @override
        def __setitem__(
            self,
            key: int,
            value: readers.PhoneNumberReader | builders.PhoneNumberBuilder | dict[str, Any],
        ) -> None: ...
        @override
        def __iter__(self) -> Iterator[builders.PhoneNumberBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> builders.PhoneNumberBuilder: ...

class _PersonList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> readers.PersonReader: ...
        @override
        def __iter__(self) -> Iterator[readers.PersonReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> builders.PersonBuilder: ...
        @override
        def __setitem__(
            self,
            key: int,
            value: readers.PersonReader | builders.PersonBuilder | dict[str, Any],
        ) -> None: ...
        @override
        def __iter__(self) -> Iterator[builders.PersonBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> builders.PersonBuilder: ...
