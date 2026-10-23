# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportUnknownMemberType=false
"""This is an automatically generated stub for `addressbook.capnp`."""

# Load schemas and build module structure
from importlib import import_module as _import_module
from typing import cast as _cast

from capnp.lib.capnp import SchemaLoader as _SchemaLoader
from capnp.lib.capnp import _EnumModule, _StructModule

from . import types as types


def _import_schema_bundle() -> object:
    bundle_module_name = "_capnp_schema_bundle_d3c9427f3b0f"
    try:
        return _import_module(bundle_module_name)
    except ModuleNotFoundError as error:
        original_error = error
        package_name = __package__

    while package_name:
        try:
            return _import_module(f"{package_name}.{bundle_module_name}")
        except ModuleNotFoundError:
            package_name = package_name.rpartition(".")[0]

    raise original_error


_schema_bundle = _import_schema_bundle()


def get_schema_by_id(schema_id: int) -> object:
    return _cast("object", _schema_bundle.get_schema_by_id(schema_id))


def load_capnp_file(path: str, imports: list[str] | tuple[str, ...] = ()) -> object:
    return _cast("object", _schema_bundle.load_capnp_file(path, imports))


_loader: _SchemaLoader = _cast("_SchemaLoader", _schema_bundle.get_schema_loader())

# Build module structure inline

qux = _loader.get(0xA4715ADA13E1E979).as_const_value()
Person = _StructModule(
    _loader.get(0xA667DB69AAB2A9A8).as_struct(),
    "Person",
)
Person.PhoneNumber = _StructModule(
    Person.schema.fields["phones"].schema.elementType,
    "PhoneNumber",
)
Person.PhoneNumber.Type = _EnumModule(
    Person.PhoneNumber.schema.fields["type"].schema,
    "Type",
)
AddressBook = _StructModule(
    _loader.get(0xDED4381D608D5D17).as_struct(),
    "AddressBook",
)

__all__ = ["AddressBook", "Person", "get_schema_by_id", "load_capnp_file", "qux", "types"]
