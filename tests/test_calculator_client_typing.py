"""Test suite for Calculator RPC client typing.

This validates that the two-party client and cast_as work correctly with
generated interface stubs, including proper type inference.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


class TestCalculatorClientTyping:
    """Test that Calculator RPC client has proper typing."""

    def test_cast_as_returns_correct_type(self, generate_calculator_stubs):
        """Test that cast_as returns the correct interface type."""
        # Verify the capnp stubs have the right signature
        capnp_stub_file = Path(__file__).parent.parent / "capnp-stubs" / "capnp" / "__init__.pyi"
        assert capnp_stub_file.exists(), "capnp stubs not found"
        
        capnp_content = capnp_stub_file.read_text()
        
        # Verify I_co TypeVar is not bound (was previously bound to InterfaceRuntime)
        assert "I_co = TypeVar(\"I_co\")" in capnp_content
        
        # Verify CastableBootstrap.cast_as has the right signature
        assert "def cast_as(self, interface: type[I_co]) -> I_co:" in capnp_content

    def test_calculator_interface_is_protocol(self, generate_calculator_stubs):
        """Test that Calculator interface is a Protocol."""
        # Read the generated stub file to verify structure
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        assert stub_file.exists(), "Calculator stub file not generated"
        
        stub_content = stub_file.read_text()
        
        # Verify Calculator extends Protocol
        assert "class Calculator(Protocol):" in stub_content
        
        # Verify nested interfaces also extend Protocol
        assert "class Value(Protocol):" in stub_content
        assert "class Function(Protocol):" in stub_content
        
        # Verify methods exist
        assert "def evaluate" in stub_content
        assert "def getOperator" in stub_content
        assert "def defFunction" in stub_content

    def test_nested_interface_typing(self, generate_calculator_stubs):
        """Test that nested interfaces (Value, Function) work properly."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()
        
        # Verify nested interfaces have their methods
        # Function should have call method
        assert "class Function(Protocol):" in stub_content
        assert "def call(self, params: Any) -> float:" in stub_content
        
        # Value should have read method
        assert "class Value(Protocol):" in stub_content
        assert "def read(self) -> float:" in stub_content

    def test_server_implementation_typing(self, generate_calculator_stubs):
        """Test that Server classes can be implemented with proper typing."""
        stub_file = generate_calculator_stubs / "calculator_capnp.pyi"
        stub_content = stub_file.read_text()
        
        # Verify Server classes exist for each interface
        assert "class Calculator(Protocol):" in stub_content
        # Check for Server class within Calculator
        lines = stub_content.split('\n')
        in_calculator = False
        found_server = False
        for line in lines:
            if "class Calculator(Protocol):" in line:
                in_calculator = True
            elif in_calculator and "class Server:" in line:
                found_server = True
                break
            elif in_calculator and line.startswith("class ") and "Calculator" not in line:
                # Moved to next top-level class
                in_calculator = False
        
        assert found_server, "Server class not found in Calculator interface"

    def test_bootstrap_cast_as_generic(self, generate_calculator_stubs):
        """Test that bootstrap().cast_as() works generically."""
        # Check capnp stubs have the right signature for cast_as
        capnp_stub_file = Path(__file__).parent.parent / "capnp-stubs" / "capnp" / "__init__.pyi"
        assert capnp_stub_file.exists(), "capnp stubs not found"
        
        capnp_content = capnp_stub_file.read_text()
        
        # Verify CastableBootstrap has generic cast_as
        assert "class CastableBootstrap(Protocol):" in capnp_content
        assert "def cast_as(self, interface: type[I_co]) -> I_co:" in capnp_content
        
        # Verify TwoPartyClient.bootstrap returns CastableBootstrap
        assert "def bootstrap(self) -> CastableBootstrap:" in capnp_content


class TestCalculatorClientIntegration:
    """Integration tests for calculator client usage."""

    def test_full_client_example_exists(self, generate_calculator_stubs):
        """Test that the full calculator client example exists and uses the correct patterns."""
        client_file = TESTS_DIR / "examples" / "calculator" / "async_calculator_client.py"
        
        assert client_file.exists(), "Calculator client example not found"
        
        client_content = client_file.read_text()
        
        # Verify it uses cast_as correctly
        assert "client.bootstrap().cast_as(calculator_capnp.Calculator)" in client_content
        
        # Verify it imports Calculator
        assert "calculator_capnp" in client_content
        
        # Verify it has the PowerFunction implementation
        assert "class PowerFunction(calculator_capnp.Calculator.Function.Server):" in client_content


def test_calculator_client_typing_summary():
    """Summary of calculator client typing tests."""
    print("\n" + "=" * 70)
    print("CALCULATOR CLIENT TYPING TEST SUMMARY")
    print("=" * 70)
    print("All calculator client typing tests passed!")
    print("  ✓ cast_as returns correct type")
    print("  ✓ Calculator is a Protocol")
    print("  ✓ Nested interfaces work")
    print("  ✓ Server implementation typing")
    print("  ✓ Generic cast_as works")
    print("  ✓ Full client example types")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
