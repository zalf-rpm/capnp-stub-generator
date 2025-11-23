from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, override

if TYPE_CHECKING:
    from capnp.lib.capnp import _EnumSchema, _InterfaceSchema, _StructSchema

    from capnp_stub_generator import helper
    from capnp_stub_generator.scope import CapnpType, Scope


# Type alias for init choice tuples
InitChoice = tuple[str, str]


@dataclass
class StructGenerationContext:
    """Context object containing all metadata needed for struct generation.

    This object groups together all the type names and metadata that are passed
    around during struct generation, reducing the number of parameters from 8+ to 1.

    Attributes:
        schema: The Cap'n Proto struct schema being processed
        type_name: The name of the type being generated
        new_type: The registered CapnpType object
        registered_params: List of generic type parameters (e.g., ["T", "U"])
        reader_type_name: Name of the Reader class (e.g., "PersonReader")
        builder_type_name: Name of the Builder class (e.g., "PersonBuilder")
        scoped_reader_type_name: Fully qualified Reader name (e.g., "Outer.PersonReader")
        scoped_builder_type_name: Fully qualified Builder name (e.g., "Outer.PersonBuilder")
    """

    schema: _StructSchema
    type_name: str
    new_type: CapnpType
    registered_params: list[str]
    reader_type_name: str
    builder_type_name: str
    scoped_reader_type_name: str
    scoped_builder_type_name: str

    @classmethod
    def create(
        cls,
        schema: _StructSchema,
        type_name: str,
        new_type: CapnpType,
        registered_params: list[str],
    ) -> StructGenerationContext:
        """Factory method to create context with auto-generated name variants.

        This factory ensures consistency by automatically generating all the
        Reader and Builder name variants from the base type name.

        Args:
            schema: The Cap'n Proto struct schema
            type_name: The base type name
            new_type: The registered type object
            registered_params: Generic type parameters

        Returns:
            A fully initialized StructGenerationContext
        """
        from capnp_stub_generator import helper

        # For TypeAlias names, use flat naming (e.g., "IdInformationBuilder")
        reader_type_name = helper.new_reader_flat(new_type.name)
        builder_type_name = helper.new_builder_flat(new_type.name)

        # For scoped names with Protocol approach, use _<Name>StructModule.Reader format
        # Build the scoped Protocol module name first
        scoped_protocol_name = new_type.scoped_name.replace(new_type.name, f"_{new_type.name}StructModule")
        scoped_reader_type_name = f"{scoped_protocol_name}.Reader"
        scoped_builder_type_name = f"{scoped_protocol_name}.Builder"

        return cls(
            schema=schema,
            type_name=type_name,
            new_type=new_type,
            registered_params=registered_params,
            reader_type_name=reader_type_name,
            builder_type_name=builder_type_name,
            scoped_reader_type_name=scoped_reader_type_name,
            scoped_builder_type_name=scoped_builder_type_name,
        )

    @classmethod
    def create_with_protocol(
        cls,
        schema: _StructSchema,
        user_type_name: str,
        _: str,
        new_type: CapnpType,
        registered_params: list[str],
    ) -> StructGenerationContext:
        """Factory method for Protocol-based struct generation.

        Args:
            schema: The Cap'n Proto struct schema
            user_type_name: The user-facing type name (e.g., "SimplePrimitives")
            protocol_class_name: The Protocol class name (e.g., "_SimplePrimitivesModule")
            new_type: The registered type object (with Protocol name)
            registered_params: Generic type parameters

        Returns:
            A fully initialized StructGenerationContext
        """
        from capnp_stub_generator import helper

        # For TypeAlias names, use the user-facing name
        reader_type_name = helper.new_reader_flat(user_type_name)
        builder_type_name = helper.new_builder_flat(user_type_name)

        # For scoped names, use the Protocol-based scoped_name directly
        # new_type.scoped_name is already the full Protocol path
        scoped_protocol_name = new_type.scoped_name
        scoped_reader_type_name = f"{scoped_protocol_name}.Reader"
        scoped_builder_type_name = f"{scoped_protocol_name}.Builder"

        return cls(
            schema=schema,
            type_name=user_type_name,
            new_type=new_type,
            registered_params=registered_params,
            reader_type_name=reader_type_name,
            builder_type_name=builder_type_name,
            scoped_reader_type_name=scoped_reader_type_name,
            scoped_builder_type_name=scoped_builder_type_name,
        )


