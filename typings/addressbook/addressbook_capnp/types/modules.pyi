"""Module helper types for `addressbook.capnp`."""

from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicStructBuilder,
    _DynamicStructReader,
    _EnumModule,
    _EnumSchema,
    _ListSchema,
    _StructModule,
    _StructSchema,
    _StructSchemaField,
)

from . import builders as builders
from . import enums as enums
from . import readers as readers
from . import schemas as schemas

class _PersonStructModule(_StructModule):
    class _PhoneNumberStructModule(_StructModule):
        class _TypeEnumModule(_EnumModule):
            mobile: int
            home: int
            work: int

            class _TypeSchema(_EnumSchema): ...

            @property
            @override
            def schema(self) -> schemas._PersonPhoneNumberTypeEnumSchema: ...

        Type: _TypeEnumModule
        class Reader(_DynamicStructReader): ...
        class Builder(_DynamicStructBuilder): ...

        class _PhoneNumberSchema(_StructSchema):
            class _TypeField(_StructSchemaField):
                @property
                @override
                def schema(self) -> schemas._PersonPhoneNumberTypeEnumSchema: ...

            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["number"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(
                    self,
                    key: Literal["type"],
                ) -> _PersonStructModule._PhoneNumberStructModule._PhoneNumberSchema._TypeField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(self) -> _PersonStructModule._PhoneNumberStructModule._PhoneNumberSchema._Fields: ...

        @property
        @override
        def schema(self) -> schemas._PersonPhoneNumberSchema: ...
        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            number: str | None = None,
            type: enums.PersonPhoneNumberTypeEnum | None = None,
            **kwargs: object,
        ) -> builders.PhoneNumberBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[readers.PhoneNumberReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[readers.PhoneNumberReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[builders.PhoneNumberBuilder]: ...
        @override
        def from_bytes_packed(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _DynamicStructReader: ...
        @override
        def read(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> readers.PhoneNumberReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> readers.PhoneNumberReader: ...

    PhoneNumber: _PhoneNumberStructModule
    class _PersonEmploymentStructModule(_StructModule):
        class Reader(_DynamicStructReader): ...
        class Builder(_DynamicStructBuilder): ...

        class _PersonEmploymentSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["unemployed"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: Literal["employer"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: Literal["school"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: Literal["selfEmployed"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(self) -> _PersonStructModule._PersonEmploymentStructModule._PersonEmploymentSchema._Fields: ...

        @property
        @override
        def schema(self) -> schemas._PersonPersonEmploymentSchema: ...
        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            unemployed: None | None = None,
            employer: str | None = None,
            school: str | None = None,
            selfEmployed: None | None = None,
            **kwargs: object,
        ) -> builders.PersonEmploymentBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[readers.PersonEmploymentReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[readers.PersonEmploymentReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[builders.PersonEmploymentBuilder]: ...
        @override
        def from_bytes_packed(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _DynamicStructReader: ...
        @override
        def read(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> readers.PersonEmploymentReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> readers.PersonEmploymentReader: ...

    PersonEmployment: _PersonEmploymentStructModule
    class _PersonTestGroupStructModule(_StructModule):
        class Reader(_DynamicStructReader): ...
        class Builder(_DynamicStructBuilder): ...

        class _PersonTestGroupSchema(_StructSchema):
            class _Fields(dict[str, _StructSchemaField]):
                @overload
                def __getitem__(self, key: Literal["field1"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: Literal["field2"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: Literal["field3"]) -> _StructSchemaField: ...
                @overload
                def __getitem__(self, key: str) -> _StructSchemaField: ...

            @property
            @override
            def fields(self) -> _PersonStructModule._PersonTestGroupStructModule._PersonTestGroupSchema._Fields: ...

        @property
        @override
        def schema(self) -> schemas._PersonPersonTestGroupSchema: ...
        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            field1: int | None = None,
            field2: int | None = None,
            field3: int | None = None,
            **kwargs: object,
        ) -> builders.PersonTestGroupBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[readers.PersonTestGroupReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[readers.PersonTestGroupReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[builders.PersonTestGroupBuilder]: ...
        @override
        def from_bytes_packed(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _DynamicStructReader: ...
        @override
        def read(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> readers.PersonTestGroupReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> readers.PersonTestGroupReader: ...

    PersonTestGroup: _PersonTestGroupStructModule
    class Reader(_DynamicStructReader): ...
    class Builder(_DynamicStructBuilder): ...

    class _PersonSchema(_StructSchema):
        class _PhonesField(_StructSchemaField):
            class _Schema(_ListSchema):
                @property
                @override
                def elementType(self) -> schemas._PersonPhoneNumberSchema: ...

            @property
            @override
            def schema(self) -> _PersonStructModule._PersonSchema._PhonesField._Schema: ...

        class _EmploymentField(_StructSchemaField):
            @property
            @override
            def schema(self) -> _StructSchema: ...

        class _TestGroupField(_StructSchemaField):
            @property
            @override
            def schema(self) -> _StructSchema: ...

        class _Fields(dict[str, _StructSchemaField]):
            @overload
            def __getitem__(self, key: Literal["id"]) -> _StructSchemaField: ...
            @overload
            def __getitem__(self, key: Literal["name"]) -> _StructSchemaField: ...
            @overload
            def __getitem__(self, key: Literal["email"]) -> _StructSchemaField: ...
            @overload
            def __getitem__(self, key: Literal["phones"]) -> _PersonStructModule._PersonSchema._PhonesField: ...
            @overload
            def __getitem__(
                self,
                key: Literal["employment"],
            ) -> _PersonStructModule._PersonSchema._EmploymentField: ...
            @overload
            def __getitem__(self, key: Literal["testGroup"]) -> _PersonStructModule._PersonSchema._TestGroupField: ...
            @overload
            def __getitem__(self, key: Literal["extraData"]) -> _StructSchemaField: ...
            @overload
            def __getitem__(self, key: str) -> _StructSchemaField: ...

        @property
        @override
        def fields(self) -> _PersonStructModule._PersonSchema._Fields: ...

    @property
    @override
    def schema(self) -> schemas._PersonSchema: ...
    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        id: int | None = None,
        name: str | None = None,
        email: str | None = None,
        phones: builders.PhoneNumberListBuilder
        | readers.PhoneNumberListReader
        | Sequence[readers.PhoneNumberReader | builders.PhoneNumberBuilder | dict[str, Any]]
        | None = None,
        employment: builders.PersonEmploymentBuilder | readers.PersonEmploymentReader | dict[str, Any] | None = None,
        testGroup: builders.PersonTestGroupBuilder | readers.PersonTestGroupReader | dict[str, Any] | None = None,
        extraData: bytes | None = None,
        **kwargs: object,
    ) -> builders.PersonBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[readers.PersonReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[readers.PersonReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[builders.PersonBuilder]: ...
    @override
    def from_bytes_packed(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> _DynamicStructReader: ...
    @override
    def read(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> readers.PersonReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> readers.PersonReader: ...

class _AddressBookStructModule(_StructModule):
    class Reader(_DynamicStructReader): ...
    class Builder(_DynamicStructBuilder): ...

    class _AddressBookSchema(_StructSchema):
        class _PeopleField(_StructSchemaField):
            class _Schema(_ListSchema):
                @property
                @override
                def elementType(self) -> schemas._PersonSchema: ...

            @property
            @override
            def schema(self) -> _AddressBookStructModule._AddressBookSchema._PeopleField._Schema: ...

        class _Fields(dict[str, _StructSchemaField]):
            @overload
            def __getitem__(
                self,
                key: Literal["people"],
            ) -> _AddressBookStructModule._AddressBookSchema._PeopleField: ...
            @overload
            def __getitem__(self, key: str) -> _StructSchemaField: ...

        @property
        @override
        def fields(self) -> _AddressBookStructModule._AddressBookSchema._Fields: ...

    @property
    @override
    def schema(self) -> schemas._AddressBookSchema: ...
    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        people: builders.PersonListBuilder
        | readers.PersonListReader
        | Sequence[readers.PersonReader | builders.PersonBuilder | dict[str, Any]]
        | None = None,
        **kwargs: object,
    ) -> builders.AddressBookBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[readers.AddressBookReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[readers.AddressBookReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[builders.AddressBookBuilder]: ...
    @override
    def from_bytes_packed(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> _DynamicStructReader: ...
    @override
    def read(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> readers.AddressBookReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> readers.AddressBookReader: ...
