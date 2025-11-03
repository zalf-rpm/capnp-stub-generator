"""Tests for send() method return type resolution."""
from __future__ import annotations
import subprocess
from pathlib import Path
import pytest

TESTS_DIR = Path(__file__).parent


def test_send_returns_proper_result_type(generate_calculator_stubs):
    """Test that request.send() returns properly typed result."""
    code = """
from _generated_examples.calculator import calculator_capnp

def test(calc: calculator_capnp.Calculator):
    request = calc.evaluate_request()
    result = request.send()
    reveal_type(result)
    reveal_type(result.value)
"""
    tmp = TESTS_DIR / "_tmp_send_test.py"
    tmp.write_text(code)
    try:
        result = subprocess.run(["pyright", str(tmp)], capture_output=True, text=True)
        # Result should be EvaluateResult
        assert "EvaluateResult" in result.stdout, result.stdout
        # result.value should be Value (the interface)
        assert '"Value"' in result.stdout or 'Value' in result.stdout, result.stdout
    finally:
        tmp.unlink(missing_ok=True)


def test_nested_interface_send_returns_proper_type(generate_calculator_stubs):
    """Test that nested interface request.send() returns properly scoped type."""
    code = """
from _generated_examples.calculator import calculator_capnp

def test(value: calculator_capnp.Calculator.Value):
    request = value.read_request()
    result = request.send()
    reveal_type(result)
    reveal_type(result.value)
"""
    tmp = TESTS_DIR / "_tmp_nested_send_test.py"
    tmp.write_text(code)
    try:
        result = subprocess.run(["pyright", str(tmp)], capture_output=True, text=True)
        # Result should be ReadResult
        assert "ReadResult" in result.stdout, result.stdout
        # result.value should be float
        assert "float" in result.stdout, result.stdout
    finally:
        tmp.unlink(missing_ok=True)


def test_send_result_is_awaitable(generate_calculator_stubs):
    """Test that send() result can be awaited."""
    code = """
from _generated_examples.calculator import calculator_capnp

async def test(calc: calculator_capnp.Calculator):
    request = calc.evaluate_request()
    result = await request.send()
    reveal_type(result)
"""
    tmp = TESTS_DIR / "_tmp_await_send_test.py"
    tmp.write_text(code)
    try:
        result = subprocess.run(["pyright", str(tmp)], capture_output=True, text=True)
        # Should show EvaluateResult type
        assert "EvaluateResult" in result.stdout, result.stdout
        # Should have no errors about awaiting
        assert "error" not in result.stdout.lower() or "0 errors" in result.stdout, result.stdout
    finally:
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
