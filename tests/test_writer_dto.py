"""Tests for writer_dto.py - Data Transfer Objects.

These tests verify that the DTOs work correctly and provide the expected
functionality for struct generation.
"""

from __future__ import annotations

from unittest.mock import Mock

from capnp_stub_generator import helper
from capnp_stub_generator.writer_dto import (
    InterfaceGenerationContext,
    MethodInfo,
    MethodSignatureCollection,
    ParameterInfo,
    ServerMethodsCollection,
    StructFieldsCollection,
    StructGenerationContext,
)


class TestStructGenerationContext:
    """Tests for StructGenerationContext."""

    def test_create_factory_method(self):
        """Test that the factory method creates context with Protocol-based name variants."""
        # Create mock objects
        mock_schema = Mock()
        mock_new_type = Mock()
        mock_new_type.name = "Person"
        mock_new_type.scoped_name = "Company.Person"

        # Create context using factory
        context = StructGenerationContext.create(
            schema=mock_schema,
            type_name="Person",
            new_type=mock_new_type,
            registered_params=["T"],
        )

        # Verify all attributes are set
        assert context.schema == mock_schema
        assert context.type_name == "Person"
        assert context.new_type == mock_new_type
        assert context.registered_params == ["T"]

        # Verify generated names - with Protocol structure
        assert context.reader_type_name == "PersonReader"
        assert context.builder_type_name == "PersonBuilder"
        # Scoped names use Protocol naming: Company.Person -> Company._PersonStructModule
        assert context.scoped_reader_type_name == "Company._PersonStructModule.Reader"
        assert context.scoped_builder_type_name == "Company._PersonStructModule.Builder"

    def test_create_with_empty_generic_params(self):
        """Test context creation with no generic parameters."""
        mock_schema = Mock()
        mock_new_type = Mock()
        mock_new_type.name = "Person"
        mock_new_type.scoped_name = "Person"

        context = StructGenerationContext.create(
            schema=mock_schema, type_name="Person", new_type=mock_new_type, registered_params=[]
        )

        assert context.registered_params == []
        assert context.reader_type_name == "PersonReader"

    def test_create_with_nested_type(self):
        """Test context creation with nested type names using Protocol structure."""
        mock_schema = Mock()
        mock_new_type = Mock()
        mock_new_type.name = "Inner"
        mock_new_type.scoped_name = "Outer.Middle.Inner"

        context = StructGenerationContext.create(
            schema=mock_schema, type_name="Inner", new_type=mock_new_type, registered_params=[]
        )

        # With Protocol structure: Outer.Middle.Inner -> Outer.Middle._InnerStructModule
        assert context.scoped_reader_type_name == "Outer.Middle._InnerStructModule.Reader"
        assert context.scoped_builder_type_name == "Outer.Middle._InnerStructModule.Builder"


class TestStructFieldsCollection:
    """Tests for StructFieldsCollection."""

    def test_initialization(self):
        """Test that collection initializes with empty lists."""
        collection = StructFieldsCollection()

        assert collection.slot_fields == []
        assert collection.init_choices == []
        assert collection.list_init_choices == []

    def test_add_slot_field(self):
        """Test adding slot fields."""
        collection = StructFieldsCollection()
        mock_field = Mock(spec=helper.TypeHintedVariable)

        collection.add_slot_field(mock_field)

        assert len(collection.slot_fields) == 1
        assert collection.slot_fields[0] == mock_field

    def test_add_multiple_slot_fields(self):
        """Test adding multiple slot fields."""
        collection = StructFieldsCollection()
        field1 = Mock(spec=helper.TypeHintedVariable)
        field2 = Mock(spec=helper.TypeHintedVariable)

        collection.add_slot_field(field1)
        collection.add_slot_field(field2)

        assert len(collection.slot_fields) == 2
        assert collection.slot_fields == [field1, field2]

    def test_add_init_choice(self):
        """Test adding init choices."""
        collection = StructFieldsCollection()

        collection.add_init_choice("address", "Address")

        assert len(collection.init_choices) == 1
        assert collection.init_choices[0] == ("address", "Address")

    def test_repr(self):
        """Test string representation for debugging."""
        collection = StructFieldsCollection()
        collection.add_slot_field(Mock(spec=helper.TypeHintedVariable))
        collection.add_init_choice("field1", "Type1")
        # collection.add_list_init_choice("field2", "Type2") # Removed

        repr_str = repr(collection)

        assert "StructFieldsCollection" in repr_str
        assert "slot_fields=1" in repr_str
        assert "init_choices=1" in repr_str
        assert "list_init_choices=0" in repr_str

    def test_complex_workflow(self):
        """Test a realistic workflow of building up field collections."""
        collection = StructFieldsCollection()

        # Add several fields like gen_struct would do
        field1 = Mock(spec=helper.TypeHintedVariable)
        field2 = Mock(spec=helper.TypeHintedVariable)
        field3 = Mock(spec=helper.TypeHintedVariable)

        collection.add_slot_field(field1)
        collection.add_init_choice("address", "Address")
        collection.add_slot_field(field2)
        # collection.add_list_init_choice("emails", "str") # Removed
        collection.add_slot_field(field3)
        collection.add_init_choice("company", "Company")
        # collection.add_list_init_choice("phones", "PhoneNumber") # Removed

        # Verify final state
        assert len(collection.slot_fields) == 3
        assert len(collection.init_choices) == 2
        assert len(collection.list_init_choices) == 0

        # Verify order is preserved
        assert collection.init_choices == [("address", "Address"), ("company", "Company")]
        assert collection.list_init_choices == []


