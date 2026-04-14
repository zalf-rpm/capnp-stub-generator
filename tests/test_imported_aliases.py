"""Tests for imported type aliases in generated stubs."""

import re
from pathlib import Path


def test_imported_type_aliases_used(zalfmas_stubs: Path) -> None:
    """Test that imported type aliases are used in method signatures."""
    # Check registry_capnp.pyi
    # It imports IdInformation from common_capnp
    # Admin.addCategory takes IdInformation

    stub_file = zalfmas_stubs / "mas/schema/registry/registry_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    # Check that AdminClient exists
    assert "class AdminClient(IdentifiableClient):" in content

    # Check that addCategory is defined with proper alias
    assert "def addCategory(" in content

    # Check imports - IdInformationBuilder and IdInformationReader should be imported
    assert "IdInformationBuilder" in content
    assert "IdInformationReader" in content

    # Check that the method uses the alias (multi-line signature)
    # The signature spans multiple lines, so search in content
    assert "category: IdInformationBuilder | IdInformationReader" in content, (
        "addCategory should use IdInformationBuilder/Reader aliases"
    )


def test_imported_return_type_aliases(zalfmas_stubs: Path) -> None:
    """Test that imported type aliases are used in flattened top-level result helpers."""
    # Check registry_capnp.pyi
    # Admin.removeCategory returns List(Identifiable)
    # Identifiable is imported from common_capnp

    stub_file = zalfmas_stubs / "mas/schema/registry/registry_capnp" / "types" / "_all.pyi"
    content = stub_file.read_text()

    result_match = re.search(
        r"class RemovecategoryResult\(Awaitable\[RemovecategoryResult\], Protocol\):(.*?)(?=\nclass |\Z)",
        content,
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
