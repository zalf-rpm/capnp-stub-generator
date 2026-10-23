"""Runtime and static typing coverage for schema-specific union discriminants."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING

import capnp

from tests.test_helpers import run_pyright

if TYPE_CHECKING:
    from collections.abc import Iterator


BASIC_SCHEMAS_DIR = Path(__file__).parent / "schemas" / "basic"


def _literal_values(annotation: ast.expr | None) -> tuple[str, ...]:
    """Extract string values from a generated ``Literal[...]`` annotation."""
    assert isinstance(annotation, ast.Subscript)
    assert isinstance(annotation.value, ast.Name)
    assert annotation.value.id == "Literal"
    elements: Iterator[ast.expr] = (
        iter(annotation.slice.elts) if isinstance(annotation.slice, ast.Tuple) else iter((annotation.slice,))
    )
    return tuple(
        element.value for element in elements if isinstance(element, ast.Constant) and isinstance(element.value, str)
    )


def _generated_which_literals(common_stub: Path) -> dict[str, tuple[str, ...]]:
    """Read generated discriminant helper return types from ``types.common``."""
    tree = ast.parse(common_stub.read_text(encoding="utf8"))
    result: dict[str, tuple[str, ...]] = {}
    for declaration in tree.body:
        if not isinstance(declaration, ast.ClassDef):
            continue
        if not any(isinstance(base, ast.Name) and base.id == "_DynamicEnumField" for base in declaration.bases):
            continue
        call = next(
            member for member in declaration.body if isinstance(member, ast.FunctionDef) and member.name == "__call__"
        )
        result[declaration.name] = _literal_values(call.returns)
    return result


def test_generated_which_literals_match_runtime_union_fields(basic_stubs: Path) -> None:
    """Generate literals from the exact field names exposed by pycapnp at runtime."""
    runtime_schema = capnp.load(str(BASIC_SCHEMAS_DIR / "unions.capnp"))
    generated_literals = _generated_which_literals(basic_stubs / "unions_capnp" / "types" / "common.pyi")

    expected = {
        "_WithNamedUnionChoiceWhich": tuple(runtime_schema.WithNamedUnion.Choice.schema.union_fields),
        "_WithUnnamedUnionWhich": tuple(runtime_schema.WithUnnamedUnion.schema.union_fields),
    }
    assert generated_literals == expected

    unnamed_builder = runtime_schema.WithUnnamedUnion.new_message(small=7)
    unnamed_reader = unnamed_builder.as_reader()
    assert unnamed_builder.which() == "small"
    assert unnamed_reader.which() == "small"
    assert unnamed_builder.which() in generated_literals["_WithUnnamedUnionWhich"]
    assert unnamed_reader.which() in generated_literals["_WithUnnamedUnionWhich"]


def test_generated_which_refinements_remain_properties(basic_stubs: Path) -> None:
    """Never replace pycapnp's runtime data descriptor with a generated method."""
    package = basic_stubs / "unions_capnp" / "types"
    declarations: list[ast.FunctionDef] = []
    for relative_path in ("readers.pyi", "builders.pyi", "modules.pyi"):
        tree = ast.parse((package / relative_path).read_text(encoding="utf8"))
        declarations.extend(
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "which"
        )

    assert declarations
    for declaration in declarations:
        decorator_names = {ast.unparse(decorator) for decorator in declaration.decorator_list}
        assert decorator_names == {"property", "override"}
        assert isinstance(declaration.returns, ast.Attribute)
        assert declaration.returns.attr.endswith("Which")


def test_generated_which_call_is_literal_typed(basic_stubs: Path) -> None:
    """The generated property retains enum-field members while narrowing its call result."""
    sample = basic_stubs / "test_union_which_precision.py"
    sample.write_text(
        """from typing import Literal, assert_type

import unions_capnp

unnamed_builder = unions_capnp.WithUnnamedUnion.new_message(small=7)
unnamed_reader = unnamed_builder.as_reader()
assert_type(unnamed_builder.which(), Literal["small", "big"])
assert_type(unnamed_reader.which(), Literal["small", "big"])
assert_type(unnamed_builder.which.raw, int)

named_builder = unions_capnp.WithNamedUnion.new_message()
choice_builder = named_builder.init("choice")
assert_type(choice_builder.which(), Literal["none", "text", "nums"])
assert_type(choice_builder.as_reader().which(), Literal["none", "text", "nums"])
""",
        encoding="utf8",
    )

    result = run_pyright(sample)
    assert result.returncode == 0, result.stdout
