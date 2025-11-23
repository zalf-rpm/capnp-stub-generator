"""Tests for registry interface fixes."""

import re


def test_server_named_tuple_interface_type(zalfmas_stubs):
    """Test that server NamedTuple result accepts both Server and Client for interfaces."""
    stub_file = zalfmas_stubs / "registry_capnp.pyi"
    content = stub_file.read_text()

    # Find Server section
    server_match = re.search(
        r"class Server\(_IdentifiableInterfaceModule.Server\):(.*?)(?=\n\s+class AdminClient)", content, re.DOTALL
    )
    assert server_match, "Server class not found"
    server_content = server_match.group(1)

    # Find RegistryResultTuple
    tuple_match = re.search(r"class RegistryResultTuple\(NamedTuple\):(.*?)(?=\n\s+class)", server_content, re.DOTALL)
    assert tuple_match, "RegistryResultTuple class not found in Server"
    tuple_content = tuple_match.group(1)

    # Check registry field
    # Should be: registry: _RegistryInterfaceModule.RegistryClient | _RegistryInterfaceModule.Server
    assert (
        "registry: _RegistryInterfaceModule.RegistryClient | _RegistryInterfaceModule.Server" in tuple_content
        or "registry: _RegistryInterfaceModule.Server | _RegistryInterfaceModule.RegistryClient" in tuple_content
    ), f"Expected RegistryClient | Server in Tuple, got: {tuple_content}"


def test_list_of_structs_not_any(zalfmas_stubs):
    """Test that List(Struct) is not Any in results."""
    stub_file = zalfmas_stubs / "registry_capnp.pyi"
    content = stub_file.read_text()

    # Find RegistryClient
    client_match = re.search(
        r"class RegistryClient\(_IdentifiableInterfaceModule.IdentifiableClient\):(.*?)(?=\n\n|\Z)", content, re.DOTALL
    )
    assert client_match, "RegistryClient class not found"
    client_content = client_match.group(1)

    # Find SupportedcategoriesResult
    result_match = re.search(
        r"class SupportedcategoriesResult\(Awaitable\[SupportedcategoriesResult\], Protocol\):(.*?)(?=\n\s+class|\Z)",
        client_content,
        re.DOTALL,
    )
    assert result_match, "SupportedcategoriesResult class not found"
    result_content = result_match.group(1)

    # Check cats field
    # Should be IdInformationListReader (or similar alias)
    # Currently it is Any
    assert "cats: Any" not in result_content, "cats field should not be Any"
    assert "cats: IdInformationListReader" in result_content, "cats field should be IdInformationListReader"


def test_list_of_interfaces_types(zalfmas_stubs):
    """Test that List(Interface) uses correct Client/Server types."""
    stub_file = zalfmas_stubs / "registry_capnp.pyi"
    content = stub_file.read_text()

    # Find AdminClient
    # Capture until the next top-level class definition (which starts with "class _") or end of file
    # AdminClient is indented, so "class _" at start of line indicates end of AdminClient's parent module or next module
    client_match = re.search(
        r"class AdminClient\(_IdentifiableInterfaceModule.IdentifiableClient\):(.*?)(?=\nclass _|\Z)",
        content,
        re.DOTALL,
    )
    assert client_match, "AdminClient class not found"
    client_content = client_match.group(1)

    # Find RemovecategoryResult
    # Just search for the line defining the class and capture subsequent lines
    result_match = re.search(
        r"class RemovecategoryResult\(Awaitable\[RemovecategoryResult\], Protocol\):(.*?)(?=\n\s+class|\n\s+def|\Z)",
        client_content,
        re.DOTALL,
    )

    if not result_match:
        print(f"Client content length: {len(client_content)}")
        print(f"Client content start: {client_content[:200]}")
        # Try to find it in the whole file to debug
        full_search = re.search(r"class RemovecategoryResult", content)
        print(f"Found in full file: {full_search}")

    assert result_match, "RemovecategoryResult class not found"
    result_content = result_match.group(1)

    # Check removedObjects field
    # Should be IdentifiableClientListReader
    # Currently it is Sequence[_IdentifiableModule] (the protocol/module)
    assert "removedObjects: IdentifiableClientListReader" in result_content, (
        f"Expected removedObjects: IdentifiableClientListReader, got: {result_content}"
    )
