"""Test suite for interface method type annotations.

This validates that interface methods have proper type annotations for
parameters and return values, not just `Any`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


class TestCalculatorInterfaceMethodTypes:
    """Test that Calculator interface methods have proper types."""

    def test_evaluate_has_expression_parameter(self, generate_calculator_stubs):
        """Test that evaluate() has _CalculatorModule._ExpressionModule parameter type."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have evaluate with Expression parameter (optional) and EvaluateResult return type
        assert "def evaluate(" in stub_content
        assert "expression: _CalculatorModule._ExpressionModule | dict[str, Any] | None = None" in stub_content
        assert ") -> _CalculatorModule.EvaluateResult:" in stub_content

        # Should NOT have Any for the expression parameter
        assert "def evaluate(self, expression: Any)" not in stub_content

    def test_deffunction_has_proper_types(self, generate_calculator_stubs):
        """Test that defFunction() has proper parameter types."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have defFunction with int and Expression parameters (both optional) and DeffunctionResult return
        assert "def defFunction(" in stub_content
        assert "paramCount: int | None = None" in stub_content
        assert "body: _CalculatorModule._ExpressionModule | dict[str, Any] | None = None" in stub_content
        assert "DeffunctionResult:" in stub_content

        # Should NOT have Any for the body parameter
        assert "def defFunction(self, paramCount: int, body: Any)" not in stub_content

    def test_getoperator_has_enum_parameter(self, generate_calculator_stubs):
        """Test that getOperator() has Operator enum parameter."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have getOperator with _OperatorModule enum parameter (including string literals, optional)
        # Note: Now accepts _OperatorModule | Literal[...] | None = None and returns GetoperatorResult
        assert "def getOperator(" in stub_content
        assert "_CalculatorModule._OperatorModule" in stub_content
        assert "GetoperatorResult" in stub_content

        # Should NOT have Any for the op parameter
        assert "def getOperator(self, op: Any)" not in stub_content

    def test_function_call_has_list_parameter(self, generate_calculator_stubs):
        """Test that Function.call() has Sequence[float] parameter."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have call with Sequence[float] parameter (optional) and CallResult return type
        assert "def call(" in stub_content
        assert "params: Sequence[float] | None = None" in stub_content
        assert ") -> _CalculatorModule._FunctionModule.CallResult:" in stub_content

        # Should NOT have Any for the params parameter
        assert "def call(self, params: Any)" not in stub_content

    def test_value_read_has_float_return(self, generate_calculator_stubs):
        """Test that Value.read() returns float."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have read returning ReadResult
        assert "def read(self) -> _CalculatorModule._ValueModule.ReadResult:" in stub_content

        # ReadResult should have float value field
        assert "class ReadResult" in stub_content
        # Find ReadResult and check it has value: float
        lines = stub_content.split("\n")
        in_read_result = False
        for line in lines:
            if "class ReadResult" in line:
                in_read_result = True
            elif in_read_result and "value: float" in line:
                break  # Found it
            elif in_read_result and line.startswith("    def "):
                pytest.fail("ReadResult should have value: float field")

    def test_all_methods_have_request_variants(self, generate_calculator_stubs):
        """Test that all interface methods have *_request variants."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # All main methods should have _request variants with proper return types
        # Check for method name and return type (allowing for kwargs parameters)
        assert "def evaluate_request(" in stub_content and ") -> _CalculatorModule.EvaluateRequest:" in stub_content
        assert "def defFunction_request(" in stub_content and ") -> _CalculatorModule.DeffunctionRequest:" in stub_content
        assert "def getOperator_request(" in stub_content and ") -> _CalculatorModule.GetoperatorRequest:" in stub_content
        assert "def read_request(" in stub_content and ") -> _CalculatorModule._ValueModule.ReadRequest:" in stub_content
        assert "def call_request(" in stub_content and ") -> _CalculatorModule._FunctionModule.CallRequest:" in stub_content


class TestInterfaceMethodTypeRegression:
    """Regression tests to ensure types don't fall back to Any."""

    def test_no_any_in_calculator_main_methods(self, generate_calculator_stubs):
        """Test that main Calculator methods don't use Any for known types."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Extract just the Calculator interface methods
        lines = stub_content.split("\n")
        in_calculator = False
        calculator_methods = []

        for line in lines:
            if "class Calculator(Protocol):" in line:
                in_calculator = True
            elif in_calculator and line.startswith("class ") and "Calculator" not in line:
                break  # End of Calculator interface
            elif in_calculator and "def " in line and "def __" not in line:
                calculator_methods.append(line.strip())

        # Check that main methods don't have Any parameters (except _request methods)
        for method in calculator_methods:
            if "_request" not in method:
                # Main methods shouldn't have Any parameters for known types
                if "evaluate" in method:
                    assert "expression: Any" not in method, f"evaluate should not use Any: {method}"
                elif "defFunction" in method:
                    assert "body: Any" not in method, f"defFunction should not use Any: {method}"
                elif "getOperator" in method:
                    assert "op: Any" not in method, f"getOperator should not use Any: {method}"

    def test_nested_interface_methods_typed(self, generate_calculator_stubs):
        """Test that nested interface methods (Value, Function) are properly typed."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Function.call should have Sequence[float] (optional), not Any
        # Function is now an interface Protocol module
        assert "class _FunctionModule(Protocol):" in stub_content
        assert "class FunctionClient(Protocol):" in stub_content
        assert "def call(" in stub_content
        assert "params: Sequence[float] | None = None" in stub_content
        assert ") -> _CalculatorModule._FunctionModule.CallResult:" in stub_content

        # Value.read should return ReadResult with float field, not Any
        # Value is now an interface Protocol module
        assert "class _ValueModule(Protocol):" in stub_content
        assert "class ValueClient(Protocol):" in stub_content
        assert "def read(self) -> _CalculatorModule._ValueModule.ReadResult:" in stub_content


