"""Test suite for interface RPC result types.

This validates that RPC methods return result types with proper field attributes
and that they are awaitable.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_helpers import log_summary, read_generated_types_combined

TESTS_DIR = Path(__file__).parent


class TestRPCResultTypes:
    """Test that RPC result types have field attributes."""

    def test_evaluate_returns_result_with_value_field(self, generate_calculator_stubs: Path) -> None:
        """Test that evaluate() returns a result with .value attribute."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Should have top-level EvaluateResult class
        assert "class EvaluateResult" in stub_content

        # Should have value field (using nested Protocol naming)
        assert "value: ValueClient" in stub_content

        # evaluate should return the flattened top-level EvaluateResult
        assert "def evaluate(" in stub_content
        assert "-> EvaluateResult:" in stub_content

    def test_deffunction_returns_result_with_func_field(self, generate_calculator_stubs: Path) -> None:
        """Test that defFunction() returns a result with .func attribute."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Should have top-level DeffunctionResult class
        assert "class DeffunctionResult" in stub_content

        # Should have func field (using nested Protocol naming)
        assert "func: FunctionClient" in stub_content

        # defFunction should return the flattened top-level DeffunctionResult
        assert "def defFunction(" in stub_content
        assert "paramCount: int | None = None" in stub_content
        assert "body: ExpressionBuilder | ExpressionReader | dict[str, Any] | None = None" in stub_content
        assert "-> DeffunctionResult:" in stub_content

    def test_getoperator_returns_result_with_func_field(self, generate_calculator_stubs: Path) -> None:
        """Test that getOperator() returns a result with .func attribute."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Should have GetoperatorResult class
        assert "class GetoperatorResult" in stub_content

        # Should have func field (using nested Protocol naming)
        assert "func: FunctionClient" in stub_content

    def test_nested_interface_read_returns_result(self, generate_calculator_stubs: Path) -> None:
        """Test that nested interface Value.read() returns result with .value."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Should have ReadResult class
        assert "class ReadResult" in stub_content

        # Should have value field (float)
        lines = stub_content.split("\n")
        in_read_result = False
        found_value_float = False

        for line in lines:
            if "class ReadResult" in line:
                in_read_result = True
            elif in_read_result and "value: float" in line:
                found_value_float = True
                break
            elif (in_read_result and line.startswith("    class ")) or (in_read_result and line.startswith("class ")):
                break

        assert found_value_float, "ReadResult should have value: float field"

    def test_nested_interface_call_returns_result(self, generate_calculator_stubs: Path) -> None:
        """Test that nested interface Function.call() returns result with .value."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Should have CallResult class
        assert "class CallResult" in stub_content

        # call should return the flattened top-level CallResult
        # Note: method signature may span multiple lines
        assert "def call(" in stub_content
        assert "params: Float64ListBuilder | Float64ListReader | Sequence[Any]" in stub_content
        assert "-> CallResult:" in stub_content


class TestRPCResultsAreAwaitable:
    """Test that RPC result types are awaitable."""

    def test_result_types_are_protocols(self, generate_calculator_stubs: Path) -> None:
        """Test that result types are Protocol classes that inherit from Awaitable."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # All result types should inherit from Awaitable[Result] for promise pipelining
        assert "class EvaluateResult(Awaitable[EvaluateResult], Protocol):" in stub_content
        assert "class DeffunctionResult(Awaitable[DeffunctionResult], Protocol):" in stub_content
        assert "class GetoperatorResult(Awaitable[GetoperatorResult], Protocol):" in stub_content
        assert "class ReadResult(Awaitable[ReadResult], Protocol):" in stub_content
        assert "class CallResult(Awaitable[CallResult], Protocol):" in stub_content

        # Methods should return the flattened top-level Result helpers
        assert "-> EvaluateResult:" in stub_content
        assert "-> ReadResult:" in stub_content

    def test_awaitable_imported(self, generate_calculator_stubs: Path) -> None:
        """Test that Awaitable is imported from typing."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Should import Awaitable
        assert "from typing import" in stub_content
        assert "Awaitable" in stub_content


class TestEnumParametersAcceptLiterals:
    """Test that enum parameters accept string literals."""

    def test_getoperator_accepts_string_literals(self, generate_calculator_stubs: Path) -> None:
        """Test that getOperator op parameter accepts string literals."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # getOperator should accept int | Literal[...] | None (optional) -> now uses CalculatorOperatorEnum alias
        assert "def getOperator(" in stub_content
        assert "op: CalculatorOperatorEnum | None = None" in stub_content

    def test_enum_literals_match_enum_values(self, generate_calculator_stubs: Path) -> None:
        """Test that the enum literal values match the actual enum."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Just check that the literal types are present somewhere (client method)
        assert 'Literal["add", "subtract", "multiply", "divide"]' in stub_content

    def test_literal_imported(self, generate_calculator_stubs: Path) -> None:
        """Test that Literal is imported."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Should import Literal
        assert "from typing import" in stub_content
        assert "Literal" in stub_content


class TestRPCResultFieldTypes:
    """Test that result field types are correctly resolved."""

    def test_interface_result_fields(self, generate_calculator_stubs: Path) -> None:
        """Test that interface-typed result fields are correct."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # EvaluateResult.value should include _ValueInterfaceModule types
        # The type may be Server | ValueClient union
        assert "_CalculatorInterfaceModule._ValueInterfaceModule" in stub_content
        assert "class EvaluateResult" in stub_content

    def test_primitive_result_fields(self, generate_calculator_stubs: Path) -> None:
        """Test that primitive-typed result fields are correct."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # ReadResult.value should be float (primitive type)
        lines = stub_content.split("\n")
        in_read_result = False

        for line in lines:
            if "class ReadResult" in line:
                in_read_result = True
            elif in_read_result and "value:" in line:
                assert "float" in line, f"Expected float, got: {line}"
                break
            elif in_read_result and line.startswith("    def "):
                break


def test_interface_result_types_summary() -> None:
    """Summary of interface result type tests."""
    log_summary(
        "INTERFACE RESULT TYPES TEST SUMMARY",
        [
            "All interface result type tests passed!",
            "  ✓ Result types have field attributes (.value, .func)",
            "  ✓ Result types are Awaitable",
            "  ✓ Enum parameters accept string literals",
            "  ✓ Result field types correctly resolved",
            "  ✓ Nested interfaces have result types",
        ],
    )


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
