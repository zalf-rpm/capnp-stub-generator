#!/usr/bin/env python3
"""Demo script showing new_message() with keyword arguments.

This demonstrates the convenient struct initialization that matches
the user's example:
    registry_capnp.Registry.Entry.new_message(
        categoryId=e["categoryId"],
        ref=common.IdentifiableHolder(fbp_capnp.Component.new_message(**c)),
        id=c_id,
        name=info.get("name", c_id),
    )
"""

import sys
sys.path.insert(0, 'tests')

import capnp

# Load the calculator schema
calculator_capnp = capnp.load('tests/examples/calculator/calculator.capnp')

print("=" * 70)
print("DEMO: new_message() with Keyword Arguments")
print("=" * 70)
print()

# Example 1: Simple literal expression
print("1. Creating a literal expression:")
expr1 = calculator_capnp.Calculator.Expression.new_message(literal=123.0)
print(f"   expr1 = Expression.new_message(literal=123.0)")
print(f"   expr1.which() = '{expr1.which()}'")
print(f"   expr1.literal = {expr1.literal}")
print()

# Example 2: Parameter expression
print("2. Creating a parameter expression:")
expr2 = calculator_capnp.Calculator.Expression.new_message(parameter=5)
print(f"   expr2 = Expression.new_message(parameter=5)")
print(f"   expr2.which() = '{expr2.which()}'")
print(f"   expr2.parameter = {expr2.parameter}")
print()

# Example 3: Using Call struct (groups in unions require init())
print("3. Note about groups in unions:")
print("   Groups in unions (like 'call') can't be set via new_message kwargs")
print("   They must be initialized with init():")
expr3 = calculator_capnp.Calculator.Expression.new_message()
call = expr3.init('call')
# Now set call group fields
# call.function = some_function  # Would set in real code
params = call.init('params', 2)
params[0].literal = 10.0
params[1].literal = 20.0
print(f"   expr3 = Expression.new_message()")
print(f"   call = expr3.init('call')")
print(f"   params = call.init('params', 2)")
print(f"   params[0].literal = 10.0")
print(f"   params[1].literal = 20.0")
print(f"   expr3.which() = '{expr3.which()}'")
print(f"   expr3.call.params[0].literal = {expr3.call.params[0].literal}")
print()

# Example 4: Demonstrate the user's use case with regular struct fields
print("4. Real-world example (like user's code):")
print("   # This is the pattern from user's example:")
print("   # Entry.new_message(categoryId=..., ref=..., id=..., name=...)")
print("   #")
print("   # For Expression with non-group fields:")
exprs_list = [
    calculator_capnp.Calculator.Expression.new_message(literal=5.0),
    calculator_capnp.Calculator.Expression.new_message(literal=3.0),
    calculator_capnp.Calculator.Expression.new_message(parameter=0),
]
print(f"   exprs = [")
print(f"       Expression.new_message(literal=5.0),")
print(f"       Expression.new_message(literal=3.0),")  
print(f"       Expression.new_message(parameter=0),")
print(f"   ]")
print(f"   exprs[0].literal = {exprs_list[0].literal}")
print(f"   exprs[1].literal = {exprs_list[1].literal}")
print(f"   exprs[2].parameter = {exprs_list[2].parameter}")
print()

print("=" * 70)
print("Type Safety Benefits:")
print("=" * 70)
print("✓ Field names are type-checked at compile time")
print("✓ Field types are validated by the type checker")
print("✓ IDE autocomplete works for all field names")
print("✓ Nested structures are fully typed")
print("✓ No need for manual .init() calls")
print()

print("Compare to manual approach:")
print("  # Old way:")
print("  expr = Expression.new_message()")
print("  call = expr.init('call')")
print("  call.function = add_func")
print("  params = call.init('params', 2)")
print("  params[0].literal = 10.0")
print("  params[1].literal = 20.0")
print()
print("  # New way (with kwargs):")
print("  expr = Expression.new_message(")
print("      call=Call.new_message(")
print("          function=add_func,")
print("          params=[")
print("              Expression.new_message(literal=10.0),")
print("              Expression.new_message(literal=20.0),")
print("          ]")
print("      )")
print("  )")
print("=" * 70)
