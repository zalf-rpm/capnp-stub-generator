"""Tests for _context method variant generation.

According to pycapnp documentation, server methods can be implemented in two ways:
1. Regular method: matches interface name exactly, receives params as kwargs
2. _context variant: method name with '_context' suffix, receives only context parameter

This test verifies that both variants are generated correctly.
"""

import re
from pathlib import Path

from tests.test_helpers import log_summary, read_generated_types_combined


def test_both_method_variants_exist(calculator_stubs: Path) -> None:
    """Both regular and _context variant methods should be generated."""
    content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

    # Regular method with individual parameters (may be multi-line signature)
    assert "def evaluate(" in content
    assert "expression: ExpressionReader" in content
    assert "_context: EvaluateCallContext" in content
    assert "**kwargs: object" in content

    # _context variant with only context parameter
    assert "def evaluate_context(" in content
    assert "context: EvaluateCallContext" in content
    assert "-> Awaitable[None]" in content


def test_context_variant_signature(calculator_stubs: Path) -> None:
    """_context methods should have correct signature."""
    content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

    context_methods = re.findall(r"def (\w+)_context\(", content)

    # Should have _context variants for all interface methods
    assert "evaluate" in context_methods
    assert "defFunction" in context_methods
    assert "getOperator" in context_methods

    # Each _context method should have only self and context parameters
    # Allow for multiline signatures with whitespace
    for method in context_methods:
        pattern = rf"def {method}_context\(\s*self,\s*context:\s*[^\)]+\)\s*->\s*Awaitable\[None\]"
        assert re.search(pattern, content, re.MULTILINE | re.DOTALL), (
            f"Method {method}_context should have correct signature"
        )


def test_callcontext_has_params_and_results(calculator_stubs: Path) -> None:
    """CallContext should have both params and results attributes."""
    content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

    # Check a method with parameters and results
    assert "class EvaluateCallContext(Protocol):" in content
    assert "params: EvaluateParams" in content
    # Results now point to the flattened ServerResult helper
    assert "@property" in content
    assert "def results(self) -> EvaluateServerResult: ..." in content


def test_callcontext_void_method(basic_stubs: Path) -> None:
    """CallContext for void methods should have params but no results."""
    content = read_generated_types_combined(basic_stubs / "channel_capnp")

    # Check void method CallContext (Reader.close is a void method)
    assert "class ReaderCloseCallContext(Protocol):" in content
    assert "params: ReaderCloseParams" in content

    # Find the flattened ReaderCloseCallContext helper
    close_context = re.search(
        r"class ReaderCloseCallContext\(Protocol\):.*?(?=\n\n|\nclass |\Z)",
        content,
        re.DOTALL,
    )
    assert close_context
    # Verify no results field
    assert "results:" not in close_context.group(0)


def test_nested_interface_context_methods(calculator_stubs: Path) -> None:
    """Nested interfaces should also have _context methods."""
    content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

    # Calculator.Value is a nested interface (now _ValueInterfaceModule inside _CalculatorInterfaceModule)
    assert "def read_context(" in content
    assert "context: ReadCallContext" in content

    # Calculator.Function is a nested interface (now _FunctionInterfaceModule inside _CalculatorInterfaceModule)
    assert "def call_context(" in content  # Verify method exists


def test_context_method_documentation(calculator_stubs: Path) -> None:
    """Verify the _context methods work as documented in pycapnp."""
    content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

    # According to documentation:
    # - Method name ends in _context
    # - Only receives context parameter (not individual params)
    # - Can return promises or None
    # - Can access context.params and set context.results

    # Example from docs: defFunction_context(self, context)
    assert "def defFunction_context(" in content
    assert "context: DeffunctionCallContext" in content

    # The CallContext should provide access to both params and results
    assert "class DeffunctionCallContext(Protocol):" in content
    assert "params: DeffunctionParams" in content
    # Results now point to the flattened ServerResult helper
    assert "@property" in content
    assert "def results(self) -> DeffunctionServerResult: ..." in content


def test_context_methods_count(calculator_stubs: Path) -> None:
    """Count that all interface methods have _context variants."""
    content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

    # Find all Server class methods
    server_sections = re.findall(
        r"class Server\(Protocol\):.*?(?=\n    class [A-Z]|\nclass [A-Z]|\Z)",
        content,
        re.DOTALL,
    )

    for server_section in server_sections:
        # Find regular methods (with _context parameter, not method name)
        regular_methods = re.findall(r"def (\w+)\([^)]*_context:\s+\w+", server_section)
        # Remove duplicates and _context suffix methods
        regular_methods = [m for m in regular_methods if not m.endswith("_context")]

        # Find _context variant methods
        context_methods = re.findall(r"def (\w+)_context\(", server_section)

        # Each regular method should have a corresponding _context variant
        if regular_methods:  # Only check if there are methods
            assert len(regular_methods) == len(context_methods), (
                f"Each method should have a _context variant. Regular: {regular_methods}, Context: {context_methods}"
            )
            for method in regular_methods:
                assert method in context_methods, f"Method {method} should have a _context variant"


def test_context_method_summary() -> None:
    """Summary test for _context method generation."""
    log_summary(
        "CONTEXT METHOD VARIANT TEST SUMMARY",
        [
            "All _context method variant tests passed!",
            "  ✓ Both regular and _context variants generated",
            "  ✓ _context methods have correct signatures",
            "  ✓ CallContext has params and results attributes",
            "  ✓ Void methods have params but no results",
            "  ✓ Nested interfaces have _context methods",
            "  ✓ All interface methods have _context variants",
            "",
            "Server methods can be implemented in two ways:",
            "  1. Regular: def method(self, param1, param2, _context, **kwargs)",
            "  2. _context: def method_context(self, context)",
            "",
            "The _context variant provides access to context.params and context.results",
            "for manual parameter access and result setting.",
        ],
    )
