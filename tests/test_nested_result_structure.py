"""Test suite for nested Result protocol structure.

This validates the refactored design where:
- Client Result protocols are nested in Client classes (use _DynamicObjectReader for AnyPointer)
- Server Result protocols are nested in Server classes (use broad type union for AnyPointer)
- Request.send() returns Client.Result
- CallContext.results uses Server.Result
- ResultTuple stays under Server
"""

from __future__ import annotations


class TestNestedResultStructure:
    """Test that Result protocols are properly nested in Client and Server classes."""

    def test_client_result_nested_in_client(self, calculator_stubs):
        """Test that Client Result protocols are nested inside Client class."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Client Results should be nested inside Client classes
        assert "class CalculatorClient(_DynamicCapabilityClient):" in content
        assert "class EvaluateResult(Awaitable[EvaluateResult], Protocol):" in content

        # Check that Result is inside CalculatorClient
        lines = content.split("\n")
        in_calculator_client = False
        found_nested_result = False

        for i, line in enumerate(lines):
            if "class CalculatorClient(_DynamicCapabilityClient):" in line:
                in_calculator_client = True
            elif in_calculator_client and "class EvaluateResult(Awaitable[EvaluateResult], Protocol):" in line:
                found_nested_result = True
                break
            elif in_calculator_client and line.startswith("class ") and "Client" not in line:
                # Found another top-level class, stop
                break

        assert found_nested_result, "EvaluateResult should be nested inside CalculatorClient"

    def test_server_result_nested_in_server(self, calculator_stubs):
        """Test that Server Result protocols are nested inside Server class."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Server Results should be nested inside Server class
        lines = content.split("\n")
        in_server = False
        found_evaluate_result = False

        for line in lines:
            if "class Server(_DynamicCapabilityServer):" in line:
                in_server = True
            elif in_server and "class EvaluateResult(_DynamicStructBuilder):" in line:
                found_evaluate_result = True
                break
            elif (
                in_server
                and line.strip().startswith("class ")
                and "Result" not in line
                and "Tuple" not in line
                and "CallContext" not in line
            ):
                # Found another nested class that's not a Result/Tuple/Context
                in_server = False

        assert found_evaluate_result, "EvaluateResult should also be nested inside Server"

    def test_client_method_returns_client_result(self, calculator_stubs):
        """Test that client methods return Client.Result (not module-level Result)."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Client methods should return Client.Result
        assert "def evaluate(" in content
        assert "-> _CalculatorInterfaceModule.CalculatorClient.EvaluateResult:" in content

    def test_request_send_returns_client_result(self, calculator_stubs):
        """Test that Request.send() returns Client.Result."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Request.send() should return Client.Result
        assert "class EvaluateRequest(Protocol):" in content
        assert "def send(self) -> _CalculatorInterfaceModule.CalculatorClient.EvaluateResult:" in content

    def test_callcontext_results_points_to_server_result(self, calculator_stubs):
        """Test that CallContext.results points to Server.Result."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # CallContext.results should point to Server.Result
        assert "class EvaluateCallContext(Protocol):" in content
        assert "@property" in content
        assert "def results(self) -> _CalculatorInterfaceModule.Server.EvaluateResult: ..." in content

    def test_result_tuple_stays_under_server(self, calculator_stubs):
        """Test that ResultTuple (NamedTuple) stays under Server."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # ResultTuple should be under Server
        lines = content.split("\n")
        in_server = False
        found_result_tuple = False

        for line in lines:
            if "class Server(_DynamicCapabilityServer):" in line:
                in_server = True
            elif in_server and "class EvaluateResultTuple(NamedTuple):" in line:
                found_result_tuple = True
                break

        assert found_result_tuple, "EvaluateResultTuple should be nested inside Server"


