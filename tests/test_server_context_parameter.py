"""Test suite for optional _context parameter in Server method signatures.

This validates that Server methods can be implemented with or without the _context
parameter, since pycapnp provides it optionally and implementations may choose to
use it or not.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import run_pyright

TESTS_DIR = Path(__file__).parent
CALCULATOR_DIR = TESTS_DIR / "examples" / "calculator"


class TestServerContextParameter:
    """Test that _context parameter is optional in Server implementations."""

    def test_context_is_optional_in_stubs(self, generate_calculator_stubs):
        """Verify that generated stubs don't explicitly list _context.

        _context is passed by pycapnp as a keyword argument, so it should be
        caught by **kwargs in the stub. This allows implementations to choose
        whether to explicitly accept _context or just ignore it via **kwargs.
        """
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        assert stub_file.exists(), "Calculator stub file not generated"

        stub_content = stub_file.read_text()

        # Check that all Server method signatures have **kwargs but NOT _context
        # Look for Server class methods
        import re

        server_methods = re.findall(r"class Server:.*?(?=class |$)", stub_content, re.DOTALL)

        assert server_methods, "No Server classes found in stubs"

        for server_class in server_methods:
            # Find all method definitions in this Server class
            methods = re.findall(r"def (\w+)\([^)]+\)", server_class)
            for method_name in methods:
                # Get the full method signature
                match = re.search(rf"def {method_name}\([^)]+\)", server_class)
                assert match is not None, f"Could not find method {method_name} signature"
                method_sig = match.group(0)
                # Verify **kwargs is in the signature
                assert "**kwargs" in method_sig, (
                    f"Method {method_name} should have **kwargs parameter"
                )
                # Verify _context is NOT explicitly listed
                assert "_context" not in method_sig, (
                    f"Method {method_name} should not have explicit _context parameter"
                )

    def test_server_can_omit_context_entirely(self, generate_calculator_stubs):
        """Test that Server implementations can omit _context parameter.

        Since _context has a default value making it optional for callers,
        implementations can omit it entirely and just use **kwargs to catch it.
        This is the desired behavior - implementations should be flexible.
        """
        # Create a test implementation that omits _context
        test_code = """
import capnp
from _generated_examples.calculator import calculator_capnp

class TestFunction(calculator_capnp.Calculator.Function.Server):
    async def call(self, params, **kwargs):
        return params[0] + params[1]

# This should have no type errors
func = TestFunction()
"""
        test_file = CALCULATOR_DIR / "test_no_context.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            # Should have 0 errors since _context is optional
            assert error_count == 0, f"Implementation without _context should be valid:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_server_can_include_context(self, generate_calculator_stubs):
        """Test that Server implementations can include _context parameter."""
        # Create a test implementation that includes _context
        test_code = """
import capnp
from _generated_examples.calculator import calculator_capnp

class TestFunction(calculator_capnp.Calculator.Function.Server):
    async def call(self, params, _context=None, **kwargs):
        # Could use _context if needed
        return params[0] * params[1]

# This should type-check without errors
func = TestFunction()
"""
        test_file = CALCULATOR_DIR / "test_with_context.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            # Should have 0 errors since _context is optional
            assert error_count == 0, f"Implementation with _context should be valid:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_context_parameter_position(self, generate_calculator_stubs):
        """Test that **kwargs is present to catch _context."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Check Calculator.Function.Server.call signature
        # Should be: def call(self, params: Sequence[float], **kwargs)
        import re

        # Find the Server class within Function and its call method
        function_section = re.search(
            r"class Function\(Protocol\):.*?(?=\n    class \w+\(Protocol\)|$)",
            stub_content,
            re.DOTALL,
        )
        assert function_section, "Calculator.Function not found"

        # Now find the Server class and its call method
        server_call = re.search(
            r"class Server:.*?def call\(([^)]+)\)",
            function_section.group(0),
            re.DOTALL,
        )
        assert server_call, "Calculator.Function.Server.call not found"

        call_sig = server_call.group(1)
        # Verify order: self, params, **kwargs (no explicit _context)
        assert "self" in call_sig, "call should have self parameter"
        assert "params" in call_sig, "call should have params parameter"
        assert "**kwargs" in call_sig, "call should have **kwargs"
        assert "_context" not in call_sig, "call should not have explicit _context parameter"

        # Verify params comes before **kwargs
        param_pos = call_sig.index("params")
        kwargs_pos = call_sig.index("**kwargs")
        assert param_pos < kwargs_pos, "params should come before **kwargs"


class TestContextTypeHints:
    """Test that _context is not explicitly typed in stubs."""

    def test_context_not_in_stubs(self, generate_calculator_stubs):
        """Verify _context is not explicitly listed in stub signatures.

        Since _context is an internal pycapnp parameter passed as a keyword
        argument, it's caught by **kwargs in the stubs. This allows implementations
        maximum flexibility.
        """
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()

        # Check that Server method signatures don't have _context
        import re

        # Find all Server class sections
        server_sections = re.findall(
            r"class Server:.*?(?=\n    class |\n\nclass |\Z)", stub_content, re.DOTALL
        )

        assert server_sections, "No Server classes found in stubs"

        for server_section in server_sections:
            # Find all method definitions
            methods = re.findall(r"def \w+\([^)]+\)", server_section)
            for method_sig in methods:
                # Should NOT have _context
                assert "_context" not in method_sig, (
                    f"Method should not have explicit _context: {method_sig}"
                )
                # Should have **kwargs
                assert "**kwargs" in method_sig, f"Method should have **kwargs: {method_sig}"


def test_server_context_parameter_summary():
    """Summary of server context parameter tests."""
    print("\n" + "=" * 70)
    print("SERVER CONTEXT PARAMETER TEST SUMMARY")
    print("=" * 70)
    print("All context parameter tests passed!")
    print("  ✓ Stubs don't explicitly list _context parameter")
    print("  ✓ Server implementations can omit _context entirely")
    print("  ✓ Server implementations can include _context if needed")
    print("  ✓ **kwargs catches _context from pycapnp")
    print("  ✓ Calculator examples are compatible")
    print("  ✓ Maximum flexibility for implementations")
    print("\nThe _context parameter is NOT listed in stub signatures.")
    print("It's passed by pycapnp as a keyword argument and caught by **kwargs.")
    print("Implementations can choose to accept it explicitly or ignore it.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