class StructFieldsCollection:
    """Collection of processed struct fields and their metadata.

    This class encapsulates the three lists that track field information
    during struct generation, providing explicit methods for adding items
    instead of direct list manipulation.

    Attributes:
        slot_fields: List of processed field variables with type hints
        init_choices: List of (field_name, type_name) tuples for struct/group fields
            that need init() method overloads
        list_init_choices: List of (field_name, element_type, needs_builder) tuples
            for list fields that need init() method overloads
    """

    def __init__(self) -> None:
        """Initialize empty collections."""
        self.slot_fields: list[helper.TypeHintedVariable] = []
        self.init_choices: list[InitChoice] = []
        self.list_init_choices: list[tuple[str, str]] = []

    def add_slot_field(self, field: helper.TypeHintedVariable) -> None:
        """Add a slot field to the collection.

        Args:
            field: The type-hinted variable representing the field
        """
        self.slot_fields.append(field)

    def add_init_choice(self, field_name: str, type_name: str) -> None:
        """Add an init choice for struct or group fields.

        Init choices are used to generate overloaded init() methods that return
        the appropriate Builder type for the field.

        Args:
            field_name: The name of the field
            type_name: The type name to return (e.g., "PersonBuilder")
        """
        self.init_choices.append((field_name, type_name))

    @override
    def __repr__(self) -> str:
        """Return a readable representation for debugging."""
        return (
            f"StructFieldsCollection("
            f"slot_fields={len(self.slot_fields)}, "
            f"init_choices={len(self.init_choices)}, "
            f"list_init_choices={len(self.list_init_choices)})"
        )


# ===== Interface Generation DTOs =====


@dataclass
class EnumGenerationContext:
    """Context object containing all metadata needed for enum generation.

    This object groups together enum-specific metadata for Protocol-based generation.

    Attributes:
        schema: The Cap'n Proto enum schema being processed
        type_name: The user-facing type name (e.g., "TestEnum")
        protocol_class_name: The Protocol class name (e.g., "_TestEnumModule")
        new_type: The registered CapnpType object
    """

    schema: _EnumSchema
    type_name: str
    protocol_class_name: str
    new_type: CapnpType

    @classmethod
    def create(
        cls,
        schema: _EnumSchema,
        type_name: str,
        new_type: CapnpType,
    ) -> EnumGenerationContext:
        """Factory method to create enum context with Protocol-based naming.

        Args:
            schema: The Cap'n Proto enum schema
            type_name: The user-facing type name
            new_type: The registered type object

        Returns:
            A fully initialized EnumGenerationContext
        """
        protocol_class_name = f"_{type_name}EnumModule"

        return cls(
            schema=schema,
            type_name=type_name,
            protocol_class_name=protocol_class_name,
            new_type=new_type,
        )


@dataclass
class InterfaceGenerationContext:
    """Context object containing all metadata needed for interface generation.

    This object groups together interface-specific metadata, reducing the number
    of parameters passed between interface generation methods.

    Attributes:
        schema: The Cap'n Proto interface schema being processed
        type_name: The user-facing interface name (e.g., "Calculator")
        protocol_class_name: The Protocol class name (e.g., "_CalculatorModule")
        client_type_name: The Client class name (e.g., "CalculatorClient")
        registered_type: The registered CapnpType object
        base_classes: List of base Protocol class names for inheritance
        parent_scope: The parent scope for this interface
    """

    schema: _InterfaceSchema
    type_name: str
    protocol_class_name: str
    client_type_name: str
    registered_type: CapnpType
    base_classes: list[str]
    parent_scope: Scope

    @classmethod
    def create(
        cls,
        schema: _InterfaceSchema,
        type_name: str,
        registered_type: CapnpType,
        base_classes: list[str],
        parent_scope: Scope,
    ) -> InterfaceGenerationContext:
        """Factory method to create interface context with Protocol-based naming.

        Args:
            schema: The Cap'n Proto interface schema
            type_name: The user-facing interface name
            registered_type: The registered type object
            base_classes: List of base class names
            parent_scope: The parent scope

        Returns:
            A fully initialized InterfaceGenerationContext
        """
        protocol_class_name = f"_{type_name}InterfaceModule"
        client_type_name = f"{type_name}Client"

        return cls(
            schema=schema,
            type_name=type_name,
            protocol_class_name=protocol_class_name,
            client_type_name=client_type_name,
            registered_type=registered_type,
            base_classes=base_classes,
            parent_scope=parent_scope,
        )


