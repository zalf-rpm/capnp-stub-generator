"""Tests for struct return types in client methods."""

import re
from pathlib import Path

from tests.test_helpers import read_generated_types_combined


def test_client_result_uses_reader_only(basic_stubs: Path) -> None:
    """Test that top-level client result helpers use Reader types only for structs."""
    content = read_generated_types_combined(basic_stubs / "struct_return_capnp")

    result_match = re.search(
        r"class InfoResult\(Awaitable\[InfoResult\], Protocol\):(.*?)(?=\nclass |\Z)", content, re.DOTALL
    )
    assert result_match, "InfoResult class not found in IdentifiableClient"
    result_content = result_match.group(1)

    # Check nested field
    assert "nested: readers.NestedReader" in result_content
    assert "NestedBuilder" not in result_content, "Client result should not reference Builder"


def test_server_result_uses_builder_and_reader(basic_stubs: Path) -> None:
    """Test that direct struct returns use Builder types via CallContext and assignment-friendly tuple fields."""
    content = read_generated_types_combined(basic_stubs / "struct_return_capnp")

    assert "class InfoCallContext(Protocol):" in content
    assert "def results(self) -> builders.IdInformationBuilder: ..." in content
    assert "class InfoResultTuple(NamedTuple):" in content
    assert "nested: builders.NestedBuilder | readers.NestedReader | dict[str, Any]" in content


def test_server_named_tuple_has_nested_field(basic_stubs: Path) -> None:
    """Test that server NamedTuple result has nested struct field."""
    content = read_generated_types_combined(basic_stubs / "struct_return_capnp")

    tuple_match = re.search(r"class InfoResultTuple\(NamedTuple\):(.*?)(?=\nclass |\Z)", content, re.DOTALL)
    assert tuple_match, "InfoResultTuple class not found"
    tuple_content = tuple_match.group(1)

    # Check nested field
    assert "nested: builders.NestedBuilder | readers.NestedReader | dict[str, Any]" in tuple_content
