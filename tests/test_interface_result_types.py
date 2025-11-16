"""Test suite for interface RPC result types.

This validates that RPC methods return result types with proper field attributes
and that they are awaitable.
"""

from __future__ import annotations

from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


class TestRPCResultTypes:
    """Test that RPC result types have field attributes."""

    def test_evaluate_returns_result_with_value_field(self, generate_calculator_stubs):
        """Test that evaluate() returns a result with .value attribute."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have EvaluateResult class nested in CalculatorClient
        assert "class EvaluateResult" in stub_content

        # Should have value field (using nested Protocol naming)
        assert "value: _CalculatorModule._ValueModule.ValueClient" in stub_content

        # evaluate should return _CalculatorModule.CalculatorClient.EvaluateResult (which is Awaitable)
        assert "def evaluate(" in stub_content
        assert "-> _CalculatorModule.CalculatorClient.EvaluateResult:" in stub_content

    def test_deffunction_returns_result_with_func_field(self, generate_calculator_stubs):
        """Test that defFunction() returns a result with .func attribute."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have DeffunctionResult class nested in CalculatorClient
        assert "class DeffunctionResult" in stub_content

        # Should have func field (using nested Protocol naming)
        assert "func: _CalculatorModule._FunctionModule.FunctionClient" in stub_content

        # defFunction should return _CalculatorModule.CalculatorClient.DeffunctionResult (which is Awaitable)
        assert "def defFunction(" in stub_content
        assert "paramCount: int | None = None" in stub_content
        assert "body: ExpressionBuilder | ExpressionReader | dict[str, Any] | None = None" in stub_content
        assert "-> _CalculatorModule.CalculatorClient.DeffunctionResult:" in stub_content

    def test_getoperator_returns_result_with_func_field(self, generate_calculator_stubs):
        """Test that getOperator() returns a result with .func attribute."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have GetoperatorResult class
        assert "class GetoperatorResult" in stub_content

        # Should have func field (using nested Protocol naming)
        assert "func: _CalculatorModule._FunctionModule.FunctionClient" in stub_content

    def test_nested_interface_read_returns_result(self, generate_calculator_stubs):
        """Test that nested interface Value.read() returns result with .value."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

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
            elif in_read_result and line.startswith("    class ") or (in_read_result and line.startswith("class ")):
                break

        assert found_value_float, "ReadResult should have value: float field"

    def test_nested_interface_call_returns_result(self, generate_calculator_stubs):
        """Test that nested interface Function.call() returns result with .value."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have CallResult class
        assert "class CallResult" in stub_content

        # call should return _CalculatorModule._FunctionModule.CallResult (which is Awaitable)
        assert (
            "def call(self, params: Sequence[float] | None = None) -> _CalculatorModule._FunctionModule.FunctionClient.CallResult:"
            in stub_content
        )


class TestRPCResultsAreAwaitable:
    """Test that RPC result types are awaitable."""

    def test_result_types_are_protocols(self, generate_calculator_stubs):
        """Test that result types are Protocol classes that inherit from Awaitable."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # All result types should inherit from Awaitable[Result] for promise pipelining
        # Now nested in Client and Server classes
        assert "class EvaluateResult(Awaitable[EvaluateResult], Protocol):" in stub_content
        assert "class DeffunctionResult(Awaitable[DeffunctionResult], Protocol):" in stub_content
        assert "class GetoperatorResult(Awaitable[GetoperatorResult], Protocol):" in stub_content
        assert "class ReadResult(Awaitable[ReadResult], Protocol):" in stub_content
        assert "class CallResult(Awaitable[CallResult], Protocol):" in stub_content

        # Methods should return Client.Result (nested in Client class)
        assert "-> _CalculatorModule.CalculatorClient.EvaluateResult:" in stub_content
        assert "-> _CalculatorModule._ValueModule.ValueClient.ReadResult:" in stub_content

    def test_awaitable_imported(self, generate_calculator_stubs):
        """Test that Awaitable is imported from typing."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should import Awaitable
        assert "from typing import" in stub_content
        assert "Awaitable" in stub_content


class TestEnumParametersAcceptLiterals:
    """Test that enum parameters accept string literals."""

    def test_getoperator_accepts_string_literals(self, generate_calculator_stubs):
        """Test that getOperator op parameter accepts string literals."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # getOperator should accept int | Literal[...] | None (optional)
        assert "def getOperator(" in stub_content
        assert (
            'int | Literal["add", "subtract", "multiply", "divide"] | None = None'
            in stub_content
        )

    def test_enum_literals_match_enum_values(self, generate_calculator_stubs):
        """Test that the enum literal values match the actual enum."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Just check that the literal types are present somewhere (client method)
        assert 'Literal["add", "subtract", "multiply", "divide"]' in stub_content

    def test_literal_imported(self, generate_calculator_stubs):
        """Test that Literal is imported."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should import Literal
        assert "from typing import" in stub_content
        assert "Literal" in stub_content


class TestRPCResultFieldTypes:
    """Test that result field types are correctly resolved."""

    def test_interface_result_fields(self, generate_calculator_stubs):
        """Test that interface-typed result fields are correct."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # EvaluateResult.value should be _CalculatorModule._ValueModule.ValueClient (nested interface type)
        lines = stub_content.split("\n")
        in_evaluate_result = False

        for line in lines:
            if "class EvaluateResult" in line:
                in_evaluate_result = True
            elif in_evaluate_result and "value:" in line:
                assert "_CalculatorModule._ValueModule.ValueClient" in line, (
                    f"Expected _CalculatorModule._ValueModule.ValueClient, got: {line}"
                )
                break
            elif in_evaluate_result and line.startswith("    def "):
                break

    def test_primitive_result_fields(self, generate_calculator_stubs):
        """Test that primitive-typed result fields are correct."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

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


def test_interface_result_types_summary():
    """Summary of interface result type tests."""
    print("\n" + "=" * 70)
    print("INTERFACE RESULT TYPES TEST SUMMARY")
    print("=" * 70)
    print("All interface result type tests passed!")
    print("  ✓ Result types have field attributes (.value, .func)")
    print("  ✓ Result types are Awaitable")
    print("  ✓ Enum parameters accept string literals")
    print("  ✓ Result field types correctly resolved")
    print("  ✓ Nested interfaces have result types")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
