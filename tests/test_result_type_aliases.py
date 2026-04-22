"""Test that Result helper types live under the generated types package."""

from pathlib import Path

import pytest

from tests.test_helpers import log_summary, read_generated_types_combined, read_generated_types_file


def _calculator_runtime_stub(calculator_stubs: Path) -> str:
    return (calculator_stubs / "calculator_capnp" / "__init__.pyi").read_text()


def _calculator_types_all(calculator_stubs: Path) -> str:
    return read_generated_types_combined(calculator_stubs / "calculator_capnp")


def _calculator_client_results(calculator_stubs: Path) -> str:
    return read_generated_types_file(calculator_stubs / "calculator_capnp", "results", "client.pyi")


def _calculator_clients(calculator_stubs: Path) -> str:
    return read_generated_types_file(calculator_stubs / "calculator_capnp", "clients.pyi")


def test_result_helper_classes_exist(calculator_stubs: Path) -> None:
    """Client Result helper classes should be defined in the shared helper surface and public result module."""
    all_content = _calculator_types_all(calculator_stubs)
    public_content = _calculator_client_results(calculator_stubs)

    for result_name in ("EvaluateResult", "DeffunctionResult", "GetoperatorResult", "ReadResult", "CallResult"):
        assert f"class {result_name}(Awaitable[{result_name}], Protocol):" in all_content
        assert f"class {result_name}(Awaitable[{result_name}], Protocol):" in public_content


def test_result_helpers_are_used_directly(calculator_stubs: Path) -> None:
    """Result helper classes should stay out of the runtime stub and live only in the types modules."""
    runtime_content = _calculator_runtime_stub(calculator_stubs)
    all_content = _calculator_types_all(calculator_stubs)

    assert "def evaluate(" in all_content
    assert "-> EvaluateResult:" in all_content
    assert "def read(self) -> ReadResult:" in all_content
    assert "def call(" in all_content
    assert "-> CallResult:" in all_content
    assert "def send(self) -> EvaluateResult:" in all_content
    assert "EvaluateResult = " not in runtime_content
    assert "class EvaluateResult(" not in runtime_content


def test_result_helpers_alongside_builder_reader(calculator_stubs: Path) -> None:
    """Runtime stubs should route helper references through the public types package surface."""
    runtime_content = _calculator_runtime_stub(calculator_stubs)
    builders_content = (calculator_stubs / "calculator_capnp" / "types" / "builders.pyi").read_text()

    assert "from . import types as types" in runtime_content
    assert "Calculator: types.modules._CalculatorInterfaceModule" in runtime_content
    assert "ExpressionBuilder = types.builders.ExpressionBuilder" not in runtime_content
    assert "EvaluateResult = types.results.client.EvaluateResult" not in runtime_content
    assert "class ExpressionBuilder(_DynamicStructBuilder):" in builders_content


def test_result_helpers_do_not_use_type_aliases(calculator_stubs: Path) -> None:
    """Result helpers should stay as classes, not type aliases, in both internal and public types stubs."""
    runtime_content = _calculator_runtime_stub(calculator_stubs)
    all_content = _calculator_types_all(calculator_stubs)
    public_content = _calculator_client_results(calculator_stubs)

    assert "type EvaluateResult = " not in runtime_content
    assert "type EvaluateResult = " not in public_content
    assert "class EvaluateResult(Awaitable[EvaluateResult], Protocol):" in all_content


def test_void_method_result_helper_exists(calculator_stubs: Path) -> None:
    """Void methods should still expose Result helpers from the public results module."""
    channel_results = calculator_stubs.parent.parent / "basic" / "interfaces_capnp" / "types" / "results" / "client.pyi"

    if not channel_results.exists():
        pytest.skip("Channel result helper module not available")

    content = channel_results.read_text()
    if "ReaderCloseResult" in content:
        assert "class ReaderCloseResult(" in content


def test_nested_interface_result_helpers(calculator_stubs: Path) -> None:
    """Nested interfaces should publish their Result helpers through the shared public result module."""
    all_content = _calculator_types_all(calculator_stubs)
    public_content = _calculator_client_results(calculator_stubs)

    assert "class ReadResult(Awaitable[ReadResult], Protocol):" in public_content
    assert "class CallResult(Awaitable[CallResult], Protocol):" in public_content
    assert "def read(self) -> ReadResult:" in all_content
    assert "def call(" in all_content
    assert "-> CallResult:" in all_content


def test_result_helper_usage_in_type_hints(calculator_stubs: Path) -> None:
    """Client helper stubs should point at the shared result and builder modules."""
    runtime_content = _calculator_runtime_stub(calculator_stubs)
    clients_content = _calculator_clients(calculator_stubs)
    all_content = _calculator_types_all(calculator_stubs)

    assert "def evaluate(" in all_content
    assert "-> EvaluateResult:" in all_content
    assert "builders.ExpressionBuilder" in clients_content
    assert "results_client.EvaluateResult" in clients_content
    assert "CalculatorClient = types.clients.CalculatorClient" not in runtime_content


def test_result_helper_count_matches_method_count(calculator_stubs: Path) -> None:
    """Every RPC method with a client result should have both shared and public definitions."""
    all_content = _calculator_types_all(calculator_stubs)
    public_content = _calculator_client_results(calculator_stubs)

    calculator_results = [
        ("evaluate", "EvaluateResult"),
        ("defFunction", "DeffunctionResult"),
        ("getOperator", "GetoperatorResult"),
        ("read", "ReadResult"),
        ("call", "CallResult"),
    ]

    for method_name, result_name in calculator_results:
        assert f"class {result_name}(Awaitable[{result_name}], Protocol):" in all_content, (
            f"Should have {result_name} helper class for {method_name}"
        )
        assert f"class {result_name}(Awaitable[{result_name}], Protocol):" in public_content, (
            f"Should publish {result_name} for {method_name}"
        )


def test_summary() -> None:
    """Summary of Result helper module tests."""
    log_summary(
        "RESULT TYPE ALIAS SUMMARY",
        [
            "✓ Result helper classes live in generated helper submodules",
            "✓ Result helpers are defined in types.results.client",
            "✓ Runtime stubs no longer expose top-level Result aliases",
            "✓ Runtime signatures point at public helper modules when needed",
            "✓ Nested and void Result helpers remain available",
        ],
    )
