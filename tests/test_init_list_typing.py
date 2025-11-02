"""Test that init() on Builder classes returns typed lists, not Any.

This is a focused test to ensure list initialization has proper return types.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


def test_init_list_explicit_type_annotation(generate_all_example_stubs):
    """Test that we can explicitly annotate the return type of init()."""
    GENERATED_DIR = generate_all_example_stubs.get("addressbook")
    test_code = """
import addressbook_capnp
from typing import TYPE_CHECKING

addresses = addressbook_capnp.AddressBook.new_message()

# Try to explicitly type the result - this should work if properly typed
if TYPE_CHECKING:
    # This reveals if init returns Any - pyright will allow any annotation with Any
    people: int = addresses.init("people", 2)  # Should error if properly typed!
    # Because people should be a list-like object, not int
"""

    test_file = GENERATED_DIR / "test_explicit_annotation.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    # If init returns Any, pyright won't complain about assigning to int
    # If init returns a proper type, pyright will error
    error_count = result.stdout.count("error:")

    if error_count == 0:
        pytest.fail(
            f"init() returns Any - it can be assigned to any type without error!\n"
            f"Pyright output:\n{result.stdout}\n\n"
            f"Expected: Error assigning list-like to int\n"
            f"Actual: No error (because Any is compatible with everything)"
        )


def test_init_list_wrong_usage(generate_all_example_stubs):
    """Test that using init result incorrectly raises type errors."""
    GENERATED_DIR = generate_all_example_stubs.get("addressbook")
    if not GENERATED_DIR:
        pytest.skip("Addressbook stubs not generated")
    test_code = """
import addressbook_capnp

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 2)

# If properly typed, these should error:
x = people + 5  # Can't add number to list
y = people.upper()  # Lists don't have upper() method
"""

    test_file = GENERATED_DIR / "test_wrong_usage.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")

    if error_count == 0:
        pytest.fail(
            f"init() returns Any - wrong operations don't cause errors!\n"
            f"Pyright output:\n{result.stdout}\n\n"
            f"Expected: Errors for invalid operations\n"
            f"Actual: No errors (Any accepts any operation)"
        )
    else:
        print(f"✓ Good! Got {error_count} type errors as expected")


def test_init_reveals_type(generate_all_example_stubs):
    """Use reveal_type to see what pyright thinks init returns."""
    GENERATED_DIR = generate_all_example_stubs.get("addressbook")
    if not GENERATED_DIR:
        pytest.skip("Addressbook stubs not generated")
    test_code = """
import addressbook_capnp
from typing import reveal_type

addresses = addressbook_capnp.AddressBook.new_message()
people = addresses.init("people", 2)

reveal_type(people)  # This will show what pyright infers
"""

    test_file = GENERATED_DIR / "test_reveal_type.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    print(f"\nReveal type output:\n{result.stdout}")

    # Check if it reveals Any
    if "Type of" in result.stdout and "Any" in result.stdout:
        pytest.fail(f"init() is inferred as Any!\nPyright output:\n{result.stdout}")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
