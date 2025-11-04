"""Tests for nested dict initialization in new_message().

This validates that new_message() accepts dict literals for nested struct fields,
allowing convenient nested initialization like:
    MyStruct.new_message(nestedField={"innerField": value})
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import run_pyright

TESTS_DIR = Path(__file__).parent


class TestNestedDictInitialization:
    """Test that new_message() accepts dicts for nested struct fields."""

    def test_simple_nested_struct(self, generate_core_stubs):
        """Test creating TestSturdyRef with dict for hostId field."""
        test_code = """
from _generated.dummy_capnp import TestSturdyRef

# Create SturdyRef with nested dict for hostId
ref = TestSturdyRef.new_message(
    hostId={"host": "example.com"}
)

# Should be able to read the nested field
host_id = ref.hostId
host_value: str = host_id.host
"""
        test_file = TESTS_DIR / "_test_nested_dict_simple.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"new_message with dict for nested struct should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_deeply_nested_dicts(self, generate_core_stubs):
        """Test creating structs with deeply nested dict initialization."""
        test_code = """
from _generated.dummy_capnp import TestSturdyRef

# The user's example from persistence_capnp
# vat={"address": {"host": hp.host, "port": hp.port}}
# For our TestSturdyRef, we have hostId with a single field

# Create with nested initialization
ref = TestSturdyRef.new_message(
    hostId={"host": "localhost"}
)

# Verify the type
host_name: str = ref.hostId.host
"""
        test_file = TESTS_DIR / "_test_nested_dict_deep.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"Deeply nested dict initialization should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_mixed_builder_and_dict(self, generate_core_stubs):
        """Test that both Builder instances and dicts work for nested fields."""
        test_code = """
from _generated.dummy_capnp import TestSturdyRef, TestSturdyRefHostId

# Method 1: Using Builder explicitly
host_builder = TestSturdyRefHostId.new_message(host="example.com")
ref1 = TestSturdyRef.new_message(hostId=host_builder)

# Method 2: Using dict (more convenient)
ref2 = TestSturdyRef.new_message(hostId={"host": "example.com"})

# Both should work and have the same type
host1: str = ref1.hostId.host
host2: str = ref2.hostId.host
"""
        test_file = TESTS_DIR / "_test_nested_dict_mixed.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"Both Builder and dict should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_optional_nested_dict(self, generate_core_stubs):
        """Test that nested dict fields are still optional."""
        test_code = """
from _generated.dummy_capnp import TestSturdyRef

# Create without specifying hostId (should still work)
ref = TestSturdyRef.new_message()

# Create with only some fields
ref2 = TestSturdyRef.new_message(hostId={"host": "test"})
"""
        test_file = TESTS_DIR / "_test_nested_dict_optional.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"Nested dict fields should be optional:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()



if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