@dataclass
class MethodInfo:
    """Information about a single RPC method.

    Encapsulates all the metadata extracted from a runtime method object,
    providing safe defaults for missing information.

    Attributes:
        method_name: Name of the method
        method: The runtime method object
        param_schema: Parameter struct schema (or None if unavailable)
        result_schema: Result struct schema (or None if unavailable)
        param_fields: List of parameter field names
        result_fields: List of result field names
    """

    method_name: str
    method: Any
    param_schema: _StructSchema | None
    result_schema: _StructSchema | None
    param_fields: list[str]
    result_fields: list[str]

    @classmethod
    def from_runtime_method(cls, method_name: str, method: Any) -> MethodInfo:
        """Create MethodInfo from a runtime method object.

        Handles all error cases and returns safe defaults when schemas
        or field information cannot be extracted.

        Args:
            method_name: Name of the method
            method: The runtime method object

        Returns:
            A MethodInfo with all available information
        """
        param_schema = None
        result_schema = None
        param_fields: list[str] = []
        result_fields: list[str] = []

        try:
            param_schema = method.param_type
            result_schema = method.result_type
            if param_schema is not None:
                param_fields = [f.name for f in param_schema.node.struct.fields]
            if result_schema is not None:
                result_fields = [f.name for f in result_schema.node.struct.fields]
        except Exception:
            # Safe defaults already set
            pass

        return cls(
            method_name=method_name,
            method=method,
            param_schema=param_schema,
            result_schema=result_schema,
            param_fields=param_fields,
            result_fields=result_fields,
        )


@dataclass
class ParameterInfo:
    """Information about a processed method parameter with type variants.

    Different method contexts (client, server, request) need different type
    representations for the same parameter. This class encapsulates all variants.

    Attributes:
        name: Parameter name
        client_type: Type for client method signature (may include dict unions)
        server_type: Type for server method signature (uses Reader types)
        request_type: Type for request builder (usually same as client_type)
    """

    name: str
    client_type: str
    server_type: str
    request_type: str

    def to_client_param(self) -> str:
        """Format as client method parameter (optional with default).

        Returns:
            Parameter string like "name: Type | None = None"
        """
        return f"{self.name}: {self.client_type} | None = None"

    def to_server_param(self) -> str:
        """Format as server method parameter (required).

        Returns:
            Parameter string like "name: Type"
        """
        return f"{self.name}: {self.server_type}"

    def to_request_param(self) -> str:
        """Format as request method parameter (optional with default).

        Returns:
            Parameter string like "name: Type | None = None"
        """
        return f"{self.name}: {self.request_type} | None = None"


