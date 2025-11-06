"""Tests for ExpressionBuilder.init("call") return type correctness."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


def test_expression_init_call_returns_callbuilder(generate_calculator_stubs):
    code = """
from _generated.examples.calculator import calculator_capnp

expr_builder: calculator_capnp.Calculator.ExpressionBuilder = calculator_capnp.Calculator.Expression.new_message()
call_builder = expr_builder.init("call")
reveal_type(call_builder)
"""
    tmp = TESTS_DIR / "_tmp_expr_init.py"
    tmp.write_text(code)
    try:
        result = subprocess.run(["pyright", str(tmp)], capture_output=True, text=True)
        # Expect revealed type to include CallBuilder
        assert "CallBuilder" in result.stdout, result.stdout
    finally:
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
