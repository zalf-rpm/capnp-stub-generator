"""Module helper types for `addressbook.capnp`."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicStructBuilder,
    _DynamicStructReader,
    _EnumSchema,
    _ListSchema,
    _StructModule,
    _StructSchema,
    _StructSchemaField,
)

from . import _all as _all

class _PersonStructModule(_StructModule):
    class _PhoneNumberStructModule(_StructModule):
        class _TypeEnumModule:
            mobile: int
            home: int
            work: int

        Type: _TypeEnumModule
        class Reader(_DynamicStructReader): ...
        class Builder(_DynamicStructBuilder): ...

        class _PhoneNumberSchema(_StructSchema):
            class _TypeField(_StructSchemaField):
                @property
                @override
                def schema(self) -> _EnumSchema: ...

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
        def schema(self) -> _PersonStructModule._PhoneNumberStructModule._PhoneNumberSchema: ...
        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            number: str | None = None,
            type: _all.PersonPhoneNumberTypeEnum | None = None,
            **kwargs: object,
        ) -> _all.PhoneNumberBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[_all.PhoneNumberReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[_all.PhoneNumberReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[_all.PhoneNumberBuilder]: ...
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
        ) -> _all.PhoneNumberReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _all.PhoneNumberReader: ...

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
        def schema(self) -> _PersonStructModule._PersonEmploymentStructModule._PersonEmploymentSchema: ...
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
        ) -> _all.PersonEmploymentBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[_all.PersonEmploymentReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[_all.PersonEmploymentReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[_all.PersonEmploymentBuilder]: ...
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
        ) -> _all.PersonEmploymentReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _all.PersonEmploymentReader: ...

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
        def schema(self) -> _PersonStructModule._PersonTestGroupStructModule._PersonTestGroupSchema: ...
        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            field1: int | None = None,
            field2: int | None = None,
            field3: int | None = None,
            **kwargs: object,
        ) -> _all.PersonTestGroupBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[_all.PersonTestGroupReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[_all.PersonTestGroupReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[_all.PersonTestGroupBuilder]: ...
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
        ) -> _all.PersonTestGroupReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> _all.PersonTestGroupReader: ...

    PersonTestGroup: _PersonTestGroupStructModule
    class Reader(_DynamicStructReader): ...
    class Builder(_DynamicStructBuilder): ...

    class _PersonSchema(_StructSchema):
        class _PhonesField(_StructSchemaField):
            class _Schema(_ListSchema):
                @property
                @override
                def elementType(self) -> _PersonStructModule._PhoneNumberStructModule._PhoneNumberSchema: ...

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
    def schema(self) -> _PersonStructModule._PersonSchema: ...
    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        id: int | None = None,
        name: str | None = None,
        email: str | None = None,
        phones: _all.PhoneNumberListBuilder | dict[str, Any] | None = None,
        employment: _all.PersonEmploymentBuilder | dict[str, Any] | None = None,
        testGroup: _all.PersonTestGroupBuilder | dict[str, Any] | None = None,
        extraData: bytes | None = None,
        **kwargs: object,
    ) -> _all.PersonBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[_all.PersonReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[_all.PersonReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[_all.PersonBuilder]: ...
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
    ) -> _all.PersonReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> _all.PersonReader: ...

class _AddressBookStructModule(_StructModule):
    class Reader(_DynamicStructReader): ...
    class Builder(_DynamicStructBuilder): ...

    class _AddressBookSchema(_StructSchema):
        class _PeopleField(_StructSchemaField):
            class _Schema(_ListSchema):
                @property
                @override
                def elementType(self) -> _PersonStructModule._PersonSchema: ...

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
    def schema(self) -> _AddressBookStructModule._AddressBookSchema: ...
    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        people: _all.PersonListBuilder | dict[str, Any] | None = None,
        **kwargs: object,
    ) -> _all.AddressBookBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[_all.AddressBookReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[_all.AddressBookReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[_all.AddressBookBuilder]: ...
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
    ) -> _all.AddressBookReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> _all.AddressBookReader: ...
