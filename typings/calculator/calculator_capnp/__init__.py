# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportUnknownMemberType=false
"""This is an automatically generated stub for `calculator.capnp`."""

from __future__ import annotations

# Load schemas and build module structure
from importlib import import_module
from typing import cast

from capnp.lib.capnp import SchemaLoader, _EnumModule, _InterfaceModule, _StructModule


def _import_schema_bundle() -> object:
    bundle_module_name = "_capnp_schema_bundle_d3c9427f3b0f"
    try:
        return import_module(bundle_module_name)
    except ModuleNotFoundError as error:
        original_error = error
        package_name = __package__

    while package_name:
        try:
            return import_module(f"{package_name}.{bundle_module_name}")
        except ModuleNotFoundError:
            package_name = package_name.rpartition(".")[0]

    raise original_error


_schema_bundle = _import_schema_bundle()


def get_schema_by_id(schema_id: int) -> object:
    return cast("object", _schema_bundle.get_schema_by_id(schema_id))


def load_capnp_file(path: str, imports: list[str] | tuple[str, ...] = ()) -> object:
    return cast("object", _schema_bundle.load_capnp_file(path, imports))


_loader: SchemaLoader = cast("SchemaLoader", _schema_bundle.get_schema_loader())

# Build module structure inline

Calculator = _InterfaceModule(
    _loader.get(0x97983392DF35CC36).as_interface(),
    "Calculator",
)
Calculator.Expression = _StructModule(
    Calculator.schema.methods["evaluate"].param_type.fields["expression"].schema,  # pyright: ignore[reportUnknownArgumentType]
    "Expression",
)
Calculator.Value = _InterfaceModule(
    Calculator.schema.methods["evaluate"].param_type.fields["expression"].schema.fields["previousResult"].schema,  # pyright: ignore[reportUnknownArgumentType]
    "Value",
)
Calculator.Function = _InterfaceModule(
    Calculator.schema.methods["defFunction"].result_type.fields["func"].schema,  # pyright: ignore[reportUnknownArgumentType]
    "Function",
)
Calculator.Operator = _EnumModule(
    Calculator.schema.methods["getOperator"].param_type.fields["op"].schema,  # pyright: ignore[reportUnknownArgumentType]
    "Operator",
)
