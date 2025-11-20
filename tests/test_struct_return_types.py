"""Tests for struct return types in client methods."""

import re


def test_client_result_uses_reader_only(basic_stubs):
    """Test that client result protocols use Reader types only for structs."""
    stub_file = basic_stubs / "struct_return_capnp.pyi"
    content = stub_file.read_text()

    # Find Client section
    client_match = re.search(
        r"class IdentifiableClient\(_DynamicCapabilityClient\):(.*?)(?=\n\n|\Z)", content, re.DOTALL
    )
    assert client_match, "IdentifiableClient class not found"
    client_content = client_match.group(1)

    # Find InfoResult in Client
    result_match = re.search(
        r"class InfoResult\(Awaitable\[InfoResult\], Protocol\):(.*?)(?=\n\s+def|\Z)", client_content, re.DOTALL
    )
    assert result_match, "InfoResult class not found in IdentifiableClient"
    result_content = result_match.group(1)

    # Check nested field
    assert "nested: NestedReader" in result_content
    assert "NestedBuilder" not in result_content, "Client result should not reference Builder"


def test_server_result_uses_builder_and_reader(basic_stubs):
    """Test that server result protocols use Builder | Reader types."""
    stub_file = basic_stubs / "struct_return_capnp.pyi"
    content = stub_file.read_text()

    # Find Server section
    server_match = re.search(
        r"class Server\(_DynamicCapabilityServer\):(.*?)(?=\n\s+class IdentifiableClient)", content, re.DOTALL
    )
    assert server_match, "Server class not found"
    server_content = server_match.group(1)

    # Find InfoResult in Server
    result_match = re.search(
        r"class InfoResult\(Awaitable\[InfoResult\], Protocol\):(.*?)(?=\n\s+class)", server_content, re.DOTALL
    )
    assert result_match, "InfoResult class not found in Server"
    result_content = result_match.group(1)

    # Check nested field
    assert "nested: NestedBuilder | NestedReader" in result_content


def test_server_named_tuple_has_nested_field(basic_stubs):
    """Test that server NamedTuple result has nested struct field."""
    stub_file = basic_stubs / "struct_return_capnp.pyi"
    content = stub_file.read_text()

    import re

    # Find InfoResultTuple in Server
    # It might be defined inside Server or at module level depending on implementation
    # In the generated file it was inside Server

    # Find Server section
    server_match = re.search(
        r"class Server\(_DynamicCapabilityServer\):(.*?)(?=\n\s+class IdentifiableClient)", content, re.DOTALL
    )
    assert server_match, "Server class not found"
    server_content = server_match.group(1)

    # Find InfoResultTuple
    tuple_match = re.search(r"class InfoResultTuple\(NamedTuple\):(.*?)(?=\n\s+class)", server_content, re.DOTALL)
    assert tuple_match, "InfoResultTuple class not found in Server"
    tuple_content = tuple_match.group(1)

    # Check nested field
    assert "nested: NestedBuilder | NestedReader" in tuple_content
