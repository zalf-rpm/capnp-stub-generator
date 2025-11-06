"""Demonstration of nested dict initialization in new_message().

This shows the new feature where struct fields in new_message() can accept
dict literals for convenient nested initialization.
"""

from __future__ import annotations


# Example 1: Simple nested struct initialization
def example_simple_nested():
    """Demonstrate simple nested dict initialization."""
    from _generated.dummy_capnp import TestSturdyRef

    # Before: Had to create nested structs explicitly
    # host_id_builder = TestSturdyRefHostId.new_message(host="example.com")
    # ref = TestSturdyRef.new_message(hostId=host_id_builder)

    # After: Can use dict for convenient nested initialization
    ref = TestSturdyRef.new_message(hostId={"host": "example.com"})

    print(f"Created SturdyRef with host: {ref.hostId.host}")
    return ref


# Example 2: Real-world use case similar to user's persistence_capnp
def example_persistence_style():
    """Demonstrate the persistence_capnp style nested initialization."""
    from _generated.dummy_capnp import TestSturdyRef

    # This mimics the user's original example:
    # persistence_capnp.SturdyRef.new_message(
    #     vat={"address": {"host": hp.host, "port": hp.port}},
    #     localRef={"text": sr_token},
    # )

    # For our TestSturdyRef (which has simpler nesting):
    ref = TestSturdyRef.new_message(hostId={"host": "localhost"})

    print(f"Persistence-style ref created with host: {ref.hostId.host}")
    return ref


# Example 3: Both Builder and dict work
def example_mixed_approaches():
    """Show that both explicit Builder and dict initialization work."""
    from _generated.dummy_capnp import TestSturdyRef, TestSturdyRefHostId

    # Method 1: Traditional Builder approach (still works)
    host_builder = TestSturdyRefHostId.new_message(host="builder-example.com")
    ref1 = TestSturdyRef.new_message(hostId=host_builder)

    # Method 2: Convenient dict approach (new feature)
    ref2 = TestSturdyRef.new_message(hostId={"host": "dict-example.com"})

    print("Both methods work:")
    print(f"  Builder method: {ref1.hostId.host}")
    print(f"  Dict method: {ref2.hostId.host}")

    return ref1, ref2


# Example 4: Calculator Expression with nested Call
def example_calculator_nested():
    """Demonstrate nested dict initialization with Calculator Expression."""
    from typing import cast

    from _generated.examples.calculator.calculator_capnp import Calculator

    # Create an expression with a nested call using dict
    # Note: In real usage, function would be a proper Calculator.Function instance
    func = cast(Calculator.Function, object())  # Placeholder for demo

    # You can now pass a dict for the Call struct
    expr = Calculator.Expression.new_message(
        call={
            "function": func,
            "params": [
                Calculator.Expression.new_message(literal=1.0),
                Calculator.Expression.new_message(literal=2.0),
            ],
        }
    )

    print("Created Calculator Expression with nested Call dict")
    return expr


if __name__ == "__main__":
    print("=" * 70)
    print("NESTED DICT INITIALIZATION DEMO")
    print("=" * 70)
    print()

    print("Example 1: Simple nested struct")
    print("-" * 70)
    example_simple_nested()
    print()

    print("Example 2: Persistence-style nested initialization")
    print("-" * 70)
    example_persistence_style()
    print()

    print("Example 3: Mixed Builder and dict approaches")
    print("-" * 70)
    example_mixed_approaches()
    print()

    print("Example 4: Calculator Expression with nested Call")
    print("-" * 70)
    example_calculator_nested()
    print()

    print("=" * 70)
    print("All examples completed successfully!")
    print("The new_message() method now accepts dict literals for struct fields,")
    print("making nested initialization much more convenient and readable.")
    print("=" * 70)