class TestIntegration:
    """Integration tests for using DTOs together."""

    def test_dto_workflow(self):
        """Test typical workflow using both DTOs together."""
        # Setup context
        mock_schema = Mock()
        mock_new_type = Mock()
        mock_new_type.name = "Person"
        mock_new_type.scoped_name = "AddressBook.Person"

        context = StructGenerationContext.create(
            schema=mock_schema,
            type_name="Person",
            new_type=mock_new_type,
            registered_params=[],
        )

        # Build field collection
        fields = StructFieldsCollection()
        fields.add_slot_field(Mock(spec=helper.TypeHintedVariable))
        fields.add_init_choice("address", "Address")

        # Verify both objects work together
        assert context.type_name == "Person"
        assert context.builder_type_name == "PersonBuilder"
        assert len(fields.slot_fields) == 1
        assert len(fields.init_choices) == 1

        # This simulates what the refactored gen_struct would do:
        # pass context and fields to helper methods instead of 8+ parameters


# ===== Interface DTO Tests =====


class TestInterfaceGenerationContext:
    """Tests for InterfaceGenerationContext."""

    def test_create_factory_method(self):
        """Test that the factory method creates context correctly."""
        mock_schema = Mock()
        mock_type = Mock()
        mock_scope = Mock()
        base_classes = ["Capability", "Protocol"]

        context = InterfaceGenerationContext.create(
            schema=mock_schema,
            type_name="Calculator",
            registered_type=mock_type,
            base_classes=base_classes,
            parent_scope=mock_scope,
        )

        assert context.schema == mock_schema
        assert context.type_name == "Calculator"
        assert context.protocol_class_name == "_CalculatorInterfaceModule"
        assert context.client_type_name == "CalculatorClient"
        assert context.registered_type == mock_type
        assert context.base_classes == base_classes
        assert context.parent_scope == mock_scope

    def test_create_with_empty_base_classes(self):
        """Test context creation with no base classes."""
        mock_schema = Mock()
        mock_type = Mock()
        mock_scope = Mock()

        context = InterfaceGenerationContext.create(
            schema=mock_schema,
            type_name="SimpleInterface",
            registered_type=mock_type,
            base_classes=[],
            parent_scope=mock_scope,
        )

        assert context.base_classes == []
        assert context.type_name == "SimpleInterface"
        assert context.protocol_class_name == "_SimpleInterfaceInterfaceModule"


class TestMethodInfo:
    """Tests for MethodInfo."""

    def test_from_runtime_method_success(self):
        """Test MethodInfo creation from valid runtime method."""
        mock_method = Mock()
        mock_param_schema = Mock()
        mock_result_schema = Mock()

        # Setup param schema
        param_field1 = Mock()
        param_field1.name = "x"
        param_field2 = Mock()
        param_field2.name = "y"
        mock_param_schema.node.struct.fields = [param_field1, param_field2]

        # Setup result schema
        result_field = Mock()
        result_field.name = "value"
        mock_result_schema.node.struct.fields = [result_field]

        mock_method.param_type = mock_param_schema
        mock_method.result_type = mock_result_schema

        method_info = MethodInfo.from_runtime_method("add", mock_method)

        assert method_info.method_name == "add"
        assert method_info.method == mock_method
        assert method_info.param_schema == mock_param_schema
        assert method_info.result_schema == mock_result_schema
        assert method_info.param_fields == ["x", "y"]
        assert method_info.result_fields == ["value"]

    def test_from_runtime_method_missing_schemas(self):
        """Test MethodInfo creation when schemas are missing."""
        mock_method = Mock()
        mock_method.param_type = None
        mock_method.result_type = None

        method_info = MethodInfo.from_runtime_method("method", mock_method)

        assert method_info.method_name == "method"
        assert method_info.param_schema is None
        assert method_info.result_schema is None
        assert method_info.param_fields == []
        assert method_info.result_fields == []

    def test_from_runtime_method_error_handling(self):
        """Test MethodInfo creation with errors during access."""
        mock_method = Mock()
        # Make param_type raise exception when .node is accessed
        mock_param_type = Mock()
        mock_param_type.node.struct.fields = Mock(side_effect=Exception("Access error"))
        mock_method.param_type = mock_param_type
        mock_method.result_type = None

        method_info = MethodInfo.from_runtime_method("broken", mock_method)

        assert method_info.method_name == "broken"
        # Even though param_schema is set, fields should be empty due to exception
        assert method_info.param_fields == []
        assert method_info.result_fields == []


