"""Test suite for _new_client method parameter types using correct module aliases.

This validates that _new_client methods use proper Protocol module aliases
(e.g., _HolderModule.Server, _IdentifiableModule.Server) instead of
user-facing type names (e.g., Holder.Server, Identifiable.Server).
"""

from __future__ import annotations


def test_new_client_uses_module_aliases_for_current_interface(generate_calculator_stubs):
    """Test that _new_client uses module alias for the current interface's Server type."""
    stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Value._new_client should accept _ValueModule.Server, not Value.Server (single line)
    assert "def _new_client(cls, server: _CalculatorModule._ValueModule.Server)" in content, (
        "_new_client should use _ValueModule.Server"
    )

    # Function._new_client should accept _FunctionModule.Server, not Function.Server (single line)
    assert "def _new_client(cls, server: _CalculatorModule._FunctionModule.Server)" in content, (
        "_new_client should use _FunctionModule.Server"
    )

    # Calculator._new_client should accept _CalculatorModule.Server, not Calculator.Server
    assert "def _new_client(cls, server: _CalculatorModule.Server) -> _CalculatorModule.CalculatorClient:" in content, (
        "_new_client should use _CalculatorModule.Server"
    )


def test_new_client_uses_module_aliases_for_inherited_interfaces(zalfmas_stubs):
    """Test that _new_client uses module aliases for inherited interface Server types."""
    # Use pre-generated zalfmas stubs which include common.capnp with interface inheritance
    stub_file = zalfmas_stubs / "common_capnp.pyi"
    content = stub_file.read_text()

    # Identifiable._new_client should accept _IdentifiableModule.Server
    assert (
        "def _new_client(cls, server: _IdentifiableModule.Server) -> _IdentifiableModule.IdentifiableClient:" in content
    ), "Identifiable._new_client should use _IdentifiableModule.Server"

    # Holder._new_client should accept _HolderModule.Server
    assert "def _new_client(cls, server: _HolderModule.Server) -> _HolderModule.HolderClient:" in content, (
        "Holder._new_client should use _HolderModule.Server"
    )

    # IdentifiableHolder extends both Identifiable and Holder
    # Its _new_client should accept:
    # 1. _IdentifiableHolderModule.Server (its own)
    # 2. _HolderModule.Server (inherited)
    # 3. _IdentifiableModule.Server (inherited)
    # All using module aliases, NOT Holder.Server or Identifiable.Server
    assert "_new_client(" in content
    # Check that the method accepts module alias types
    assert (
        "cls, server: _IdentifiableHolderModule.Server | _HolderModule.Server | _IdentifiableModule.Server" in content
    ), "IdentifiableHolder._new_client should accept _HolderModule.Server and _IdentifiableModule.Server"

    # Ensure it does NOT use the old incorrect naming
    # (checking that we don't have both old and new - only new should exist)
    lines = content.split("\n")
    new_client_lines = [line for line in lines if "_new_client" in line and "cls, server:" in line]

    for line in new_client_lines:
        # None of the parameter types should use user-facing names without proper module prefix
        # The pattern "Holder.Server" without "_HolderModule" is incorrect
        # The pattern "Identifiable.Server" without "_IdentifiableModule" is incorrect
        if "Holder.Server" in line:
            assert "_HolderModule.Server" in line, (
                f"Found incorrect Holder.Server (should be _HolderModule.Server) in: {line}"
            )
        if "Identifiable.Server" in line:
            assert "_IdentifiableModule.Server" in line, (
                f"Found incorrect Identifiable.Server (should be _IdentifiableModule.Server) in: {line}"
            )


def test_new_client_nested_interface_uses_full_module_path(basic_stubs):
    """Test that nested interface _new_client methods use full module path."""
    stub_file = basic_stubs / "channel_capnp.pyi"
    content = stub_file.read_text()

    # Channel.Reader._new_client should use _ChannelModule._ReaderModule.Server
    # NOT just _ReaderModule.Server (which would be undefined) (single line)
    assert "def _new_client(cls, server: _ChannelModule._ReaderModule.Server)" in content, (
        "Nested interface _new_client should use full module path"
    )

    # Channel.Writer._new_client should use _ChannelModule._WriterModule.Server (single line)
    assert "def _new_client(cls, server: _ChannelModule._WriterModule.Server)" in content, (
        "Nested interface _new_client should use full module path"
    )


def test_new_client_return_types_use_client_aliases(zalfmas_stubs):
    """Test that _new_client return types use proper Client type aliases."""
    stub_file = zalfmas_stubs / "common_capnp.pyi"
    content = stub_file.read_text()

    # _new_client should return Client types
    assert "_IdentifiableModule.IdentifiableClient:" in content
    assert "_HolderModule.HolderClient:" in content
    assert "_IdentifiableHolderModule.IdentifiableHolderClient:" in content


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-xvs"])
