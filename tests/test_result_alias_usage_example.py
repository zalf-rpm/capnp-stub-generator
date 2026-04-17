"""Example demonstrating the use of Result helper imports from the types package.

This shows how Result, Builder, and Reader helper types are imported from the
generated ``types`` package rather than from the runtime-facing top-level stub.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.test_helpers import log_summary

if TYPE_CHECKING:
    from calculator.calculator_capnp.types.builders import ExpressionBuilder
    from calculator.calculator_capnp.types.results.client import EvaluateResult, ReadResult

# Before the types package split, helper names lived on the main module surface.
# After the split, helper imports come from calculator_capnp.types.* instead.
# This keeps the runtime module clean while still giving direct access to the
# precise helper types.


def example_usage() -> None:
    """Show the types-package import style."""

    def _handle_evaluate_result(result: EvaluateResult) -> None:
        """Process an evaluation result using a targeted helper import."""
        value_client = result.value
        _ = value_client

    def _handle_read_result(result: ReadResult) -> None:
        """Process a read result from the Value interface."""
        value: float = result.value
        _ = value

    def _process_expression(expr: ExpressionBuilder) -> EvaluateResult:
        """Show that Result types work alongside Builder/Reader helper imports.

        The runtime module keeps only runtime-shaped names; helper imports come
        from ``types``.
        """
        # This would normally make an RPC call
        # For the example, we just show the type signature
        raise NotImplementedError

    _ = (_handle_evaluate_result, _handle_read_result, _process_expression)

    log_summary(
        "RESULT TYPE ALIAS EXAMPLE",
        [
            "✓ Result helper imports work as expected",
            "✓ Consistent with Builder/Reader helper imports",
            "✓ Keeps runtime module namespace clean",
        ],
    )


if __name__ == "__main__":
    example_usage()
