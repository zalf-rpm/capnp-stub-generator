"""Test suite for flattened interface helper structure.

This validates the refactored design where:
- Client Result protocols are flattened to module top level
- Server Result protocols are flattened to module top level
- Request.send() returns top-level Result helpers
- CallContext.results uses top-level ServerResult helpers
- ResultTuple helpers are flattened to module top level
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.test_helpers import read_generated_types_combined

if TYPE_CHECKING:
    from pathlib import Path


class TestNestedResultStructure:
    """Test that Result protocols are properly flattened to module top level."""

    def test_client_result_nested_in_client(self, calculator_stubs: Path) -> None:
        """Test that Client Result protocols are top-level helpers."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "class CalculatorClient(_DynamicCapabilityClient):" in content
        assert "class EvaluateResult(Awaitable[EvaluateResult], Protocol):" in content
        assert "def evaluate(" in content
        assert "-> EvaluateResult:" in content

    def test_server_result_nested_in_server(self, calculator_stubs: Path) -> None:
        """Test that Server Result helpers are top-level."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "class EvaluateServerResult(_DynamicStructBuilder):" in content
        assert "def results(self) -> EvaluateServerResult: ..." in content

    def test_client_method_returns_client_result(self, calculator_stubs: Path) -> None:
        """Test that client methods return top-level Result helpers."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "def evaluate(" in content
        assert "-> EvaluateResult:" in content

    def test_request_send_returns_client_result(self, calculator_stubs: Path) -> None:
        """Test that Request.send() returns a top-level Result helper."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "class EvaluateRequest(Protocol):" in content
        assert "def send(self) -> EvaluateResult:" in content

    def test_callcontext_results_points_to_server_result(self, calculator_stubs: Path) -> None:
        """Test that CallContext.results points to a top-level ServerResult helper."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "class EvaluateCallContext(Protocol):" in content
        assert "@property" in content
        assert "def results(self) -> EvaluateServerResult: ..." in content

    def test_result_tuple_stays_under_server(self, calculator_stubs: Path) -> None:
        """Test that ResultTuple helpers are flattened to module top level."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "class EvaluateResultTuple(NamedTuple):" in content


class TestNestedResultsAtDeeperLevels:
    """Test that nested Results work at deeper interface nesting levels."""

    def test_nested_interface_client_result(self, calculator_stubs: Path) -> None:
        """Test nested interface (Calculator.Value) has top-level Result helpers."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "def read(self) -> ReadResult:" in content

    def test_nested_interface_server_result(self, calculator_stubs: Path) -> None:
        """Test nested interface Server uses top-level ServerResult helpers."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "class ReadServerResult(_DynamicStructBuilder):" in content
        assert "def results(self) -> ReadServerResult: ..." in content

    def test_nested_interface_request_send(self, calculator_stubs: Path) -> None:
        """Test nested interface Request.send() returns a top-level Result helper."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "class ReadRequest(Protocol):" in content
        assert "def send(self) -> ReadResult:" in content

    def test_nested_interface_callcontext(self, calculator_stubs: Path) -> None:
        """Test nested interface CallContext.results points to a top-level ServerResult helper."""
        content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

        assert "class ReadCallContext(Protocol):" in content
        assert "@property" in content
        assert "def results(self) -> ReadServerResult: ..." in content


class TestAnyPointerTypeDifferences:
    """Test that AnyPointer types differ between Client and Server Results."""

    def test_client_anypointer_uses_dynamic_object_reader(self, zalfmas_stubs: Path) -> None:
        """Test that Client Result uses _DynamicObjectReader for AnyPointer."""
        content = read_generated_types_combined(zalfmas_stubs / "mas/schema/common/common_capnp")

        # Holder.ValueResult should use _DynamicObjectReader
        lines = content.split("\n")
        in_value_result = False
        found_dynamic_object_reader = False

        for line in lines:
            if "class ValueResult(Awaitable[ValueResult], Protocol):" in line:
                in_value_result = True
            elif in_value_result and "value: _DynamicObjectReader" in line:
                found_dynamic_object_reader = True
                break

        assert found_dynamic_object_reader, "Client Result should use _DynamicObjectReader for AnyPointer"

    def test_server_anypointer_uses_broad_union(self, zalfmas_stubs: Path) -> None:
        """Test that Server Result uses broad type union for AnyPointer."""
        content = read_generated_types_combined(zalfmas_stubs / "mas/schema/common/common_capnp")

        # ServerResult should use broad union (now via AnyPointer type alias)
        assert "type AnyPointer = (" in content
        assert "_DynamicCapabilityServer" in content
        assert "_DynamicStructBuilder" in content
        assert "class ValueServerResult(_DynamicStructBuilder):" in content

    def test_server_result_tuple_uses_broad_union(self, zalfmas_stubs: Path) -> None:
        """Test that Server ResultTuple also uses broad type union for AnyPointer."""
        content = read_generated_types_combined(zalfmas_stubs / "mas/schema/common/common_capnp")

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