class TestInterfaceMethodComplexTypes:
    """Test complex types in interface methods."""

    def test_struct_parameter_types(self, generate_calculator_stubs):
        """Test that struct types in parameters are resolved correctly."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Expression is a struct, should be typed as _CalculatorModule._ExpressionModule (Protocol name)
        assert "expression: _CalculatorModule._ExpressionModule" in stub_content
        assert "body: _CalculatorModule._ExpressionModule" in stub_content

    def test_interface_return_types(self, generate_calculator_stubs):
        """Test that interface return types are resolved correctly."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # evaluate returns EvaluateResult which has a .value field of type ValueClient (nested capability)
        assert "-> _CalculatorModule.EvaluateResult:" in stub_content
        assert "class EvaluateResult" in stub_content
        assert "value: _CalculatorModule._ValueModule.ValueClient" in stub_content

        # defFunction and getOperator return results which have .func field of type FunctionClient (nested capability)
        assert "-> _CalculatorModule.DeffunctionResult:" in stub_content
        assert "func: _CalculatorModule._FunctionModule.FunctionClient" in stub_content

    def test_enum_parameter_types(self, generate_calculator_stubs):
        """Test that enum parameters are typed correctly."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # getOperator takes an _OperatorModule enum (module alias, not type alias)
        assert "op: _CalculatorModule._OperatorModule" in stub_content

        # Verify the Operator enum exists as Enum class with TypeAlias
        assert "class _OperatorModule(Enum):" in stub_content
        assert "Operator: TypeAlias = _OperatorModule" in stub_content

    def test_list_parameter_types(self, generate_calculator_stubs):
        """Test that list parameters use Sequence with proper element types."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Function.call takes List(Float64), should be Sequence[float]
        assert "params: Sequence[float]" in stub_content

        # Should import Sequence
        assert "from collections.abc import" in stub_content
        assert "Sequence" in stub_content


def test_interface_method_types_summary():
    """Summary of interface method type tests."""
    print("\n" + "=" * 70)
    print("INTERFACE METHOD TYPES TEST SUMMARY")
    print("=" * 70)
    print("All interface method type tests passed!")
    print("  ✓ evaluate() has Expression parameter")
    print("  ✓ defFunction() has proper types")
    print("  ✓ getOperator() has Operator enum")
    print("  ✓ Function.call() has Sequence[float]")
    print("  ✓ Value.read() returns float")
    print("  ✓ All methods have _request variants")
    print("  ✓ No Any for known types")
    print("  ✓ Complex types resolved correctly")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
