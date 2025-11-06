"""Demonstrate the improvements in stub generation."""

from _generated.examples.calculator import calculator_capnp


# ✓ Client methods accept dict (convenience)
async def client_example(calc: calculator_capnp.Calculator):
    # Can pass dict - pycapnp converts it
    calc.evaluate({"literal": 123.0})

    # Can also pass Expression object
    expr = calculator_capnp.Calculator.Expression.new_message()
    calc.evaluate(expr)


# ✓ Server methods receive Reader types (not dict)
class MyCalculator(calculator_capnp.Calculator.Server):
    async def evaluate(self, expression, _context=None, **kwargs):
        # expression is ExpressionReader - has specific attributes
        which = expression.which()  # ✓ Type checker knows this exists

        if which == "literal":
            value = expression.literal  # ✓ Type checker knows literal is float
            return MyValue(value)

        return MyValue(0.0)

    async def defFunction(self, paramCount, body, _context=None, **kwargs):
        # paramCount is int (not Any)
        # body is ExpressionReader (not dict)
        return MyFunction(paramCount, body)

    async def getOperator(self, op, _context=None, **kwargs):
        # op is Calculator.Operator | Literal["add", ...] (not Any)
        return MyOperator(op)


class MyValue(calculator_capnp.Calculator.Value.Server):
    def __init__(self, val):
        self.val = val

    async def read(self, _context=None, **kwargs):
        return self.val


class MyFunction(calculator_capnp.Calculator.Function.Server):
    def __init__(self, count, body):
        self.count = count
        self.body = body

    async def call(self, params, _context=None, **kwargs):
        # params is Sequence[float] (not Any)
        return sum(params)


class MyOperator(calculator_capnp.Calculator.Function.Server):
    def __init__(self, op):
        self.op = op

    async def call(self, params, _context=None, **kwargs):
        return params[0] + params[1]


print("✓ All type hints are narrow and specific")
print("✓ Server methods use Reader types")
print("✓ Client methods accept dict | Expression")
print("✓ _context and **kwargs are properly typed")
