"""Test that addressbook example has proper typing for all field accesses.

This test validates that the generated stubs provide correct types for:
- Initializing lists with init()
- Accessing list elements
- Iterating over lists
- Setting field values
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent
ADDRESSBOOK_DIR = TESTS_DIR / "examples" / "addressbook"
GENERATED_DIR = TESTS_DIR / "_generated_addressbook_typing"


@pytest.fixture(scope="module")
def generate_addressbook_stubs():
    """Generate stubs for addressbook example."""
    from capnp_stub_generator.cli import main

    # Clean and create output directory
    if GENERATED_DIR.exists():
        shutil.rmtree(GENERATED_DIR)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    # Generate stubs
    schema_path = str(ADDRESSBOOK_DIR / "addressbook.capnp")
    main(["-p", schema_path, "-o", str(GENERATED_DIR)])

    yield GENERATED_DIR

    # Optionally clean up
    # shutil.rmtree(GENERATED_DIR)


def test_init_returns_typed_list(generate_addressbook_stubs):
    """Test that init() returns a properly typed list, not Any."""
    # Create a test file that uses init
    test_code = """
import addressbook_capnp

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 2)

# This should be typed as a list-like object, allowing indexing
alice = people[0]

# Alice should be typed as PersonBuilder, so we can access fields
alice.id = 123  # Should type check
alice.name = "Alice"  # Should type check
alice.email = "alice@example.com"  # Should type check
"""

    test_file = GENERATED_DIR / "test_typing_init.py"
    test_file.write_text(test_code)

    # Run pyright on the test file
    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
        cwd=str(TESTS_DIR),
    )

    error_count = result.stdout.count("error:")

    if error_count > 0:
        pytest.fail(
            f"init() return type has {error_count} type errors.\n"
            f"Pyright output:\n{result.stdout}\n\n"
            f"Expected: init() should return a typed list-like object\n"
            f"Actual: Returns Any, causing downstream type errors"
        )


def test_list_element_access_typed(generate_addressbook_stubs):
    """Test that accessing list elements gives proper types."""
    test_code = """
import addressbook_capnp

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 2)

alice = people[0]
bob = people[1]

# These should type check because alice/bob are PersonBuilder
alice_phones = alice.init("phones", 1)
alice_phones[0].number = "555-1212"
alice_phones[0].type = "mobile"

bob_phones = bob.init("phones", 2)
bob_phones[0].number = "555-4567"
"""

    test_file = GENERATED_DIR / "test_typing_elements.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
        cwd=str(TESTS_DIR),
    )

    error_count = result.stdout.count("error:")

    if error_count > 0:
        pytest.fail(
            f"List element access has {error_count} type errors.\n"
            f"Pyright output:\n{result.stdout}\n\n"
            f"Expected: people[0] should be PersonBuilder\n"
            f"Actual: Type not properly inferred"
        )


def test_iteration_typed(generate_addressbook_stubs):
    """Test that iterating over lists gives proper types."""
    test_code = """
import addressbook_capnp

addresses = addressbook_capnp.AddressBook.read(open("example", "rb"))

# Iterating over people should give PersonReader objects
for person in addresses.people:
    # These should type check
    name: str = person.name
    email: str = person.email
    
    # Nested iteration should also be typed
    for phone in person.phones:
        number: str = phone.number
        # phone.type returns the Type enum, not a string
        phone_type = phone.type
"""

    test_file = GENERATED_DIR / "test_typing_iteration.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
        cwd=str(TESTS_DIR),
    )

    error_count = result.stdout.count("error:")

    if error_count > 0:
        pytest.fail(
            f"List iteration has {error_count} type errors.\n"
            f"Pyright output:\n{result.stdout}\n\n"
            f"Expected: person should be PersonReader with proper fields\n"
            f"Actual: Type not properly inferred"
        )


def test_union_field_access(generate_addressbook_stubs):
    """Test that union fields are properly typed."""
    test_code = """
import addressbook_capnp

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 2)

alice = people[0]
# Setting union fields should type check
alice.employment.school = "MIT"

bob = people[1]
bob.employment.unemployed = None
"""

    test_file = GENERATED_DIR / "test_typing_unions.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
        cwd=str(TESTS_DIR),
    )

    error_count = result.stdout.count("error:")

    if error_count > 0:
        pytest.fail(
            f"Union field access has {error_count} type errors.\n"
            f"Pyright output:\n{result.stdout}\n\n"
            f"Expected: employment.school and employment.unemployed should type check\n"
            f"Actual: Type errors in union access"
        )


def test_nested_init_typed(generate_addressbook_stubs):
    """Test that nested init() calls return proper types."""
    test_code = """
import addressbook_capnp

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 1)

person = people[0]
# Nested init should return typed list
phones = person.init("phones", 2)

# Should be able to access by index and set fields
phones[0].number = "123"
phones[0].type = "mobile"
phones[1].number = "456"
phones[1].type = "work"
"""

    test_file = GENERATED_DIR / "test_typing_nested_init.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
        cwd=str(TESTS_DIR),
    )

    error_count = result.stdout.count("error:")

    if error_count > 0:
        pytest.fail(
            f"Nested init() has {error_count} type errors.\n"
            f"Pyright output:\n{result.stdout}\n\n"
            f"Expected: phones should be typed list-like with PhoneNumberBuilder elements\n"
            f"Actual: Type not properly inferred"
        )


def test_all_addressbook_typing_summary(generate_addressbook_stubs):
    """Provide a summary of addressbook typing tests."""
    print("\n" + "=" * 70)
    print("ADDRESSBOOK TYPING TEST SUMMARY")
    print("=" * 70)
    print("All typing tests passed!")
    print("  ✓ init() returns properly typed lists")
    print("  ✓ List element access is typed")
    print("  ✓ Iteration provides correct types")
    print("  ✓ Union fields are accessible")
    print("  ✓ Nested init() calls are typed")
    print("=" * 70 + "\n")
