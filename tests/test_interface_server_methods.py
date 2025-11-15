"""Tests for interface Server class method signatures."""


def test_server_class_exists_for_interfaces(calculator_stub_lines):
    """Server classes should be generated for all interfaces."""
    lines = calculator_stub_lines

    # Check that interface modules exist (now inherit from _InterfaceModule)
    assert any("class _ValueModule(_InterfaceModule):" in line for line in lines)
    assert any("class _FunctionModule(_InterfaceModule):" in line for line in lines)
    assert any("class _CalculatorModule(_InterfaceModule):" in line for line in lines)

    # Check that Server classes exist (now inherit from _DynamicCapabilityServer)
    assert any("class Server(_DynamicCapabilityServer):" in line for line in lines)

    # Count Server classes - should be 3 (Value, Function, Calculator)
    server_count = sum(1 for line in lines if line.strip() == "class Server(_DynamicCapabilityServer):")
    assert server_count == 3, f"Expected 3 Server classes, found {server_count}"


def test_server_methods_have_signatures(calculator_stub_lines):
    """Server class methods should have proper type signatures."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # Function.Server should have call method
    assert "class Server(_DynamicCapabilityServer):" in content
    assert "def call(self, params: Sequence[float], _context:" in content
    assert "Awaitable[" in content  # Server.call returns Awaitable

    # Value.Server should have read method with _context parameter and returns NamedTuple with "Tuple" suffix
    # CallContext is now inside Server, so reference is _CalculatorModule._ValueModule.Server.ReadCallContext
    assert "def read(" in content
    assert "_context: _CalculatorModule._ValueModule.Server.ReadCallContext" in content
    assert "Awaitable[float | _CalculatorModule._ValueModule.Server.ReadResultTuple | None]" in content

    # Calculator.Server should have evaluate method with Reader type and return NamedTuple with "Tuple" suffix
    assert "def evaluate(" in content
    assert "expression: _CalculatorModule._ExpressionModule.Reader" in content
    assert (
        "Awaitable[_CalculatorModule._ValueModule.Server | _CalculatorModule.Server.EvaluateResultTuple | None]"
        in content
    )


def test_server_methods_accept_context(calculator_stub_lines):
    """Server methods should accept _context parameter and **kwargs."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # All server methods should have **kwargs
    assert "**kwargs" in content

    # Find all Server classes and verify their methods
    import re

    server_sections = re.findall(
        r"class Server\(_DynamicCapabilityServer\):.*?(?=\n    class |\n\nclass |\Z)", content, re.DOTALL
    )

    assert len(server_sections) > 0, "Should find at least one Server class"

    for server_section in server_sections:
        # Find all method definitions in this Server class
        methods = re.findall(r"def \w+\([^)]*(?:\).*?)?(?=\n|$)", server_section, re.DOTALL)
        for method in methods:
            # Skip dunder methods
            if "def __" in method:
                continue
            # Skip _context variant methods (they don't have **kwargs)
            if "_context(" in method:
                continue
            # Skip methods that don't have _context parameter (these are request/client methods)
            if "_context:" not in method:
                continue
            # Each regular RPC method should have **kwargs
            assert "**kwargs" in method, f"Server method should have **kwargs: {method}"
            # _context should have a CallContext type
            assert "CallContext" in method, f"Server method _context should be typed with CallContext: {method}"


def test_server_methods_return_interface_or_implementation(calculator_stub_lines):
    """Server methods returning interfaces return Server types."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # Server methods returning interfaces return Interface.Server types
    # (not Interface | Interface.Server because servers work with Server implementations)
    # With nested Protocol naming, these are referenced via the full path
    assert "_CalculatorModule._ValueModule.Server" in content
    assert "_CalculatorModule._FunctionModule.Server" in content


def test_server_method_parameters_match_protocol(calculator_stub_lines):
    """Server method parameters should match the Protocol interface plus _context."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # Find Function Protocol's call method (now optional parameters)
    protocol_call_found = False
    for i, line in enumerate(lines):
        if "def call(self, params: Sequence[float] | None = None)" in line:
            # Make sure it's not in a Server class
            context = "".join(lines[max(0, i - 10) : i])
            if "class Server:" not in context:
                protocol_call_found = True
                break

    assert protocol_call_found, "Could not find Protocol call method"

    # Find Function.Server's call method - should have params (required), _context, and **kwargs
    # Server parameters remain required for type safety
    # CallContext is now inside Server, so reference is _CalculatorModule._FunctionModule.Server.CallCallContext
    server_call_found = (
        "def call(self, params: Sequence[float], _context: _CalculatorModule._FunctionModule.Server.CallCallContext, **kwargs: Any)"
        in content
    )

    assert server_call_found, "Server call method should have same params as Protocol plus _context and **kwargs"
