"""This is an automatically generated stub for `schema_new.capnp`."""

from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from typing import IO, Any, Literal, overload, override

from capnp.lib.capnp import (
    _DynamicCapabilityClient,
    _DynamicCapabilityServer,
    _DynamicListBuilder,
    _DynamicListReader,
    _DynamicObjectBuilder,
    _DynamicObjectReader,
    _DynamicStructBuilder,
    _DynamicStructReader,
    _StructModule,
)

# Type alias for AnyPointer parameters (accepts all Cap'n Proto pointer types)
type AnyPointer = (
    str
    | bytes
    | _DynamicStructBuilder
    | _DynamicStructReader
    | _DynamicCapabilityClient
    | _DynamicCapabilityServer
    | _DynamicListBuilder
    | _DynamicListReader
    | _DynamicObjectReader
    | _DynamicObjectBuilder
)

class _MemberList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> MemberReader: ...
        @override
        def __iter__(self) -> Iterator[MemberReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> MemberBuilder: ...
        @override
        def __setitem__(self, key: int, value: MemberReader | MemberBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[MemberBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> MemberBuilder: ...

class _NestedNodeList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> NestedNodeReader: ...
        @override
        def __iter__(self) -> Iterator[NestedNodeReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> NestedNodeBuilder: ...
        @override
        def __setitem__(self, key: int, value: NestedNodeReader | NestedNodeBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[NestedNodeBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> NestedNodeBuilder: ...

class _ValueStructModule(_StructModule):
    class Reader(_DynamicStructReader):
        @property
        def void(self) -> None: ...
        @property
        def bool(self) -> bool: ...
        @property
        def int8(self) -> int: ...
        @property
        def int16(self) -> int: ...
        @property
        def int32(self) -> int: ...
        @property
        def int64(self) -> int: ...
        @property
        def uint8(self) -> int: ...
        @property
        def uint16(self) -> int: ...
        @property
        def uint32(self) -> int: ...
        @property
        def uint64(self) -> int: ...
        @property
        def float32(self) -> float: ...
        @property
        def float64(self) -> float: ...
        @property
        def text(self) -> str: ...
        @property
        def data(self) -> bytes: ...
        @property
        def list(self) -> _DynamicObjectReader: ...
        @property
        def enum(self) -> int: ...
        @property
        def struct(self) -> _DynamicObjectReader: ...
        @property
        def interface(self) -> None: ...
        @property
        def anyPointer(self) -> _DynamicObjectReader: ...
        @override
        def which(
            self,
        ) -> Literal[
            "void",
            "bool",
            "int8",
            "int16",
            "int32",
            "int64",
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "float32",
            "float64",
            "text",
            "data",
            "list",
            "enum",
            "struct",
            "interface",
            "anyPointer",
        ]: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> ValueBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def void(self) -> None: ...
        @void.setter
        def void(self, value: None) -> None: ...
        @property
        def bool(self) -> bool: ...
        @bool.setter
        def bool(self, value: bool) -> None: ...
        @property
        def int8(self) -> int: ...
        @int8.setter
        def int8(self, value: int) -> None: ...
        @property
        def int16(self) -> int: ...
        @int16.setter
        def int16(self, value: int) -> None: ...
        @property
        def int32(self) -> int: ...
        @int32.setter
        def int32(self, value: int) -> None: ...
        @property
        def int64(self) -> int: ...
        @int64.setter
        def int64(self, value: int) -> None: ...
        @property
        def uint8(self) -> int: ...
        @uint8.setter
        def uint8(self, value: int) -> None: ...
        @property
        def uint16(self) -> int: ...
        @uint16.setter
        def uint16(self, value: int) -> None: ...
        @property
        def uint32(self) -> int: ...
        @uint32.setter
        def uint32(self, value: int) -> None: ...
        @property
        def uint64(self) -> int: ...
        @uint64.setter
        def uint64(self, value: int) -> None: ...
        @property
        def float32(self) -> float: ...
        @float32.setter
        def float32(self, value: float) -> None: ...
        @property
        def float64(self) -> float: ...
        @float64.setter
        def float64(self, value: float) -> None: ...
        @property
        def text(self) -> str: ...
        @text.setter
        def text(self, value: str) -> None: ...
        @property
        def data(self) -> bytes: ...
        @data.setter
        def data(self, value: bytes) -> None: ...
        @property
        def list(self) -> _DynamicObjectBuilder: ...
        @list.setter
        def list(self, value: AnyPointer) -> None: ...
        @property
        def enum(self) -> int: ...
        @enum.setter
        def enum(self, value: int) -> None: ...
        @property
        def struct(self) -> _DynamicObjectBuilder: ...
        @struct.setter
        def struct(self, value: AnyPointer) -> None: ...
        @property
        def interface(self) -> None: ...
        @interface.setter
        def interface(self, value: None) -> None: ...
        @property
        def anyPointer(self) -> _DynamicObjectBuilder: ...
        @anyPointer.setter
        def anyPointer(self, value: AnyPointer) -> None: ...
        @override
        def which(
            self,
        ) -> Literal[
            "void",
            "bool",
            "int8",
            "int16",
            "int32",
            "int64",
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "float32",
            "float64",
            "text",
            "data",
            "list",
            "enum",
            "struct",
            "interface",
            "anyPointer",
        ]: ...
        @override
        def as_reader(self) -> ValueReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        void: None | None = None,
        bool: bool | None = None,
        int8: int | None = None,
        int16: int | None = None,
        int32: int | None = None,
        int64: int | None = None,
        uint8: int | None = None,
        uint16: int | None = None,
        uint32: int | None = None,
        uint64: int | None = None,
        float32: float | None = None,
        float64: float | None = None,
        text: str | None = None,
        data: bytes | None = None,
        list: AnyPointer | None = None,
        enum: int | None = None,
        struct: AnyPointer | None = None,
        interface: None | None = None,
        anyPointer: AnyPointer | None = None,
        **kwargs: Any,
    ) -> ValueBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[ValueReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[ValueReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[ValueBuilder]: ...
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
    ) -> ValueReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> ValueReader: ...

Value: _ValueStructModule

class _TypeStructModule(_StructModule):
    class _TypeListStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def elementType(self) -> TypeReader: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> TypeListBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def elementType(self) -> TypeBuilder: ...
            @elementType.setter
            def elementType(self, value: TypeBuilder | TypeReader | dict[str, Any]) -> None: ...
            @override
            def init(self, field: Literal["elementType"], size: int | None = None) -> TypeBuilder: ...
            @override
            def as_reader(self) -> TypeListReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            elementType: TypeBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> TypeListBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[TypeListReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[TypeListReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[TypeListBuilder]: ...
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
        ) -> TypeListReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> TypeListReader: ...

    type TypeListReader = _TypeListStructModule.Reader
    type TypeListBuilder = _TypeListStructModule.Builder
    TypeList: _TypeListStructModule
    class _TypeEnumStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def typeId(self) -> int: ...
            @property
            def brand(self) -> BrandReader: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> TypeEnumBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def typeId(self) -> int: ...
            @typeId.setter
            def typeId(self, value: int) -> None: ...
            @property
            def brand(self) -> BrandBuilder: ...
            @brand.setter
            def brand(self, value: BrandBuilder | BrandReader | dict[str, Any]) -> None: ...
            @override
            def init(self, field: Literal["brand"], size: int | None = None) -> BrandBuilder: ...
            @override
            def as_reader(self) -> TypeEnumReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            typeId: int | None = None,
            brand: BrandBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> TypeEnumBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[TypeEnumReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[TypeEnumReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[TypeEnumBuilder]: ...
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
        ) -> TypeEnumReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> TypeEnumReader: ...

    type TypeEnumReader = _TypeEnumStructModule.Reader
    type TypeEnumBuilder = _TypeEnumStructModule.Builder
    TypeEnum: _TypeEnumStructModule
    class _TypeStructStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def typeId(self) -> int: ...
            @property
            def brand(self) -> BrandReader: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> TypeStructBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def typeId(self) -> int: ...
            @typeId.setter
            def typeId(self, value: int) -> None: ...
            @property
            def brand(self) -> BrandBuilder: ...
            @brand.setter
            def brand(self, value: BrandBuilder | BrandReader | dict[str, Any]) -> None: ...
            @override
            def init(self, field: Literal["brand"], size: int | None = None) -> BrandBuilder: ...
            @override
            def as_reader(self) -> TypeStructReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            typeId: int | None = None,
            brand: BrandBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> TypeStructBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[TypeStructReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[TypeStructReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[TypeStructBuilder]: ...
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
        ) -> TypeStructReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> TypeStructReader: ...

    type TypeStructReader = _TypeStructStructModule.Reader
    type TypeStructBuilder = _TypeStructStructModule.Builder
    TypeStruct: _TypeStructStructModule
    class _TypeInterfaceStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def typeId(self) -> int: ...
            @property
            def brand(self) -> BrandReader: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> TypeInterfaceBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def typeId(self) -> int: ...
            @typeId.setter
            def typeId(self, value: int) -> None: ...
            @property
            def brand(self) -> BrandBuilder: ...
            @brand.setter
            def brand(self, value: BrandBuilder | BrandReader | dict[str, Any]) -> None: ...
            @override
            def init(self, field: Literal["brand"], size: int | None = None) -> BrandBuilder: ...
            @override
            def as_reader(self) -> TypeInterfaceReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            typeId: int | None = None,
            brand: BrandBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> TypeInterfaceBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[TypeInterfaceReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[TypeInterfaceReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[TypeInterfaceBuilder]: ...
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
        ) -> TypeInterfaceReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> TypeInterfaceReader: ...

    type TypeInterfaceReader = _TypeInterfaceStructModule.Reader
    type TypeInterfaceBuilder = _TypeInterfaceStructModule.Builder
    TypeInterface: _TypeInterfaceStructModule
    class _TypeAnyPointerStructModule(_StructModule):
        class _TypeAnyPointerUnconstrainedStructModule(_StructModule):
            class Reader(_DynamicStructReader):
                @property
                def anyKind(self) -> None: ...
                @property
                def struct(self) -> None: ...
                @property
                def list(self) -> None: ...
                @property
                def capability(self) -> None: ...
                @override
                def which(self) -> Literal["anyKind", "struct", "list", "capability"]: ...
                @override
                def as_builder(
                    self,
                    num_first_segment_words: int | None = None,
                    allocate_seg_callable: Callable[[int], bytearray] | None = None,
                ) -> TypeAnyPointerUnconstrainedBuilder: ...

            class Builder(_DynamicStructBuilder):
                @property
                def anyKind(self) -> None: ...
                @anyKind.setter
                def anyKind(self, value: None) -> None: ...
                @property
                def struct(self) -> None: ...
                @struct.setter
                def struct(self, value: None) -> None: ...
                @property
                def list(self) -> None: ...
                @list.setter
                def list(self, value: None) -> None: ...
                @property
                def capability(self) -> None: ...
                @capability.setter
                def capability(self, value: None) -> None: ...
                @override
                def which(self) -> Literal["anyKind", "struct", "list", "capability"]: ...
                @override
                def as_reader(self) -> TypeAnyPointerUnconstrainedReader: ...

            @override
            def new_message(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
                anyKind: None | None = None,
                struct: None | None = None,
                list: None | None = None,
                capability: None | None = None,
                **kwargs: Any,
            ) -> TypeAnyPointerUnconstrainedBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[TypeAnyPointerUnconstrainedReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[TypeAnyPointerUnconstrainedReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[TypeAnyPointerUnconstrainedBuilder]: ...
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
            ) -> TypeAnyPointerUnconstrainedReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> TypeAnyPointerUnconstrainedReader: ...

        type TypeAnyPointerUnconstrainedReader = _TypeAnyPointerUnconstrainedStructModule.Reader
        type TypeAnyPointerUnconstrainedBuilder = _TypeAnyPointerUnconstrainedStructModule.Builder
        TypeAnyPointerUnconstrained: _TypeAnyPointerUnconstrainedStructModule
        class _TypeAnyPointerParameterStructModule(_StructModule):
            class Reader(_DynamicStructReader):
                @property
                def scopeId(self) -> int: ...
                @property
                def parameterIndex(self) -> int: ...
                @override
                def as_builder(
                    self,
                    num_first_segment_words: int | None = None,
                    allocate_seg_callable: Callable[[int], bytearray] | None = None,
                ) -> TypeAnyPointerParameterBuilder: ...

            class Builder(_DynamicStructBuilder):
                @property
                def scopeId(self) -> int: ...
                @scopeId.setter
                def scopeId(self, value: int) -> None: ...
                @property
                def parameterIndex(self) -> int: ...
                @parameterIndex.setter
                def parameterIndex(self, value: int) -> None: ...
                @override
                def as_reader(self) -> TypeAnyPointerParameterReader: ...

            @override
            def new_message(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
                scopeId: int | None = None,
                parameterIndex: int | None = None,
                **kwargs: Any,
            ) -> TypeAnyPointerParameterBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[TypeAnyPointerParameterReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[TypeAnyPointerParameterReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[TypeAnyPointerParameterBuilder]: ...
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
            ) -> TypeAnyPointerParameterReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> TypeAnyPointerParameterReader: ...

        type TypeAnyPointerParameterReader = _TypeAnyPointerParameterStructModule.Reader
        type TypeAnyPointerParameterBuilder = _TypeAnyPointerParameterStructModule.Builder
        TypeAnyPointerParameter: _TypeAnyPointerParameterStructModule
        class _TypeAnyPointerImplicitMethodParameterStructModule(_StructModule):
            class Reader(_DynamicStructReader):
                @property
                def parameterIndex(self) -> int: ...
                @override
                def as_builder(
                    self,
                    num_first_segment_words: int | None = None,
                    allocate_seg_callable: Callable[[int], bytearray] | None = None,
                ) -> TypeAnyPointerImplicitMethodParameterBuilder: ...

            class Builder(_DynamicStructBuilder):
                @property
                def parameterIndex(self) -> int: ...
                @parameterIndex.setter
                def parameterIndex(self, value: int) -> None: ...
                @override
                def as_reader(self) -> TypeAnyPointerImplicitMethodParameterReader: ...

            @override
            def new_message(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
                parameterIndex: int | None = None,
                **kwargs: Any,
            ) -> TypeAnyPointerImplicitMethodParameterBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[TypeAnyPointerImplicitMethodParameterReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[TypeAnyPointerImplicitMethodParameterReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[TypeAnyPointerImplicitMethodParameterBuilder]: ...
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
            ) -> TypeAnyPointerImplicitMethodParameterReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> TypeAnyPointerImplicitMethodParameterReader: ...

        type TypeAnyPointerImplicitMethodParameterReader = _TypeAnyPointerImplicitMethodParameterStructModule.Reader
        type TypeAnyPointerImplicitMethodParameterBuilder = _TypeAnyPointerImplicitMethodParameterStructModule.Builder
        TypeAnyPointerImplicitMethodParameter: _TypeAnyPointerImplicitMethodParameterStructModule
        class Reader(_DynamicStructReader):
            @property
            def unconstrained(self) -> TypeAnyPointerUnconstrainedReader: ...
            @property
            def parameter(self) -> TypeAnyPointerParameterReader: ...
            @property
            def implicitMethodParameter(self) -> TypeAnyPointerImplicitMethodParameterReader: ...
            @override
            def which(self) -> Literal["unconstrained", "parameter", "implicitMethodParameter"]: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> TypeAnyPointerBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def unconstrained(self) -> TypeAnyPointerUnconstrainedBuilder: ...
            @unconstrained.setter
            def unconstrained(
                self,
                value: TypeAnyPointerUnconstrainedBuilder | TypeAnyPointerUnconstrainedReader | dict[str, Any],
            ) -> None: ...
            @property
            def parameter(self) -> TypeAnyPointerParameterBuilder: ...
            @parameter.setter
            def parameter(
                self,
                value: TypeAnyPointerParameterBuilder | TypeAnyPointerParameterReader | dict[str, Any],
            ) -> None: ...
            @property
            def implicitMethodParameter(self) -> TypeAnyPointerImplicitMethodParameterBuilder: ...
            @implicitMethodParameter.setter
            def implicitMethodParameter(
                self,
                value: TypeAnyPointerImplicitMethodParameterBuilder
                | TypeAnyPointerImplicitMethodParameterReader
                | dict[str, Any],
            ) -> None: ...
            @override
            def which(self) -> Literal["unconstrained", "parameter", "implicitMethodParameter"]: ...
            @override
            @overload
            def init(
                self,
                field: Literal["unconstrained"],
                size: int | None = None,
            ) -> TypeAnyPointerUnconstrainedBuilder: ...
            @overload
            def init(self, field: Literal["parameter"], size: int | None = None) -> TypeAnyPointerParameterBuilder: ...
            @overload
            def init(
                self,
                field: Literal["implicitMethodParameter"],
                size: int | None = None,
            ) -> TypeAnyPointerImplicitMethodParameterBuilder: ...
            @overload
            def init(self, field: str, size: int | None = None) -> Any: ...
            @override
            def as_reader(self) -> TypeAnyPointerReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            unconstrained: TypeAnyPointerUnconstrainedBuilder | dict[str, Any] | None = None,
            parameter: TypeAnyPointerParameterBuilder | dict[str, Any] | None = None,
            implicitMethodParameter: TypeAnyPointerImplicitMethodParameterBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> TypeAnyPointerBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[TypeAnyPointerReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[TypeAnyPointerReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[TypeAnyPointerBuilder]: ...
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
        ) -> TypeAnyPointerReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> TypeAnyPointerReader: ...

    type TypeAnyPointerReader = _TypeAnyPointerStructModule.Reader
    type TypeAnyPointerBuilder = _TypeAnyPointerStructModule.Builder
    TypeAnyPointer: _TypeAnyPointerStructModule
    class Reader(_DynamicStructReader):
        @property
        def void(self) -> None: ...
        @property
        def bool(self) -> None: ...
        @property
        def int8(self) -> None: ...
        @property
        def int16(self) -> None: ...
        @property
        def int32(self) -> None: ...
        @property
        def int64(self) -> None: ...
        @property
        def uint8(self) -> None: ...
        @property
        def uint16(self) -> None: ...
        @property
        def uint32(self) -> None: ...
        @property
        def uint64(self) -> None: ...
        @property
        def float32(self) -> None: ...
        @property
        def float64(self) -> None: ...
        @property
        def text(self) -> None: ...
        @property
        def data(self) -> None: ...
        @property
        def list(self) -> TypeListReader: ...
        @property
        def enum(self) -> TypeEnumReader: ...
        @property
        def struct(self) -> TypeStructReader: ...
        @property
        def interface(self) -> TypeInterfaceReader: ...
        @property
        def anyPointer(self) -> TypeAnyPointerReader: ...
        @override
        def which(
            self,
        ) -> Literal[
            "void",
            "bool",
            "int8",
            "int16",
            "int32",
            "int64",
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "float32",
            "float64",
            "text",
            "data",
            "list",
            "enum",
            "struct",
            "interface",
            "anyPointer",
        ]: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> TypeBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def void(self) -> None: ...
        @void.setter
        def void(self, value: None) -> None: ...
        @property
        def bool(self) -> None: ...
        @bool.setter
        def bool(self, value: None) -> None: ...
        @property
        def int8(self) -> None: ...
        @int8.setter
        def int8(self, value: None) -> None: ...
        @property
        def int16(self) -> None: ...
        @int16.setter
        def int16(self, value: None) -> None: ...
        @property
        def int32(self) -> None: ...
        @int32.setter
        def int32(self, value: None) -> None: ...
        @property
        def int64(self) -> None: ...
        @int64.setter
        def int64(self, value: None) -> None: ...
        @property
        def uint8(self) -> None: ...
        @uint8.setter
        def uint8(self, value: None) -> None: ...
        @property
        def uint16(self) -> None: ...
        @uint16.setter
        def uint16(self, value: None) -> None: ...
        @property
        def uint32(self) -> None: ...
        @uint32.setter
        def uint32(self, value: None) -> None: ...
        @property
        def uint64(self) -> None: ...
        @uint64.setter
        def uint64(self, value: None) -> None: ...
        @property
        def float32(self) -> None: ...
        @float32.setter
        def float32(self, value: None) -> None: ...
        @property
        def float64(self) -> None: ...
        @float64.setter
        def float64(self, value: None) -> None: ...
        @property
        def text(self) -> None: ...
        @text.setter
        def text(self, value: None) -> None: ...
        @property
        def data(self) -> None: ...
        @data.setter
        def data(self, value: None) -> None: ...
        @property
        def list(self) -> TypeListBuilder: ...
        @list.setter
        def list(self, value: TypeListBuilder | TypeListReader | dict[str, Any]) -> None: ...
        @property
        def enum(self) -> TypeEnumBuilder: ...
        @enum.setter
        def enum(self, value: TypeEnumBuilder | TypeEnumReader | dict[str, Any]) -> None: ...
        @property
        def struct(self) -> TypeStructBuilder: ...
        @struct.setter
        def struct(self, value: TypeStructBuilder | TypeStructReader | dict[str, Any]) -> None: ...
        @property
        def interface(self) -> TypeInterfaceBuilder: ...
        @interface.setter
        def interface(self, value: TypeInterfaceBuilder | TypeInterfaceReader | dict[str, Any]) -> None: ...
        @property
        def anyPointer(self) -> TypeAnyPointerBuilder: ...
        @anyPointer.setter
        def anyPointer(self, value: TypeAnyPointerBuilder | TypeAnyPointerReader | dict[str, Any]) -> None: ...
        @override
        def which(
            self,
        ) -> Literal[
            "void",
            "bool",
            "int8",
            "int16",
            "int32",
            "int64",
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "float32",
            "float64",
            "text",
            "data",
            "list",
            "enum",
            "struct",
            "interface",
            "anyPointer",
        ]: ...
        @override
        @overload
        def init(self, field: Literal["list"], size: int | None = None) -> TypeListBuilder: ...
        @overload
        def init(self, field: Literal["enum"], size: int | None = None) -> TypeEnumBuilder: ...
        @overload
        def init(self, field: Literal["struct"], size: int | None = None) -> TypeStructBuilder: ...
        @overload
        def init(self, field: Literal["interface"], size: int | None = None) -> TypeInterfaceBuilder: ...
        @overload
        def init(self, field: Literal["anyPointer"], size: int | None = None) -> TypeAnyPointerBuilder: ...
        @overload
        def init(self, field: str, size: int | None = None) -> Any: ...
        @override
        def as_reader(self) -> TypeReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        void: None | None = None,
        bool: None | None = None,
        int8: None | None = None,
        int16: None | None = None,
        int32: None | None = None,
        int64: None | None = None,
        uint8: None | None = None,
        uint16: None | None = None,
        uint32: None | None = None,
        uint64: None | None = None,
        float32: None | None = None,
        float64: None | None = None,
        text: None | None = None,
        data: None | None = None,
        list: TypeListBuilder | dict[str, Any] | None = None,
        enum: TypeEnumBuilder | dict[str, Any] | None = None,
        struct: TypeStructBuilder | dict[str, Any] | None = None,
        interface: TypeInterfaceBuilder | dict[str, Any] | None = None,
        anyPointer: TypeAnyPointerBuilder | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> TypeBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[TypeReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[TypeReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[TypeBuilder]: ...
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
    ) -> TypeReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> TypeReader: ...

Type: _TypeStructModule

class _BindingList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> BindingReader: ...
        @override
        def __iter__(self) -> Iterator[BindingReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> BindingBuilder: ...
        @override
        def __setitem__(self, key: int, value: BindingReader | BindingBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[BindingBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> BindingBuilder: ...

class _ScopeList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> ScopeReader: ...
        @override
        def __iter__(self) -> Iterator[ScopeReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> ScopeBuilder: ...
        @override
        def __setitem__(self, key: int, value: ScopeReader | ScopeBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[ScopeBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> ScopeBuilder: ...

class _BrandStructModule(_StructModule):
    class _BindingStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def unbound(self) -> None: ...
            @property
            def type(self) -> TypeReader: ...
            @override
            def which(self) -> Literal["unbound", "type"]: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> BindingBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def unbound(self) -> None: ...
            @unbound.setter
            def unbound(self, value: None) -> None: ...
            @property
            def type(self) -> TypeBuilder: ...
            @type.setter
            def type(self, value: TypeBuilder | TypeReader | dict[str, Any]) -> None: ...
            @override
            def which(self) -> Literal["unbound", "type"]: ...
            @override
            def init(self, field: Literal["type"], size: int | None = None) -> TypeBuilder: ...
            @override
            def as_reader(self) -> BindingReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            unbound: None | None = None,
            type: TypeBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> BindingBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[BindingReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[BindingReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[BindingBuilder]: ...
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
        ) -> BindingReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> BindingReader: ...

    type BindingReader = _BindingStructModule.Reader
    type BindingBuilder = _BindingStructModule.Builder
    Binding: _BindingStructModule
    class _ScopeStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def scopeId(self) -> int: ...
            @property
            def bind(self) -> BindingListReader: ...
            @property
            def inherit(self) -> None: ...
            @override
            def which(self) -> Literal["bind", "inherit"]: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> ScopeBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def scopeId(self) -> int: ...
            @scopeId.setter
            def scopeId(self, value: int) -> None: ...
            @property
            def bind(self) -> BindingListBuilder: ...
            @bind.setter
            def bind(self, value: BindingListBuilder | BindingListReader | dict[str, Any]) -> None: ...
            @property
            def inherit(self) -> None: ...
            @inherit.setter
            def inherit(self, value: None) -> None: ...
            @override
            def which(self) -> Literal["bind", "inherit"]: ...
            @override
            def init(self, field: Literal["bind"], size: int | None = None) -> BindingListBuilder: ...
            @override
            def as_reader(self) -> ScopeReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            scopeId: int | None = None,
            bind: BindingListBuilder | dict[str, Any] | None = None,
            inherit: None | None = None,
            **kwargs: Any,
        ) -> ScopeBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[ScopeReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[ScopeReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[ScopeBuilder]: ...
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
        ) -> ScopeReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> ScopeReader: ...

    type ScopeReader = _ScopeStructModule.Reader
    type ScopeBuilder = _ScopeStructModule.Builder
    Scope: _ScopeStructModule
    class Reader(_DynamicStructReader):
        @property
        def scopes(self) -> ScopeListReader: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> BrandBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def scopes(self) -> ScopeListBuilder: ...
        @scopes.setter
        def scopes(self, value: ScopeListBuilder | ScopeListReader | dict[str, Any]) -> None: ...
        @override
        def init(self, field: Literal["scopes"], size: int | None = None) -> ScopeListBuilder: ...
        @override
        def as_reader(self) -> BrandReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        scopes: ScopeListBuilder | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> BrandBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[BrandReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[BrandReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[BrandBuilder]: ...
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
    ) -> BrandReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> BrandReader: ...

Brand: _BrandStructModule

class _AnnotationStructModule(_StructModule):
    class Reader(_DynamicStructReader):
        @property
        def id(self) -> int: ...
        @property
        def value(self) -> ValueReader: ...
        @property
        def brand(self) -> BrandReader: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> AnnotationBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def id(self) -> int: ...
        @id.setter
        def id(self, value: int) -> None: ...
        @property
        def value(self) -> ValueBuilder: ...
        @value.setter
        def value(self, value: ValueBuilder | ValueReader | dict[str, Any]) -> None: ...
        @property
        def brand(self) -> BrandBuilder: ...
        @brand.setter
        def brand(self, value: BrandBuilder | BrandReader | dict[str, Any]) -> None: ...
        @override
        @overload
        def init(self, field: Literal["value"], size: int | None = None) -> ValueBuilder: ...
        @overload
        def init(self, field: Literal["brand"], size: int | None = None) -> BrandBuilder: ...
        @overload
        def init(self, field: str, size: int | None = None) -> Any: ...
        @override
        def as_reader(self) -> AnnotationReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        id: int | None = None,
        value: ValueBuilder | dict[str, Any] | None = None,
        brand: BrandBuilder | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AnnotationBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[AnnotationReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[AnnotationReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[AnnotationBuilder]: ...
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
    ) -> AnnotationReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AnnotationReader: ...

Annotation: _AnnotationStructModule

class _AnnotationList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> AnnotationReader: ...
        @override
        def __iter__(self) -> Iterator[AnnotationReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> AnnotationBuilder: ...
        @override
        def __setitem__(self, key: int, value: AnnotationReader | AnnotationBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[AnnotationBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> AnnotationBuilder: ...

class _ElementSizeEnumModule:
    empty: int
    bit: int
    byte: int
    twoBytes: int
    fourBytes: int
    eightBytes: int
    pointer: int
    inlineComposite: int

class _FieldStructModule(_StructModule):
    noDiscriminant: int
    class _FieldSlotStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def offset(self) -> int: ...
            @property
            def type(self) -> TypeReader: ...
            @property
            def defaultValue(self) -> ValueReader: ...
            @property
            def hadExplicitDefault(self) -> bool: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> FieldSlotBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def offset(self) -> int: ...
            @offset.setter
            def offset(self, value: int) -> None: ...
            @property
            def type(self) -> TypeBuilder: ...
            @type.setter
            def type(self, value: TypeBuilder | TypeReader | dict[str, Any]) -> None: ...
            @property
            def defaultValue(self) -> ValueBuilder: ...
            @defaultValue.setter
            def defaultValue(self, value: ValueBuilder | ValueReader | dict[str, Any]) -> None: ...
            @property
            def hadExplicitDefault(self) -> bool: ...
            @hadExplicitDefault.setter
            def hadExplicitDefault(self, value: bool) -> None: ...
            @override
            @overload
            def init(self, field: Literal["type"], size: int | None = None) -> TypeBuilder: ...
            @overload
            def init(self, field: Literal["defaultValue"], size: int | None = None) -> ValueBuilder: ...
            @overload
            def init(self, field: str, size: int | None = None) -> Any: ...
            @override
            def as_reader(self) -> FieldSlotReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            offset: int | None = None,
            type: TypeBuilder | dict[str, Any] | None = None,
            defaultValue: ValueBuilder | dict[str, Any] | None = None,
            hadExplicitDefault: bool | None = None,
            **kwargs: Any,
        ) -> FieldSlotBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[FieldSlotReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[FieldSlotReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[FieldSlotBuilder]: ...
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
        ) -> FieldSlotReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> FieldSlotReader: ...

    type FieldSlotReader = _FieldSlotStructModule.Reader
    type FieldSlotBuilder = _FieldSlotStructModule.Builder
    FieldSlot: _FieldSlotStructModule
    class _FieldGroupStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def typeId(self) -> int: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> FieldGroupBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def typeId(self) -> int: ...
            @typeId.setter
            def typeId(self, value: int) -> None: ...
            @override
            def as_reader(self) -> FieldGroupReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            typeId: int | None = None,
            **kwargs: Any,
        ) -> FieldGroupBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[FieldGroupReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[FieldGroupReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[FieldGroupBuilder]: ...
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
        ) -> FieldGroupReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> FieldGroupReader: ...

    type FieldGroupReader = _FieldGroupStructModule.Reader
    type FieldGroupBuilder = _FieldGroupStructModule.Builder
    FieldGroup: _FieldGroupStructModule
    class _FieldOrdinalStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def implicit(self) -> None: ...
            @property
            def explicit(self) -> int: ...
            @override
            def which(self) -> Literal["implicit", "explicit"]: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> FieldOrdinalBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def implicit(self) -> None: ...
            @implicit.setter
            def implicit(self, value: None) -> None: ...
            @property
            def explicit(self) -> int: ...
            @explicit.setter
            def explicit(self, value: int) -> None: ...
            @override
            def which(self) -> Literal["implicit", "explicit"]: ...
            @override
            def as_reader(self) -> FieldOrdinalReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            implicit: None | None = None,
            explicit: int | None = None,
            **kwargs: Any,
        ) -> FieldOrdinalBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[FieldOrdinalReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[FieldOrdinalReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[FieldOrdinalBuilder]: ...
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
        ) -> FieldOrdinalReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> FieldOrdinalReader: ...

    type FieldOrdinalReader = _FieldOrdinalStructModule.Reader
    type FieldOrdinalBuilder = _FieldOrdinalStructModule.Builder
    FieldOrdinal: _FieldOrdinalStructModule
    class Reader(_DynamicStructReader):
        @property
        def name(self) -> str: ...
        @property
        def codeOrder(self) -> int: ...
        @property
        def annotations(self) -> AnnotationListReader: ...
        @property
        def discriminantValue(self) -> int: ...
        @property
        def slot(self) -> FieldSlotReader: ...
        @property
        def group(self) -> FieldGroupReader: ...
        @property
        def ordinal(self) -> FieldOrdinalReader: ...
        @override
        def which(self) -> Literal["slot", "group"]: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> FieldBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def name(self) -> str: ...
        @name.setter
        def name(self, value: str) -> None: ...
        @property
        def codeOrder(self) -> int: ...
        @codeOrder.setter
        def codeOrder(self, value: int) -> None: ...
        @property
        def annotations(self) -> AnnotationListBuilder: ...
        @annotations.setter
        def annotations(self, value: AnnotationListBuilder | AnnotationListReader | dict[str, Any]) -> None: ...
        @property
        def discriminantValue(self) -> int: ...
        @discriminantValue.setter
        def discriminantValue(self, value: int) -> None: ...
        @property
        def slot(self) -> FieldSlotBuilder: ...
        @slot.setter
        def slot(self, value: FieldSlotBuilder | FieldSlotReader | dict[str, Any]) -> None: ...
        @property
        def group(self) -> FieldGroupBuilder: ...
        @group.setter
        def group(self, value: FieldGroupBuilder | FieldGroupReader | dict[str, Any]) -> None: ...
        @property
        def ordinal(self) -> FieldOrdinalBuilder: ...
        @ordinal.setter
        def ordinal(self, value: FieldOrdinalBuilder | FieldOrdinalReader | dict[str, Any]) -> None: ...
        @override
        def which(self) -> Literal["slot", "group"]: ...
        @override
        @overload
        def init(self, field: Literal["slot"], size: int | None = None) -> FieldSlotBuilder: ...
        @overload
        def init(self, field: Literal["group"], size: int | None = None) -> FieldGroupBuilder: ...
        @overload
        def init(self, field: Literal["ordinal"], size: int | None = None) -> FieldOrdinalBuilder: ...
        @overload
        def init(self, field: Literal["annotations"], size: int | None = None) -> AnnotationListBuilder: ...
        @overload
        def init(self, field: str, size: int | None = None) -> Any: ...
        @override
        def as_reader(self) -> FieldReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        name: str | None = None,
        codeOrder: int | None = None,
        annotations: AnnotationListBuilder | dict[str, Any] | None = None,
        discriminantValue: int | None = None,
        slot: FieldSlotBuilder | dict[str, Any] | None = None,
        group: FieldGroupBuilder | dict[str, Any] | None = None,
        ordinal: FieldOrdinalBuilder | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> FieldBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[FieldReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[FieldReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[FieldBuilder]: ...
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
    ) -> FieldReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> FieldReader: ...

Field: _FieldStructModule

class _FieldList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> FieldReader: ...
        @override
        def __iter__(self) -> Iterator[FieldReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> FieldBuilder: ...
        @override
        def __setitem__(self, key: int, value: FieldReader | FieldBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[FieldBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> FieldBuilder: ...

class _EnumerantStructModule(_StructModule):
    class Reader(_DynamicStructReader):
        @property
        def name(self) -> str: ...
        @property
        def codeOrder(self) -> int: ...
        @property
        def annotations(self) -> AnnotationListReader: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> EnumerantBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def name(self) -> str: ...
        @name.setter
        def name(self, value: str) -> None: ...
        @property
        def codeOrder(self) -> int: ...
        @codeOrder.setter
        def codeOrder(self, value: int) -> None: ...
        @property
        def annotations(self) -> AnnotationListBuilder: ...
        @annotations.setter
        def annotations(self, value: AnnotationListBuilder | AnnotationListReader | dict[str, Any]) -> None: ...
        @override
        def init(self, field: Literal["annotations"], size: int | None = None) -> AnnotationListBuilder: ...
        @override
        def as_reader(self) -> EnumerantReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        name: str | None = None,
        codeOrder: int | None = None,
        annotations: AnnotationListBuilder | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> EnumerantBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[EnumerantReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[EnumerantReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[EnumerantBuilder]: ...
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
    ) -> EnumerantReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> EnumerantReader: ...

Enumerant: _EnumerantStructModule

class _EnumerantList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> EnumerantReader: ...
        @override
        def __iter__(self) -> Iterator[EnumerantReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> EnumerantBuilder: ...
        @override
        def __setitem__(self, key: int, value: EnumerantReader | EnumerantBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[EnumerantBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> EnumerantBuilder: ...

class _ParameterList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> ParameterReader: ...
        @override
        def __iter__(self) -> Iterator[ParameterReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> ParameterBuilder: ...
        @override
        def __setitem__(self, key: int, value: ParameterReader | ParameterBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[ParameterBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> ParameterBuilder: ...

class _MethodStructModule(_StructModule):
    class Reader(_DynamicStructReader):
        @property
        def name(self) -> str: ...
        @property
        def codeOrder(self) -> int: ...
        @property
        def paramStructType(self) -> int: ...
        @property
        def resultStructType(self) -> int: ...
        @property
        def annotations(self) -> AnnotationListReader: ...
        @property
        def paramBrand(self) -> BrandReader: ...
        @property
        def resultBrand(self) -> BrandReader: ...
        @property
        def implicitParameters(self) -> ParameterListReader: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> MethodBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def name(self) -> str: ...
        @name.setter
        def name(self, value: str) -> None: ...
        @property
        def codeOrder(self) -> int: ...
        @codeOrder.setter
        def codeOrder(self, value: int) -> None: ...
        @property
        def paramStructType(self) -> int: ...
        @paramStructType.setter
        def paramStructType(self, value: int) -> None: ...
        @property
        def resultStructType(self) -> int: ...
        @resultStructType.setter
        def resultStructType(self, value: int) -> None: ...
        @property
        def annotations(self) -> AnnotationListBuilder: ...
        @annotations.setter
        def annotations(self, value: AnnotationListBuilder | AnnotationListReader | dict[str, Any]) -> None: ...
        @property
        def paramBrand(self) -> BrandBuilder: ...
        @paramBrand.setter
        def paramBrand(self, value: BrandBuilder | BrandReader | dict[str, Any]) -> None: ...
        @property
        def resultBrand(self) -> BrandBuilder: ...
        @resultBrand.setter
        def resultBrand(self, value: BrandBuilder | BrandReader | dict[str, Any]) -> None: ...
        @property
        def implicitParameters(self) -> ParameterListBuilder: ...
        @implicitParameters.setter
        def implicitParameters(self, value: ParameterListBuilder | ParameterListReader | dict[str, Any]) -> None: ...
        @override
        @overload
        def init(self, field: Literal["paramBrand"], size: int | None = None) -> BrandBuilder: ...
        @overload
        def init(self, field: Literal["resultBrand"], size: int | None = None) -> BrandBuilder: ...
        @overload
        def init(self, field: Literal["annotations"], size: int | None = None) -> AnnotationListBuilder: ...
        @overload
        def init(self, field: Literal["implicitParameters"], size: int | None = None) -> ParameterListBuilder: ...
        @overload
        def init(self, field: str, size: int | None = None) -> Any: ...
        @override
        def as_reader(self) -> MethodReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        name: str | None = None,
        codeOrder: int | None = None,
        paramStructType: int | None = None,
        resultStructType: int | None = None,
        annotations: AnnotationListBuilder | dict[str, Any] | None = None,
        paramBrand: BrandBuilder | dict[str, Any] | None = None,
        resultBrand: BrandBuilder | dict[str, Any] | None = None,
        implicitParameters: ParameterListBuilder | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> MethodBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[MethodReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[MethodReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[MethodBuilder]: ...
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
    ) -> MethodReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> MethodReader: ...

Method: _MethodStructModule

class _MethodList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> MethodReader: ...
        @override
        def __iter__(self) -> Iterator[MethodReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> MethodBuilder: ...
        @override
        def __setitem__(self, key: int, value: MethodReader | MethodBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[MethodBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> MethodBuilder: ...

class _SuperclassStructModule(_StructModule):
    class Reader(_DynamicStructReader):
        @property
        def id(self) -> int: ...
        @property
        def brand(self) -> BrandReader: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> SuperclassBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def id(self) -> int: ...
        @id.setter
        def id(self, value: int) -> None: ...
        @property
        def brand(self) -> BrandBuilder: ...
        @brand.setter
        def brand(self, value: BrandBuilder | BrandReader | dict[str, Any]) -> None: ...
        @override
        def init(self, field: Literal["brand"], size: int | None = None) -> BrandBuilder: ...
        @override
        def as_reader(self) -> SuperclassReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        id: int | None = None,
        brand: BrandBuilder | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> SuperclassBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[SuperclassReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[SuperclassReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[SuperclassBuilder]: ...
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
    ) -> SuperclassReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> SuperclassReader: ...

Superclass: _SuperclassStructModule

class _SuperclassList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> SuperclassReader: ...
        @override
        def __iter__(self) -> Iterator[SuperclassReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> SuperclassBuilder: ...
        @override
        def __setitem__(self, key: int, value: SuperclassReader | SuperclassBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[SuperclassBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> SuperclassBuilder: ...

class _NodeStructModule(_StructModule):
    class _ParameterStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def name(self) -> str: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> ParameterBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def name(self) -> str: ...
            @name.setter
            def name(self, value: str) -> None: ...
            @override
            def as_reader(self) -> ParameterReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            name: str | None = None,
            **kwargs: Any,
        ) -> ParameterBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[ParameterReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[ParameterReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[ParameterBuilder]: ...
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
        ) -> ParameterReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> ParameterReader: ...

    type ParameterReader = _ParameterStructModule.Reader
    type ParameterBuilder = _ParameterStructModule.Builder
    Parameter: _ParameterStructModule
    class _NestedNodeStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def name(self) -> str: ...
            @property
            def id(self) -> int: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> NestedNodeBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def name(self) -> str: ...
            @name.setter
            def name(self, value: str) -> None: ...
            @property
            def id(self) -> int: ...
            @id.setter
            def id(self, value: int) -> None: ...
            @override
            def as_reader(self) -> NestedNodeReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            name: str | None = None,
            id: int | None = None,
            **kwargs: Any,
        ) -> NestedNodeBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[NestedNodeReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[NestedNodeReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[NestedNodeBuilder]: ...
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
        ) -> NestedNodeReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> NestedNodeReader: ...

    type NestedNodeReader = _NestedNodeStructModule.Reader
    type NestedNodeBuilder = _NestedNodeStructModule.Builder
    NestedNode: _NestedNodeStructModule
    class _SourceInfoStructModule(_StructModule):
        class _MemberStructModule(_StructModule):
            class Reader(_DynamicStructReader):
                @property
                def docComment(self) -> str: ...
                @property
                def startByte(self) -> int: ...
                @property
                def endByte(self) -> int: ...
                @override
                def as_builder(
                    self,
                    num_first_segment_words: int | None = None,
                    allocate_seg_callable: Callable[[int], bytearray] | None = None,
                ) -> MemberBuilder: ...

            class Builder(_DynamicStructBuilder):
                @property
                def docComment(self) -> str: ...
                @docComment.setter
                def docComment(self, value: str) -> None: ...
                @property
                def startByte(self) -> int: ...
                @startByte.setter
                def startByte(self, value: int) -> None: ...
                @property
                def endByte(self) -> int: ...
                @endByte.setter
                def endByte(self, value: int) -> None: ...
                @override
                def as_reader(self) -> MemberReader: ...

            @override
            def new_message(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
                docComment: str | None = None,
                startByte: int | None = None,
                endByte: int | None = None,
                **kwargs: Any,
            ) -> MemberBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[MemberReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[MemberReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[MemberBuilder]: ...
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
            ) -> MemberReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> MemberReader: ...

        type MemberReader = _MemberStructModule.Reader
        type MemberBuilder = _MemberStructModule.Builder
        Member: _MemberStructModule
        class Reader(_DynamicStructReader):
            @property
            def id(self) -> int: ...
            @property
            def docComment(self) -> str: ...
            @property
            def members(self) -> MemberListReader: ...
            @property
            def startByte(self) -> int: ...
            @property
            def endByte(self) -> int: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> SourceInfoBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def id(self) -> int: ...
            @id.setter
            def id(self, value: int) -> None: ...
            @property
            def docComment(self) -> str: ...
            @docComment.setter
            def docComment(self, value: str) -> None: ...
            @property
            def members(self) -> MemberListBuilder: ...
            @members.setter
            def members(self, value: MemberListBuilder | MemberListReader | dict[str, Any]) -> None: ...
            @property
            def startByte(self) -> int: ...
            @startByte.setter
            def startByte(self, value: int) -> None: ...
            @property
            def endByte(self) -> int: ...
            @endByte.setter
            def endByte(self, value: int) -> None: ...
            @override
            def init(self, field: Literal["members"], size: int | None = None) -> MemberListBuilder: ...
            @override
            def as_reader(self) -> SourceInfoReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            id: int | None = None,
            docComment: str | None = None,
            members: MemberListBuilder | dict[str, Any] | None = None,
            startByte: int | None = None,
            endByte: int | None = None,
            **kwargs: Any,
        ) -> SourceInfoBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[SourceInfoReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[SourceInfoReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[SourceInfoBuilder]: ...
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
        ) -> SourceInfoReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> SourceInfoReader: ...

    type SourceInfoReader = _SourceInfoStructModule.Reader
    type SourceInfoBuilder = _SourceInfoStructModule.Builder
    SourceInfo: _SourceInfoStructModule
    class _NodeStructStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def dataWordCount(self) -> int: ...
            @property
            def pointerCount(self) -> int: ...
            @property
            def preferredListEncoding(self) -> ElementSizeEnum: ...
            @property
            def isGroup(self) -> bool: ...
            @property
            def discriminantCount(self) -> int: ...
            @property
            def discriminantOffset(self) -> int: ...
            @property
            def fields(self) -> FieldListReader: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> NodeStructBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def dataWordCount(self) -> int: ...
            @dataWordCount.setter
            def dataWordCount(self, value: int) -> None: ...
            @property
            def pointerCount(self) -> int: ...
            @pointerCount.setter
            def pointerCount(self, value: int) -> None: ...
            @property
            def preferredListEncoding(self) -> ElementSizeEnum: ...
            @preferredListEncoding.setter
            def preferredListEncoding(self, value: ElementSizeEnum) -> None: ...
            @property
            def isGroup(self) -> bool: ...
            @isGroup.setter
            def isGroup(self, value: bool) -> None: ...
            @property
            def discriminantCount(self) -> int: ...
            @discriminantCount.setter
            def discriminantCount(self, value: int) -> None: ...
            @property
            def discriminantOffset(self) -> int: ...
            @discriminantOffset.setter
            def discriminantOffset(self, value: int) -> None: ...
            @property
            def fields(self) -> FieldListBuilder: ...
            @fields.setter
            def fields(self, value: FieldListBuilder | FieldListReader | dict[str, Any]) -> None: ...
            @override
            def init(self, field: Literal["fields"], size: int | None = None) -> FieldListBuilder: ...
            @override
            def as_reader(self) -> NodeStructReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            dataWordCount: int | None = None,
            pointerCount: int | None = None,
            preferredListEncoding: ElementSizeEnum | None = None,
            isGroup: bool | None = None,
            discriminantCount: int | None = None,
            discriminantOffset: int | None = None,
            fields: FieldListBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> NodeStructBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[NodeStructReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[NodeStructReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[NodeStructBuilder]: ...
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
        ) -> NodeStructReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> NodeStructReader: ...

    type NodeStructReader = _NodeStructStructModule.Reader
    type NodeStructBuilder = _NodeStructStructModule.Builder
    NodeStruct: _NodeStructStructModule
    class _NodeEnumStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def enumerants(self) -> EnumerantListReader: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> NodeEnumBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def enumerants(self) -> EnumerantListBuilder: ...
            @enumerants.setter
            def enumerants(self, value: EnumerantListBuilder | EnumerantListReader | dict[str, Any]) -> None: ...
            @override
            def init(self, field: Literal["enumerants"], size: int | None = None) -> EnumerantListBuilder: ...
            @override
            def as_reader(self) -> NodeEnumReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            enumerants: EnumerantListBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> NodeEnumBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[NodeEnumReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[NodeEnumReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[NodeEnumBuilder]: ...
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
        ) -> NodeEnumReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> NodeEnumReader: ...

    type NodeEnumReader = _NodeEnumStructModule.Reader
    type NodeEnumBuilder = _NodeEnumStructModule.Builder
    NodeEnum: _NodeEnumStructModule
    class _NodeInterfaceStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def methods(self) -> MethodListReader: ...
            @property
            def superclasses(self) -> SuperclassListReader: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> NodeInterfaceBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def methods(self) -> MethodListBuilder: ...
            @methods.setter
            def methods(self, value: MethodListBuilder | MethodListReader | dict[str, Any]) -> None: ...
            @property
            def superclasses(self) -> SuperclassListBuilder: ...
            @superclasses.setter
            def superclasses(self, value: SuperclassListBuilder | SuperclassListReader | dict[str, Any]) -> None: ...
            @override
            @overload
            def init(self, field: Literal["methods"], size: int | None = None) -> MethodListBuilder: ...
            @overload
            def init(self, field: Literal["superclasses"], size: int | None = None) -> SuperclassListBuilder: ...
            @overload
            def init(self, field: str, size: int | None = None) -> Any: ...
            @override
            def as_reader(self) -> NodeInterfaceReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            methods: MethodListBuilder | dict[str, Any] | None = None,
            superclasses: SuperclassListBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> NodeInterfaceBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[NodeInterfaceReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[NodeInterfaceReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[NodeInterfaceBuilder]: ...
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
        ) -> NodeInterfaceReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> NodeInterfaceReader: ...

    type NodeInterfaceReader = _NodeInterfaceStructModule.Reader
    type NodeInterfaceBuilder = _NodeInterfaceStructModule.Builder
    NodeInterface: _NodeInterfaceStructModule
    class _NodeConstStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def type(self) -> TypeReader: ...
            @property
            def value(self) -> ValueReader: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> NodeConstBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def type(self) -> TypeBuilder: ...
            @type.setter
            def type(self, value: TypeBuilder | TypeReader | dict[str, Any]) -> None: ...
            @property
            def value(self) -> ValueBuilder: ...
            @value.setter
            def value(self, value: ValueBuilder | ValueReader | dict[str, Any]) -> None: ...
            @override
            @overload
            def init(self, field: Literal["type"], size: int | None = None) -> TypeBuilder: ...
            @overload
            def init(self, field: Literal["value"], size: int | None = None) -> ValueBuilder: ...
            @overload
            def init(self, field: str, size: int | None = None) -> Any: ...
            @override
            def as_reader(self) -> NodeConstReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            type: TypeBuilder | dict[str, Any] | None = None,
            value: ValueBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> NodeConstBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[NodeConstReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[NodeConstReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[NodeConstBuilder]: ...
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
        ) -> NodeConstReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> NodeConstReader: ...

    type NodeConstReader = _NodeConstStructModule.Reader
    type NodeConstBuilder = _NodeConstStructModule.Builder
    NodeConst: _NodeConstStructModule
    class _NodeAnnotationStructModule(_StructModule):
        class Reader(_DynamicStructReader):
            @property
            def type(self) -> TypeReader: ...
            @property
            def targetsFile(self) -> bool: ...
            @property
            def targetsConst(self) -> bool: ...
            @property
            def targetsEnum(self) -> bool: ...
            @property
            def targetsEnumerant(self) -> bool: ...
            @property
            def targetsStruct(self) -> bool: ...
            @property
            def targetsField(self) -> bool: ...
            @property
            def targetsUnion(self) -> bool: ...
            @property
            def targetsGroup(self) -> bool: ...
            @property
            def targetsInterface(self) -> bool: ...
            @property
            def targetsMethod(self) -> bool: ...
            @property
            def targetsParam(self) -> bool: ...
            @property
            def targetsAnnotation(self) -> bool: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> NodeAnnotationBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def type(self) -> TypeBuilder: ...
            @type.setter
            def type(self, value: TypeBuilder | TypeReader | dict[str, Any]) -> None: ...
            @property
            def targetsFile(self) -> bool: ...
            @targetsFile.setter
            def targetsFile(self, value: bool) -> None: ...
            @property
            def targetsConst(self) -> bool: ...
            @targetsConst.setter
            def targetsConst(self, value: bool) -> None: ...
            @property
            def targetsEnum(self) -> bool: ...
            @targetsEnum.setter
            def targetsEnum(self, value: bool) -> None: ...
            @property
            def targetsEnumerant(self) -> bool: ...
            @targetsEnumerant.setter
            def targetsEnumerant(self, value: bool) -> None: ...
            @property
            def targetsStruct(self) -> bool: ...
            @targetsStruct.setter
            def targetsStruct(self, value: bool) -> None: ...
            @property
            def targetsField(self) -> bool: ...
            @targetsField.setter
            def targetsField(self, value: bool) -> None: ...
            @property
            def targetsUnion(self) -> bool: ...
            @targetsUnion.setter
            def targetsUnion(self, value: bool) -> None: ...
            @property
            def targetsGroup(self) -> bool: ...
            @targetsGroup.setter
            def targetsGroup(self, value: bool) -> None: ...
            @property
            def targetsInterface(self) -> bool: ...
            @targetsInterface.setter
            def targetsInterface(self, value: bool) -> None: ...
            @property
            def targetsMethod(self) -> bool: ...
            @targetsMethod.setter
            def targetsMethod(self, value: bool) -> None: ...
            @property
            def targetsParam(self) -> bool: ...
            @targetsParam.setter
            def targetsParam(self, value: bool) -> None: ...
            @property
            def targetsAnnotation(self) -> bool: ...
            @targetsAnnotation.setter
            def targetsAnnotation(self, value: bool) -> None: ...
            @override
            def init(self, field: Literal["type"], size: int | None = None) -> TypeBuilder: ...
            @override
            def as_reader(self) -> NodeAnnotationReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            type: TypeBuilder | dict[str, Any] | None = None,
            targetsFile: bool | None = None,
            targetsConst: bool | None = None,
            targetsEnum: bool | None = None,
            targetsEnumerant: bool | None = None,
            targetsStruct: bool | None = None,
            targetsField: bool | None = None,
            targetsUnion: bool | None = None,
            targetsGroup: bool | None = None,
            targetsInterface: bool | None = None,
            targetsMethod: bool | None = None,
            targetsParam: bool | None = None,
            targetsAnnotation: bool | None = None,
            **kwargs: Any,
        ) -> NodeAnnotationBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[NodeAnnotationReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[NodeAnnotationReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[NodeAnnotationBuilder]: ...
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
        ) -> NodeAnnotationReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> NodeAnnotationReader: ...

    type NodeAnnotationReader = _NodeAnnotationStructModule.Reader
    type NodeAnnotationBuilder = _NodeAnnotationStructModule.Builder
    NodeAnnotation: _NodeAnnotationStructModule
    class Reader(_DynamicStructReader):
        @property
        def id(self) -> int: ...
        @property
        def displayName(self) -> str: ...
        @property
        def displayNamePrefixLength(self) -> int: ...
        @property
        def scopeId(self) -> int: ...
        @property
        def nestedNodes(self) -> NestedNodeListReader: ...
        @property
        def annotations(self) -> AnnotationListReader: ...
        @property
        def file(self) -> None: ...
        @property
        def struct(self) -> NodeStructReader: ...
        @property
        def enum(self) -> NodeEnumReader: ...
        @property
        def interface(self) -> NodeInterfaceReader: ...
        @property
        def const(self) -> NodeConstReader: ...
        @property
        def annotation(self) -> NodeAnnotationReader: ...
        @property
        def parameters(self) -> ParameterListReader: ...
        @property
        def isGeneric(self) -> bool: ...
        @property
        def startByte(self) -> int: ...
        @property
        def endByte(self) -> int: ...
        @override
        def which(self) -> Literal["file", "struct", "enum", "interface", "const", "annotation"]: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> NodeBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def id(self) -> int: ...
        @id.setter
        def id(self, value: int) -> None: ...
        @property
        def displayName(self) -> str: ...
        @displayName.setter
        def displayName(self, value: str) -> None: ...
        @property
        def displayNamePrefixLength(self) -> int: ...
        @displayNamePrefixLength.setter
        def displayNamePrefixLength(self, value: int) -> None: ...
        @property
        def scopeId(self) -> int: ...
        @scopeId.setter
        def scopeId(self, value: int) -> None: ...
        @property
        def nestedNodes(self) -> NestedNodeListBuilder: ...
        @nestedNodes.setter
        def nestedNodes(self, value: NestedNodeListBuilder | NestedNodeListReader | dict[str, Any]) -> None: ...
        @property
        def annotations(self) -> AnnotationListBuilder: ...
        @annotations.setter
        def annotations(self, value: AnnotationListBuilder | AnnotationListReader | dict[str, Any]) -> None: ...
        @property
        def file(self) -> None: ...
        @file.setter
        def file(self, value: None) -> None: ...
        @property
        def struct(self) -> NodeStructBuilder: ...
        @struct.setter
        def struct(self, value: NodeStructBuilder | NodeStructReader | dict[str, Any]) -> None: ...
        @property
        def enum(self) -> NodeEnumBuilder: ...
        @enum.setter
        def enum(self, value: NodeEnumBuilder | NodeEnumReader | dict[str, Any]) -> None: ...
        @property
        def interface(self) -> NodeInterfaceBuilder: ...
        @interface.setter
        def interface(self, value: NodeInterfaceBuilder | NodeInterfaceReader | dict[str, Any]) -> None: ...
        @property
        def const(self) -> NodeConstBuilder: ...
        @const.setter
        def const(self, value: NodeConstBuilder | NodeConstReader | dict[str, Any]) -> None: ...
        @property
        def annotation(self) -> NodeAnnotationBuilder: ...
        @annotation.setter
        def annotation(self, value: NodeAnnotationBuilder | NodeAnnotationReader | dict[str, Any]) -> None: ...
        @property
        def parameters(self) -> ParameterListBuilder: ...
        @parameters.setter
        def parameters(self, value: ParameterListBuilder | ParameterListReader | dict[str, Any]) -> None: ...
        @property
        def isGeneric(self) -> bool: ...
        @isGeneric.setter
        def isGeneric(self, value: bool) -> None: ...
        @property
        def startByte(self) -> int: ...
        @startByte.setter
        def startByte(self, value: int) -> None: ...
        @property
        def endByte(self) -> int: ...
        @endByte.setter
        def endByte(self, value: int) -> None: ...
        @override
        def which(self) -> Literal["file", "struct", "enum", "interface", "const", "annotation"]: ...
        @override
        @overload
        def init(self, field: Literal["struct"], size: int | None = None) -> NodeStructBuilder: ...
        @overload
        def init(self, field: Literal["enum"], size: int | None = None) -> NodeEnumBuilder: ...
        @overload
        def init(self, field: Literal["interface"], size: int | None = None) -> NodeInterfaceBuilder: ...
        @overload
        def init(self, field: Literal["const"], size: int | None = None) -> NodeConstBuilder: ...
        @overload
        def init(self, field: Literal["annotation"], size: int | None = None) -> NodeAnnotationBuilder: ...
        @overload
        def init(self, field: Literal["nestedNodes"], size: int | None = None) -> NestedNodeListBuilder: ...
        @overload
        def init(self, field: Literal["annotations"], size: int | None = None) -> AnnotationListBuilder: ...
        @overload
        def init(self, field: Literal["parameters"], size: int | None = None) -> ParameterListBuilder: ...
        @overload
        def init(self, field: str, size: int | None = None) -> Any: ...
        @override
        def as_reader(self) -> NodeReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        id: int | None = None,
        displayName: str | None = None,
        displayNamePrefixLength: int | None = None,
        scopeId: int | None = None,
        nestedNodes: NestedNodeListBuilder | dict[str, Any] | None = None,
        annotations: AnnotationListBuilder | dict[str, Any] | None = None,
        file: None | None = None,
        struct: NodeStructBuilder | dict[str, Any] | None = None,
        enum: NodeEnumBuilder | dict[str, Any] | None = None,
        interface: NodeInterfaceBuilder | dict[str, Any] | None = None,
        const: NodeConstBuilder | dict[str, Any] | None = None,
        annotation: NodeAnnotationBuilder | dict[str, Any] | None = None,
        parameters: ParameterListBuilder | dict[str, Any] | None = None,
        isGeneric: bool | None = None,
        startByte: int | None = None,
        endByte: int | None = None,
        **kwargs: Any,
    ) -> NodeBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[NodeReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[NodeReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[NodeBuilder]: ...
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
    ) -> NodeReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> NodeReader: ...

Node: _NodeStructModule

class _CapnpVersionStructModule(_StructModule):
    class Reader(_DynamicStructReader):
        @property
        def major(self) -> int: ...
        @property
        def minor(self) -> int: ...
        @property
        def micro(self) -> int: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> CapnpVersionBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def major(self) -> int: ...
        @major.setter
        def major(self, value: int) -> None: ...
        @property
        def minor(self) -> int: ...
        @minor.setter
        def minor(self, value: int) -> None: ...
        @property
        def micro(self) -> int: ...
        @micro.setter
        def micro(self, value: int) -> None: ...
        @override
        def as_reader(self) -> CapnpVersionReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        major: int | None = None,
        minor: int | None = None,
        micro: int | None = None,
        **kwargs: Any,
    ) -> CapnpVersionBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[CapnpVersionReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[CapnpVersionReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[CapnpVersionBuilder]: ...
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
    ) -> CapnpVersionReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> CapnpVersionReader: ...

CapnpVersion: _CapnpVersionStructModule

class _IdentifierList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> IdentifierReader: ...
        @override
        def __iter__(self) -> Iterator[IdentifierReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> IdentifierBuilder: ...
        @override
        def __setitem__(self, key: int, value: IdentifierReader | IdentifierBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[IdentifierBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> IdentifierBuilder: ...

class _ImportList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> ImportReader: ...
        @override
        def __iter__(self) -> Iterator[ImportReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> ImportBuilder: ...
        @override
        def __setitem__(self, key: int, value: ImportReader | ImportBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[ImportBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> ImportBuilder: ...

class _NodeList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> NodeReader: ...
        @override
        def __iter__(self) -> Iterator[NodeReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> NodeBuilder: ...
        @override
        def __setitem__(self, key: int, value: NodeReader | NodeBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[NodeBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> NodeBuilder: ...

class _RequestedFileList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> RequestedFileReader: ...
        @override
        def __iter__(self) -> Iterator[RequestedFileReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> RequestedFileBuilder: ...
        @override
        def __setitem__(self, key: int, value: RequestedFileReader | RequestedFileBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[RequestedFileBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> RequestedFileBuilder: ...

class _SourceInfoList:
    class Reader(_DynamicListReader):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> SourceInfoReader: ...
        @override
        def __iter__(self) -> Iterator[SourceInfoReader]: ...

    class Builder(_DynamicListBuilder):
        @override
        def __len__(self) -> int: ...
        @override
        def __getitem__(self, key: int) -> SourceInfoBuilder: ...
        @override
        def __setitem__(self, key: int, value: SourceInfoReader | SourceInfoBuilder | dict[str, Any]) -> None: ...
        @override
        def __iter__(self) -> Iterator[SourceInfoBuilder]: ...
        @override
        def init(self, index: int, size: int | None = None) -> SourceInfoBuilder: ...

class _CodeGeneratorRequestStructModule(_StructModule):
    class _RequestedFileStructModule(_StructModule):
        class _ImportStructModule(_StructModule):
            class Reader(_DynamicStructReader):
                @property
                def id(self) -> int: ...
                @property
                def name(self) -> str: ...
                @override
                def as_builder(
                    self,
                    num_first_segment_words: int | None = None,
                    allocate_seg_callable: Callable[[int], bytearray] | None = None,
                ) -> ImportBuilder: ...

            class Builder(_DynamicStructBuilder):
                @property
                def id(self) -> int: ...
                @id.setter
                def id(self, value: int) -> None: ...
                @property
                def name(self) -> str: ...
                @name.setter
                def name(self, value: str) -> None: ...
                @override
                def as_reader(self) -> ImportReader: ...

            @override
            def new_message(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
                id: int | None = None,
                name: str | None = None,
                **kwargs: Any,
            ) -> ImportBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[ImportReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[ImportReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[ImportBuilder]: ...
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
            ) -> ImportReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> ImportReader: ...

        type ImportReader = _ImportStructModule.Reader
        type ImportBuilder = _ImportStructModule.Builder
        Import: _ImportStructModule
        class _FileSourceInfoStructModule(_StructModule):
            class _IdentifierStructModule(_StructModule):
                class _IdentifierMemberStructModule(_StructModule):
                    class Reader(_DynamicStructReader):
                        @property
                        def parentTypeId(self) -> int: ...
                        @property
                        def ordinal(self) -> int: ...
                        @override
                        def as_builder(
                            self,
                            num_first_segment_words: int | None = None,
                            allocate_seg_callable: Callable[[int], bytearray] | None = None,
                        ) -> IdentifierMemberBuilder: ...

                    class Builder(_DynamicStructBuilder):
                        @property
                        def parentTypeId(self) -> int: ...
                        @parentTypeId.setter
                        def parentTypeId(self, value: int) -> None: ...
                        @property
                        def ordinal(self) -> int: ...
                        @ordinal.setter
                        def ordinal(self, value: int) -> None: ...
                        @override
                        def as_reader(self) -> IdentifierMemberReader: ...

                    @override
                    def new_message(
                        self,
                        num_first_segment_words: int | None = None,
                        allocate_seg_callable: Callable[[int], bytearray] | None = None,
                        parentTypeId: int | None = None,
                        ordinal: int | None = None,
                        **kwargs: Any,
                    ) -> IdentifierMemberBuilder: ...
                    @override
                    @overload
                    def from_bytes(
                        self,
                        buf: bytes,
                        traversal_limit_in_words: int | None = None,
                        nesting_limit: int | None = None,
                    ) -> AbstractContextManager[IdentifierMemberReader]: ...
                    @overload
                    def from_bytes(
                        self,
                        buf: bytes,
                        traversal_limit_in_words: int | None = None,
                        nesting_limit: int | None = None,
                        *,
                        builder: Literal[False],
                    ) -> AbstractContextManager[IdentifierMemberReader]: ...
                    @overload
                    def from_bytes(
                        self,
                        buf: bytes,
                        traversal_limit_in_words: int | None = None,
                        nesting_limit: int | None = None,
                        *,
                        builder: Literal[True],
                    ) -> AbstractContextManager[IdentifierMemberBuilder]: ...
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
                    ) -> IdentifierMemberReader: ...
                    @override
                    def read_packed(
                        self,
                        file: IO[str] | IO[bytes],
                        traversal_limit_in_words: int | None = None,
                        nesting_limit: int | None = None,
                    ) -> IdentifierMemberReader: ...

                type IdentifierMemberReader = _IdentifierMemberStructModule.Reader
                type IdentifierMemberBuilder = _IdentifierMemberStructModule.Builder
                IdentifierMember: _IdentifierMemberStructModule
                class Reader(_DynamicStructReader):
                    @property
                    def startByte(self) -> int: ...
                    @property
                    def endByte(self) -> int: ...
                    @property
                    def typeId(self) -> int: ...
                    @property
                    def member(self) -> IdentifierMemberReader: ...
                    @override
                    def which(self) -> Literal["typeId", "member"]: ...
                    @override
                    def as_builder(
                        self,
                        num_first_segment_words: int | None = None,
                        allocate_seg_callable: Callable[[int], bytearray] | None = None,
                    ) -> IdentifierBuilder: ...

                class Builder(_DynamicStructBuilder):
                    @property
                    def startByte(self) -> int: ...
                    @startByte.setter
                    def startByte(self, value: int) -> None: ...
                    @property
                    def endByte(self) -> int: ...
                    @endByte.setter
                    def endByte(self, value: int) -> None: ...
                    @property
                    def typeId(self) -> int: ...
                    @typeId.setter
                    def typeId(self, value: int) -> None: ...
                    @property
                    def member(self) -> IdentifierMemberBuilder: ...
                    @member.setter
                    def member(
                        self,
                        value: IdentifierMemberBuilder | IdentifierMemberReader | dict[str, Any],
                    ) -> None: ...
                    @override
                    def which(self) -> Literal["typeId", "member"]: ...
                    @override
                    def init(self, field: Literal["member"], size: int | None = None) -> IdentifierMemberBuilder: ...
                    @override
                    def as_reader(self) -> IdentifierReader: ...

                @override
                def new_message(
                    self,
                    num_first_segment_words: int | None = None,
                    allocate_seg_callable: Callable[[int], bytearray] | None = None,
                    startByte: int | None = None,
                    endByte: int | None = None,
                    typeId: int | None = None,
                    member: IdentifierMemberBuilder | dict[str, Any] | None = None,
                    **kwargs: Any,
                ) -> IdentifierBuilder: ...
                @override
                @overload
                def from_bytes(
                    self,
                    buf: bytes,
                    traversal_limit_in_words: int | None = None,
                    nesting_limit: int | None = None,
                ) -> AbstractContextManager[IdentifierReader]: ...
                @overload
                def from_bytes(
                    self,
                    buf: bytes,
                    traversal_limit_in_words: int | None = None,
                    nesting_limit: int | None = None,
                    *,
                    builder: Literal[False],
                ) -> AbstractContextManager[IdentifierReader]: ...
                @overload
                def from_bytes(
                    self,
                    buf: bytes,
                    traversal_limit_in_words: int | None = None,
                    nesting_limit: int | None = None,
                    *,
                    builder: Literal[True],
                ) -> AbstractContextManager[IdentifierBuilder]: ...
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
                ) -> IdentifierReader: ...
                @override
                def read_packed(
                    self,
                    file: IO[str] | IO[bytes],
                    traversal_limit_in_words: int | None = None,
                    nesting_limit: int | None = None,
                ) -> IdentifierReader: ...

            type IdentifierReader = _IdentifierStructModule.Reader
            type IdentifierBuilder = _IdentifierStructModule.Builder
            Identifier: _IdentifierStructModule
            class Reader(_DynamicStructReader):
                @property
                def identifiers(self) -> IdentifierListReader: ...
                @override
                def as_builder(
                    self,
                    num_first_segment_words: int | None = None,
                    allocate_seg_callable: Callable[[int], bytearray] | None = None,
                ) -> FileSourceInfoBuilder: ...

            class Builder(_DynamicStructBuilder):
                @property
                def identifiers(self) -> IdentifierListBuilder: ...
                @identifiers.setter
                def identifiers(self, value: IdentifierListBuilder | IdentifierListReader | dict[str, Any]) -> None: ...
                @override
                def init(self, field: Literal["identifiers"], size: int | None = None) -> IdentifierListBuilder: ...
                @override
                def as_reader(self) -> FileSourceInfoReader: ...

            @override
            def new_message(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
                identifiers: IdentifierListBuilder | dict[str, Any] | None = None,
                **kwargs: Any,
            ) -> FileSourceInfoBuilder: ...
            @override
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> AbstractContextManager[FileSourceInfoReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[False],
            ) -> AbstractContextManager[FileSourceInfoReader]: ...
            @overload
            def from_bytes(
                self,
                buf: bytes,
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
                *,
                builder: Literal[True],
            ) -> AbstractContextManager[FileSourceInfoBuilder]: ...
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
            ) -> FileSourceInfoReader: ...
            @override
            def read_packed(
                self,
                file: IO[str] | IO[bytes],
                traversal_limit_in_words: int | None = None,
                nesting_limit: int | None = None,
            ) -> FileSourceInfoReader: ...

        type FileSourceInfoReader = _FileSourceInfoStructModule.Reader
        type FileSourceInfoBuilder = _FileSourceInfoStructModule.Builder
        FileSourceInfo: _FileSourceInfoStructModule
        class Reader(_DynamicStructReader):
            @property
            def id(self) -> int: ...
            @property
            def filename(self) -> str: ...
            @property
            def imports(self) -> ImportListReader: ...
            @property
            def fileSourceInfo(self) -> FileSourceInfoReader: ...
            @override
            def as_builder(
                self,
                num_first_segment_words: int | None = None,
                allocate_seg_callable: Callable[[int], bytearray] | None = None,
            ) -> RequestedFileBuilder: ...

        class Builder(_DynamicStructBuilder):
            @property
            def id(self) -> int: ...
            @id.setter
            def id(self, value: int) -> None: ...
            @property
            def filename(self) -> str: ...
            @filename.setter
            def filename(self, value: str) -> None: ...
            @property
            def imports(self) -> ImportListBuilder: ...
            @imports.setter
            def imports(self, value: ImportListBuilder | ImportListReader | dict[str, Any]) -> None: ...
            @property
            def fileSourceInfo(self) -> FileSourceInfoBuilder: ...
            @fileSourceInfo.setter
            def fileSourceInfo(self, value: FileSourceInfoBuilder | FileSourceInfoReader | dict[str, Any]) -> None: ...
            @override
            @overload
            def init(self, field: Literal["fileSourceInfo"], size: int | None = None) -> FileSourceInfoBuilder: ...
            @overload
            def init(self, field: Literal["imports"], size: int | None = None) -> ImportListBuilder: ...
            @overload
            def init(self, field: str, size: int | None = None) -> Any: ...
            @override
            def as_reader(self) -> RequestedFileReader: ...

        @override
        def new_message(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
            id: int | None = None,
            filename: str | None = None,
            imports: ImportListBuilder | dict[str, Any] | None = None,
            fileSourceInfo: FileSourceInfoBuilder | dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> RequestedFileBuilder: ...
        @override
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> AbstractContextManager[RequestedFileReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[False],
        ) -> AbstractContextManager[RequestedFileReader]: ...
        @overload
        def from_bytes(
            self,
            buf: bytes,
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
            *,
            builder: Literal[True],
        ) -> AbstractContextManager[RequestedFileBuilder]: ...
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
        ) -> RequestedFileReader: ...
        @override
        def read_packed(
            self,
            file: IO[str] | IO[bytes],
            traversal_limit_in_words: int | None = None,
            nesting_limit: int | None = None,
        ) -> RequestedFileReader: ...

    type RequestedFileReader = _RequestedFileStructModule.Reader
    type RequestedFileBuilder = _RequestedFileStructModule.Builder
    RequestedFile: _RequestedFileStructModule
    class Reader(_DynamicStructReader):
        @property
        def nodes(self) -> NodeListReader: ...
        @property
        def requestedFiles(self) -> RequestedFileListReader: ...
        @property
        def capnpVersion(self) -> CapnpVersionReader: ...
        @property
        def sourceInfo(self) -> SourceInfoListReader: ...
        @override
        def as_builder(
            self,
            num_first_segment_words: int | None = None,
            allocate_seg_callable: Callable[[int], bytearray] | None = None,
        ) -> CodeGeneratorRequestBuilder: ...

    class Builder(_DynamicStructBuilder):
        @property
        def nodes(self) -> NodeListBuilder: ...
        @nodes.setter
        def nodes(self, value: NodeListBuilder | NodeListReader | dict[str, Any]) -> None: ...
        @property
        def requestedFiles(self) -> RequestedFileListBuilder: ...
        @requestedFiles.setter
        def requestedFiles(
            self,
            value: RequestedFileListBuilder | RequestedFileListReader | dict[str, Any],
        ) -> None: ...
        @property
        def capnpVersion(self) -> CapnpVersionBuilder: ...
        @capnpVersion.setter
        def capnpVersion(self, value: CapnpVersionBuilder | CapnpVersionReader | dict[str, Any]) -> None: ...
        @property
        def sourceInfo(self) -> SourceInfoListBuilder: ...
        @sourceInfo.setter
        def sourceInfo(self, value: SourceInfoListBuilder | SourceInfoListReader | dict[str, Any]) -> None: ...
        @override
        @overload
        def init(self, field: Literal["capnpVersion"], size: int | None = None) -> CapnpVersionBuilder: ...
        @overload
        def init(self, field: Literal["nodes"], size: int | None = None) -> NodeListBuilder: ...
        @overload
        def init(self, field: Literal["requestedFiles"], size: int | None = None) -> RequestedFileListBuilder: ...
        @overload
        def init(self, field: Literal["sourceInfo"], size: int | None = None) -> SourceInfoListBuilder: ...
        @overload
        def init(self, field: str, size: int | None = None) -> Any: ...
        @override
        def as_reader(self) -> CodeGeneratorRequestReader: ...

    @override
    def new_message(
        self,
        num_first_segment_words: int | None = None,
        allocate_seg_callable: Callable[[int], bytearray] | None = None,
        nodes: NodeListBuilder | dict[str, Any] | None = None,
        requestedFiles: RequestedFileListBuilder | dict[str, Any] | None = None,
        capnpVersion: CapnpVersionBuilder | dict[str, Any] | None = None,
        sourceInfo: SourceInfoListBuilder | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> CodeGeneratorRequestBuilder: ...
    @override
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> AbstractContextManager[CodeGeneratorRequestReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[False],
    ) -> AbstractContextManager[CodeGeneratorRequestReader]: ...
    @overload
    def from_bytes(
        self,
        buf: bytes,
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
        *,
        builder: Literal[True],
    ) -> AbstractContextManager[CodeGeneratorRequestBuilder]: ...
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
    ) -> CodeGeneratorRequestReader: ...
    @override
    def read_packed(
        self,
        file: IO[str] | IO[bytes],
        traversal_limit_in_words: int | None = None,
        nesting_limit: int | None = None,
    ) -> CodeGeneratorRequestReader: ...

CodeGeneratorRequest: _CodeGeneratorRequestStructModule

# Top-level type aliases for use in type annotations
type AnnotationBuilder = _AnnotationStructModule.Builder
type AnnotationListBuilder = _AnnotationList.Builder
type AnnotationListReader = _AnnotationList.Reader
type AnnotationReader = _AnnotationStructModule.Reader
type BindingBuilder = _BrandStructModule._BindingStructModule.Builder
type BindingListBuilder = _BindingList.Builder
type BindingListReader = _BindingList.Reader
type BindingReader = _BrandStructModule._BindingStructModule.Reader
type BrandBuilder = _BrandStructModule.Builder
type BrandReader = _BrandStructModule.Reader
type CapnpVersionBuilder = _CapnpVersionStructModule.Builder
type CapnpVersionReader = _CapnpVersionStructModule.Reader
type CodeGeneratorRequestBuilder = _CodeGeneratorRequestStructModule.Builder
type CodeGeneratorRequestReader = _CodeGeneratorRequestStructModule.Reader
type ElementSizeEnum = (
    int | Literal["empty", "bit", "byte", "twoBytes", "fourBytes", "eightBytes", "pointer", "inlineComposite"]
)
type EnumerantBuilder = _EnumerantStructModule.Builder
type EnumerantListBuilder = _EnumerantList.Builder
type EnumerantListReader = _EnumerantList.Reader
type EnumerantReader = _EnumerantStructModule.Reader
type FieldBuilder = _FieldStructModule.Builder
type FieldGroupBuilder = _FieldStructModule._FieldGroupStructModule.Builder
type FieldGroupReader = _FieldStructModule._FieldGroupStructModule.Reader
type FieldListBuilder = _FieldList.Builder
type FieldListReader = _FieldList.Reader
type FieldOrdinalBuilder = _FieldStructModule._FieldOrdinalStructModule.Builder
type FieldOrdinalReader = _FieldStructModule._FieldOrdinalStructModule.Reader
type FieldReader = _FieldStructModule.Reader
type FieldSlotBuilder = _FieldStructModule._FieldSlotStructModule.Builder
type FieldSlotReader = _FieldStructModule._FieldSlotStructModule.Reader
type FileSourceInfoBuilder = (
    _CodeGeneratorRequestStructModule._RequestedFileStructModule._FileSourceInfoStructModule.Builder
)
type FileSourceInfoReader = (
    _CodeGeneratorRequestStructModule._RequestedFileStructModule._FileSourceInfoStructModule.Reader
)
type IdentifierBuilder = _CodeGeneratorRequestStructModule._RequestedFileStructModule._FileSourceInfoStructModule._IdentifierStructModule.Builder
type IdentifierListBuilder = _IdentifierList.Builder
type IdentifierListReader = _IdentifierList.Reader
type IdentifierMemberBuilder = _CodeGeneratorRequestStructModule._RequestedFileStructModule._FileSourceInfoStructModule._IdentifierStructModule._IdentifierMemberStructModule.Builder
type IdentifierMemberReader = _CodeGeneratorRequestStructModule._RequestedFileStructModule._FileSourceInfoStructModule._IdentifierStructModule._IdentifierMemberStructModule.Reader
type IdentifierReader = _CodeGeneratorRequestStructModule._RequestedFileStructModule._FileSourceInfoStructModule._IdentifierStructModule.Reader
type ImportBuilder = _CodeGeneratorRequestStructModule._RequestedFileStructModule._ImportStructModule.Builder
type ImportListBuilder = _ImportList.Builder
type ImportListReader = _ImportList.Reader
type ImportReader = _CodeGeneratorRequestStructModule._RequestedFileStructModule._ImportStructModule.Reader
type MemberBuilder = _NodeStructModule._SourceInfoStructModule._MemberStructModule.Builder
type MemberListBuilder = _MemberList.Builder
type MemberListReader = _MemberList.Reader
type MemberReader = _NodeStructModule._SourceInfoStructModule._MemberStructModule.Reader
type MethodBuilder = _MethodStructModule.Builder
type MethodListBuilder = _MethodList.Builder
type MethodListReader = _MethodList.Reader
type MethodReader = _MethodStructModule.Reader
type NestedNodeBuilder = _NodeStructModule._NestedNodeStructModule.Builder
type NestedNodeListBuilder = _NestedNodeList.Builder
type NestedNodeListReader = _NestedNodeList.Reader
type NestedNodeReader = _NodeStructModule._NestedNodeStructModule.Reader
type NodeAnnotationBuilder = _NodeStructModule._NodeAnnotationStructModule.Builder
type NodeAnnotationReader = _NodeStructModule._NodeAnnotationStructModule.Reader
type NodeBuilder = _NodeStructModule.Builder
type NodeConstBuilder = _NodeStructModule._NodeConstStructModule.Builder
type NodeConstReader = _NodeStructModule._NodeConstStructModule.Reader
type NodeEnumBuilder = _NodeStructModule._NodeEnumStructModule.Builder
type NodeEnumReader = _NodeStructModule._NodeEnumStructModule.Reader
type NodeInterfaceBuilder = _NodeStructModule._NodeInterfaceStructModule.Builder
type NodeInterfaceReader = _NodeStructModule._NodeInterfaceStructModule.Reader
type NodeListBuilder = _NodeList.Builder
type NodeListReader = _NodeList.Reader
type NodeReader = _NodeStructModule.Reader
type NodeStructBuilder = _NodeStructModule._NodeStructStructModule.Builder
type NodeStructReader = _NodeStructModule._NodeStructStructModule.Reader
type ParameterBuilder = _NodeStructModule._ParameterStructModule.Builder
type ParameterListBuilder = _ParameterList.Builder
type ParameterListReader = _ParameterList.Reader
type ParameterReader = _NodeStructModule._ParameterStructModule.Reader
type RequestedFileBuilder = _CodeGeneratorRequestStructModule._RequestedFileStructModule.Builder
type RequestedFileListBuilder = _RequestedFileList.Builder
type RequestedFileListReader = _RequestedFileList.Reader
type RequestedFileReader = _CodeGeneratorRequestStructModule._RequestedFileStructModule.Reader
type ScopeBuilder = _BrandStructModule._ScopeStructModule.Builder
type ScopeListBuilder = _ScopeList.Builder
type ScopeListReader = _ScopeList.Reader
type ScopeReader = _BrandStructModule._ScopeStructModule.Reader
type SourceInfoBuilder = _NodeStructModule._SourceInfoStructModule.Builder
type SourceInfoListBuilder = _SourceInfoList.Builder
type SourceInfoListReader = _SourceInfoList.Reader
type SourceInfoReader = _NodeStructModule._SourceInfoStructModule.Reader
type SuperclassBuilder = _SuperclassStructModule.Builder
type SuperclassListBuilder = _SuperclassList.Builder
type SuperclassListReader = _SuperclassList.Reader
type SuperclassReader = _SuperclassStructModule.Reader
type TypeAnyPointerBuilder = _TypeStructModule._TypeAnyPointerStructModule.Builder
type TypeAnyPointerImplicitMethodParameterBuilder = (
    _TypeStructModule._TypeAnyPointerStructModule._TypeAnyPointerImplicitMethodParameterStructModule.Builder
)
type TypeAnyPointerImplicitMethodParameterReader = (
    _TypeStructModule._TypeAnyPointerStructModule._TypeAnyPointerImplicitMethodParameterStructModule.Reader
)
type TypeAnyPointerParameterBuilder = (
    _TypeStructModule._TypeAnyPointerStructModule._TypeAnyPointerParameterStructModule.Builder
)
type TypeAnyPointerParameterReader = (
    _TypeStructModule._TypeAnyPointerStructModule._TypeAnyPointerParameterStructModule.Reader
)
type TypeAnyPointerReader = _TypeStructModule._TypeAnyPointerStructModule.Reader
type TypeAnyPointerUnconstrainedBuilder = (
    _TypeStructModule._TypeAnyPointerStructModule._TypeAnyPointerUnconstrainedStructModule.Builder
)
type TypeAnyPointerUnconstrainedReader = (
    _TypeStructModule._TypeAnyPointerStructModule._TypeAnyPointerUnconstrainedStructModule.Reader
)
type TypeBuilder = _TypeStructModule.Builder
type TypeEnumBuilder = _TypeStructModule._TypeEnumStructModule.Builder
type TypeEnumReader = _TypeStructModule._TypeEnumStructModule.Reader
type TypeInterfaceBuilder = _TypeStructModule._TypeInterfaceStructModule.Builder
type TypeInterfaceReader = _TypeStructModule._TypeInterfaceStructModule.Reader
type TypeListBuilder = _TypeStructModule._TypeListStructModule.Builder
type TypeListReader = _TypeStructModule._TypeListStructModule.Reader
type TypeReader = _TypeStructModule.Reader
type TypeStructBuilder = _TypeStructModule._TypeStructStructModule.Builder
type TypeStructReader = _TypeStructModule._TypeStructStructModule.Reader
type ValueBuilder = _ValueStructModule.Builder
type ValueReader = _ValueStructModule.Reader
