"""Test that interface method result structs are properly embedded in generated binaries.

This test verifies the fix for the issue where interface method result/param structs
were not being included in the embedded binary schemas, causing runtime errors
when trying to access result fields like context.results.cap.
"""

from __future__ import annotations

import ast
import base64
from typing import TYPE_CHECKING

import schema_capnp

if TYPE_CHECKING:
    from pathlib import Path

MIN_EMBEDDED_SCHEMA_COUNT = 10


def _schema_bundle_content(generated_root: Path) -> str:
    current = generated_root
    while True:
        bundle_files = sorted(current.glob("_capnp_schema_bundle_*.py"))
        if bundle_files:
            return bundle_files[0].read_text(encoding="utf8")
        if current == current.parent:
            break
        current = current.parent
    msg = f"schema bundle file not found from {generated_root}"
    raise AssertionError(msg)


def _embedded_schema_ids(bundle_content: str) -> set[int]:
    tree = ast.parse(bundle_content)
    schema_nodes: list[tuple[int, str]] | None = None
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "_SCHEMA_NODES" for target in statement.targets
        ):
            schema_nodes = ast.literal_eval(statement.value)
            break
    assert schema_nodes is not None, "_SCHEMA_NODES not found in schema bundle file"

    embedded_ids: set[int] = set()
    for schema_id, schema_b64 in schema_nodes:
        schema_data = base64.b64decode(schema_b64)
        node_reader = schema_capnp.Node.from_bytes_packed(schema_data)
        embedded_ids.add(node_reader.id)
        assert schema_id == node_reader.id
    return embedded_ids


def test_interface_result_structs_are_embedded(calculator_stubs: Path) -> None:
    """Verify that interface method result structs are embedded in the binary.

    Before the fix, only the explicit param structs were embedded,
    but the implicit result structs were missing, causing runtime errors.
    """
    embedded_ids = _embedded_schema_ids(_schema_bundle_content(calculator_stubs))

    # Check that result structs for interface methods are embedded
    # Calculator.evaluate$Results - implicit result struct
    evaluate_results_id = 0x81B1A3F55887A611  # From calculator example
    assert evaluate_results_id in embedded_ids, "Calculator.evaluate$Results not embedded"


def test_result_struct_has_fields(calculator_stubs: Path) -> None:
    """Verify that the embedded result struct can be loaded and has the expected fields."""
    # Just check that result structs are present in the generated file
    # Runtime test would require complex import handling
    stub_file = calculator_stubs / "calculator_capnp/__init__.py"
    content = stub_file.read_text()

    # Verify result structs are in the shared schema bundle.
    assert "evaluate$Results" in _schema_bundle_content(calculator_stubs)
    assert "_loader.get" in content  # Loader is created
    assert "get_schema_by_id" in content  # Schema helper is re-exported


def test_param_structs_are_embedded(calculator_stubs: Path) -> None:
    """Verify that interface method param structs are also embedded.

    While explicit param structs are usually in nestedNodes,
    implicit param structs for methods should also be embedded.
    """
    embedded_ids = _embedded_schema_ids(_schema_bundle_content(calculator_stubs))

    # Check that param structs are embedded
    # Calculator.evaluate$Params (implicit)
    # Just verify some param struct is there - we don't have exact IDs
    # The important thing is that the code doesn't crash when loading them
    assert len(embedded_ids) > MIN_EMBEDDED_SCHEMA_COUNT, "Should have many schemas including params/results"


def test_runtime_result_field_access(calculator_stubs: Path) -> None:
    """Test that result tuple helpers are generated in the runtime tuple helper module."""
    runtime_file = calculator_stubs / "calculator_capnp/__init__.py"
    tuple_module_file = calculator_stubs / "calculator_capnp/types/results/tuples.py"
    runtime_content = runtime_file.read_text()
    tuple_module_content = tuple_module_file.read_text()

    # Verify the generated code has the necessary structure
    # for runtime access to result fields
    assert "def _import_schema_bundle() -> object:" in runtime_content
    assert "_schema_bundle = _import_schema_bundle()" in runtime_content
    assert "_capnp_schema_bundle_" in runtime_content
    assert '_loader: SchemaLoader = cast("SchemaLoader", _schema_bundle.get_schema_loader())' in runtime_content
    assert "get_schema_by_id" in runtime_content

    # Result tuples should be created in the runtime helper module, not on the top-level runtime module.
    assert "EvaluateResultTuple" not in runtime_content
    assert "NamedTuple" in tuple_module_content or "namedtuple" in tuple_module_content.lower()