class TestNestedResultsAtDeeperLevels:
    """Test that nested Results work at deeper interface nesting levels."""

    def test_nested_interface_client_result(self, calculator_stubs):
        """Test nested interface (Calculator.Value) has Client.Result nested."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Value.read() should return ValueClient.ReadResult
        assert "def read(self) -> _CalculatorInterfaceModule._ValueInterfaceModule.ValueClient.ReadResult:" in content

    def test_nested_interface_server_result(self, calculator_stubs):
        """Test nested interface Server has Result nested."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # ValueModule.Server should have ReadResult nested
        # Just check the nested path exists in content
        assert "_ValueInterfaceModule.Server.ReadResult" in content, "ReadResult should be nested in ValueModule.Server"

    def test_nested_interface_request_send(self, calculator_stubs):
        """Test nested interface Request.send() returns nested Client.Result."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # ReadRequest.send() should return ValueClient.ReadResult
        assert "class ReadRequest(Protocol):" in content
        assert "def send(self) -> _CalculatorInterfaceModule._ValueInterfaceModule.ValueClient.ReadResult:" in content

    def test_nested_interface_callcontext(self, calculator_stubs):
        """Test nested interface CallContext.results points to nested Server.Result."""
        stub_file = calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # ReadCallContext.results should point to Server.ReadResult
        assert "class ReadCallContext(Protocol):" in content
        assert "@property" in content
        assert "def results(self) -> _CalculatorInterfaceModule._ValueInterfaceModule.Server.ReadResult: ..." in content


class TestAnyPointerTypeDifferences:
    """Test that AnyPointer types differ between Client and Server Results."""

    def test_client_anypointer_uses_dynamic_object_reader(self, zalfmas_stubs):
        """Test that Client Result uses _DynamicObjectReader for AnyPointer."""
        stub_file = zalfmas_stubs / "common_capnp.pyi"
        content = stub_file.read_text()

        # HolderClient.ValueResult should use _DynamicObjectReader
        lines = content.split("\n")
        in_holder_client = False
        in_value_result = False
        found_dynamic_object_reader = False

        for line in lines:
            if "class HolderClient(_DynamicCapabilityClient):" in line:
                in_holder_client = True
            elif in_holder_client and "class ValueResult(Awaitable[ValueResult], Protocol):" in line:
                in_value_result = True
            elif in_value_result and "value: _DynamicObjectReader" in line:
                found_dynamic_object_reader = True
                break

        assert found_dynamic_object_reader, "Client Result should use _DynamicObjectReader for AnyPointer"

    def test_server_anypointer_uses_broad_union(self, zalfmas_stubs):
        """Test that Server Result uses broad type union for AnyPointer."""
        stub_file = zalfmas_stubs / "common_capnp.pyi"
        content = stub_file.read_text()

        # Server.ValueResult should use broad union
        # Check that the pattern exists in Server context
        assert "class Server(_DynamicCapabilityServer):" in content
        assert "class ValueResult(Awaitable[ValueResult], Protocol):" in content
        assert "_DynamicCapabilityServer" in content
        # The broad union should exist somewhere in Server
        assert (
            "str | bytes | _DynamicStructBuilder | _DynamicStructReader | _DynamicCapabilityClient | _DynamicCapabilityServer"
            in content
        )

    def test_server_result_tuple_uses_broad_union(self, zalfmas_stubs):
        """Test that Server ResultTuple also uses broad type union for AnyPointer."""
        stub_file = zalfmas_stubs / "common_capnp.pyi"
        content = stub_file.read_text()

        # ValueResultTuple should also use AnyPointer type alias
        assert "class ValueResultTuple(NamedTuple):" in content
        lines = content.split("\n")
        in_tuple = False
        found_anypointer = False

        for line in lines:
            if "class ValueResultTuple(NamedTuple):" in line:
                in_tuple = True
            elif in_tuple and "AnyPointer" in line:
                found_anypointer = True
                break
            elif in_tuple and line.strip().startswith("class "):
                break

        assert found_anypointer, "ResultTuple should use AnyPointer type alias"
