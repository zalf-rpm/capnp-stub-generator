"""This is an automatically generated stub for `addressbook.capnp`."""

from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicListBuilder,
    _DynamicListReader,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _EnumSchema,
    _ListSchema,
    _StructModule,
    _StructSchema,
    _StructSchemaField,
)

qux: int

class PhoneNumberReader(_DynamicStructReader):
    @property
    def number(self) -> str: ...
    @property
    def type(self) -> PersonPhoneNumberTypeEnum: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> PhoneNumberBuilder: ...

class PhoneNumberBuilder(_DynamicStructBuilder):
    @property
    def number(self) -> str: ...
    @number.setter
    def number(self, value: str) -> None: ...
    @property
    def type(self) -> PersonPhoneNumberTypeEnum: ...
    @type.setter
    def type(self, value: PersonPhoneNumberTypeEnum) -> None: ...
    @override
    def as_reader(self) -> PhoneNumberReader: ...

class _PhoneNumberList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> PhoneNumberReader: ...
        @override
        def __iter__(self) -> Iterator[PhoneNumberReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> PhoneNumberBuilder: ...
        @override
        def __setitem__(self, key: int, value: PhoneNumberReader | PhoneNumberBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[PhoneNumberBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> PhoneNumberBuilder: ...

class PersonEmploymentReader(_DynamicStructReader):
    @property
    def unemployed(self) -> None: ...
    @property
    def employer(self) -> str: ...
    @property
    def school(self) -> str: ...
    @property
    def selfEmployed(self) -> None: ...
    @override
    def which(self) -> Literal["unemployed", "employer", "school", "selfEmployed"]: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> PersonEmploymentBuilder: ...

class PersonEmploymentBuilder(_DynamicStructBuilder):
    @property
    def unemployed(self) -> None: ...
    @unemployed.setter
    def unemployed(self, value: None) -> None: ...
    @property
    def employer(self) -> str: ...
    @employer.setter
    def employer(self, value: str) -> None: ...
    @property
    def school(self) -> str: ...
    @school.setter
    def school(self, value: str) -> None: ...
    @property
    def selfEmployed(self) -> None: ...
    @selfEmployed.setter
    def selfEmployed(self, value: None) -> None: ...
    @override
    def which(self) -> Literal["unemployed", "employer", "school", "selfEmployed"]: ...
    @override
    def as_reader(self) -> PersonEmploymentReader: ...

class PersonTestGroupReader(_DynamicStructReader):
    @property
    def field1(self) -> int: ...
    @property
    def field2(self) -> int: ...
    @property
    def field3(self) -> int: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> PersonTestGroupBuilder: ...

class PersonTestGroupBuilder(_DynamicStructBuilder):
    @property
    def field1(self) -> int: ...
    @field1.setter
    def field1(self, value: int) -> None: ...
    @property
    def field2(self) -> int: ...
    @field2.setter
    def field2(self, value: int) -> None: ...
    @property
    def field3(self) -> int: ...
    @field3.setter
    def field3(self, value: int) -> None: ...
    @override
    def as_reader(self) -> PersonTestGroupReader: ...

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
            type: PersonPhoneNumberTypeEnum | None = None,
            **kwargs: object,
        ) -> PhoneNumberBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[PhoneNumberReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[PhoneNumberReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[PhoneNumberBuilder]: ...
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
        ) -> PhoneNumberReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> PhoneNumberReader: ...

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
        ) -> PersonEmploymentBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[PersonEmploymentReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[PersonEmploymentReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[PersonEmploymentBuilder]: ...
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
        ) -> PersonEmploymentReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> PersonEmploymentReader: ...

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
        ) -> PersonTestGroupBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[PersonTestGroupReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[PersonTestGroupReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[PersonTestGroupBuilder]: ...
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
        ) -> PersonTestGroupReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> PersonTestGroupReader: ...

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
        phones: PhoneNumberListBuilder | dict[str, Any] | None = None,
        employment: PersonEmploymentBuilder | dict[str, Any] | None = None,
        testGroup: PersonTestGroupBuilder | dict[str, Any] | None = None,
        extraData: bytes | None = None,
        **kwargs: object,
    ) -> PersonBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[PersonReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[PersonReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[PersonBuilder]: ...
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
    ) -> PersonReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> PersonReader: ...

class PersonReader(_DynamicStructReader):
    @property
    def id(self) -> int: ...
    @property
    def name(self) -> str: ...
    @property
    def email(self) -> str: ...
    @property
    def phones(self) -> PhoneNumberListReader: ...
    @property
    def employment(self) -> PersonEmploymentReader: ...
    @property
    def testGroup(self) -> PersonTestGroupReader: ...
    @property
    def extraData(self) -> bytes: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> PersonBuilder: ...

class PersonBuilder(_DynamicStructBuilder):
    @property
    def id(self) -> int: ...
    @id.setter
    def id(self, value: int) -> None: ...
    @property
    def name(self) -> str: ...
    @name.setter
    def name(self, value: str) -> None: ...
    @property
    def email(self) -> str: ...
    @email.setter
    def email(self, value: str) -> None: ...
    @property
    def phones(self) -> PhoneNumberListBuilder: ...
    @phones.setter
    def phones(self, value: PhoneNumberListBuilder | PhoneNumberListReader | dict[str, Any]) -> None: ...
    @property
    def employment(self) -> PersonEmploymentBuilder: ...
    @employment.setter
    def employment(self, value: PersonEmploymentBuilder | PersonEmploymentReader | dict[str, Any]) -> None: ...
    @property
    def testGroup(self) -> PersonTestGroupBuilder: ...
    @testGroup.setter
    def testGroup(self, value: PersonTestGroupBuilder | PersonTestGroupReader | dict[str, Any]) -> None: ...
    @property
    def extraData(self) -> bytes: ...
    @extraData.setter
    def extraData(self, value: bytes) -> None: ...
    @override
    @overload
    def init(self, field: Literal["employment"], size: int | None = None) -> PersonEmploymentBuilder: ...
    @overload
    def init(self, field: Literal["testGroup"], size: int | None = None) -> PersonTestGroupBuilder: ...
    @overload
    def init(self, field: Literal["phones"], size: int | None = None) -> PhoneNumberListBuilder: ...
    @overload
    def init(self, field: str, size: int | None = None) -> Any: ...
    @override
    def as_reader(self) -> PersonReader: ...

Person: _PersonStructModule

class _PersonList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> PersonReader: ...
        @override
        def __iter__(self) -> Iterator[PersonReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> PersonBuilder: ...
        @override
        def __setitem__(self, key: int, value: PersonReader | PersonBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[PersonBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> PersonBuilder: ...

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
        people: PersonListBuilder | dict[str, Any] | None = None,
        **kwargs: object,
    ) -> AddressBookBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[AddressBookReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[AddressBookReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[AddressBookBuilder]: ...
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
    ) -> AddressBookReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AddressBookReader: ...

class AddressBookReader(_DynamicStructReader):
    @property
    def people(self) -> PersonListReader: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> AddressBookBuilder: ...

class AddressBookBuilder(_DynamicStructBuilder):
    @property
    def people(self) -> PersonListBuilder: ...
    @people.setter
    def people(self, value: PersonListBuilder | PersonListReader | dict[str, Any]) -> None: ...
    @override
    def init(self, field: Literal["people"], size: int | None = None) -> PersonListBuilder: ...
    @override
    def as_reader(self) -> AddressBookReader: ...

AddressBook: _AddressBookStructModule

# Top-level type aliases for use in type annotations
type PersonListBuilder = _PersonList.Builder
type PersonListReader = _PersonList.Reader
type PersonPhoneNumberTypeEnum = int | Literal["mobile", "home", "work"]
type PhoneNumberListBuilder = _PhoneNumberList.Builder
type PhoneNumberListReader = _PhoneNumberList.Reader
