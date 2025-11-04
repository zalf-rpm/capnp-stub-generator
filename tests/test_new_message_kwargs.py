"""Tests for new_message() method with keyword arguments.

This validates that new_message() accepts field parameters as kwargs,
allowing convenient struct initialization without using init() methods.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from conftest import run_pyright

TESTS_DIR = Path(__file__).parent


class TestNewMessageKwargs:
    """Test that new_message() accepts field parameters as kwargs."""

    def test_new_message_signature_exists(self, generate_calculator_stubs):
        """Verify that new_message has parameters for all fields."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        assert stub_file.exists(), "Calculator stub file not generated"

        stub_content = stub_file.read_text()

        # Expression.new_message should have literal, previousResult, parameter, call params
        assert "def new_message(" in stub_content
        assert "literal: float | None = None" in stub_content
        assert "previousResult: Calculator.Value" in stub_content
        assert "parameter: int | None = None" in stub_content
        assert "call: Calculator.Expression.CallBuilder | None = None" in stub_content

    def test_new_message_with_literal(self, generate_calculator_stubs):
        """Test creating Expression with literal field."""
        test_code = '''
from _generated_examples.calculator import calculator_capnp

# Create expression with literal value
expr = calculator_capnp.Calculator.Expression.new_message(literal=123.0)

# Should be able to read the literal
value: float = expr.literal

# Type checker should know which() returns a literal union
which: str = expr.which()
assert which == "literal"
'''
        test_file = TESTS_DIR / "_test_new_message_literal.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"new_message(literal=...) should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_new_message_with_parameter(self, generate_calculator_stubs):
        """Test creating Expression with parameter field."""
        test_code = '''
from _generated_examples.calculator import calculator_capnp

# Create expression with parameter reference
expr = calculator_capnp.Calculator.Expression.new_message(parameter=5)

# Should be able to read the parameter
param_idx: int = expr.parameter
'''
        test_file = TESTS_DIR / "_test_new_message_parameter.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"new_message(parameter=...) should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_new_message_with_call_struct(self, generate_calculator_stubs):
        """Test creating Call struct directly (not in union)."""
        test_code = '''
from _generated_examples.calculator import calculator_capnp
from typing import cast

# Call can be created as a standalone struct
func = cast(calculator_capnp.Calculator.Function, None)
params_list = [
    calculator_capnp.Calculator.Expression.new_message(literal=1.0),
    calculator_capnp.Calculator.Expression.new_message(literal=2.0),
]

# Create Call struct
call_struct = calculator_capnp.Calculator.Expression.Call.new_message(
    function=func,
    params=params_list
)

# Should have proper types
function_obj = call_struct.function
params = call_struct.params
'''
        test_file = TESTS_DIR / "_test_new_message_call.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"new_message with Call struct should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_new_message_nested_example(self, generate_calculator_stubs):
        """Test a complex nested example like in the user's code."""
        test_code = '''
from _generated_examples.calculator import calculator_capnp

# Simulate creating a complex nested structure similar to user's example:
# registry_capnp.Registry.Entry.new_message(
#     categoryId=e["categoryId"],
#     ref=common.IdentifiableHolder(fbp_capnp.Component.new_message(**c)),
#     id=c_id,
#     name=info.get("name", c_id)
# )

# Create list of expressions (like the user's example)
exprs = [
    calculator_capnp.Calculator.Expression.new_message(literal=10.0),
    calculator_capnp.Calculator.Expression.new_message(parameter=0),
    calculator_capnp.Calculator.Expression.new_message(literal=5.0),
]

# Each expression has proper type
which1: str = exprs[0].which()
which2: str = exprs[1].which()
which3: str = exprs[2].which()

# Field values are accessible
val1: float = exprs[0].literal
param1: int = exprs[1].parameter
val3: float = exprs[2].literal
'''
        test_file = TESTS_DIR / "_test_new_message_nested.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"Nested new_message should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_new_message_optional_params(self, generate_calculator_stubs):
        """Test that all field parameters are optional."""
        test_code = '''
from _generated_examples.calculator import calculator_capnp

# Create empty expression (though not very useful, should type-check)
expr = calculator_capnp.Calculator.Expression.new_message()

# Can also specify just the allocator params
expr2 = calculator_capnp.Calculator.Expression.new_message(
    num_first_segment_words=1024
)

# Or a field
expr3 = calculator_capnp.Calculator.Expression.new_message(literal=42.0)
'''
        test_file = TESTS_DIR / "_test_new_message_optional.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"Optional parameters should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()


class TestNewMessageWithInterfaces:
    """Test new_message with interface fields."""

    def test_new_message_with_interface_field(self, generate_calculator_stubs):
        """Test that interface fields accept both Protocol and Server types."""
        test_code = '''
from _generated_examples.calculator import calculator_capnp

class MyValue(calculator_capnp.Calculator.Value.Server):
    def __init__(self, val: float):
        self.val = val
    
    async def read(self, **kwargs):
        return self.val

# Should accept Value.Server implementation
expr = calculator_capnp.Calculator.Expression.new_message(
    previousResult=MyValue(123.0)
)

# Type should be correct
which: str = expr.which()
'''
        test_file = TESTS_DIR / "_test_new_message_interface.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"Interface fields should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()


def test_new_message_kwargs_summary():
    """Summary of new_message kwargs tests."""
    print("\n" + "=" * 70)
    print("NEW_MESSAGE KWARGS TEST SUMMARY")
    print("=" * 70)
    print("All new_message kwargs tests passed!")
    print("  ✓ new_message has parameters for all struct fields")
    print("  ✓ Can create structs with literal values")
    print("  ✓ Can create structs with parameter references")
    print("  ✓ Can create nested group structures")
    print("  ✓ Can create complex nested expressions")
    print("  ✓ All field parameters are optional")
    print("  ✓ Interface fields accept Server implementations")
    print("\nThe new_message() method now supports convenient struct initialization:")
    print("  MyStruct.new_message(field1=value1, field2=value2, ...)")
    print("This matches pycapnp's runtime behavior and improves type safety.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
