"""Tests for imported type aliases in generated stubs."""

import re


def test_imported_type_aliases_used(zalfmas_stubs):
    """Test that imported type aliases are used in method signatures."""
    # Check registry_capnp.pyi
    # It imports IdInformation from common_capnp
    # Admin.addCategory takes IdInformation

    stub_file = zalfmas_stubs / "registry_capnp.pyi"
    content = stub_file.read_text()

    # Find AdminClient
    client_match = re.search(
        r"class AdminClient\(_IdentifiableInterfaceModule.IdentifiableClient\):(.*?)(?=\nclass _|\Z)",
        content,
        re.DOTALL,
    )
    assert client_match, "AdminClient class not found"
    client_content = client_match.group(1)

    # Find addCategory method
    # Should use IdInformationReader or IdInformationBuilder (or dict)
    # Currently it might be using _IdInformationStructModule.Reader/Builder

    # We expect: category: IdInformationReader | dict[str, Any] | None = None
    # Or: category: IdInformationBuilder | dict[str, Any] | None = None

    # Let's check what we have
    method_match = re.search(r"def addCategory\(self, category: (.*?),", client_content)
    assert method_match, "addCategory method not found"
    params = method_match.group(1)

    # Check for alias usage
    # Note: IdInformation is imported as _IdInformationStructModule in the file usually
    # But we want to see IdInformationReader/Builder if possible

    # If the alias is used, it should be imported.
    # Check imports
    assert "from .common_capnp import" in content

    # If we successfully used the alias, we should see it in the file content
    # But wait, did we import the alias in the generated file?
    # Yes, we modified register_import to import aliases.

    # Let's check if IdInformationReader is imported
    assert "IdInformationReader" in content, "IdInformationReader should be imported/used"

    # Check usage in addCategory
    # It might be _IdInformationStructModule | dict... because for Client methods we accept Reader/Builder/Dict
    # But for specific types we prefer aliases.

    # Actually, for client methods, we usually take `Reader | Builder | dict`.
    # If we use aliases, it should be `IdInformationReader | IdInformationBuilder | dict`.

    # Let's check the generated signature
    print(f"addCategory params: {params}")

    # We want to avoid `_IdInformationStructModule.Reader`
    assert "_IdInformationStructModule.Reader" not in params, "Should use IdInformationReader alias"
    assert "IdInformationReader" in params, "Should use IdInformationReader alias"


def test_imported_return_type_aliases(zalfmas_stubs):
    """Test that imported type aliases are used in return types."""
    # Check registry_capnp.pyi
    # Admin.removeCategory returns List(Identifiable)
    # Identifiable is imported from common_capnp

    stub_file = zalfmas_stubs / "registry_capnp.pyi"
    content = stub_file.read_text()

    # Find AdminClient
    client_match = re.search(
        r"class AdminClient\(_IdentifiableInterfaceModule.IdentifiableClient\):(.*?)(?=\nclass _|\Z)",
        content,
        re.DOTALL,
    )
    assert client_match, "AdminClient class not found"
    client_content = client_match.group(1)

    # Find RemovecategoryResult in AdminClient
    result_match = re.search(
        r"class RemovecategoryResult\(Awaitable\[RemovecategoryResult\], Protocol\):(.*?)(?=\n\s+class|\n\s+def|\Z)",
        client_content,
        re.DOTALL,
    )
    assert result_match
    result_content = result_match.group(1)

    # Check removedObjects
    # Should be IdentifiableClientListReader (alias for _IdentifiableClientList.Reader)
    # IdentifiableClient is imported from common_capnp

    # We expect: removedObjects: IdentifiableClientListReader

    assert "removedObjects: IdentifiableClientListReader" in result_content, (
        f"Expected removedObjects: IdentifiableClientListReader, got: {result_content}"
    )
