"""Tests that raw Python list inputs match pycapnp runtime behavior."""

from __future__ import annotations

import re
from pathlib import Path
from string import Template

from tests.test_helpers import read_generated_types_file, run_pyright, run_python_file

TESTS_DIR = Path(__file__).parent
BASIC_SCHEMAS_DIR = TESTS_DIR / "schemas" / "basic"
EXAMPLES_SCHEMAS_DIR = TESTS_DIR / "schemas" / "examples"


def _run_runtime_probe(tmp_path: Path, script: str) -> None:
    """Execute one isolated runtime probe script."""
    script_file = tmp_path / "runtime_probe.py"
    script_file.write_text(script)
    result = run_python_file(script_file, cwd=TESTS_DIR.parent)
    assert result.returncode == 0, f"Runtime probe failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_struct_new_message_accepts_mixed_python_list_shapes(tmp_path: Path) -> None:
    """Struct constructors should accept mixed dict/Builder/Reader list elements."""
    script = Template(
        """
from pathlib import Path
import capnp

basic_schemas = Path($basic_schemas)
examples_schemas = Path($examples_schemas)

basic_low = capnp.load(str(basic_schemas / "basic_low.capnp"))
addressbook = capnp.load(str(examples_schemas / "addressbook" / "addressbook.capnp"))
advanced = capnp.load(str(basic_schemas / "advanced_features.capnp"), imports=[str(basic_schemas)])

person_builder = addressbook.Person.new_message(id=2, name="Bob", email="bob@example.com")
person_reader = addressbook.Person.new_message(id=3, name="Carol", email="carol@example.com").as_reader()
inner_builder = advanced.AdvancedContainer.Nested.Inner.new_message(value=8)
inner_reader = advanced.AdvancedContainer.Nested.Inner.new_message(value=9).as_reader()

basic_message = basic_low.BasicLow.new_message(scores=[1, 2, 3], tags=["a", "b"])
addressbook_message = addressbook.AddressBook.new_message(
    people=[
        {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
            "phones": [{"number": "123", "type": "mobile"}],
        },
        person_builder,
        person_reader,
    ]
)
advanced_message = advanced.AdvancedContainer.new_message(
    label="advanced",
    nested={
        "note": "nested",
        "listInner": [{"value": 2}, {"value": 3}],
        "listListInner": [[{"value": 4}], [{"value": 5}, {"value": 6}]],
        "stateList": ["start", "end"],
    },
    ints2d=[[1, 2], [3]],
    inners2d=[[{"value": 7}, inner_builder, inner_reader]],
)

assert basic_message.to_dict()["scores"] == [1, 2, 3]
assert [person["name"] for person in addressbook_message.to_dict()["people"]] == ["Alice", "Bob", "Carol"]
assert addressbook_message.to_dict()["people"][0]["phones"] == [{"number": "123", "type": "mobile"}]
assert advanced_message.to_dict()["ints2d"] == [[1, 2], [3]]
assert advanced_message.to_dict()["inners2d"] == [[{"value": 7}, {"value": 8}, {"value": 9}]]
"""
    ).substitute(
        basic_schemas=repr(str(BASIC_SCHEMAS_DIR)),
        examples_schemas=repr(str(EXAMPLES_SCHEMAS_DIR)),
    )
    _run_runtime_probe(tmp_path, script)


def test_builder_setters_accept_python_lists(tmp_path: Path) -> None:
    """Builder setters should accept raw Python lists for concrete list fields."""
    script = Template(
        """
from pathlib import Path
import capnp

basic_schemas = Path($basic_schemas)
examples_schemas = Path($examples_schemas)

mid_features = capnp.load(str(basic_schemas / "mid_features.capnp"))
addressbook = capnp.load(str(examples_schemas / "addressbook" / "addressbook.capnp"))
advanced = capnp.load(str(basic_schemas / "advanced_features.capnp"), imports=[str(basic_schemas)])

phone_builder = addressbook.Person.PhoneNumber.new_message(number="456", type="work")
phone_reader = addressbook.Person.PhoneNumber.new_message(number="789", type="home").as_reader()
inner_builder = advanced.AdvancedContainer.Nested.Inner.new_message(value=8)
inner_reader = advanced.AdvancedContainer.Nested.Inner.new_message(value=9).as_reader()

mid_message = mid_features.MidFeatureContainer.new_message(id=1)
mid_message.nestedList = [{"flag": False, "count": 1, "state": "start"}]
mid_message.enumList = ["alpha", "beta"]
mid_message.stateList = ["start", "done"]

person = addressbook.Person.new_message(id=1, name="Alice", email="alice@example.com")
person.phones = [{"number": "123", "type": "mobile"}, phone_builder, phone_reader]

advanced_message = advanced.AdvancedContainer.new_message(label="advanced")
advanced_message.ints2d = [[1, 2], [3]]
advanced_message.inners2d = [[{"value": 7}, inner_builder, inner_reader]]

assert mid_message.to_dict()["nestedList"] == [{"flag": False, "count": 1, "state": "start"}]
assert person.to_dict()["phones"] == [
    {"number": "123", "type": "mobile"},
    {"number": "456", "type": "work"},
    {"number": "789", "type": "home"},
]
assert advanced_message.to_dict()["ints2d"] == [[1, 2], [3]]
assert advanced_message.to_dict()["inners2d"] == [[{"value": 7}, {"value": 8}, {"value": 9}]]
"""
    ).substitute(
        basic_schemas=repr(str(BASIC_SCHEMAS_DIR)),
        examples_schemas=repr(str(EXAMPLES_SCHEMAS_DIR)),
    )
    _run_runtime_probe(tmp_path, script)


