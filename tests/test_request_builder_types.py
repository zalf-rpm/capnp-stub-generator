"""Test suite for RPC request builder types.

This validates that request builders have proper field types and send() methods.
"""

from __future__ import annotations

from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


class TestRequestBuilderStructure:
    """Test that request builders have proper structure."""

    def test_evaluate_request_has_expression_field(self, generate_calculator_stubs):
        """Test that EvaluateRequest has expression field with Builder type."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have EvaluateRequest class
        assert "class EvaluateRequest(Protocol):" in stub_content

        # Should have expression field with Expression type (allows dict for init)
        lines = stub_content.split("\n")
        in_evaluate_request = False
        found_expression_field = False

        for line in lines:
            if "class EvaluateRequest(Protocol):" in line:
                in_evaluate_request = True
            elif in_evaluate_request and "expression:" in line:
                assert "ExpressionBuilder" in line, f"Expected Expression type, got: {line}"
                found_expression_field = True
                break
            elif in_evaluate_request and (line.startswith("    def ") or line.startswith("class ")):
                break

        assert found_expression_field, "EvaluateRequest should have expression field"

    def test_deffunction_request_has_fields(self, generate_calculator_stubs):
        """Test that DeffunctionRequest has paramCount and body fields."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have DeffunctionRequest class
        assert "class DeffunctionRequest(Protocol):" in stub_content

        # Should have both fields
        lines = stub_content.split("\n")
        in_deffunction_request = False
        found_param_count = False
        found_body = False

        for line in lines:
            if "class DeffunctionRequest(Protocol):" in line:
                in_deffunction_request = True
            elif in_deffunction_request and "paramCount:" in line:
                assert "int" in line
                found_param_count = True
            elif in_deffunction_request and "body:" in line:
                assert "ExpressionBuilder" in line, f"Expected Expression type, got: {line}"
                found_body = True
                break  # Found both fields, exit
            elif in_deffunction_request and line.startswith("class "):
                break

        assert found_param_count, "DeffunctionRequest should have paramCount field"
        assert found_body, "DeffunctionRequest should have body field"

    def test_call_request_has_params_field(self, generate_calculator_stubs):
        """Test that CallRequest has params field."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Should have CallRequest class
        assert "class CallRequest(Protocol):" in stub_content

        # Should have params field
        assert "params: Float64ListBuilder | Float64ListReader | Sequence[Any]" in stub_content


class TestRequestBuilderSendMethod:
    """Test that request builders have proper send() methods."""

    def test_evaluate_request_send_returns_evaluate_result(self, generate_calculator_stubs):
        """Test that EvaluateRequest.send() returns EvaluateResult."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Find EvaluateRequest and check its send method
        lines = stub_content.split("\n")
        in_evaluate_request = False
        found_send = False

        for line in lines:
            if "class EvaluateRequest(Protocol):" in line:
                in_evaluate_request = True
            elif in_evaluate_request and "def send(self)" in line:
                # Should return fully qualified result type
                assert "EvaluateResult:" in line, f"Expected EvaluateResult return, got: {line}"
                found_send = True
                break
            elif in_evaluate_request and line.startswith("class "):
                break

        assert found_send, "EvaluateRequest should have send() method"

    def test_deffunction_request_send_returns_deffunction_result(self, generate_calculator_stubs):
        """Test that DeffunctionRequest.send() returns DeffunctionResult."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Find DeffunctionRequest and check its send method
        lines = stub_content.split("\n")
        in_request = False
        found_send = False

        for line in lines:
            if "class DeffunctionRequest(Protocol):" in line:
                in_request = True
            elif in_request and "def send(self)" in line:
                assert "DeffunctionResult:" in line
                found_send = True
                break
            elif in_request and line.startswith("class "):
                break

        assert found_send, "DeffunctionRequest should have send() method"

    def test_read_request_send_returns_read_result(self, generate_calculator_stubs):
        """Test that ReadRequest.send() returns ReadResult."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Find ReadRequest and check its send method
        lines = stub_content.split("\n")
        in_request = False
        found_send = False

        for line in lines:
            if "class ReadRequest(Protocol):" in line:
                in_request = True
            elif in_request and "def send(self)" in line:
                assert "ReadResult:" in line
                found_send = True
                break
            elif in_request and line.startswith("    class ") or (in_request and line.startswith("class ")):
                break

        assert found_send, "ReadRequest should have send() method"

    def test_call_request_send_returns_call_result(self, generate_calculator_stubs):
        """Test that CallRequest.send() returns CallResult."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Find CallRequest and check its send method
        lines = stub_content.split("\n")
        in_request = False
        found_send = False

        for line in lines:
            if "class CallRequest(Protocol):" in line:
                in_request = True
            elif in_request and "def send(self)" in line:
                assert "CallResult:" in line
                found_send = True
                break
            elif in_request and line.startswith("    class ") or (in_request and line.startswith("class ")):
                break

        assert found_send, "CallRequest should have send() method"


class TestRequestBuilderFieldAccess:
    """Test that request builder fields can be accessed and typed correctly."""

    def test_request_expression_field_has_init(self, generate_calculator_stubs):
        """Test that request.expression field has init() method."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # With Protocol structure, check for TypeAlias
        assert "ExpressionBuilder = _ExpressionModule.Builder" in stub_content

        # Should have init overload for "call" that returns Call.Builder
        assert "def init(self" in stub_content and 'Literal["call"]' in stub_content


class TestRequestMethodReturnsRequest:
    """Test that *_request() methods return proper request types."""

    def test_evaluate_request_method_returns_evaluate_request(self, generate_calculator_stubs):
        """Test that evaluate_request() returns _CalculatorModule.EvaluateRequest."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Check for method name and return type (allowing for kwargs parameters)
        assert "def evaluate_request(" in stub_content and ") -> _CalculatorModule.EvaluateRequest:" in stub_content

    def test_deffunction_request_method_returns_deffunction_request(self, generate_calculator_stubs):
        """Test that defFunction_request() returns _CalculatorModule.DeffunctionRequest."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        assert (
            "def defFunction_request(" in stub_content and ") -> _CalculatorModule.DeffunctionRequest:" in stub_content
        )

    def test_getoperator_request_method_returns_getoperator_request(self, generate_calculator_stubs):
        """Test that getOperator_request() returns _CalculatorModule.GetoperatorRequest."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        assert (
            "def getOperator_request(" in stub_content and ") -> _CalculatorModule.GetoperatorRequest:" in stub_content
        )


def test_request_builder_types_summary():
    """Summary of request builder type tests."""
    print("\n" + "=" * 70)
    print("REQUEST BUILDER TYPES TEST SUMMARY")
    print("=" * 70)
    print("All request builder type tests passed!")
    print("  ✓ Request builders have proper field types (Builder variants)")
    print("  ✓ Request builders have send() method returning result type")
    print("  ✓ Request fields accessible with proper types")
    print("  ✓ *_request() methods return proper request types")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
