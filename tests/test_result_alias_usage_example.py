"""Example demonstrating the use of Result type aliases.

This shows how Result types can now be used as top-level type aliases,
just like Builder and Reader types.
"""

# Before this change, you had to use the full nested path:
# def process_result(result: calculator_capnp._CalculatorModule.CalculatorClient.EvaluateResult) -> None:
#     ...

# After this change, you can use the convenient top-level alias:
# def process_result(result: calculator_capnp.EvaluateResult) -> None:
#     ...

# This makes type annotations much more readable and consistent with Builder/Reader patterns:
# - calculator_capnp.ExpressionBuilder  (was already available)
# - calculator_capnp.ExpressionReader   (was already available)
# - calculator_capnp.EvaluateResult     (now available!)

def example_usage():
    """Example showing the improved type annotation style."""
    import sys
    sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + '/_generated/examples/calculator')
    
    import calculator_capnp
    
    # Type aliases are now available at module level
    def handle_evaluate_result(result: calculator_capnp.EvaluateResult) -> None:
        """Process an evaluation result using the convenient type alias."""
        # The result is still the same Protocol type, just with a shorter name
        value_client = result.value  # type: calculator_capnp.ValueClient
        print(f"Got value client: {value_client}")
    
    def handle_read_result(result: calculator_capnp.ReadResult) -> None:
        """Process a read result from the Value interface."""
        value = result.value  # type: float
        print(f"Read value: {value}")
    
    def process_expression(expr: calculator_capnp.ExpressionBuilder) -> calculator_capnp.EvaluateResult:
        """
        Example showing Result types work alongside Builder/Reader types.
        
        All three patterns now work consistently:
        - ExpressionBuilder (struct Builder)
        - ExpressionReader (struct Reader)  
        - EvaluateResult (interface method Result)
        """
        # This would normally make an RPC call
        # For the example, we just show the type signature
        pass
    
    print("✓ Result type aliases work as expected")
    print("✓ Consistent with Builder/Reader naming patterns")
    print("✓ Makes type hints more readable")


if __name__ == "__main__":
    example_usage()
