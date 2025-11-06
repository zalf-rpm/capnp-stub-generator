"""Experiment with different ways to handle direct struct returns."""

import asyncio
import sys
from pathlib import Path

import capnp
import pytest

TESTS_DIR = Path(__file__).parent


@pytest.fixture(scope="module")
def generate_stubs(tmp_path_factory):
    """Generate stubs for struct_return.capnp"""
    from capnp_stub_generator.cli import main

    schema_path = TESTS_DIR / "schemas" / "struct_return.capnp"
    output_dir = tmp_path_factory.mktemp("direct_return_stubs")

    main(["-p", str(schema_path), "-o", str(output_dir)])

    sys.path.insert(0, str(output_dir))

    yield output_dir

    if str(output_dir) in sys.path:
        sys.path.remove(str(output_dir))


def test_return_builder_object(generate_stubs):
    """Test returning values as a tuple."""

    import struct_return_capnp

    class IdentifiableImpl(struct_return_capnp.Identifiable.Server):
        async def info(self, _context, **kwargs):
            # Set fields on _context.results
            _context.results.id = "test-id"
            _context.results.name = "test-name"
            _context.results.description = "test-desc"

            # Return values as tuple
            return _context.results.id, _context.results.name, _context.results.description

    async def test():
        server_impl = IdentifiableImpl()
        client = struct_return_capnp.Identifiable._new_client(server_impl)

        try:
            result = await client.info()
            print(f"✅ Result: id={result.id}, name={result.name}")
            return True
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    result = asyncio.run(capnp.run(test()))
    print(f"Test result: {result}")


def test_return_as_reader(generate_stubs):
    """Test returning values as a tuple."""

    import struct_return_capnp

    class IdentifiableImpl(struct_return_capnp.Identifiable.Server):
        async def info(self, _context, **kwargs):
            # Set fields
            _context.results.id = "test-id"
            _context.results.name = "test-name"
            _context.results.description = "test-desc"

            # Return values as tuple
            return _context.results.id, _context.results.name, _context.results.description

    async def test():
        server_impl = IdentifiableImpl()
        client = struct_return_capnp.Identifiable._new_client(server_impl)

        try:
            result = await client.info()
            print(f"✅ Result: id={result.id}, name={result.name}")
            return True
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    result = asyncio.run(capnp.run(test()))
    print(f"Test result: {result}")


def test_check_new_client_signature(generate_stubs):
    """Check what _new_client() looks like in the stubs."""

    stub_file = generate_stubs / "struct_return_capnp.pyi"
    content = stub_file.read_text()

    print("\n" + "=" * 70)
    print("CHECKING _new_client() SIGNATURE")
    print("=" * 70)

    import re

    # Find Identifiable class
    match = re.search(r"class Identifiable.*?(?=\nclass |\Z)", content, re.DOTALL)
    if match:
        identifiable = match.group(0)

        # Look for _new_client
        if "_new_client" in identifiable:
            print("✅ _new_client found in Identifiable")

            # Extract the signature
            new_client_match = re.search(r"(def _new_client.*?)(?=\n    def |\n    class )", identifiable, re.DOTALL)
            if new_client_match:
                print(f"\nSignature:\n{new_client_match.group(1)}")
            else:
                print("Could not extract signature")
        else:
            print("❌ _new_client NOT found in Identifiable")
            print("\nSearching for _new_client anywhere in file...")
            if "_new_client" in content:
                print("Found _new_client elsewhere")
                matches = re.findall(r".{50}_new_client.{50}", content)
                for m in matches[:3]:
                    print(f"  {m}")
            else:
                print("❌ _new_client not in stub file at all!")

    print("=" * 70)


def test_what_is_context_results_type(generate_stubs):
    """Check the actual type of _context.results at runtime."""

    import struct_return_capnp

    class IdentifiableImpl(struct_return_capnp.Identifiable.Server):
        async def info(self, _context, **kwargs):
            print(f"\n_context type: {type(_context)}")
            print(f"_context.results type: {type(_context.results)}")
            print(f"_context.results.__class__.__name__: {_context.results.__class__.__name__}")

            # Check what attributes it has
            attrs = [x for x in dir(_context.results) if not x.startswith("_")]
            print(f"\n_context.results attributes: {attrs[:20]}")

            # Check if it has our fields
            print(f"\nHas 'id': {hasattr(_context.results, 'id')}")
            print(f"Has 'name': {hasattr(_context.results, 'name')}")
            print(f"Has 'as_reader': {hasattr(_context.results, 'as_reader')}")

            # Set the fields
            _context.results.id = "test-id"
            _context.results.name = "test-name"
            _context.results.description = "test-desc"

            return _context.results.id, _context.results.name, _context.results.description

    async def test():
        server_impl = IdentifiableImpl()
        client = struct_return_capnp.Identifiable._new_client(server_impl)

        try:
            result = await client.info()
            print(f"\n✅ Success! Result type: {type(result)}")
            print(f"Result.id: {result.id}")
            return True
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            return False

    result = asyncio.run(capnp.run(test()))
    assert result
