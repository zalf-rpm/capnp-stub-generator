"""Test suite for RPC request builder types.

This validates that request builders have proper field types and send() methods.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_helpers import log_summary, read_generated_types_combined

TESTS_DIR = Path(__file__).parent


class TestRequestBuilderStructure:
    """Test that request builders have proper structure."""

    def test_evaluate_request_has_expression_field(self, generate_calculator_stubs: Path) -> None:
        """Test that EvaluateRequest has expression field with Builder type."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

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
            elif in_evaluate_request and (line.startswith(("    def ", "class "))):
                break

        assert found_expression_field, "EvaluateRequest should have expression field"

    def test_deffunction_request_has_fields(self, generate_calculator_stubs: Path) -> None:
        """Test that DeffunctionRequest has paramCount and body fields."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

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

    def test_call_request_has_params_field(self, generate_calculator_stubs: Path) -> None:
        """Test that CallRequest has params field."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Should have CallRequest class
        assert "class CallRequest(Protocol):" in stub_content

        # Should have params field
        assert "params: Float64ListBuilder | Float64ListReader | Sequence[Any]" in stub_content


class TestRequestBuilderSendMethod:
    """Test that request builders have proper send() methods."""

    def test_evaluate_request_send_returns_evaluate_result(self, generate_calculator_stubs: Path) -> None:
        """Test that EvaluateRequest.send() returns EvaluateResult."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

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

    def test_deffunction_request_send_returns_deffunction_result(self, generate_calculator_stubs: Path) -> None:
        """Test that DeffunctionRequest.send() returns DeffunctionResult."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

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

    def test_read_request_send_returns_read_result(self, generate_calculator_stubs: Path) -> None:
        """Test that ReadRequest.send() returns ReadResult."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

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
            elif (in_request and line.startswith("    class ")) or (in_request and line.startswith("class ")):
                break

        assert found_send, "ReadRequest should have send() method"

    def test_call_request_send_returns_call_result(self, generate_calculator_stubs: Path) -> None:
        """Test that CallRequest.send() returns CallResult."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

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
            elif (in_request and line.startswith("    class ")) or (in_request and line.startswith("class ")):
                break

        assert found_send, "CallRequest should have send() method"


class TestRequestBuilderFieldAccess:
    """Test that request builder fields can be accessed and typed correctly."""

    def test_request_expression_field_has_init(self, generate_calculator_stubs: Path) -> None:
        """Test that request.expression field has init() method."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # The precise struct typing class is flattened to module top level.
        assert "class ExpressionBuilder(_DynamicStructBuilder):" in stub_content

        # Should have init overload for "call" that returns Call.Builder
        assert "def init(self" in stub_content
        assert 'Literal["call"]' in stub_content


class TestRequestMethodReturnsRequest:
    """Test that *_request() methods return proper request types."""

    def test_evaluate_request_method_returns_evaluate_request(self, generate_calculator_stubs: Path) -> None:
        """Test that evaluate_request() returns the flattened top-level EvaluateRequest."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Check for method name and return type (allowing for kwargs parameters)
        assert "def evaluate_request(" in stub_content
        assert ") -> EvaluateRequest:" in stub_content

    def test_deffunction_request_method_returns_deffunction_request(self, generate_calculator_stubs: Path) -> None:
        """Test that defFunction_request() returns the flattened top-level DeffunctionRequest."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        assert "def defFunction_request(" in stub_content
        assert ") -> DeffunctionRequest:" in stub_content

    def test_getoperator_request_method_returns_getoperator_request(self, generate_calculator_stubs: Path) -> None:
        """Test that getOperator_request() returns the flattened top-level GetoperatorRequest."""
        stub_content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        assert "def getOperator_request(" in stub_content
        assert ") -> GetoperatorRequest:" in stub_content


def test_request_builder_types_summary() -> None:
    """Summary of request builder type tests."""
    log_summary(
        "REQUEST BUILDER TYPES TEST SUMMARY",
        [
            "All request builder type tests passed!",
            "  ✓ Request builders have proper field types (Builder variants)",
            "  ✓ Request builders have send() method returning result type",
            "  ✓ Request fields accessible with proper types",
            "  ✓ *_request() methods return proper request types",
        ],
    )


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
