"""Tests for interface result types in generated stubs."""

import re
from pathlib import Path


def test_registry_result_type(zalfmas_stubs: Path) -> None:
    """Test that flattened RegistryResult has proper interface type, not Any."""
    # The Admin interface is in registry.capnp
    stub_file = zalfmas_stubs / "mas/schema/registry/registry_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    result_match = re.search(
        r"class RegistryResult\(Awaitable\[RegistryResult\], Protocol\):(.*?)(?=\nclass |\Z)",
        content,
        re.DOTALL,
    )

    assert result_match, "RegistryResult class not found"
    result_content = result_match.group(1)

    # Check registry field
    # Should be: registry: RegistryClient
    # Currently failing as: registry: Any
    assert "registry: RegistryClient" in result_content, f"Expected RegistryClient, got: {result_content}"


def test_server_registry_result_type(zalfmas_stubs: Path) -> None:
    """Test that flattened RegistryServerResult has proper interface type."""
    stub_file = zalfmas_stubs / "mas/schema/registry/registry_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    result_match = re.search(
        r"class RegistryServerResult\(_DynamicStructBuilder\):(.*?)(?=\nclass |\Z)",
        content,
        re.DOTALL,
    )
    assert result_match, "RegistryServerResult class not found"
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
    assert "RegistryClient" in result_content