class TestParameterInfo:
    """Tests for ParameterInfo."""

    def test_to_client_param(self):
        """Test client parameter formatting."""
        param = ParameterInfo(
            name="value",
            client_type="int",
            server_type="int",
            request_type="int",
        )

        assert param.to_client_param() == "value: int | None = None"

    def test_to_server_param(self):
        """Test server parameter formatting."""
        param = ParameterInfo(
            name="data",
            client_type="DataStruct | dict[str, Any]",
            server_type="DataStructReader",
            request_type="DataStruct | dict[str, Any]",
        )

        assert param.to_server_param() == "data: DataStructReader"

    def test_to_request_param(self):
        """Test request parameter formatting."""
        param = ParameterInfo(
            name="items",
            client_type="Sequence[Item]",
            server_type="Sequence[ItemReader]",
            request_type="Sequence[Item] | Sequence[dict[str, Any]]",
        )

        assert param.to_request_param() == "items: Sequence[Item] | Sequence[dict[str, Any]] | None = None"

    def test_different_types_for_contexts(self):
        """Test that different contexts can have different types."""
        param = ParameterInfo(
            name="obj",
            client_type="MyStruct | dict[str, Any]",
            server_type="MyStructReader",
            request_type="MyStruct",
        )

        assert "dict[str, Any]" in param.to_client_param()
        assert "Reader" in param.to_server_param()
        assert "dict[str, Any]" not in param.to_request_param()


class TestMethodSignatureCollection:
    """Tests for MethodSignatureCollection."""

    def test_initialization(self):
        """Test collection initializes with empty lists."""
        collection = MethodSignatureCollection("calculate")

        assert collection.method_name == "calculate"
        assert collection.client_method_lines == []
        assert collection.request_class_lines == []
        assert collection.result_class_lines == []
        assert collection.request_helper_lines == []

    def test_set_client_method(self):
        """Test setting client method lines."""
        collection = MethodSignatureCollection("add")
        lines = ["def add(self, x: int, y: int) -> Awaitable[int]: ..."]

        collection.set_client_method(lines)

        assert collection.client_method_lines == lines

    def test_set_request_class(self):
        """Test setting Request Protocol class lines."""
        collection = MethodSignatureCollection("multiply")
        lines = [
            "class MultiplyRequest(Protocol):",
            "    x: int",
            "    y: int",
            "    def send(self) -> Awaitable[int]: ...",
        ]

        collection.set_request_class(lines)

        assert collection.request_class_lines == lines
        assert len(collection.request_class_lines) == 4

    def test_set_request_helper(self):
        """Test setting _request helper method lines."""
        collection = MethodSignatureCollection("process")
        lines = ["def process_request(self, data: str | None = None) -> ProcessRequest: ..."]

        collection.set_request_helper(lines)

        assert collection.request_helper_lines == lines

    def test_repr(self):
        """Test string representation for debugging."""
        collection = MethodSignatureCollection("test")
        collection.set_client_method(["line1"])
        collection.set_request_class(["line2", "line3"])
        # collection.set_result_class(["line4"]) # Removed

        repr_str = repr(collection)

        assert "MethodSignatureCollection" in repr_str
        assert "method=test" in repr_str
        assert "client_lines=1" in repr_str
        assert "request_lines=2" in repr_str
        assert "result_lines=0" in repr_str

    def test_complete_workflow(self):
        """Test a realistic workflow of building up method signatures."""
        collection = MethodSignatureCollection("calculate")

        # Set all components
        collection.set_client_method(["def calculate(...) -> Awaitable[int]: ..."])
        collection.set_request_class(
            [
                "class CalculateRequest(Protocol):",
                "    def send(self) -> Awaitable[int]: ...",
            ]
        )
        # collection.set_result_class([])  # Removed
        collection.set_request_helper(["def calculate_request(...) -> CalculateRequest: ..."])
        # collection.set_server_method("    def calculate(self, context: Any) -> int: ...") # Removed

        # Verify all components are set
        assert len(collection.client_method_lines) == 1
        assert len(collection.request_class_lines) == 2
        assert len(collection.result_class_lines) == 0
        assert len(collection.request_helper_lines) == 1


