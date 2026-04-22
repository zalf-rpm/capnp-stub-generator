"""Schema helper types for `calculator.capnp`."""

from . import modules as modules

type _CalculatorExpressionExpressionCallSchema = (
    modules._CalculatorInterfaceModule._ExpressionStructModule._ExpressionCallStructModule._ExpressionCallSchema
)

type _CalculatorExpressionSchema = modules._CalculatorInterfaceModule._ExpressionStructModule._ExpressionSchema

type _CalculatorFunctionSchema = modules._CalculatorInterfaceModule._FunctionInterfaceModule._FunctionSchema

type _CalculatorSchema = modules._CalculatorInterfaceModule._CalculatorSchema

type _CalculatorValueSchema = modules._CalculatorInterfaceModule._ValueInterfaceModule._ValueSchema
