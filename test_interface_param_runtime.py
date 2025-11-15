#!/usr/bin/env python3
"""Runtime test to verify what types can be passed for interface parameters."""
import capnp

capnp.remove_import_hook()
calculator_capnp = capnp.load("tests/schemas/examples/calculator/calculator.capnp")

class ValueImpl(calculator_capnp.Calculator.Value.Server):
    def __init__(self, value):
        self._value = value
    def read_context(self, context):
        context.results.value = self._value

# Test 1: Server
print("Test 1: Server implementation")
try:
    value_server = ValueImpl(42.0)
    expr = calculator_capnp.Calculator.Expression.new_message()
    expr.previousResult = value_server
    print("✓ SUCCESS: Can assign Server")
    print(f"  Type: {type(value_server).__name__}, Bases: {[b.__name__ for b in value_server.__class__.__bases__]}")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test 2: Client
print("\nTest 2: Client")
try:
    value_client = calculator_capnp.Calculator.Value._new_client(ValueImpl(99.0))
    expr = calculator_capnp.Calculator.Expression.new_message()
    expr.previousResult = value_client
    print("✓ SUCCESS: Can assign Client")
    print(f"  Type: {type(value_client).__name__}, Bases: {[b.__name__ for b in value_client.__class__.__bases__]}")
except Exception as e:
    print(f"✗ FAILED: {e}")

print("\n" + "="*70)
print("CONCLUSION: Both Server and Client can be assigned to interface fields")
print("Type hint should be: ValueClient | Value.Server")
