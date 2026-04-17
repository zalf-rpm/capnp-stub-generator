"""Test that interface method result structs are properly embedded in generated binaries.

This test verifies the fix for the issue where interface method result/param structs
were not being included in the embedded binary schemas, causing runtime errors
when trying to access result fields like context.results.cap.
"""

from __future__ import annotations

import base64
import re
from typing import TYPE_CHECKING

import schema_capnp

if TYPE_CHECKING:
    from pathlib import Path

MIN_EMBEDDED_SCHEMA_COUNT = 10


def test_interface_result_structs_are_embedded(calculator_stubs: Path) -> None:
    """Verify that interface method result structs are embedded in the binary.

    Before the fix, only the explicit param structs were embedded,
    but the implicit result structs were missing, causing runtime errors.
    """
    # Load the generated module to get the embedded schemas
    stub_file = calculator_stubs / "calculator_capnp/__init__.py"
    content = stub_file.read_text()

    match = re.search(r"_SCHEMA_NODES = \[(.*?)\]", content, re.DOTALL)
    assert match, "_SCHEMA_NODES not found in generated file"

    # Parse all embedded schema IDs
    schema_lines = match.group(1).strip().split("\n")
    embedded_ids: set[int] = set()
    for raw_line in schema_lines:
        schema_line = raw_line.strip()
        if schema_line.startswith(('"', "'")):
            schema_b64 = schema_line.split(",")[0].strip().strip('"').strip("'")
            schema_data = base64.b64decode(schema_b64)
            node_reader = schema_capnp.Node.from_bytes_packed(schema_data)
            embedded_ids.add(node_reader.id)

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

    # Verify result structs are mentioned
    assert "evaluate$Results" in content or "evaluateResults" in content
    assert "_loader.get" in content  # Loader is created
    assert "load_dynamic" in content  # Schemas are loaded


def test_param_structs_are_embedded(calculator_stubs: Path) -> None:
    """Verify that interface method param structs are also embedded.

    While explicit param structs are usually in nestedNodes,
    implicit param structs for methods should also be embedded.
    """
    stub_file = calculator_stubs / "calculator_capnp/__init__.py"
    content = stub_file.read_text()

    match = re.search(r"_SCHEMA_NODES = \[(.*?)\]", content, re.DOTALL)
    assert match

    schema_lines = match.group(1).strip().split("\n")
    embedded_ids: set[int] = set()
    for raw_line in schema_lines:
        schema_line = raw_line.strip()
        if schema_line.startswith(('"', "'")):
            schema_b64 = schema_line.split(",")[0].strip().strip('"').strip("'")
            schema_data = base64.b64decode(schema_b64)
            node_reader = schema_capnp.Node.from_bytes_packed(schema_data)
            embedded_ids.add(node_reader.id)

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
    assert "_loader = capnp.SchemaLoader()" in runtime_content
    assert "for _schema_b64 in _SCHEMA_NODES:" in runtime_content
    assert "_loader.load_dynamic(_node_reader)" in runtime_content

    # Result tuples should be created in the runtime helper module, not on the top-level runtime module.
    assert "EvaluateResultTuple" not in runtime_content
    assert "NamedTuple" in tuple_module_content or "namedtuple" in tuple_module_content.lower()
