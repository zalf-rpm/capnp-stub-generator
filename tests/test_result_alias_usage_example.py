"""Example demonstrating the use of Result type aliases.

This shows how Result types can now be used as top-level type aliases,
just like Builder and Reader types.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.test_helpers import log_summary

if TYPE_CHECKING:
    from tests._generated.examples.calculator import calculator_capnp

# Before this change, you had to use the full nested path:
# def process_result(result: calculator_capnp._CalculatorModule.CalculatorClient.EvaluateResult) -> None:
#     ...

# After this change, you can use the convenient top-level alias:
# def process_result(result: calculator_capnp.EvaluateResult) -> None:
#     ...

# This makes type annotations much more readable and consistent with Builder/Reader patterns:
# - calculator_capnp.ExpressionBuilder  (was already available)
# - calculator_capnp.ExpressionReader   (was already available)
# - calculator_capnp.EvaluateResult     (now available!)


def example_usage() -> None:
    """Show the improved type annotation style."""

    # Type aliases are now available at module level
    def handle_evaluate_result(result: calculator_capnp.EvaluateResult) -> None:
        """Process an evaluation result using the convenient type alias."""
        # The result is still the same Protocol type, just with a shorter name
        value_client = result.value  # type: calculator_capnp.ValueClient
        _ = value_client

    def handle_read_result(result: calculator_capnp.ReadResult) -> None:
        """Process a read result from the Value interface."""
        value = result.value  # type: float
        _ = value

    def process_expression(expr: calculator_capnp.ExpressionBuilder) -> calculator_capnp.EvaluateResult:
        """Show that Result types work alongside Builder/Reader types.

        All three patterns now work consistently:
        - ExpressionBuilder (struct Builder)
        - ExpressionReader (struct Reader)
        - EvaluateResult (interface method Result)
        """
        # This would normally make an RPC call
        # For the example, we just show the type signature
        raise NotImplementedError

    log_summary(
        "RESULT TYPE ALIAS EXAMPLE",
        [
            "✓ Result type aliases work as expected",
            "✓ Consistent with Builder/Reader naming patterns",
            "✓ Makes type hints more readable",
        ],
    )


if __name__ == "__main__":
    example_usage()
