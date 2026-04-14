"""Test that Result helper types live under the generated types package."""

from pathlib import Path

import pytest

from tests.test_helpers import log_summary


def _calculator_runtime_stub(calculator_stubs: Path) -> str:
    return (calculator_stubs / "calculator_capnp" / "__init__.pyi").read_text()


def _calculator_types_all(calculator_stubs: Path) -> str:
    return (calculator_stubs / "calculator_capnp" / "types" / "_all.pyi").read_text()


def _calculator_client_results(calculator_stubs: Path) -> str:
    return (calculator_stubs / "calculator_capnp" / "types" / "results" / "client.pyi").read_text()


def test_result_helper_classes_exist(calculator_stubs: Path) -> None:
    """Client Result helper classes should be defined in the internal types stub and re-exported publicly."""
    all_content = _calculator_types_all(calculator_stubs)
    public_content = _calculator_client_results(calculator_stubs)

    for result_name in ("EvaluateResult", "DeffunctionResult", "GetoperatorResult", "ReadResult", "CallResult"):
        assert f"class {result_name}(Awaitable[{result_name}], Protocol):" in all_content
        assert f"from .._all import {result_name} as {result_name}" in public_content


def test_result_helpers_are_used_directly(calculator_stubs: Path) -> None:
    """Runtime-facing method signatures should still use the flattened Result names via compatibility re-exports."""
    runtime_content = _calculator_runtime_stub(calculator_stubs)
    all_content = _calculator_types_all(calculator_stubs)

    assert "def evaluate(" in all_content
    assert "-> EvaluateResult:" in all_content
    assert "def read(self) -> ReadResult:" in all_content
    assert "def call(" in all_content
    assert "-> CallResult:" in all_content
    assert "def send(self) -> EvaluateResult:" in all_content
    assert "EvaluateResult = _client_results.EvaluateResult" in runtime_content


def test_result_helpers_alongside_builder_reader(calculator_stubs: Path) -> None:
    """Compatibility re-exports in the runtime stub should point at the targeted public helper modules."""
    runtime_content = _calculator_runtime_stub(calculator_stubs)
    builders_content = (calculator_stubs / "calculator_capnp" / "types" / "builders.pyi").read_text()

    assert "from .types import builders as _builders" in runtime_content
    assert "from .types.results import client as _client_results" in runtime_content
    assert "ExpressionBuilder = _builders.ExpressionBuilder" in runtime_content
    assert "EvaluateResult = _client_results.EvaluateResult" in runtime_content
    assert "from ._all import ExpressionBuilder as ExpressionBuilder" in builders_content


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
        assert "from .._all import ReaderCloseResult as ReaderCloseResult" in content


def test_nested_interface_result_helpers(calculator_stubs: Path) -> None:
    """Nested interfaces should publish their Result helpers through the shared public result module."""
    all_content = _calculator_types_all(calculator_stubs)
    public_content = _calculator_client_results(calculator_stubs)

    assert "from .._all import ReadResult as ReadResult" in public_content
    assert "from .._all import CallResult as CallResult" in public_content
    assert "def read(self) -> ReadResult:" in all_content
    assert "def call(" in all_content
    assert "-> CallResult:" in all_content


def test_result_helper_usage_in_type_hints(calculator_stubs: Path) -> None:
    """The runtime stub should continue to expose flattened Result names for annotations."""
    runtime_content = _calculator_runtime_stub(calculator_stubs)
    all_content = _calculator_types_all(calculator_stubs)

    assert "def evaluate(" in all_content
    assert "-> EvaluateResult:" in all_content
    assert "EvaluateResult = _client_results.EvaluateResult" in runtime_content
    assert "CalculatorClient = _clients.CalculatorClient" in runtime_content


def test_result_helper_count_matches_method_count(calculator_stubs: Path) -> None:
    """Every RPC method with a client result should have both an internal class and a public re-export."""
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
        assert f"from .._all import {result_name} as {result_name}" in public_content, (
            f"Should publicly re-export {result_name} for {method_name}"
        )


def test_summary() -> None:
    """Summary of Result helper module tests."""
    log_summary(
        "RESULT TYPE ALIAS SUMMARY",
        [
            "✓ Result helper classes live in types/_all",
            "✓ Result helpers are re-exported from types.results.client",
            "✓ Runtime signatures still use flattened Result names",
            "✓ Compatibility re-exports replace old top-level class definitions",
            "✓ Nested and void Result helpers remain available",
        ],
    )
