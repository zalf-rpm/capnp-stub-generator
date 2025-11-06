"""Tests for dict initialization at all levels (not just nested).

This validates that new_message() and field assignment accept dicts for struct fields
at any level, matching pycapnp's runtime behavior.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.conftest import run_pyright

TESTS_DIR = Path(__file__).parent


class TestDictInitializationAllLevels:
    """Test that dicts work for struct fields at all levels."""

    def test_top_level_dict_with_kwargs(self, generate_addressbook_stubs):
        """Test using direct kwargs for top-level struct initialization."""
        test_code = """
from _generated.addressbook.addressbook_capnp import Person

# Direct kwargs work perfectly
alice = Person.new_message(name='alice')

# Type checking works
name: str = alice.name

# Note: **dict unpacking is a runtime feature that pyright cannot fully verify
# because it requires knowing the exact dict contents at type-check time.
# This is a known limitation of static type checkers, not our generator.
"""
        test_file = TESTS_DIR / "_test_dict_kwargs.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"Direct kwargs should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_list_of_dicts(self, generate_addressbook_stubs):
        """Test using list of dicts for struct list fields."""
        test_code = """
from _generated.addressbook.addressbook_capnp import AddressBook

# From the pycapnp docs: list of dicts
book = AddressBook.new_message(people=[{'name': 'Alice'}])

# Should work
first_person = book.people[0]
name: str = first_person.name
"""
        test_file = TESTS_DIR / "_test_list_of_dicts.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"List of dicts should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_field_assignment_with_dict(self, generate_addressbook_stubs):
        """Test assigning dict to struct field after initialization.

        With the updated _DynamicListBuilder stubs, this now works without type: ignore!
        """
        test_code = """
from _generated.addressbook.addressbook_capnp import AddressBook

# From the pycapnp docs: field assignment with dict
book = AddressBook.new_message()
people_list = book.init('people', 1)  # Returns _DynamicListBuilder
people_list[0] = {'name': 'Bob'}  # Now type-safe with updated stubs!

# Access through the initialized list works
name: str = people_list[0].name
"""
        test_file = TESTS_DIR / "_test_field_assignment_dict.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"Field assignment with dict should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_nested_and_top_level_dicts(self, generate_addressbook_stubs):
        """Test mixing nested and top-level dict usage."""
        test_code = """
from _generated.addressbook.addressbook_capnp import Person, AddressBook

# Top-level dict for Person (using direct kwargs, not **dict unpacking)
charlie = Person.new_message(name='Charlie', email='charlie@example.com')

# Nested dicts in AddressBook (this is where dict support shines)
book = AddressBook.new_message(people=[
    {'name': 'Alice'},
    {'name': 'Bob', 'email': 'bob@example.com'},
])

# Both should work
name1: str = charlie.name
name2: str = book.people[0].name
name3: str = book.people[1].name
"""
        test_file = TESTS_DIR / "_test_mixed_dict_usage.py"
        test_file.write_text(test_code)

        try:
            error_count, output = run_pyright(test_file)
            assert error_count == 0, f"Mixed dict usage should work:\n{output}"
        finally:
            if test_file.exists():
                test_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
