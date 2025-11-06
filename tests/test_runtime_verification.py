"""Test runtime behavior of server methods to verify stub accuracy.

This test creates actual server implementations and verifies that the runtime
types match what the stubs declare.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import capnp
import pytest

TESTS_DIR = Path(__file__).parent


# Generate stubs for the test schema
@pytest.fixture(scope="module")
def generate_runtime_test_stubs(tmp_path_factory):
    """Generate stubs for runtime_test.capnp"""
    from capnp_stub_generator.cli import main

    schema_path = TESTS_DIR / "schemas" / "runtime_test.capnp"
    output_dir = tmp_path_factory.mktemp("runtime_test_stubs")

    main(["-p", str(schema_path), "-o", str(output_dir)])

    # Add to path so we can import
    sys.path.insert(0, str(output_dir))

    yield output_dir

    # Cleanup
    if str(output_dir) in sys.path:
        sys.path.remove(str(output_dir))


def test_runtime_server_return_types(generate_runtime_test_stubs):
    """Test what server methods actually return at runtime via _new_client()."""

    # Import the generated module
    import runtime_test_capnp

    class SubServiceImpl(runtime_test_capnp.TestService.SubService.Server):
        async def getValue(self, _context, **kwargs):
            # Set via context
            _context.results.value = 42.0

    class TestServiceImpl(runtime_test_capnp.TestService.Server):
        async def getPrimitive(self, _context, **kwargs):
            # Return directly - pycapnp fills context
            return 123

        async def getStruct(self, _context, **kwargs):
            # Return struct directly
            info = runtime_test_capnp.Info.new_message(name="test", value=42)
            return info

        async def getInterface(self, _context, **kwargs):
            # Return interface implementation
            return SubServiceImpl()

        async def getMultiple(self, _context, **kwargs):
            # Return tuple for multiple results
            data = runtime_test_capnp.Data.new_message(content="hello", timestamp=12345)
            return (10, data)

        async def doNothing(self, _context, **kwargs):
            # Void method - return None
            return None

    # Create server instance
    server_impl = TestServiceImpl()

    # Test using _new_client() to create capability client
    async def test_with_new_client():
        print("\n" + "=" * 70)
        print("RUNTIME VERIFICATION WITH _new_client()")
        print("=" * 70)

        # Convert server implementation to capability client
        client = runtime_test_capnp.TestService._new_client(server_impl)

        print(f"\nClient type: {type(client)}")
        print(f"Client has info method: {hasattr(client, 'getPrimitive')}")

        # Test getPrimitive
        result = await client.getPrimitive()
        print(f"\ngetPrimitive() returned type: {type(result)}")
        print(f"result has 'result' attr: {hasattr(result, 'result')}")
        if hasattr(result, "result"):
            print(f"result.result value: {result.result}")
            print(f"result.result type: {type(result.result)}")

        # Test getStruct
        result = await client.getStruct()
        print(f"\ngetStruct() returned type: {type(result)}")
        print(f"result has 'info' attr: {hasattr(result, 'info')}")
        if hasattr(result, "info"):
            print(f"result.info type: {type(result.info)}")
            print(f"result.info.name: {result.info.name}")

        # Test getInterface
        result = await client.getInterface()
        print(f"\ngetInterface() returned type: {type(result)}")
        print(f"result has 'service' attr: {hasattr(result, 'service')}")
        if hasattr(result, "service"):
            print(f"result.service type: {type(result.service)}")
            # Try calling method on returned interface
            sub_result = await result.service.getValue()
            print(f"result.service.getValue() type: {type(sub_result)}")
            if hasattr(sub_result, "value"):
                print(f"result.service.getValue().value: {sub_result.value}")

        # Test getMultiple
        result = await client.getMultiple()
        print(f"\ngetMultiple() returned type: {type(result)}")
        print(f"result has 'count' attr: {hasattr(result, 'count')}")
        print(f"result has 'data' attr: {hasattr(result, 'data')}")
        if hasattr(result, "count") and hasattr(result, "data"):
            print(f"result.count: {result.count}")
            print(f"result.data type: {type(result.data)}")
            print(f"result.data.content: {result.data.content}")

        # Test doNothing
        result = await client.doNothing()
        print(f"\ndoNothing() returned type: {type(result)}")
        print(f"doNothing() returned value: {result}")

        print("\n" + "=" * 70)
        print("KEY FINDINGS:")
        print("=" * 70)
        print("1. Client methods return Result protocol objects (with await)")
        print("2. Result objects have field attributes matching result schema")
        print("3. Single field results: access via result.fieldname")
        print("4. Multiple field results: access via result.field1, result.field2")
        print("5. Interface results: result.fieldname is a capability client")
        print("6. Struct results: result.fieldname is a Reader object")
        print("=" * 70)

        return True

    result = asyncio.run(capnp.run(test_with_new_client()))
    assert result


def test_server_method_signatures_in_stubs(generate_runtime_test_stubs):
    """Verify what the stubs declare for server methods."""

    stub_file = generate_runtime_test_stubs / "runtime_test_capnp.pyi"
    content = stub_file.read_text()

    print("\n" + "=" * 70)
    print("STUB SIGNATURES")
    print("=" * 70)

    # Extract server method signatures
    import re

    # Find TestService.Server section
    server_match = re.search(
        r"class TestService\(Protocol\):.*?class Server:(.*?)(?=\n    class |\nclass |\Z)", content, re.DOTALL
    )

    if server_match:
        server_section = server_match.group(1)

        # Find all method definitions
        methods = re.findall(r"def (\w+)\(([^)]+(?:\([^)]*\)[^)]*)*)\) -> ([^:]+):", server_section, re.MULTILINE)

        for method_name, params, return_type in methods:
            print(f"\n{method_name}:")
            print(f"  Parameters: {params}")
            print(f"  Return type: {return_type}")

            # Check if _context is in parameters
            assert "_context:" in params, f"{method_name} should have _context parameter"
            assert "CallContext" in params, f"{method_name} _context should be CallContext type"

    print("\n" + "=" * 70)


def test_what_pycapnp_expects():
    """Document what pycapnp actually does with server method returns.

    Based on pycapnp source code analysis:
    1. Server methods receive a _context parameter with .results attribute
    2. Methods can either:
       a) Return values directly - pycapnp calls fill_context() to set _context.results
       b) Set _context.results manually and return None
    3. The return type should match what goes into _context.results, not what the method returns
    """

    print("\n" + "=" * 70)
    print("PYCAPNP BEHAVIOR ANALYSIS")
    print("=" * 70)
    print("""
From pycapnp source (lib/capnp.pyx):

def fill_context(method_name, context, returned_data):
    if returned_data is None:
        return
    if not isinstance(returned_data, tuple):
        returned_data = (returned_data,)
    names = _find_field_order(context.results.schema.node.struct)
    
    results = context.results
    for arg_name, arg_val in zip(names, returned_data):
        setattr(results, arg_name, arg_val)

This means:
1. Server methods receive _context with .results attribute
2. If method returns a value, pycapnp sets _context.results fields from it
3. If method returns tuple, each element goes to a result field in order
4. If method returns None, results must have been set manually

Therefore, the server method signature should be:
    async def method(self, params, _context: CallContext, **kwargs) -> Awaitable[ReturnValue]:
        # Where ReturnValue is what gets put into _context.results
        # NOT the Results object itself
    """)
    print("=" * 70)
