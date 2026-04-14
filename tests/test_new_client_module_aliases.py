"""Test suite for _new_client method parameter types using correct helper imports.

This validates that runtime stubs use private helper-module imports for
typing-only client return types rather than re-exporting public top-level
aliases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def test_new_client_uses_module_aliases_for_current_interface(generate_calculator_stubs: Path) -> None:
    """Test that _new_client uses module alias for the current interface's Server type."""
    stub_file = generate_calculator_stubs / "calculator_capnp" / "__init__.pyi"
    content = stub_file.read_text()

    # Value._new_client should accept _DynamicCapabilityServer
    assert "def _new_client(self, server: _DynamicCapabilityServer)" in content, (
        "_new_client should use _DynamicCapabilityServer"
    )

    # Function._new_client should accept _DynamicCapabilityServer
    assert "def _new_client(self, server: _DynamicCapabilityServer)" in content, (
        "_new_client should use _DynamicCapabilityServer"
    )

    # Calculator._new_client should return the private clients helper type
    assert "def _new_client(self, server: _DynamicCapabilityServer) -> _clients.CalculatorClient:" in content, (
        "_new_client should use the private clients helper return type"
    )


def test_new_client_uses_module_aliases_for_inherited_interfaces(zalfmas_stubs: Path) -> None:
    """Test that _new_client uses module aliases for inherited interface Server types."""
    # Use pre-generated zalfmas stubs which include common.capnp with interface inheritance
    stub_file = zalfmas_stubs / "mas/schema/common/common_capnp" / "__init__.pyi"
    content = stub_file.read_text()

    # Identifiable._new_client should return the private clients helper type
    assert "def _new_client(self, server: _DynamicCapabilityServer) -> _clients.IdentifiableClient:" in content, (
        "Identifiable._new_client should use the private clients helper return type"
    )

    # Holder._new_client should return the private clients helper type
    assert "def _new_client(self, server: _DynamicCapabilityServer) -> _clients.HolderClient:" in content, (
        "Holder._new_client should use the private clients helper return type"
    )

    # IdentifiableHolder extends both Identifiable and Holder
    # Its _new_client should accept _DynamicCapabilityServer
    assert "_new_client(" in content
    # Check that the method accepts module alias types
    assert "self, server: _DynamicCapabilityServer" in content, (
        "IdentifiableHolder._new_client should accept _DynamicCapabilityServer"
    )

    # Ensure it does NOT use the old incorrect naming
    # (checking that we don't have both old and new - only new should exist)
    lines = content.split("\n")
    new_client_lines = [line for line in lines if "_new_client" in line and "self, server:" in line]

    for line in new_client_lines:
        # None of the parameter types should use user-facing names without proper module prefix
        # The pattern "Holder.Server" without "_HolderInterfaceModule" is incorrect
        # The pattern "Identifiable.Server" without "_IdentifiableInterfaceModule" is incorrect
        if "Holder.Server" in line:
            assert "_HolderInterfaceModule.Server" in line, (
                f"Found incorrect Holder.Server (should be _HolderInterfaceModule.Server) in: {line}"
            )
        if "Identifiable.Server" in line:
            assert "_IdentifiableInterfaceModule.Server" in line, (
                f"Found incorrect Identifiable.Server (should be _IdentifiableInterfaceModule.Server) in: {line}"
            )


def test_new_client_nested_interface_uses_full_module_path(basic_stubs: Path) -> None:
    """Test that nested interface _new_client methods use full module path."""
    stub_file = basic_stubs / "channel_capnp" / "__init__.pyi"
    content = stub_file.read_text()

    # Channel.Reader._new_client should use _DynamicCapabilityServer
    assert "def _new_client(self, server: _DynamicCapabilityServer)" in content, (
        "Nested interface _new_client should use _DynamicCapabilityServer"
    )

    # Channel.Writer._new_client should use _DynamicCapabilityServer
    assert "def _new_client(self, server: _DynamicCapabilityServer)" in content, (
        "Nested interface _new_client should use _DynamicCapabilityServer"
    )


def test_new_client_return_types_use_private_client_imports(zalfmas_stubs: Path) -> None:
    """Test that _new_client return types use private client helper imports."""
    stub_file = zalfmas_stubs / "mas/schema/common/common_capnp" / "__init__.pyi"
    content = stub_file.read_text()

    # _new_client should return private helper-module client types
    assert "-> _clients.IdentifiableClient:" in content
    assert "-> _clients.HolderClient:" in content
    assert "-> _clients.IdentifiableHolderClient:" in content

    # The runtime stub should not expose those helpers as top-level aliases.
    assert "IdentifiableClient = _clients.IdentifiableClient" not in content
    assert "HolderClient = _clients.HolderClient" not in content
    assert "IdentifiableHolderClient = _clients.IdentifiableHolderClient" not in content


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-xvs"])
