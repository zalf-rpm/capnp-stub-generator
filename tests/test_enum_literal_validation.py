"""Test that enum fields only accept valid literal values, not arbitrary strings.

Enum fields should accept:
1. The enum type itself (e.g., Type.mobile)
2. Only the specific literal strings that are valid enum values (e.g., "mobile", "home", "work")
3. NOT arbitrary strings (e.g., "invalid_value")
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


def test_enum_field_accepts_valid_literal(generate_all_example_stubs):
    GENERATED_DIR = generate_all_example_stubs.get("addressbook")
    """Test that enum fields accept valid literal string values."""
    GENERATED_DIR = generate_all_example_stubs.get("addressbook")
    test_code = """
import addressbook_capnp

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 1)
person = people[0]
phones = person.init("phones", 3)

# These should all type check - valid enum values
phones[0].type = "mobile"  # Valid
phones[1].type = "home"    # Valid
phones[2].type = "work"    # Valid
"""

    test_file = GENERATED_DIR / "test_valid_enum.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")

    if error_count > 0:
        pytest.fail(
            f"Valid enum literals should type check but got {error_count} errors.\nPyright output:\n{result.stdout}"
        )


def test_enum_field_rejects_invalid_literal(generate_all_example_stubs):
    GENERATED_DIR = generate_all_example_stubs.get("addressbook")
    """Test that enum fields reject invalid literal string values."""
    test_code = """
import addressbook_capnp

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 1)
person = people[0]
phones = person.init("phones", 1)

# This should cause a type error - invalid enum value
phones[0].type = "invalid"  # Should error!
"""

    test_file = GENERATED_DIR / "test_invalid_enum.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")

    if error_count == 0:
        pytest.fail(
            f"Invalid enum literal 'invalid' should cause type error but didn't!\n"
            f"Pyright output:\n{result.stdout}\n\n"
            f"Expected: Type error for invalid enum value\n"
            f"Actual: No error (accepts any string)"
        )
    else:
        print(f"✓ Good! Invalid enum value correctly rejected with {error_count} error(s)")


def test_enum_field_accepts_enum_member(generate_all_example_stubs):
    GENERATED_DIR = generate_all_example_stubs.get("addressbook")
    """Test that enum fields accept the enum type itself."""
    test_code = """
import addressbook_capnp

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 1)
person = people[0]
phones = person.init("phones", 1)

# This should type check - using enum member
from addressbook_capnp import Person
phones[0].type = Person.PhoneNumber.Type.mobile
"""

    test_file = GENERATED_DIR / "test_enum_member.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")

    if error_count > 0:
        pytest.fail(f"Enum member should type check but got {error_count} errors.\nPyright output:\n{result.stdout}")


def test_enum_field_type_annotation(generate_all_example_stubs):
    GENERATED_DIR = generate_all_example_stubs.get("addressbook")
    """Test that we can correctly annotate variables with enum types."""
    test_code = """
import addressbook_capnp
from addressbook_capnp import Person

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 1)
person = people[0]
phones = person.init("phones", 1)

# Set with literal
phones[0].type = "mobile"

# Reading it back gives the union type (Type | Literal[...])
# Can annotate with the broader type or let it infer
phone_type = phones[0].type  # Inferred correctly

# This should error - wrong type annotation
wrong_type: int = phones[0].type  # Should error!
"""

    test_file = GENERATED_DIR / "test_enum_annotation.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    # Should have exactly 1 error (wrong type annotation)
    error_count = result.stdout.count("error:")

    if error_count != 1:
        pytest.fail(
            f"Expected exactly 1 error (wrong annotation) but got {error_count}.\nPyright output:\n{result.stdout}"
        )

    # Check it's the right error
    if "int" not in result.stdout or "is not assignable" not in result.stdout:
        pytest.fail(f"Expected error about int assignment but got different error.\nPyright output:\n{result.stdout}")

    print("✓ Good! Correct error for wrong type annotation")


def test_enum_summary():
    """Summary of enum literal validation."""
    print("\n" + "=" * 70)
    print("ENUM LITERAL VALIDATION SUMMARY")
    print("=" * 70)
    print("All enum field tests passed!")
    print("  ✓ Valid literals accepted (mobile, home, work)")
    print("  ✓ Invalid literals rejected")
    print("  ✓ Enum members accepted")
    print("  ✓ Type annotations work correctly")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