class TestServerMethodsCollection:
    """Tests for ServerMethodsCollection."""

    def test_initialization(self):
        """Test collection initializes with empty containers."""
        collection = ServerMethodsCollection()

        assert collection.server_methods == []
        assert collection.namedtuples == {}
        assert collection.has_methods() is False

    def test_add_server_method(self):
        """Test adding server method signatures."""
        collection = ServerMethodsCollection()

        collection.add_server_method("    def method1(self, context: Any) -> None: ...")
        collection.add_server_method("    def method2(self, context: Any, x: int) -> int: ...")

        assert len(collection.server_methods) == 2
        assert collection.has_methods() is True

    def test_add_namedtuple(self):
        """Test adding NamedTuple definitions."""
        collection = ServerMethodsCollection()

        collection.add_namedtuple("Result1", [("value", "int")])
        collection.add_namedtuple("Result2", [("data", "str"), ("count", "int")])

        assert len(collection.namedtuples) == 2
        assert "Result1" in collection.namedtuples
        assert "Result2" in collection.namedtuples
        assert collection.namedtuples["Result1"] == [("value", "int")]
        assert collection.namedtuples["Result2"] == [("data", "str"), ("count", "int")]

    def test_has_methods_false(self):
        """Test has_methods returns False when empty."""
        collection = ServerMethodsCollection()

        assert collection.has_methods() is False

    def test_has_methods_true(self):
        """Test has_methods returns True after adding methods."""
        collection = ServerMethodsCollection()
        collection.add_server_method("    def test(self, context: Any) -> None: ...")

        assert collection.has_methods() is True

    def test_repr(self):
        """Test string representation for debugging."""
        collection = ServerMethodsCollection()
        collection.add_server_method("method1")
        collection.add_server_method("method2")
        collection.add_namedtuple("Result", [("field", "Type")])

        repr_str = repr(collection)

        assert "ServerMethodsCollection" in repr_str
        assert "methods=2" in repr_str
        assert "namedtuples=1" in repr_str

    def test_complete_workflow(self):
        """Test a realistic workflow of accumulating server components."""
        collection = ServerMethodsCollection()

        # Add multiple methods
        collection.add_server_method("    def add(self, context: Any, x: int, y: int) -> int: ...")
        collection.add_server_method("    def subtract(self, context: Any, x: int, y: int) -> int: ...")
        collection.add_server_method("    def multiply(self, context: Any, x: int, y: int) -> int: ...")

        # Add some NamedTuples
        collection.add_namedtuple("AddResult", [("sum", "int")])
        collection.add_namedtuple("MultiplyResult", [("product", "int")])

        # Verify final state
        assert len(collection.server_methods) == 3
        assert len(collection.namedtuples) == 2
        assert collection.has_methods() is True


class TestInterfaceDTOIntegration:
    """Integration tests for using interface DTOs together."""

    def test_full_interface_workflow(self):
        """Test typical workflow using all interface DTOs together."""
        # Setup context
        mock_schema = Mock()
        mock_type = Mock()
        mock_scope = Mock()

        context = InterfaceGenerationContext.create(
            schema=mock_schema,
            type_name="Calculator",
            registered_type=mock_type,
            base_classes=["Protocol"],
            parent_scope=mock_scope,
        )

        # Create method info
        mock_method = Mock()
        mock_method.param_type = None
        mock_method.result_type = None

        method_info = MethodInfo.from_runtime_method("add", mock_method)

        # Create parameter info
        param = ParameterInfo(
            name="x",
            client_type="int",
            server_type="int",
            request_type="int",
        )

        # Build method signature collection
        method_collection = MethodSignatureCollection("add")
        method_collection.set_client_method([f"def add(self, {param.to_client_param()}) -> Awaitable[int]: ..."])
        # method_collection.set_server_method(...) # Removed

        # Build server collection
        server_collection = ServerMethodsCollection()
        server_collection.add_server_method(f"    def add(self, context: Any, {param.to_server_param()}) -> int: ...")

        # Verify everything works together
        assert context.type_name == "Calculator"
        assert context.protocol_class_name == "_CalculatorInterfaceModule"
        assert method_info.method_name == "add"
        assert "int | None = None" in method_collection.client_method_lines[0]
        assert server_collection.has_methods() is True

    def test_multiple_methods_workflow(self):
        """Test workflow with multiple methods."""
        server_collection = ServerMethodsCollection()

        # Process multiple methods
        for method_name in ["add", "subtract", "multiply"]:
            method_collection = MethodSignatureCollection(method_name)
            # method_collection.set_server_method(...) # Removed
            server_collection.add_server_method(f"    def {method_name}(self, context: Any) -> int: ...")

        # Verify all methods collected
        assert len(server_collection.server_methods) == 3
        assert all("context: Any" in sig for sig in server_collection.server_methods)
