"""Reader helper types for `addressbook.capnp`."""

from collections.abc import Callable
from typing import Literal, override

from capnp.lib.capnp import (
    _DynamicStructReader,
)

from . import builders as builders
from . import enums as enums
from . import lists as lists

class PhoneNumberReader(_DynamicStructReader):
    @property
    def number(self) -> str: ...
    @property
    def type(self) -> enums.PersonPhoneNumberTypeEnum: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> builders.PhoneNumberBuilder: ...

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
    ) -> builders.PersonEmploymentBuilder: ...

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
    ) -> builders.PersonTestGroupBuilder: ...

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
    ) -> builders.PersonBuilder: ...

class AddressBookReader(_DynamicStructReader):
    @property
    def people(self) -> PersonListReader: ...
    @override
    def as_builder(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
    ) -> builders.AddressBookBuilder: ...

type PersonListReader = lists._PersonList.Reader

type PhoneNumberListReader = lists._PhoneNumberList.Reader