class MethodSignatureCollection:
    """Collection of generated method signatures and Protocol classes.

    Accumulates all the components needed for a complete method implementation:
    - Client method signature
    - Request Protocol class lines
    - Result Protocol class lines
    - _request helper method
    - Server CallContext and ResultsBuilder lines
    - Server method signature
    - NamedTuple info for direct struct returns

    Attributes:
        method_name: Name of the method
        client_method_lines: Lines for the client method
        request_class_lines: Lines for the Request Protocol class
        result_class_lines: Lines for the Result Protocol class
        request_helper_lines: Lines for the _request helper method
        server_context_lines: Lines for CallContext and ResultsBuilder Protocols
        server_method_signature: Server method signature line
        uses_direct_struct_return: Flag for NamedTuple direct returns
        namedtuple_info: Tuple of (result_type, field_name, field_type) or None
    """

    method_name: str
    client_method_lines: list[str]
    request_class_lines: list[str]
    result_class_lines: list[str]
    client_result_lines: list[str]
    server_result_lines: list[str]
    request_helper_lines: list[str]
    server_context_lines: list[str]

    def __init__(self, method_name: str):
        """Initialize empty collection for a method.

        Args:
            method_name: Name of the method being processed
        """
        self.method_name = method_name
        self.client_method_lines = []
        self.request_class_lines = []
        self.result_class_lines = []  # For module-level (to be removed)
        self.client_result_lines = []  # Nested in Client
        self.server_result_lines = []  # Nested in Server
        self.request_helper_lines = []
        self.server_context_lines = []

    def set_client_method(self, lines: list[str]) -> None:
        """Set the client method signature lines.

        Args:
            lines: List of lines for the client method
        """
        self.client_method_lines = lines

    def set_request_class(self, lines: list[str]) -> None:
        """Set the Request Protocol class lines.

        Args:
            lines: List of lines for the Request Protocol class
        """
        self.request_class_lines = lines

    def set_client_result_class(self, lines: list[str]) -> None:
        """Set the Client-side Result Protocol class lines (nested in Client).

        Args:
            lines: List of lines for the Client Result Protocol class
        """
        self.client_result_lines = lines

    def set_server_result_class(self, lines: list[str]) -> None:
        """Set the Server-side Result Protocol class lines (nested in Server).

        Args:
            lines: List of lines for the Server Result Protocol class
        """
        self.server_result_lines = lines

    def set_request_helper(self, lines: list[str]) -> None:
        """Set the _request helper method lines.

        Args:
            lines: List of lines for the _request helper method
        """
        self.request_helper_lines = lines

    @override
    def __repr__(self) -> str:
        """Return a readable representation for debugging."""
        return (
            f"MethodSignatureCollection("
            f"method={self.method_name}, "
            f"client_lines={len(self.client_method_lines)}, "
            f"request_lines={len(self.request_class_lines)}, "
            f"result_lines={len(self.result_class_lines)})"
        )


class ServerMethodsCollection:
    """Collection of server method signatures for Server class generation.

    Accumulates server method signatures, NamedTuple definitions, and context classes
    as methods are processed, providing everything needed to generate the final Server class.

    Attributes:
        server_methods: List of server method signature lines
        namedtuples: Dict mapping result type names to list of (field_name, field_type) tuples
        context_classes: List of context class lines (CallContext and ResultsBuilder)
    """

    server_methods: list[str]
    namedtuples: dict[str, list[tuple[str, str]]]
    context_classes: list[str]

    def __init__(self):
        """Initialize empty collection."""
        self.server_methods = []
        self.namedtuples = {}
        self.context_classes = []

    def add_server_method(self, signature: str) -> None:
        """Add a server method signature.

        Args:
            signature: Single-line server method signature
        """
        self.server_methods.append(signature)

    def add_namedtuple(self, result_type: str, fields: list[tuple[str, str]]) -> None:
        """Add a NamedTuple definition.

        Args:
            result_type: The result type name (used as key)
            fields: List of (field_name, field_type) tuples
        """
        self.namedtuples[result_type] = fields

    def add_context_lines(self, lines: list[str]) -> None:
        """Add context class lines (CallContext and ResultsBuilder).

        Args:
            lines: List of lines for context classes
        """
        self.context_classes.extend(lines)

    def has_methods(self) -> bool:
        """Check if any server methods were added.

        Returns:
            True if at least one server method exists
        """
        return len(self.server_methods) > 0

    @override
    def __repr__(self) -> str:
        """Return a readable representation for debugging."""
        return (
            f"ServerMethodsCollection("
            f"methods={len(self.server_methods)}, "
            f"namedtuples={len(self.namedtuples)}, "
            f"context_classes={len(self.context_classes)})"
        )
