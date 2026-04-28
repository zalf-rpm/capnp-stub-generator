"""Regression tests for the dogfooded `typings/` snapshot."""

from __future__ import annotations

from pathlib import Path

from tests.test_helpers import run_pyright

TESTS_DIR = Path(__file__).parent
REPO_ROOT = TESTS_DIR.parent
GENERATED_EXAMPLES_DIR = TESTS_DIR / "_generated" / "examples"
TYPINGS_DIR = REPO_ROOT / "typings"
IGNORED_EXAMPLE_DIRS = {"capnp-stubs", "schema_capnp", "__pycache__", ".ruff_cache"}


def _generated_example_package_names() -> set[str]:
    return {
        path.name
        for path in GENERATED_EXAMPLES_DIR.iterdir()
        if path.is_dir() and path.name not in IGNORED_EXAMPLE_DIRS
    }


def test_typings_snapshot_mirrors_generated_examples() -> None:
    """The tracked typings snapshot should mirror the generated example packages."""
    assert (TYPINGS_DIR / "capnp-stubs" / "lib" / "capnp.pyi").exists()
    assert (TYPINGS_DIR / "schema_capnp" / "__init__.pyi").exists()

    generated_package_names = _generated_example_package_names()
    assert generated_package_names

    for package_name in generated_package_names:
        assert (TYPINGS_DIR / package_name / "__init__.pyi").exists()
        assert (TYPINGS_DIR / package_name / f"{package_name}_capnp" / "__init__.pyi").exists()


def test_typings_snapshot_supports_capnp_autocomplete(tmp_path: Path) -> None:
    """Dogfooded typings should provide example-aware autocomplete for `capnp`."""
    sample = tmp_path / "test_typings_snapshot.py"
    sample.write_text(
        """
import capnp
from calculator import calculator_capnp
from restorer import restorer_capnp
from single_value import single_value_capnp


def check(
    capability: capnp.lib.capnp._CapabilityClient,
    any_pointer: capnp.lib.capnp._DynamicObjectReader,
    any_builder: capnp.lib.capnp._DynamicObjectBuilder,
    request: restorer_capnp.types.requests.SetanypointerRequest,
) -> None:
    calculator_client = capability.cast_as(calculator_capnp.Calculator)
    tester_client = any_pointer.as_interface(restorer_capnp.AnyTester)
    expression_reader = any_pointer.as_struct(calculator_capnp.Calculator.Expression)
    expression_builder: calculator_capnp.types.builders.ExpressionBuilder = any_builder.as_struct(
        calculator_capnp.Calculator.Expression
    )
    restore_params_builder: restorer_capnp.types.builders.RestoreParamsBuilder = request.p.as_struct(
        restorer_capnp.Restorer.RestoreParams
    )
    int_list_builder: single_value_capnp.types.builders.Int32ListBuilder = any_builder.as_list(
        single_value_capnp.types.lists._Int32List
    )
    _ = (calculator_client, tester_client, expression_reader, expression_builder, restore_params_builder, int_list_builder)
""".strip(),
        encoding="utf8",
    )

    result = run_pyright(sample, cwd=REPO_ROOT)
    assert result.returncode == 0, result.stdout
