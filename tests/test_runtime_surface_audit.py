"""Runtime-shape regressions for generated schema packages."""

from __future__ import annotations

import ast
import importlib
from typing import TYPE_CHECKING, cast

import capnp

if TYPE_CHECKING:
    from pathlib import Path


def _class_definition(stub: Path, name: str) -> ast.ClassDef:
    tree = ast.parse(stub.read_text(encoding="utf8"))
    return next(node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name == name)


def _module_which_attributes(declaration: ast.ClassDef) -> set[str]:
    return {
        target.id
        for statement in declaration.body
        if isinstance(statement, ast.AnnAssign)
        and isinstance((target := statement.target), ast.Name)
        and "ModuleWhich" in ast.unparse(statement.annotation)
    }


def test_generated_runtime_module_has_no_public_loader_helpers(basic_stubs: Path) -> None:
    """The generated Python loader should expose exactly its declared runtime API."""
    module = importlib.import_module("tests._generated.basic.dummy_capnp")
    public_names = {name for name in vars(module) if not name.startswith("_")}

    assert public_names == set(module.__all__)
    assert {"types", "get_schema_by_id", "load_capnp_file"} <= public_names
    assert {"annotations", "cast", "import_module", "SchemaLoader"}.isdisjoint(public_names)

    runtime_source = (basic_stubs / "dummy_capnp" / "__init__.py").read_text(encoding="utf8")
    assert "from __future__ import annotations" not in runtime_source
    assert "import_module as _import_module" in runtime_source
    assert "cast as _cast" in runtime_source
    assert "SchemaLoader as _SchemaLoader" in runtime_source


def test_generated_group_module_names_match_runtime(basic_stubs: Path) -> None:
    """Only publish the group/discriminant names that pycapnp creates at runtime."""
    module = importlib.import_module("tests._generated.basic.dummy_capnp")
    modules_stub = basic_stubs / "dummy_capnp" / "types" / "modules.pyi"

    cases = {
        "TestUnion": "_TestUnionStructModule",
        "TestGroups": "_TestGroupsStructModule",
        "TestInterleavedGroups": "_TestInterleavedGroupsStructModule",
    }
    for runtime_name, stub_name in cases.items():
        runtime_module = getattr(module, runtime_name)
        runtime_namespace = cast("dict[str, object]", vars(runtime_module))
        runtime_markers = {name for name, value in runtime_namespace.items() if type(value).__name__ == "EnumType"}
        stub_markers = _module_which_attributes(_class_definition(modules_stub, stub_name))
        assert stub_markers == runtime_markers

    content = modules_stub.read_text(encoding="utf8")
    assert "TestUnionUnion0:" not in content
    assert "TestGroupsGroups:" not in content
    assert "TestInterleavedGroupsGroup1:" not in content


def test_generated_nonprimitive_constants_match_runtime_types(basic_stubs: Path) -> None:
    """Struct, enum, and list constants should retain their concrete runtime reader types."""
    module = importlib.import_module("tests._generated.basic.dummy_capnp")
    root_stub = (basic_stubs / "dummy_capnp" / "__init__.pyi").read_text(encoding="utf8")
    modules_stub = (basic_stubs / "dummy_capnp" / "types" / "modules.pyi").read_text(encoding="utf8")

    assert "globalStruct: types.readers.TestAllTypesReader" in root_stub
    assert "globalPrintableStruct: types.readers.TestPrintInlineStructsReader" in root_stub
    assert "derivedConstant: types.readers.TestAllTypesReader" in root_stub
    assert "structConst: readers.TestAllTypesReader" in modules_stub
    assert "enumConst: enums.TestEnumValue" in modules_stub
    assert "structListConst: readers.TestAllTypesListReader" in modules_stub
    assert "enumListConst: readers.TestEnumEnumListReader" in modules_stub

    assert type(module.globalStruct) is capnp.lib.capnp._DynamicStructReader
    assert type(module.TestConstants.structConst) is capnp.lib.capnp._DynamicStructReader
    assert type(module.TestConstants.enumConst) is capnp.lib.capnp._DynamicEnum
    assert type(module.TestConstants.structListConst) is capnp.lib.capnp._DynamicListReader


def test_generated_struct_modules_refine_real_runtime_methods(basic_stubs: Path) -> None:
    """Schema-specific modules should narrow real methods without adding helper-only methods."""
    content = (basic_stubs / "dummy_capnp" / "types" / "modules.pyi").read_text(encoding="utf8")

    for method_name in (
        "from_bytes_packed",
        "from_segments",
        "read_async",
        "read_multiple",
        "read_multiple_packed",
        "read_multiple_bytes",
        "read_multiple_bytes_packed",
        "__call__",
    ):
        assert f"def {method_name}(" in content or f"async def {method_name}(" in content

    assert "readers.TestAllTypesReader | None" in content
    assert "allocate_seg_callable: Callable[[int], Any] | None = None" in content
