"""Tests for registry interface fixes."""

import re
from pathlib import Path


def test_server_named_tuple_interface_type(zalfmas_stubs: Path) -> None:
    """Test that server NamedTuple result accepts both Server and Client for interfaces."""
    stub_file = zalfmas_stubs / "mas/schema/registry/registry_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    tuple_match = re.search(r"class RegistryResultTuple\(NamedTuple\):(.*?)(?=\nclass |\Z)", content, re.DOTALL)
    assert tuple_match, "RegistryResultTuple class not found"
    tuple_content = tuple_match.group(1)

    # Check registry field
    # Should be: registry: RegistryClient | _RegistryInterfaceModule.Server
    assert (
        "registry: RegistryClient | _RegistryInterfaceModule.Server" in tuple_content
        or "registry: _RegistryInterfaceModule.Server | RegistryClient" in tuple_content
    ), f"Expected RegistryClient | Server in Tuple, got: {tuple_content}"


def test_list_of_structs_not_any(zalfmas_stubs: Path) -> None:
    """Test that List(Struct) is not Any in results."""
    stub_file = zalfmas_stubs / "mas/schema/registry/registry_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    result_match = re.search(
        r"class SupportedcategoriesResult\(Awaitable\[SupportedcategoriesResult\], Protocol\):(.*?)(?=\nclass |\Z)",
        content,
        re.DOTALL,
    )
    assert result_match, "SupportedcategoriesResult class not found"
    result_content = result_match.group(1)

    # Check cats field
    # Should be IdInformationListReader (or similar alias)
    # Currently it is Any
    assert "cats: Any" not in result_content, "cats field should not be Any"
    assert "cats: IdInformationListReader" in result_content, "cats field should be IdInformationListReader"


def test_list_of_interfaces_types(zalfmas_stubs: Path) -> None:
    """Test that List(Interface) uses correct Client/Server types."""
    stub_file = zalfmas_stubs / "mas/schema/registry/registry_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    result_match = re.search(
        r"class RemovecategoryResult\(Awaitable\[RemovecategoryResult\], Protocol\):(.*?)(?=\nclass |\Z)",
        content,
        re.DOTALL,
    )

    assert result_match, (
        f"RemovecategoryResult class not found\nFound in full file: {re.search(r'class RemovecategoryResult', content)}"
    )
    result_content = result_match.group(1)

    # Check removedObjects field
    # Should be IdentifiableClientListReader
    # Currently it is Sequence[_IdentifiableModule] (the protocol/module)
    assert "removedObjects: IdentifiableClientListReader" in result_content, (
        f"Expected removedObjects: IdentifiableClientListReader, got: {result_content}"
    )
