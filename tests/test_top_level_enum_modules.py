"""Tests for top-level enum helper module placement and runtime annotations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.test_helpers import run_command, run_pyright

if TYPE_CHECKING:
    from pathlib import Path

TOP_LEVEL_CLIMATE_ENUMS = ("GCM", "RCM", "SSP", "RCP", "Element")


def _climate_package_dir(zalfmas_stubs: Path) -> Path:
    """Return the generated climate schema package directory."""
    return zalfmas_stubs / "mas" / "schema" / "climate" / "climate_capnp"


def test_top_level_enum_helpers_live_in_types_modules(zalfmas_stubs: Path) -> None:
    """Top-level enum helper classes should live in `types.modules.pyi`, not `__init__.pyi`."""
    package_dir = _climate_package_dir(zalfmas_stubs)
    runtime_stub = (package_dir / "__init__.pyi").read_text()
    modules_stub = (package_dir / "types" / "modules.pyi").read_text()
    schemas_stub = (package_dir / "types" / "schemas.pyi").read_text()
    modules_runtime = (package_dir / "types" / "modules.py").read_text()

    for enum_name in TOP_LEVEL_CLIMATE_ENUMS:
        enum_helper_name = f"_{enum_name}EnumModule"
        assert f"{enum_name}: types.modules.{enum_helper_name}" in runtime_stub
        assert f"class {enum_helper_name}:" not in runtime_stub
        assert f"class {enum_helper_name}(_EnumModule):" in modules_stub
        assert f"def schema(self) -> schemas._{enum_name}EnumSchema: ..." in modules_stub
        assert f"type _{enum_name}EnumSchema = modules.{enum_helper_name}._{enum_name}Schema" in schemas_stub
        assert enum_helper_name not in modules_runtime


def test_runtime_types_modules_are_placeholders(zalfmas_stubs: Path) -> None:
    """Runtime helper modules under `types/` should stay empty placeholders except tuples."""
    package_dir = _climate_package_dir(zalfmas_stubs)
    types_dir = package_dir / "types"

    for relative_path in ("__init__.py", "modules.py", "servers.py", "results/__init__.py"):
        content = (types_dir / relative_path).read_text()
        assert "class " not in content
        assert "from typing import TYPE_CHECKING" not in content
        assert " = " not in content

    tuples_runtime = (types_dir / "results" / "tuples.py").read_text()
    assert "NamedTuple" in tuples_runtime


def test_top_level_enum_runtime_annotations_type_check(zalfmas_stubs: Path) -> None:
    """Top-level enum runtime objects and schemas should type check through their stub annotations."""
    test_file = zalfmas_stubs / "test_climate_enum_runtime_annotations.py"
    test_file.write_text(
        """
from mas.schema.climate import climate_capnp
from mas.schema.climate.climate_capnp.types.enums import ElementEnum, GCMEnum

def use_element(value: ElementEnum) -> None:
    pass

def use_gcm(value: GCMEnum) -> None:
    pass

use_element(climate_capnp.Element.tmin)
use_gcm(climate_capnp.GCM.cccmaCanEsm2)

element_schema = climate_capnp.Element.schema
resolution_schema = climate_capnp.TimeSeries.Resolution.schema
_ = element_schema.enumerants["tmin"]
_ = resolution_schema.enumerants["daily"]
""".lstrip(),
    )

    try:
        result = run_pyright(test_file, cwd=zalfmas_stubs)
    finally:
        test_file.unlink(missing_ok=True)

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed:\n{result.stdout}"


def test_climate_schema_helpers_keep_precise_nested_element_types(zalfmas_stubs: Path) -> None:
    """Schema helper stubs should keep concrete list element schemas for local and imported types."""
    modules_stub = (_climate_package_dir(zalfmas_stubs) / "types" / "modules.pyi").read_text()

    assert (
        "from mas.schema.common.common_capnp.types import schemas as _mas_schema_common_common_capnp_schemas"
        in modules_stub
    )
    assert "def elementType(self) -> schemas._ElementEnumSchema: ..." in modules_stub
    assert "def elementType(self) -> _mas_schema_common_common_capnp_schemas._IdInformationSchema: ..." in modules_stub
    assert "def elementType(self) -> _mas_schema_common_common_capnp_schemas._PairSchema: ..." in modules_stub


def test_climate_schema_helper_chains_type_check_precisely(zalfmas_stubs: Path) -> None:
    """Deep schema helper chains should preserve their concrete schema targets."""
    test_file = zalfmas_stubs / "test_climate_precise_schema_helpers.py"
    test_file.write_text(
        """
from mas.schema.climate import climate_capnp
from mas.schema.climate.climate_capnp.types import schemas as climate_schemas
from mas.schema.common.common_capnp.types import schemas as common_schemas

header_schema: climate_schemas._ElementEnumSchema = climate_capnp.TimeSeriesData.schema.fields["header"].schema.elementType
categories_schema: common_schemas._IdInformationSchema = climate_capnp.Metadata.Supported.schema.methods["categories"].result_type.fields["types"].schema.elementType
values_schema: common_schemas._IdInformationSchema = climate_capnp.Metadata.Supported.schema.methods["supportedValues"].result_type.fields["values"].schema.elementType
for_all_schema: common_schemas._PairSchema = climate_capnp.Metadata.Information.schema.methods["forAll"].result_type.fields["all"].schema.elementType
header_map_schema: common_schemas._PairSchema = climate_capnp.CSVTimeSeriesFactory.CSVConfig.schema.fields["headerMap"].schema.elementType
_ = (header_schema, categories_schema, values_schema, for_all_schema, header_map_schema)
""".lstrip(),
    )

    try:
        result = run_command(["basedpyright", str(test_file)], cwd=zalfmas_stubs)
    finally:
        test_file.unlink(missing_ok=True)

    assert result.returncode == 0, result.stdout or result.stderr