def test_struct_inputs_accept_dict_builder_and_reader_shapes(tmp_path: Path) -> None:
    """Struct-typed inputs should accept dicts, Builders, and Readers."""
    script = Template(
        """
import asyncio
from pathlib import Path
import capnp

basic_schemas = Path($basic_schemas)
examples_schemas = Path($examples_schemas)

advanced = capnp.load(str(basic_schemas / "advanced_features.capnp"), imports=[str(basic_schemas)])
calculator = capnp.load(str(examples_schemas / "calculator" / "calculator.capnp"))

nested_builder = advanced.AdvancedContainer.Nested.new_message(note="builder", listInner=[{"value": 1}])
nested_reader = advanced.AdvancedContainer.Nested.new_message(note="reader", listInner=[{"value": 2}]).as_reader()
expr_builder = calculator.Calculator.Expression.new_message(literal=3.5)
expr_reader = calculator.Calculator.Expression.new_message(literal=4.5).as_reader()

dict_message = advanced.AdvancedContainer.new_message(
    label="dict",
    nested={"note": "dict", "listInner": [{"value": 3}]},
)
builder_message = advanced.AdvancedContainer.new_message(label="builder", nested=nested_builder)
reader_message = advanced.AdvancedContainer.new_message(label="reader", nested=nested_reader)

setter_message = advanced.AdvancedContainer.new_message(label="setter")
setter_message.nested = {"note": "setter-dict", "listInner": [{"value": 4}]}
setter_message.nested = nested_builder
setter_message.nested = nested_reader

class ValueImpl(calculator.Calculator.Value.Server):
    def __init__(self, value: float) -> None:
        self._value = value

    async def read(self, **_kwargs: object) -> float:
        return self._value

class FunctionImpl(calculator.Calculator.Function.Server):
    async def call(self, params: object, **_kwargs: object) -> float:
        return float(sum(params))

class CalculatorImpl(calculator.Calculator.Server):
    async def evaluate(self, expression: object, **_kwargs: object):
        if expression.which() == "literal":
            value = float(expression.literal)
        else:
            value = 0.0
        return calculator.Calculator.Value._new_client(ValueImpl(value))

    async def defFunction(self, paramCount: object, body: object, **_kwargs: object):
        return calculator.Calculator.Function._new_client(FunctionImpl())

    async def getOperator(self, op: object, **_kwargs: object):
        return calculator.Calculator.Function._new_client(FunctionImpl())

async def main() -> None:
    calc = calculator.Calculator._new_client(CalculatorImpl())
    direct_dict = await calc.evaluate({"literal": 1.25})
    direct_builder = await calc.evaluate(expr_builder)
    direct_reader = await calc.evaluate(expr_reader)

    request_dict = calc.evaluate_request()
    request_dict.expression = {"literal": 2.25}
    request_dict_result = await request_dict.send()

    request_builder = calc.evaluate_request()
    request_builder.expression = expr_builder
    request_builder_result = await request_builder.send()

    request_reader = calc.evaluate_request()
    request_reader.expression = expr_reader
    request_reader_result = await request_reader.send()

    assert (await direct_dict.value.read()).value == 1.25
    assert (await direct_builder.value.read()).value == 3.5
    assert (await direct_reader.value.read()).value == 4.5
    assert (await request_dict_result.value.read()).value == 2.25
    assert (await request_builder_result.value.read()).value == 3.5
    assert (await request_reader_result.value.read()).value == 4.5

asyncio.run(capnp.run(main()))

assert dict_message.to_dict()["nested"]["note"] == "dict"
assert builder_message.to_dict()["nested"]["note"] == "builder"
assert reader_message.to_dict()["nested"]["note"] == "reader"
assert setter_message.to_dict()["nested"]["note"] == "reader"
"""
    ).substitute(
        basic_schemas=repr(str(BASIC_SCHEMAS_DIR)),
        examples_schemas=repr(str(EXAMPLES_SCHEMAS_DIR)),
    )
    _run_runtime_probe(tmp_path, script)


