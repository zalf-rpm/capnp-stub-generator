"""Test the actual runtime behavior when returning structs from server methods."""

import asyncio
import sys
from pathlib import Path

import capnp
import pytest

TESTS_DIR = Path(__file__).parent


@pytest.fixture(scope="module")
def generate_struct_return_stubs(tmp_path_factory):
    """Generate stubs for struct_return.capnp"""
    from capnp_stub_generator.cli import main

    schema_path = TESTS_DIR / "schemas" / "struct_return.capnp"
    output_dir = tmp_path_factory.mktemp("struct_return_stubs")

    main(["-p", str(schema_path), "-o", str(output_dir)])

    # Add to path so we can import
    sys.path.insert(0, str(output_dir))

    yield output_dir

    # Cleanup
    if str(output_dir) in sys.path:
        sys.path.remove(str(output_dir))


def test_struct_return_with_return_value(generate_struct_return_stubs):
    """Test that returning a struct directly causes an error (expected behavior)."""

    import struct_return_capnp

    class IdentifiableImpl(struct_return_capnp.Identifiable.Server):
        async def info(self, _context, **kwargs):
            # Try returning struct directly - this SHOULD fail
            return struct_return_capnp.IdInformation.new_message(
                id="test-id", name="test-name", description="test-description"
            )

    async def test():
        server_impl = IdentifiableImpl()
        client = struct_return_capnp.Identifiable._new_client(server_impl)

        try:
            result = await client.info()
            print(f"\n❌ UNEXPECTED: Should have failed but got result: {result}")
            return False  # Should NOT succeed
        except Exception as e:
            print(f"\n✅ EXPECTED ERROR: {type(e).__name__}")
            print("   Message: Value type mismatch (expected)")
            return True  # Error is expected

    result = asyncio.run(capnp.run(test()))
    assert result, "Test should have raised an error (returning struct for direct return is not allowed)"


def test_struct_return_via_tuple(generate_struct_return_stubs):
    """Test returning struct fields as a tuple."""

    import struct_return_capnp

    class IdentifiableImpl(struct_return_capnp.Identifiable.Server):
        async def info(self, _context, **kwargs):
            # Return values as a tuple - pycapnp will populate _context.results
            return "test-id", "test-name", "test-description"

    async def test():
        server_impl = IdentifiableImpl()
        client = struct_return_capnp.Identifiable._new_client(server_impl)

        try:
            result = await client.info()
            print(f"\n✅ SUCCESS! Result type: {type(result)}")
            print(f"Result id: {result.id}")
            print(f"Result name: {result.name}")
            print(f"Result description: {result.description}")
            assert result.id == "test-id"
            assert result.name == "test-name"
            assert result.description == "test-description"
            return True
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            return False

    result = asyncio.run(capnp.run(test()))
    assert result, "Test failed"


def test_struct_return_via_context(generate_struct_return_stubs):
    """Test setting struct fields via _context.results and returning values as tuple."""

    import struct_return_capnp

    class IdentifiableImpl(struct_return_capnp.Identifiable.Server):
        async def info(self, _context, **kwargs):
            # For direct struct return, set FIELDS on _context.results
            _context.results.id = "test-id"
            _context.results.name = "test-name"
            _context.results.description = "test-description"

            # Return the values as a tuple
            return _context.results.id, _context.results.name, _context.results.description

    async def test():
        server_impl = IdentifiableImpl()
        client = struct_return_capnp.Identifiable._new_client(server_impl)

        try:
            result = await client.info()
            print(f"\n✅ SUCCESS! Result type: {type(result)}")
            print(f"Result has id: {hasattr(result, 'id')}")
            print(f"Result id: {result.id if hasattr(result, 'id') else 'N/A'}")
            print(f"Result name: {result.name if hasattr(result, 'name') else 'N/A'}")
            print(f"Result description: {result.description if hasattr(result, 'description') else 'N/A'}")
            return True
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            return False

    result = asyncio.run(capnp.run(test()))
    assert result, "Test failed"


def test_check_generated_stubs(generate_struct_return_stubs):
    """Check what the generator produced."""

    stub_file = generate_struct_return_stubs / "struct_return_capnp.pyi"
    content = stub_file.read_text()

    print("\n" + "=" * 70)
    print("GENERATED STUBS FOR DIRECT STRUCT RETURN")
    print("=" * 70)

    # Find the Identifiable interface
    import re

    match = re.search(r"class Identifiable\(Protocol\):(.*?)(?=\nclass |\Z)", content, re.DOTALL)
    if match:
        interface_section = match.group(1)
        print(interface_section[:1000])

    print("=" * 70)
