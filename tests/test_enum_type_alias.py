"""Test enum type alias generation and usage."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.test_helpers import CommandResult, read_generated_types_combined, run_pyright


def _run_pyright_sample(calculator_stubs: Path, filename: str, test_code: str) -> CommandResult:
    env = os.environ.copy()
    python_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(path for path in (str(calculator_stubs), python_path) if path)

    # Generated output is excluded from the project-wide basedpyright scan. Put
    # usage samples outside that tree so explicitly requested samples are still
    # analyzed rather than silently skipped by the exclusion.
    with TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / filename
        test_file.write_text(test_code)
        return run_pyright(test_file, env=env)


def test_enum_type_alias_exists(calculator_stubs: Path) -> None:
    """Test that enum type aliases are generated."""
    content = read_generated_types_combined(calculator_stubs / "calculator_capnp")

    # Check that the enum type alias exists (flattened name)
    assert 'type CalculatorOperatorEnum = int | Literal["add", "subtract", "multiply", "divide"]' in content


def test_enum_type_alias_accepts_literals(calculator_stubs: Path) -> None:
    """Test that the Operator type accepts string literals."""
    test_code = '''
from calculator_capnp.types.enums import CalculatorOperatorEnum

def use_operator_literal(op: CalculatorOperatorEnum):
    """Function that accepts Operator."""
    pass

# Should accept string literals
use_operator_literal("add")
use_operator_literal("subtract")
use_operator_literal("multiply")
use_operator_literal("divide")
'''

    result = _run_pyright_sample(calculator_stubs, "test_enum_literal_typing.py", test_code)

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"


def test_enum_type_alias_accepts_int(calculator_stubs: Path) -> None:
    """Test that the Operator accepts integer values."""
    test_code = '''
from calculator_capnp.types.enums import CalculatorOperatorEnum

def use_operator_int(op: CalculatorOperatorEnum):
    """Function that accepts Operator."""
    pass

# Should accept integer values
use_operator_int(0)
use_operator_int(1)
use_operator_int(2)
use_operator_int(3)
'''

    result = _run_pyright_sample(calculator_stubs, "test_enum_int_typing.py", test_code)

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"


def test_enum_getters_use_runtime_dynamic_values(basic_stubs: Path) -> None:
    """Getters return pycapnp enum objects while setters retain ergonomic input aliases."""
    sample = basic_stubs / "test_enum_runtime_value_typing.py"
    sample.write_text(
        """from typing import Literal, assert_type

import dummy_capnp
from dummy_capnp.types.enums import TestEnumValue

message = dummy_capnp.TestAllTypes.new_message(enumField="foo")
assert_type(message.enumField, TestEnumValue)
assert_type(message.as_reader().enumField, TestEnumValue)
assert_type(
    message.enumField.__str__(),
    Literal["foo", "bar", "baz", "qux", "quux", "corge", "grault", "garply"],
)
assert_type(str(message.enumField), str)
message.enumField = "bar"
message.enumField = dummy_capnp.TestEnum.baz
""",
        encoding="utf8",
    )

    result = run_pyright(sample)
    assert result.returncode == 0, result.stdout


def test_enum_type_alias_accepts_enum_attribute(calculator_stubs: Path) -> None:
    """Test that the Operator accepts enum dot notation."""
    test_code = '''
import calculator_capnp
from calculator_capnp.types.enums import CalculatorOperatorEnum

def use_operator_enum(op: CalculatorOperatorEnum):
    """Function that accepts Operator."""
    pass

# Should accept enum attributes (which are int at runtime)
use_operator_enum(calculator_capnp.Calculator.Operator.add)
use_operator_enum(calculator_capnp.Calculator.Operator.subtract)
use_operator_enum(calculator_capnp.Calculator.Operator.multiply)
use_operator_enum(calculator_capnp.Calculator.Operator.divide)
'''

    result = _run_pyright_sample(calculator_stubs, "test_enum_attr_typing.py", test_code)

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"


def test_enum_type_alias_rejects_invalid_literals(calculator_stubs: Path) -> None:
    """Test that the Operator rejects invalid string literals."""
    test_code = '''
from calculator_capnp.types.enums import CalculatorOperatorEnum

def use_operator(op: CalculatorOperatorEnum):
    """Function that accepts Operator."""
    pass

# Should reject invalid string literals
use_operator("invalid")
'''

    result = _run_pyright_sample(calculator_stubs, "test_enum_invalid_typing.py", test_code)
    error_count = result.stdout.count("error:")
    assert error_count == 1, f"Type checking should reject one invalid literal:\n{result.stdout}"


def test_enum_type_alias_in_class_init(calculator_stubs: Path) -> None:
    """Test using Operator in a class __init__ method (real-world example)."""
    test_code = '''
from typing import Any
import calculator_capnp
from calculator_capnp.types.enums import CalculatorOperatorEnum

class OperatorImpl(calculator_capnp.Calculator.Function.Server):
    """Implementation wrapping arithmetic operators."""

    def __init__(self, op: CalculatorOperatorEnum):
        self.op = op

    async def call(self, params: Any, _context: Any, **kwargs: Any) -> float:
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

    result = _run_pyright_sample(calculator_stubs, "test_enum_class_typing.py", test_code)

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"


def test_enum_comparison_with_literals(calculator_stubs: Path) -> None:
    """Test that enum values can be compared with string literals."""
    test_code = '''
import calculator_capnp
from calculator_capnp.types.enums import CalculatorOperatorEnum

def process_operator(op: CalculatorOperatorEnum) -> str:
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

    result = _run_pyright_sample(calculator_stubs, "test_enum_comparison_typing.py", test_code)

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"