def test_rpc_surfaces_accept_python_lists(tmp_path: Path) -> None:
    """RPC list params and list results should accept raw Python lists."""
    script = Template(
        """
import asyncio
from pathlib import Path
import capnp

basic_schemas = Path($basic_schemas)
examples_schemas = Path($examples_schemas)

calculator = capnp.load(str(examples_schemas / "calculator" / "calculator.capnp"))
list_result = capnp.load(str(basic_schemas / "list_result.capnp"))
item_builder = list_result.Item.new_message(name="B", value=2)
item_reader = list_result.Item.new_message(name="C", value=3).as_reader()

async def main() -> None:
    class FunctionImpl(calculator.Calculator.Function.Server):
        async def call(self, params: object, **_kwargs: object) -> float:
            return float(sum(params))

    function = calculator.Calculator.Function._new_client(FunctionImpl())
    direct_call = await function.call([1.0, 2.0, 3.0])

    request = function.call_request()
    request.params = [4.0, 5.0]
    request_call = await request.send()

    class ItemServiceImpl(list_result.ItemService.Server):
        async def getItems(self, **_kwargs: object) -> list[object]:
            return [{"name": "A", "value": 1}, item_builder, item_reader]

    item_service = list_result.ItemService._new_client(ItemServiceImpl())
    list_result_message = await item_service.getItems()

    assert direct_call.value == 6.0
    assert request_call.value == 9.0
    assert list_result_message.to_dict() == {"items": [{"name": "A", "value": 1}, {"name": "B", "value": 2}, {"name": "C", "value": 3}]}

asyncio.run(capnp.run(main()))
"""
    ).substitute(
        basic_schemas=repr(str(BASIC_SCHEMAS_DIR)),
        examples_schemas=repr(str(EXAMPLES_SCHEMAS_DIR)),
    )
    _run_runtime_probe(tmp_path, script)


def test_generated_struct_inputs_advertise_reader_and_dict_shapes(basic_stubs: Path) -> None:
    """Generated struct constructors should advertise Builder, Reader, and dict inputs."""
    package_dir = basic_stubs / "advanced_features_capnp"
    modules_content = read_generated_types_file(package_dir, "modules.pyi")

    assert re.search(
        r"nested:\s+builders\.NestedBuilder\s*\|\s*readers\.NestedReader\s*\|\s*dict\[str, Any\]\s*\|\s*None = None",
        modules_content,
    )


def test_generated_struct_list_inputs_advertise_sequences(addressbook_stubs: Path) -> None:
    """Generated struct helpers should advertise raw Sequence inputs for list fields."""
    package_dir = addressbook_stubs / "addressbook_capnp"
    modules_content = read_generated_types_file(package_dir, "modules.pyi")
    builders_content = read_generated_types_file(package_dir, "builders.pyi")

    assert re.search(
        r"people:\s+builders\.PersonListBuilder\s*\|\s*readers\.PersonListReader\s*\|\s*"
        r"Sequence\[readers\.PersonReader\s*\|\s*builders\.PersonBuilder\s*\|\s*dict\[str, Any\]\]\s*\|\s*None = None",
        modules_content,
    )
    assert re.search(
        r"value:\s+PersonListBuilder\s*\|\s*readers\.PersonListReader\s*\|\s*"
        r"Sequence\[readers\.PersonReader\s*\|\s*PersonBuilder\s*\|\s*dict\[str, Any\]\]",
        builders_content,
    )
    assert re.search(
        r"phones:\s+builders\.PhoneNumberListBuilder\s*\|\s*readers\.PhoneNumberListReader\s*\|\s*"
        r"Sequence\[readers\.PhoneNumberReader\s*\|\s*builders\.PhoneNumberBuilder\s*\|\s*dict\[str, Any\]\]"
        r"\s*\|\s*None = None",
        modules_content,
    )
    assert re.search(
        r"value:\s+PhoneNumberListBuilder\s*\|\s*readers\.PhoneNumberListReader\s*\|\s*"
        r"Sequence\[readers\.PhoneNumberReader\s*\|\s*PhoneNumberBuilder\s*\|\s*dict\[str, Any\]\]",
        builders_content,
    )


