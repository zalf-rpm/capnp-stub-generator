"""Functional tests for calculator nested interface generation.

Tests that nested interfaces (Calculator.Function, Calculator.Value) and
their Server classes are properly generated in stubs.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import run_pyright

TESTS_DIR = Path(__file__).parent
CALCULATOR_DIR = TESTS_DIR / "examples" / "calculator"


class TestCalculatorNestedInterfaceGeneration:
    """Test that nested interfaces are properly generated."""

    def test_nested_interfaces_exist_in_stub(self, generate_calculator_stubs):
        """Test that Calculator.Function and Calculator.Value are in the stub."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Check that the Calculator class exists
        assert "class Calculator" in content, "Calculator class should exist"

        # Check for nested interfaces - these should be generated as nested classes
        # The current implementation fails this
        assert "class Function" in content or "Function:" in content, (
            "Calculator.Function should be generated (nested interface)"
        )

        assert "class Value" in content or "Value:" in content, (
            "Calculator.Value should be generated (nested interface)"
        )

    def test_nested_struct_exists_in_stub(self, generate_calculator_stubs):
        """Test that Calculator.Expression (nested struct) is in the stub."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Calculator.Expression is a nested struct, should be generated
        assert "class Expression" in content, (
            "Calculator.Expression should be generated (nested struct)"
        )

    def test_nested_enum_exists_in_stub(self, generate_calculator_stubs):
        """Test that Calculator.Operator (nested enum) is in the stub."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Calculator.Operator is a nested enum, should be generated
        assert "class Operator" in content, "Calculator.Operator should be generated (nested enum)"

    def test_server_class_exists_for_interfaces(self, generate_calculator_stubs):
        """Test that Server classes are generated for interfaces."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Each interface should have a .Server class
        # This is critical for implementing servers
        assert "class Server" in content, "Server class should be generated for interfaces"

    def test_client_code_has_no_function_access_error(self, generate_calculator_stubs):
        """Test that Calculator.Function.Server can be accessed in client code."""
        file_path = CALCULATOR_DIR / "async_calculator_client.py"
        _, output = run_pyright(file_path)

        # This specific error should not exist after proper nesting implementation
        assert 'Cannot access attribute "Function"' not in output, (
            "Calculator.Function should be accessible"
        )

    def test_server_code_has_no_value_access_error(self, generate_calculator_stubs):
        """Test that Calculator.Value.Server can be accessed in server code."""
        file_path = CALCULATOR_DIR / "async_calculator_server.py"
        _, output = run_pyright(file_path)

        # These specific errors should not exist after proper nesting implementation
        assert 'Cannot access attribute "Value"' not in output, (
            "Calculator.Value should be accessible"
        )

        assert 'Cannot access attribute "Function"' not in output, (
            "Calculator.Function should be accessible"
        )

    def test_server_code_has_no_calculator_server_error(self, generate_calculator_stubs):
        """Test that Calculator.Server can be accessed."""
        file_path = CALCULATOR_DIR / "async_calculator_server.py"
        _, output = run_pyright(file_path)

        # Check that Calculator.Server is accessible
        if 'Cannot access attribute "Server"' in output and "Calculator" in output:
            pytest.fail(f"Calculator.Server should be accessible\nPyright output:\n{output}")


class TestCalculatorNestedInterfaceStructure:
    """Test the structure of nested interface generation."""

    def test_function_interface_has_call_method(self, generate_calculator_stubs):
        """Test that Calculator.Function has a call method."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # The Function interface should have a call method
        # This might be in a nested class or as part of the Protocol
        if "class Function" in content:
            # Find the Function class definition and check for call method
            lines = content.split("\n")
            in_function_class = False
            has_call_method = False

            for line in lines:
                if "class Function" in line:
                    in_function_class = True
                elif in_function_class and "class " in line and not line.startswith("    "):
                    # We've left the Function class
                    break
                elif in_function_class and "def call" in line:
                    has_call_method = True
                    break

            assert has_call_method, "Function interface should have a call method"

    def test_value_interface_has_read_method(self, generate_calculator_stubs):
        """Test that Calculator.Value has a read method."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # The Value interface should have a read method
        if "class Value" in content:
            lines = content.split("\n")
            in_value_class = False
            has_read_method = False

            for line in lines:
                if "class Value" in line:
                    in_value_class = True
                elif in_value_class and "class " in line and not line.startswith("    "):
                    # We've left the Value class
                    break
                elif in_value_class and "def read" in line:
                    has_read_method = True
                    break

            assert has_read_method, "Value interface should have a read method"


class TestCalculatorNestedTypesImprovement:
    """Track the overall improvement in nested types handling."""

    def test_overall_error_reduction_goal(self, generate_calculator_stubs):
        """Track progress toward zero errors in calculator example.

        Goal: Reduce errors to 0 by properly generating nested interfaces.
        Current baseline: 7 errors (1 client + 6 server)
        After nested interface fix: Should be significantly reduced
        """
        client_errors, client_output = run_pyright(CALCULATOR_DIR / "async_calculator_client.py")
        server_errors, server_output = run_pyright(CALCULATOR_DIR / "async_calculator_server.py")

        total_errors = client_errors + server_errors

        print(f"\nTotal calculator errors: {total_errors}")
        print(f"  Client: {client_errors}")
        print(f"  Server: {server_errors}")

        # Count specific error types
        nested_interface_errors = (
            client_output.count('Cannot access attribute "Function"')
            + client_output.count('Cannot access attribute "Value"')
            + server_output.count('Cannot access attribute "Function"')
            + server_output.count('Cannot access attribute "Value"')
            + server_output.count('Cannot access attribute "Server"')
        )

        print(f"  Nested interface access errors: {nested_interface_errors}")

        # Goal: After fixing nested interface generation, these should be 0
        assert nested_interface_errors == 0, (
            f"Nested interface errors should be 0 after fix, got {nested_interface_errors}\n"
            f"Client output:\n{client_output}\n\n"
            f"Server output:\n{server_output}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
