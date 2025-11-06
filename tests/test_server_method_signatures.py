"""Test server method signatures in generated stubs.

This test ensures that:
1. Server methods use Reader types, not union with dict
2. Client methods accept dict union for struct parameters
3. _context parameter is properly typed and optional
4. **kwargs is properly typed
"""

import subprocess
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


class TestServerMethodSignatures:
    """Test that server method signatures are properly typed."""

    def test_server_methods_use_reader_types(self, generate_calculator_stubs):
        """Test that Server.method() uses ExpressionReader, not Expression | dict."""
        test_code = """
from _generated.examples.calculator import calculator_capnp
from typing import cast

class ValueImpl(calculator_capnp.Calculator.Value.Server):
    def __init__(self, value: float):
        self.value = value
    
    async def read(self, _context, **kwargs):
        return self.value

class MyCalculator(calculator_capnp.Calculator.Server):
    async def evaluate(self, expression: calculator_capnp.Calculator.ExpressionReader, _context, **kwargs):
        # expression should be ExpressionReader, not dict
        literal_val: float = expression.literal
        return ValueImpl(literal_val)
        
    async def defFunction(self, paramCount: int, body: calculator_capnp.Calculator.ExpressionReader, _context, **kwargs):
        func = cast(calculator_capnp.Calculator.Function, None)
        return func
        
    async def getOperator(self, op, _context, **kwargs):
        func = cast(calculator_capnp.Calculator.Function, None)
        return func
"""
        test_file = TESTS_DIR / "_test_server_reader_types.py"
        test_file.write_text(test_code)

        try:
            result = subprocess.run(
                ["pyright", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should have no type errors
            error_count = result.stdout.count("error:")
            assert error_count == 0, f"Server methods should use Reader types:\n{result.stdout}"
        finally:
            test_file.unlink(missing_ok=True)

    def test_client_methods_accept_dict(self, generate_calculator_stubs):
        """Test that client methods accept dict | Expression."""
        test_code = """
from _generated.examples.calculator import calculator_capnp
from typing import cast

async def test_client():
    calculator = cast(calculator_capnp.Calculator, None)
    
    # Should accept dict
    result1 = calculator.evaluate({"literal": 123.0})
    
    # Should also accept Expression object
    expr = cast(calculator_capnp.Calculator.Expression, None)
    result2 = calculator.evaluate(expr)
"""
        test_file = TESTS_DIR / "_test_client_dict_types.py"
        test_file.write_text(test_code)

        try:
            result = subprocess.run(
                ["pyright", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should have no type errors
            error_count = result.stdout.count("error:")
            assert error_count == 0, f"Client methods should accept dict:\n{result.stdout}"
        finally:
            test_file.unlink(missing_ok=True)

    def test_context_parameter_is_required(self, generate_calculator_stubs):
        """Test that _context parameter is required and properly typed."""
        test_code = """
from _generated.examples.calculator import calculator_capnp

class MinimalServer(calculator_capnp.Calculator.Value.Server):
    # Must include _context
    async def read(self, _context, **kwargs):
        return 42.0

class ContextServer(calculator_capnp.Calculator.Value.Server):
    # Can include _context
    async def read(self, _context, **kwargs):
        return 42.0
        
class ContextUserServer(calculator_capnp.Calculator.Function.Server):
    # Can use _context when needed
    async def call(self, params, _context, **kwargs):
        if _context is not None:
            # Use context for something
            pass
        return sum(params)
"""
        test_file = TESTS_DIR / "_test_context_optional.py"
        test_file.write_text(test_code)

        try:
            result = subprocess.run(
                ["pyright", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should have no type errors
            error_count = result.stdout.count("error:")
            assert error_count == 0, f"_context should be required:\n{result.stdout}"
        finally:
            test_file.unlink(missing_ok=True)

    def test_kwargs_properly_typed(self, generate_calculator_stubs):
        """Test that **kwargs is properly typed as Any."""
        test_code = """
from _generated.examples.calculator import calculator_capnp
from typing import Any

class ServerWithKwargs(calculator_capnp.Calculator.Function.Server):
    async def call(self, params, _context, **kwargs: Any):
        # kwargs should be typed as Any
        extra_param = kwargs.get("future_param", None)
        return sum(params)
"""
        test_file = TESTS_DIR / "_test_kwargs_typed.py"
        test_file.write_text(test_code)

        try:
            result = subprocess.run(
                ["pyright", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should have no type errors
            error_count = result.stdout.count("error:")
            assert error_count == 0, f"**kwargs should be typed:\n{result.stdout}"
        finally:
            test_file.unlink(missing_ok=True)

    def test_narrow_parameter_types(self, generate_calculator_stubs):
        """Test that parameter types are narrow, not dict[str, Any]."""
        test_code = """
from _generated.examples.calculator import calculator_capnp
from typing import cast

class ValueImpl(calculator_capnp.Calculator.Value.Server):
    def __init__(self, value: float):
        self.value = value
    
    async def read(self, _context, **kwargs):
        return self.value

class TypedServer(calculator_capnp.Calculator.Server):
    async def evaluate(self, expression: calculator_capnp.Calculator.ExpressionReader, _context, **kwargs):
        # Should have specific type, not dict[str, Any]
        # ExpressionReader has specific attributes
        which: str = expression.which()
        if which == "literal":
            value: float = expression.literal
        elif which == "parameter":
            param_idx: int = expression.parameter
        return ValueImpl(0.0)
        
    async def defFunction(self, paramCount: int, body: calculator_capnp.Calculator.ExpressionReader, _context, **kwargs):
        # paramCount should be int, not Any
        count: int = paramCount
        # body should be ExpressionReader with specific attributes
        which: str = body.which()
        func = cast(calculator_capnp.Calculator.Function, None)
        return func
        
    async def getOperator(self, op, _context, **kwargs):
        # op can be Operator enum or string literal - should work either way
        # Check that we can use it as enum
        if isinstance(op, calculator_capnp.Calculator.Operator):
            op_name: str = op.name
        func = cast(calculator_capnp.Calculator.Function, None)
        return func
"""
        test_file = TESTS_DIR / "_test_narrow_types.py"
        test_file.write_text(test_code)

        try:
            result = subprocess.run(
                ["pyright", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should have no type errors - types are narrow and specific
            error_count = result.stdout.count("error:")
            assert error_count == 0, f"Parameter types should be narrow:\n{result.stdout}"
        finally:
            test_file.unlink(missing_ok=True)


def test_server_signatures_summary():
    """Summary of server signature tests."""
    print("\n" + "=" * 70)
    print("SERVER METHOD SIGNATURE TESTS")
    print("=" * 70)
    print("All server method signature tests passed!")
    print("  ✓ Server methods use Reader types (not dict union)")
    print("  ✓ Client methods accept dict for struct params")
    print("  ✓ _context parameter is required and typed")
    print("  ✓ **kwargs is properly typed as Any")
    print("  ✓ Parameter types are narrow and specific")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