def test_generated_rpc_list_inputs_use_precise_sequences(calculator_stubs: Path, basic_stubs: Path) -> None:
    """Generated RPC helpers should expose precise raw sequence input shapes."""
    calculator_package = calculator_stubs / "calculator_capnp"
    calculator_clients = read_generated_types_file(calculator_package, "clients.pyi")
    calculator_requests = read_generated_types_file(calculator_package, "requests.pyi")
    list_result_package = basic_stubs / "list_result_capnp"
    list_result_tuples = read_generated_types_file(list_result_package, "results", "tuples.pyi")

    assert "params: builders.Float64ListBuilder | readers.Float64ListReader | Sequence[float] | None = None" in (
        calculator_clients
    )
    assert "params: builders.Float64ListBuilder | readers.Float64ListReader | Sequence[float]" in calculator_requests
    assert re.search(
        r"items:\s*\(\s*builders\.ItemListBuilder\s*\|\s*readers\.ItemListReader\s*\|\s*"
        r"Sequence\[readers\.ItemReader\s*\|\s*builders\.ItemBuilder\s*\|\s*dict\[str, Any\]\]\s*\)",
        list_result_tuples,
        re.DOTALL,
    )


def test_struct_python_inputs_type_check(addressbook_stubs: Path, basic_stubs: Path) -> None:
    """Pyright should accept mixed struct dict/Builder/Reader inputs."""
    addressbook_code = """
import addressbook_capnp

person_builder = addressbook_capnp.Person.new_message(id=2, name="Bob", email="bob@example.com")
person_reader = person_builder.as_reader()
phone_builder = addressbook_capnp.Person.PhoneNumber.new_message(number="456", type="work")
phone_reader = phone_builder.as_reader()

book = addressbook_capnp.AddressBook.new_message(
    people=[
        {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
            "phones": [{"number": "123", "type": "mobile"}],
        },
        person_builder,
        person_reader,
    ]
)
person = addressbook_capnp.Person.new_message(
    id=1,
    name="Alice",
    email="alice@example.com",
    phones=[{"number": "123", "type": "mobile"}, phone_builder, phone_reader],
)
person.phones = [{"number": "789", "type": "home"}, phone_builder, phone_reader]

first_person = book.people[0]
first_phone = person.phones[0]
name: str = first_person.name
number: str = first_phone.number
"""

    addressbook_file = addressbook_stubs / "test_python_struct_inputs.py"
    addressbook_file.write_text(addressbook_code)

    addressbook_result = run_pyright(addressbook_file, cwd=TESTS_DIR)
    assert addressbook_result.returncode == 0, f"Type checking failed: {addressbook_result.stdout}"

    advanced_code = """
import advanced_features_capnp

nested_builder = advanced_features_capnp.AdvancedContainer.Nested.new_message(note="builder")
nested_reader = nested_builder.as_reader()

container = advanced_features_capnp.AdvancedContainer.new_message(
    label="advanced",
    nested=nested_reader,
)
container.nested = {"note": "dict", "listInner": [{"value": 2}]}
container.nested = nested_builder
container.nested = nested_reader

note: str = container.nested.note
"""

    advanced_file = basic_stubs / "test_python_struct_reader_inputs.py"
    advanced_file.write_text(advanced_code)

    advanced_result = run_pyright(advanced_file, cwd=TESTS_DIR)
    assert advanced_result.returncode == 0, f"Type checking failed: {advanced_result.stdout}"


def test_rpc_python_lists_type_check(calculator_stubs: Path, basic_stubs: Path) -> None:
    """Pyright should accept raw Python lists for RPC list params and list results."""
    calculator_code = """
import calculator_capnp

class FunctionImpl(calculator_capnp.Calculator.Function.Server):
    async def call(
        self,
        params: calculator_capnp.types.readers.Float64ListReader,
        _context: object,
        **kwargs: object,
    ) -> float:
        return float(sum(params))

function = calculator_capnp.Calculator.Function._new_client(FunctionImpl())
request = function.call_request()
request.params = [1.0, 2.0, 3.0]

async def use_function() -> float:
    sent = await request.send()
    called = await function.call([4.0, 5.0])
    return sent.value + called.value
"""
    calculator_file = calculator_stubs / "test_python_list_inputs.py"
    calculator_file.write_text(calculator_code)

    calculator_result = run_pyright(calculator_file, cwd=TESTS_DIR)
    assert calculator_result.returncode == 0, f"Type checking failed: {calculator_result.stdout}"

    list_result_code = """
import list_result_capnp

item_builder = list_result_capnp.Item.new_message(name="builder", value=2)
item_reader = item_builder.as_reader()

class ItemServiceImpl(list_result_capnp.ItemService.Server):
    async def getItems(self, _context: object, **kwargs: object):
        return [{"name": "demo", "value": 1}, item_builder, item_reader]
"""
    list_result_file = basic_stubs / "test_list_result_python_inputs.py"
    list_result_file.write_text(list_result_code)

    list_result_result = run_pyright(list_result_file, cwd=TESTS_DIR)
    assert list_result_result.returncode == 0, f"Type checking failed: {list_result_result.stdout}"
