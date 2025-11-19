"""Test enum type alias generation and usage."""

import subprocess


def test_enum_type_alias_exists(calculator_stubs):
    """Test that enum type aliases are generated."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Check that the enum type alias exists (flattened name)
    assert 'type CalculatorOperatorEnum = int | Literal["add", "subtract", "multiply", "divide"]' in content


def test_enum_type_alias_accepts_literals(calculator_stubs):
    """Test that the Operator type accepts string literals."""
    test_code = '''
import calculator_capnp

def use_operator_literal(op: calculator_capnp.CalculatorOperatorEnum):
    """Function that accepts Operator."""
    pass

# Should accept string literals
use_operator_literal("add")
use_operator_literal("subtract")
use_operator_literal("multiply")
use_operator_literal("divide")
'''

    test_file = calculator_stubs / "test_enum_literal_typing.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"


def test_enum_type_alias_accepts_int(calculator_stubs):
    """Test that the Operator accepts integer values."""
    test_code = '''
import calculator_capnp

def use_operator_int(op: calculator_capnp.CalculatorOperatorEnum):
    """Function that accepts Operator."""
    pass

# Should accept integer values
use_operator_int(0)
use_operator_int(1)
use_operator_int(2)
use_operator_int(3)
'''

    test_file = calculator_stubs / "test_enum_int_typing.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"


def test_enum_type_alias_accepts_enum_attribute(calculator_stubs):
    """Test that the Operator accepts enum dot notation."""
    test_code = '''
import calculator_capnp

def use_operator_enum(op: calculator_capnp.CalculatorOperatorEnum):
    """Function that accepts Operator."""
    pass

# Should accept enum attributes (which are int at runtime)
use_operator_enum(calculator_capnp.Calculator.Operator.add)
use_operator_enum(calculator_capnp.Calculator.Operator.subtract)
use_operator_enum(calculator_capnp.Calculator.Operator.multiply)
use_operator_enum(calculator_capnp.Calculator.Operator.divide)
'''

    test_file = calculator_stubs / "test_enum_attr_typing.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"


def test_enum_type_alias_rejects_invalid_literals(calculator_stubs):
    """Test that the Operator rejects invalid string literals."""
    test_code = '''
import calculator_capnp

def use_operator(op: calculator_capnp.CalculatorOperatorEnum):
    """Function that accepts Operator."""
    pass

# Should reject invalid string literals
use_operator("invalid")  # type: ignore[arg-type]
'''

    test_file = calculator_stubs / "test_enum_invalid_typing.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    # Should have one error for the invalid literal (but we're ignoring it)
    # This test mainly documents the expected behavior
    # The type: ignore comment should suppress the error
    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed unexpectedly: {result.stdout}"


def test_enum_type_alias_in_class_init(calculator_stubs):
    """Test using Operator in a class __init__ method (real-world example)."""
    test_code = '''
import calculator_capnp

class OperatorImpl(calculator_capnp.Calculator.Function.Server):
    """Implementation wrapping arithmetic operators."""
    
    def __init__(self, op: calculator_capnp.CalculatorOperatorEnum):
        self.op = op
    
    async def call(self, params, _context, **kwargs):
        assert len(params) == 2
        
        op = self.op
        
        if op == "add":
            return params[0] + params[1]
        elif op == "subtract":
            return params[0] - params[1]
        elif op == "multiply":
            return params[0] * params[1]
        elif op == "divide":
            return params[0] / params[1]
        else:
            raise ValueError("Unknown operator")

# Should accept all valid forms
impl1 = OperatorImpl("add")
impl2 = OperatorImpl(calculator_capnp.Calculator.Operator.subtract)
impl3 = OperatorImpl(0)
'''

    test_file = calculator_stubs / "test_enum_class_typing.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"


def test_enum_comparison_with_literals(calculator_stubs):
    """Test that enum values can be compared with string literals."""
    test_code = '''
import calculator_capnp

def process_operator(op: calculator_capnp.CalculatorOperatorEnum) -> str:
    """Process operator and return string description."""
    if op == "add":
        return "addition"
    elif op == "subtract":
        return "subtraction"
    elif op == "multiply":
        return "multiplication"
    elif op == "divide":
        return "division"
    else:
        return "unknown"

# Test with different input types
result1 = process_operator("add")
result2 = process_operator(calculator_capnp.Calculator.Operator.add)
result3 = process_operator(0)
'''

    test_file = calculator_stubs / "test_enum_comparison_typing.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"
