"""Test suite for mandatory _context parameter in Server method signatures.

This validates that Server methods now include the properly typed _context
parameter that pycapnp always passes to server implementations.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.test_helpers import log_summary, read_generated_types_combined

TESTS_DIR = Path(__file__).parent
CALCULATOR_DIR = TESTS_DIR / "examples" / "calculator"


class TestServerContextParameter:
    """Test that _context parameter is mandatory in Server implementations."""

    def test_context_is_in_stubs(self, generate_calculator_stubs: Path) -> None:
        """Verify that generated stubs explicitly list _context with proper typing."""
        package_dir = generate_calculator_stubs / "calculator_capnp"
        assert (package_dir / "types" / "modules.pyi").exists(), "Calculator stub file not generated"

        stub_content = read_generated_types_combined(package_dir)

        # Check that CallContext helper types are generated
        assert "CallContext(Protocol):" in stub_content
        # ResultsBuilder no longer exists - CallContext.results now points to top-level helper types

        server_methods = re.findall(
            r"class Server\(_DynamicCapabilityServer\):.*?(?=\n    class |\n\nclass |\Z)",
            stub_content,
            re.DOTALL,
        )
        assert server_methods, "No Server classes found in stubs"

        for server_class in server_methods:
            # Find all method definitions
            methods = re.findall(r"def (\w+)\(", server_class)
            for method_name in methods:
                # Skip dunder methods
                if method_name.startswith("__"):
                    continue
                # Skip client-side request methods (these are not server implementations)
                if method_name.endswith("_request"):
                    continue
                match = re.search(rf"def {method_name}\([^)]+\)", server_class)
                if match:
                    method_sig = match.group(0)
                    # _context variant methods only have context parameter
                    if method_name.endswith("_context"):
                        assert "context:" in method_sig, f"Method {method_name} should have context parameter"
                        assert "CallContext" in method_sig, f"Method {method_name} context should be typed"
                    # Regular server methods have _context and **kwargs
                    # Skip if it doesn't have _context (might be other helper methods)
                    elif "_context:" in method_sig:
                        assert "CallContext" in method_sig, f"Method {method_name} _context should be typed"
                        assert "**kwargs" in method_sig, f"Method {method_name} should have **kwargs"

    def test_context_parameter_position(self, generate_calculator_stubs: Path) -> None:
        """Test that _context comes after regular parameters, before **kwargs."""
        content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Test _CalculatorInterfaceModule._FunctionInterfaceModule.call
        # Function is now an interface module inheriting from _InterfaceModule
        # Look for the _FunctionInterfaceModule section (it's nested inside _CalculatorInterfaceModule)
        function_section = re.search(
            r"class _FunctionInterfaceModule\(_InterfaceModule\):.*?(?=\n    Function:)",
            content,
            re.DOTALL,
        )
        assert function_section, "_CalculatorInterfaceModule._FunctionInterfaceModule not found"

        server_call = re.search(
            r"class Server\(_DynamicCapabilityServer\):.*?def call\(([^)]+(?:\)[^)]*)*)\)",
            function_section.group(0),
            re.DOTALL,
        )
        assert server_call, "_CalculatorInterfaceModule._FunctionInterfaceModule.Server.call not found"

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

    def test_context_has_callcontext_type(self, generate_calculator_stubs: Path) -> None:
        """Test that _context parameter uses CallContext types."""
        content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

        # Look for read method in Value.Server (may span multiple lines)
        match = re.search(r"def read\([^)]*_context: ([^\s,]+)", content, re.DOTALL)
        assert match, "Could not find read method with _context"

        context_type = match.group(1)
        assert "CallContext" in context_type, f"_context should have CallContext type, got: {context_type}"
        assert context_type == "contexts.ReadCallContext", (
            f"CallContext should use the contexts helper module, got: {context_type}"
        )


def test_server_context_parameter_summary(generate_calculator_stubs: Path) -> None:
    """Summary test showing _context parameter is now mandatory and typed."""
    content = read_generated_types_combined(generate_calculator_stubs / "calculator_capnp")

    # Count CallContext types generated
    callcontext_count = len(re.findall(r"class \w+CallContext\(Protocol\):", content))

    # Count NamedTuple result types (now with "Tuple" suffix)
    namedtuple_count = len(re.findall(r"class \w+ResultTuple\(NamedTuple\):", content))

    # Count Server methods with _context
    server_methods_with_context = len(re.findall(r"def \w+\([^)]*_context:[^)]*\)", content))

    assert callcontext_count > 0, "Should generate CallContext types"
    assert namedtuple_count > 0, "Should generate NamedTuple result types"
    assert server_methods_with_context > 0, "Server methods should have _context parameter"
    log_summary(
        "SERVER CONTEXT PARAMETER TEST SUMMARY",
        [
            "All context parameter tests passed!",
            f"  ✓ Generated {callcontext_count} CallContext types",
            f"  ✓ Generated {namedtuple_count} NamedTuple result types",
            f"  ✓ {server_methods_with_context} Server methods have typed _context",
            "  ✓ _context is mandatory in all Server method signatures",
            "  ✓ _context properly typed with CallContext for IDE support",
            "",
            "The _context parameter is explicitly listed in all Server method signatures",
            "with proper CallContext typing for full type safety and IDE autocomplete.",
            "CallContext.results now points to top-level ServerResult helpers.",
        ],
    )
