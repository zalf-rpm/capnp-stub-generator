"""Tests for interface Server class method signatures."""

import re

EXPECTED_SERVER_CLASS_COUNT = 3


def test_server_class_exists_for_interfaces(calculator_stub_lines: list[str]) -> None:
    """Server classes should be generated for all interfaces."""
    lines = calculator_stub_lines

    # Check that interface modules exist (now inherit from _InterfaceModule)
    assert any("class _ValueInterfaceModule(_InterfaceModule):" in line for line in lines)
    assert any("class _FunctionInterfaceModule(_InterfaceModule):" in line for line in lines)
    assert any("class _CalculatorInterfaceModule(_InterfaceModule):" in line for line in lines)

    # Check that Server classes exist (now inherit from _DynamicCapabilityServer)
    assert any("class Server(_DynamicCapabilityServer):" in line for line in lines)

    # Count Server classes - should be 3 (Value, Function, Calculator)
    server_count = sum(1 for line in lines if line.strip() == "class Server(_DynamicCapabilityServer):")
    assert server_count == EXPECTED_SERVER_CLASS_COUNT, f"Expected 3 Server classes, found {server_count}"


def test_server_methods_have_signatures(calculator_stub_lines: list[str]) -> None:
    """Server class methods should have proper type signatures."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # Function.Server should have call method
    assert "class Server(_DynamicCapabilityServer):" in content
    # Note: method signatures may span multiple lines
    assert "def call(" in content
    assert "params: Float64ListReader" in content
    assert "Awaitable[" in content  # Server.call returns Awaitable

    # Value.Server should have read method with _context parameter
    assert "def read(" in content
    assert "_context: ReadCallContext" in content

    # Calculator.Server should have evaluate method with Reader type
    assert "def evaluate(" in content
    assert "expression: ExpressionReader" in content


def test_server_methods_accept_context(calculator_stub_lines: list[str]) -> None:
    """Server methods should accept _context parameter and **kwargs."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # All server methods should have **kwargs
    assert "**kwargs" in content

    server_sections = re.findall(
        r"class Server\(_DynamicCapabilityServer\):.*?(?=\n    class |\n\nclass |\Z)",
        content,
        re.DOTALL,
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


def test_server_methods_return_interface_or_implementation(calculator_stub_lines: list[str]) -> None:
    """Server methods returning interfaces return Server types."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # Server methods returning interfaces return Interface.Server types
    # (not Interface | Interface.Server because servers work with Server implementations)
    # With nested Protocol naming, these are referenced via the full path
    assert "_CalculatorInterfaceModule._ValueInterfaceModule.Server" in content
    assert "_CalculatorInterfaceModule._FunctionInterfaceModule.Server" in content


def test_server_method_parameters_match_protocol(calculator_stub_lines: list[str]) -> None:
    """Server method parameters should match the Protocol interface plus _context."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # Find Function Protocol's call method (now optional parameters)
    protocol_call_found = False
    for i, line in enumerate(lines):
        # Check for call method in FunctionClient (multi-line)
        if "def call(" in line and "FunctionClient" in "".join(lines[max(0, i - 20) : i]):
            protocol_call_found = True
            break

    assert protocol_call_found, "Could not find Protocol call method"

    # Find Function.Server's call method - should have params, _context, and **kwargs
    # Note: method signatures may span multiple lines
    assert "params: Float64ListReader" in content
    assert "_context: CallCallContext" in content
    assert "**kwargs: Any" in content
