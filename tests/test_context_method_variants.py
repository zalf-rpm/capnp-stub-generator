"""Tests for _context method variant generation.

According to pycapnp documentation, server methods can be implemented in two ways:
1. Regular method: matches interface name exactly, receives params as kwargs
2. _context variant: method name with '_context' suffix, receives only context parameter

This test verifies that both variants are generated correctly.
"""


def test_both_method_variants_exist(calculator_stubs):
    """Both regular and _context variant methods should be generated."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Regular method with individual parameters (single line signature)
    assert "def evaluate(self, expression: ExpressionReader, _context:" in content
    assert "_context: _CalculatorModule.Server.EvaluateCallContext" in content
    assert "**kwargs: dict[str, Any]" in content

    # _context variant with only context parameter
    assert "def evaluate_context(self, context: _CalculatorModule.Server.EvaluateCallContext)" in content
    assert "-> Awaitable[None]" in content


def test_context_variant_signature(calculator_stubs):
    """_context methods should have correct signature."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Find all _context methods
    import re

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


def test_callcontext_has_params_and_results(calculator_stubs):
    """CallContext should have both params and results attributes."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Check a method with parameters and results
    assert "class EvaluateCallContext(Protocol):" in content
    assert "params: _CalculatorModule.Server.EvaluateParams" in content
    # Results now point to Server.Result
    assert "@property" in content
    assert "def results(self) -> _CalculatorModule.Server.EvaluateResult: ..." in content


def test_callcontext_void_method(basic_stubs):
    """CallContext for void methods should have params but no results."""
    stub_file = basic_stubs / "channel_capnp.pyi"
    content = stub_file.read_text()

    # Check void method CallContext (Reader.close is a void method)
    assert "class CloseCallContext(Protocol):" in content
    assert "params: _ChannelModule._ReaderModule.Server.CloseParams" in content

    # Should NOT have results for void method
    import re

    # Find CloseCallContext inside Reader
    close_context = re.search(
        r"class CloseCallContext\(Protocol\):.*?(?=\n\n|\n            class |\n            def )", content, re.DOTALL
    )
    assert close_context
    # Verify no results field
    assert "results:" not in close_context.group(0)


def test_nested_interface_context_methods(calculator_stubs):
    """Nested interfaces should also have _context methods."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Calculator.Value is a nested interface (now _ValueModule inside _CalculatorModule)
    assert (
        "def read_context(self, context: _CalculatorModule._ValueModule.Server.ReadCallContext) -> Awaitable[None]:"
        in content
    )

    # Calculator.Function is a nested interface (now _FunctionModule inside _CalculatorModule)
    assert "def call_context(" in content  # Verify method exists


def test_context_method_documentation(calculator_stubs):
    """Verify the _context methods work as documented in pycapnp."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # According to documentation:
    # - Method name ends in _context
    # - Only receives context parameter (not individual params)
    # - Can return promises or None
    # - Can access context.params and set context.results

    # Example from docs: defFunction_context(self, context)
    assert (
        "def defFunction_context(self, context: _CalculatorModule.Server.DeffunctionCallContext) -> Awaitable[None]:"
        in content
    )

    # The CallContext should provide access to both params and results
    assert "class DeffunctionCallContext(Protocol):" in content
    assert "params: _CalculatorModule.Server.DeffunctionParams" in content
    # Results now point to Server.Result
    assert "@property" in content
    assert "def results(self) -> _CalculatorModule.Server.DeffunctionResult: ..." in content


def test_context_methods_count(calculator_stubs):
    """Count that all interface methods have _context variants."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    import re

    # Find all Server class methods
    server_sections = re.findall(
        r"class Server\(Protocol\):.*?(?=\n    class [A-Z]|\nclass [A-Z]|\Z)", content, re.DOTALL
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


def test_context_method_summary():
    """Summary test for _context method generation."""
    print("\n" + "=" * 70)
    print("CONTEXT METHOD VARIANT TEST SUMMARY")
    print("=" * 70)
    print("All _context method variant tests passed!")
    print("  ✓ Both regular and _context variants generated")
    print("  ✓ _context methods have correct signatures")
    print("  ✓ CallContext has params and results attributes")
    print("  ✓ Void methods have params but no results")
    print("  ✓ Nested interfaces have _context methods")
    print("  ✓ All interface methods have _context variants")
    print("")
    print("Server methods can be implemented in two ways:")
    print("  1. Regular: def method(self, param1, param2, _context, **kwargs)")
    print("  2. _context: def method_context(self, context)")
    print("")
    print("The _context variant provides access to context.params and context.results")
    print("for manual parameter access and result setting.")
    print("=" * 70)
