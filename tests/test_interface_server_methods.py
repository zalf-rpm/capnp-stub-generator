"""Tests for interface Server class method signatures."""

import pytest

from tests.conftest import read_stub_file


@pytest.fixture(scope="module")
def calculator_stub_lines(generate_calculator_stubs):
    """Read calculator.capnp stub file lines."""
    stub_path = generate_calculator_stubs / "calculator_capnp.pyi"
    return read_stub_file(stub_path)


def test_server_class_exists_for_interfaces(calculator_stub_lines):
    """Server classes should be generated for all interfaces."""
    lines = calculator_stub_lines

    # Check that Server classes exist for each interface
    assert any("class Value(Protocol):" in line for line in lines)
    assert any("class Server:" in line for line in lines)

    # Count Server classes - should be 3 (Value, Function, Calculator)
    server_count = sum(1 for line in lines if line.strip() == "class Server:")
    assert server_count == 3, f"Expected 3 Server classes, found {server_count}"


def test_server_methods_have_signatures(calculator_stub_lines):
    """Server class methods should have proper type signatures."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # Function.Server should have call method
    assert "class Server:" in content
    assert "def call(self, params: Sequence[float]" in content
    assert "Awaitable[float" in content

    # Value.Server should have read method with _context parameter
    assert "def read(self, _context: Calculator.Value.ReadCallContext, **kwargs: Any) -> Awaitable[float | None]:" in content

    # Calculator.Server should have evaluate method with Reader type
    assert "def evaluate(" in content
    assert "expression: Calculator.ExpressionReader" in content
    assert "Awaitable[Calculator.Value | Calculator.Value.Server | None]" in content


def test_server_methods_accept_context(calculator_stub_lines):
    """Server methods should accept _context parameter and **kwargs."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # All server methods should have **kwargs
    assert "**kwargs" in content

    # Find all Server classes and verify their methods
    import re

    server_sections = re.findall(r"class Server:.*?(?=\n    class |\n\nclass |\Z)", content, re.DOTALL)

    assert len(server_sections) > 0, "Should find at least one Server class"

    for server_section in server_sections:
        # Find all method definitions in this Server class
        methods = re.findall(r"def \w+\([^)]*(?:\).*?)?(?=\n|$)", server_section, re.DOTALL)
        for method in methods:
            # Each method should have **kwargs
            assert "**kwargs" in method, f"Server method should have **kwargs: {method}"
            # Should have explicit _context parameter with type annotation
            assert "_context:" in method, f"Server method should have _context parameter: {method}"
            # _context should have a CallContext type
            assert "CallContext" in method, f"Server method _context should be typed with CallContext: {method}"


def test_server_methods_return_interface_or_implementation(calculator_stub_lines):
    """Server methods returning interfaces should accept implementations."""
    lines = calculator_stub_lines
    content = "".join(lines)

    # Methods returning interfaces should allow Interface | Interface.Server
    assert "Calculator.Value | Calculator.Value.Server" in content
    assert "Calculator.Function | Calculator.Function.Server" in content


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
    # Check for multi-line signature
    server_call_found = (
        "def call(\n                self, params: Sequence[float], _context: Calculator.Function.CallCallContext, **kwargs"
        in content
    )
    server_call_found = (
        server_call_found
        or "def call(self, params: Sequence[float], _context: Calculator.Function.CallCallContext, **kwargs)" in content
    )

    assert server_call_found, "Server call method should have same params as Protocol plus _context and **kwargs"
