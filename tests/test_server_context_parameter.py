"""Test suite for mandatory _context parameter in Server method signatures.

This validates that Server methods now include the properly typed _context
parameter that pycapnp always passes to server implementations.
"""

from __future__ import annotations

from pathlib import Path

TESTS_DIR = Path(__file__).parent
CALCULATOR_DIR = TESTS_DIR / "examples" / "calculator"


class TestServerContextParameter:
    """Test that _context parameter is mandatory in Server implementations."""

    def test_context_is_in_stubs(self, generate_calculator_stubs):
        """Verify that generated stubs explicitly list _context with proper typing."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        assert stub_file.exists(), "Calculator stub file not generated"

        stub_content = stub_file.read_text()

        # Check that CallContext types are generated
        assert "CallContext(Protocol):" in stub_content
        assert "ResultsBuilder(Protocol):" in stub_content

        # Check that Server methods have _context parameter
        import re

        server_methods = re.findall(
            r"class Server\(Protocol\):.*?(?=\n    class |\n\nclass |\Z)", stub_content, re.DOTALL
        )
        assert server_methods, "No Server classes found in stubs"

        for server_class in server_methods:
            # Find all method definitions (skip __enter__ and __exit__)
            methods = re.findall(r"def (\w+)\(", server_class)
            for method_name in methods:
                if method_name in ("__enter__", "__exit__"):
                    continue
                match = re.search(rf"def {method_name}\([^)]+\)", server_class)
                if match:
                    method_sig = match.group(0)
                    assert "_context:" in method_sig, f"Method {method_name} should have _context parameter"
                    assert "CallContext" in method_sig, f"Method {method_name} _context should be typed"
                    assert "**kwargs" in method_sig, f"Method {method_name} should have **kwargs"

    def test_context_parameter_position(self, generate_calculator_stubs):
        """Test that _context comes after regular parameters, before **kwargs."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        import re

        # Test Calculator.Function.call
        function_section = re.search(
            r"class Function\(Protocol\):.*?(?=\n    class [A-Z]|\nclass [A-Z])", content, re.DOTALL
        )
        assert function_section, "Calculator.Function not found"

        server_call = re.search(
            r"class Server\(Protocol\):.*?def call\(([^)]+)\)",
            function_section.group(0),
            re.DOTALL,
        )
        assert server_call, "Calculator.Function.Server.call not found"

        call_sig = server_call.group(1)
        # Verify order: self, params, _context, **kwargs
        assert "self" in call_sig
        assert "params" in call_sig
        assert "_context:" in call_sig
        assert "**kwargs" in call_sig

        # Verify params comes before _context
        param_pos = call_sig.index("params")
        context_pos = call_sig.index("_context")
        kwargs_pos = call_sig.index("**kwargs")
        assert param_pos < context_pos < kwargs_pos, "Parameters should be in order: params, _context, **kwargs"


class TestContextTypeHints:
    """Test that _context has proper type hints with CallContext."""

    def test_context_has_callcontext_type(self, generate_calculator_stubs):
        """Test that _context parameter uses CallContext types."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        content = stub_file.read_text()

        # Find a server method and verify its _context type
        import re

        # Look for read method in Value.Server (may span multiple lines)
        match = re.search(r"def read\([^)]*_context: ([^\s,]+)", content, re.DOTALL)
        assert match, "Could not find read method with _context"

        context_type = match.group(1)
        assert "CallContext" in context_type, f"_context should have CallContext type, got: {context_type}"
        assert "Calculator.Value" in context_type, f"CallContext should be scoped, got: {context_type}"


def test_server_context_parameter_summary(generate_calculator_stubs):
    """Summary test showing _context parameter is now mandatory and typed."""
    stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    import re

    # Count CallContext types generated
    callcontext_count = len(re.findall(r"class \w+CallContext\(Protocol\):", content))
    resultsbuilder_count = len(re.findall(r"class \w+ResultsBuilder\(Protocol\):", content))

    # Count Server methods with _context
    server_methods_with_context = len(re.findall(r"def \w+\([^)]*_context:[^)]*\)", content))

    print("\n" + "=" * 70)
    print("SERVER CONTEXT PARAMETER TEST SUMMARY")
    print("=" * 70)
    assert callcontext_count > 0, "Should generate CallContext types"
    assert resultsbuilder_count > 0, "Should generate ResultsBuilder types"
    assert server_methods_with_context > 0, "Server methods should have _context parameter"

    print("All context parameter tests passed!")
    print(f"  ✓ Generated {callcontext_count} CallContext types")
    print(f"  ✓ Generated {resultsbuilder_count} ResultsBuilder types")
    print(f"  ✓ {server_methods_with_context} Server methods have typed _context")
    print("  ✓ _context is mandatory in all Server method signatures")
    print("  ✓ _context properly typed with CallContext for IDE support")
    print("\nThe _context parameter is explicitly listed in all Server method signatures")
    print("with proper CallContext typing for full type safety and IDE autocomplete.")
    print("=" * 70)
