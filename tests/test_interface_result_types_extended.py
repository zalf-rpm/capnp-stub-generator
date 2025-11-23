"""Tests for interface result types in generated stubs."""

import re


def test_registry_result_type(zalfmas_stubs):
    """Test that RegistryResult has proper interface type, not Any."""
    # The Admin interface is in registry.capnp
    stub_file = zalfmas_stubs / "registry_capnp.pyi"
    content = stub_file.read_text()

    # Find AdminClient
    # AdminClient is inside _AdminInterfaceModule.
    # It ends before "Admin: _AdminInterfaceModule" which is at the end of _AdminInterfaceModule block (actually Admin: _AdminInterfaceModule is after _AdminInterfaceModule class)

    # Let's capture until the end of the file or a clear marker
    client_match = re.search(
        r"class AdminClient\(_IdentifiableInterfaceModule.IdentifiableClient\):(.*?)(?=Admin: _AdminInterfaceModule|\Z)",
        content,
        re.DOTALL,
    )
    assert client_match, "AdminClient class not found"
    client_content = client_match.group(1)

    # Find RegistryResult in Client
    # Use a simpler regex that just finds the class start and captures until the next dedented line or end of block
    # Since we are inside an indented block (AdminClient), the next dedented line would be the end of AdminClient
    # But inside AdminClient, methods are indented.

    # Let's just search for the class definition and capture a few lines
    result_match = re.search(
        r"class RegistryResult\(Awaitable\[RegistryResult\], Protocol\):(.*?)(?=\n\s+def|\n\s+class|\Z)",
        client_content,
        re.DOTALL,
    )

    if not result_match:
        # Fallback debugging
        print(f"Client content:\n{client_content}")

    assert result_match, "RegistryResult class not found in AdminClient"
    result_content = result_match.group(1)

    # Check registry field
    # Should be: registry: _RegistryInterfaceModule.RegistryClient
    # Currently failing as: registry: Any
    assert "registry: _RegistryInterfaceModule.RegistryClient" in result_content, (
        f"Expected RegistryClient, got: {result_content}"
    )


def test_server_registry_result_type(zalfmas_stubs):
    """Test that Server RegistryResult has proper interface type."""
    stub_file = zalfmas_stubs / "registry_capnp.pyi"
    content = stub_file.read_text()

    # Find Server
    server_match = re.search(
        r"class Server\(_IdentifiableInterfaceModule.Server\):(.*?)(?=\n\s+class AdminClient)", content, re.DOTALL
    )
    assert server_match, "Server class not found"
    server_content = server_match.group(1)

    # Find RegistryResult in Server
    # Now inherits from _DynamicStructBuilder
    result_match = re.search(
        r"class RegistryResult\(_DynamicStructBuilder\):(.*?)(?=\n\s+class)", server_content, re.DOTALL
    )
    assert result_match, "RegistryResult class not found in Server"
    result_content = result_match.group(1)

    # Check registry field
    # For server, it should be a property with getter and setter
    # Getter returns Server | Client (or just Server/Client depending on logic)
    # Setter accepts Server | Client

    # We expect property definition
    assert "@property" in result_content
    assert "def registry(self) ->" in result_content
    assert "@registry.setter" in result_content

    # Check types in getter/setter
    # The exact order might vary, so check for presence of types
    assert "_RegistryInterfaceModule.Server" in result_content
    assert "_RegistryInterfaceModule.RegistryClient" in result_content
