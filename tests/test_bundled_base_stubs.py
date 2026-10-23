"""Regression tests for the bundled base pycapnp stubs."""

from __future__ import annotations

import ast
import difflib
import inspect
import re
from pathlib import Path

import capnp

import schema_capnp
from tests.test_helpers import run_pyright

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLED_STUBS_DIR = REPO_ROOT / "src" / "pycapnp_base_stubs"
TYPINGS_STUBS_DIR = REPO_ROOT / "typings" / "capnp-stubs"
_AUGMENTED_OVERLOAD_METHODS = {
    "_DynamicObjectBuilder": {"as_interface", "as_list", "as_struct"},
    "_DynamicObjectReader": {"as_interface", "as_list", "as_struct"},
    "_CapabilityClient": {"cast_as"},
    "_DynamicCapabilityClient": {"cast_as"},
}


def _stub_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def _normalize_stub(relative_path: str, content: str) -> str:
    if relative_path != "lib/capnp.pyi":
        return content

    lines = _strip_project_specific_imports(content.splitlines())
    lines = _normalize_capnp_preamble(lines)
    lines = _strip_augmented_overload_blocks(lines)
    lines = _restore_method_spacing(lines)
    return "\n".join(line for line in lines if line)


def _strip_project_specific_imports(lines: list[str]) -> list[str]:
    project_import = re.compile(r"from [A-Za-z_][A-Za-z0-9_]* import [A-Za-z_][A-Za-z0-9_]*_capnp$")
    return [
        line
        for line in lines
        if line != "# Generated imports for project-specific types" and not project_import.fullmatch(line)
    ]


def _normalize_capnp_preamble(lines: list[str]) -> list[str]:
    type_alias_marker = "type AnyPointer = ("
    try:
        preamble_end = lines.index(type_alias_marker)
    except ValueError:
        return lines

    preamble = lines[:preamble_end]
    remainder = lines[preamble_end:]

    schema_block: list[str] = []
    internal_block: list[str] = []
    header: list[str] = []
    collecting_internal = False

    for line in preamble:
        if line == "# Import schema.capnp types for precise node property types":
            schema_block = [
                "# Import schema.capnp types for precise node property types",
                "# These are _DynamicStructReader at runtime but typed more precisely",
                "from schema_capnp import FieldReader as _SchemaFieldReader",
                "from schema_capnp import NodeReader as _SchemaNodeReader",
            ]
            continue

        if line.startswith("from .._internal import"):
            collecting_internal = True
            internal_block.append(line)
            continue

        if collecting_internal:
            internal_block.append(line)
            if line == ")":
                collecting_internal = False
            continue

        if line in {
            "# These are _DynamicStructReader at runtime but typed more precisely",
            "from schema_capnp import FieldReader as _SchemaFieldReader",
            "from schema_capnp import NodeReader as _SchemaNodeReader",
            "# Type alias for anypointer to reflect what is really allowed for anypointer inputs",
            "",
        }:
            continue

        header.append(line)

    normalized = [*header, ""]
    if schema_block:
        normalized.extend([*schema_block, ""])
    normalized.append("# Type alias for anypointer to reflect what is really allowed for anypointer inputs")
    normalized.extend(internal_block)
    normalized.append("")
    return normalized + remainder


def _strip_augmented_overload_blocks(lines: list[str]) -> list[str]:
    normalized: list[str] = []
    current_class: str | None = None
    index = 0

    while index < len(lines):
        line = lines[index]
        if line.startswith("class "):
            current_class = line.split()[1].split("(", 1)[0].rstrip(":")

        if line == "    @overload" and current_class in _AUGMENTED_OVERLOAD_METHODS:
            next_index = index
            while next_index < len(lines) and lines[next_index] == "    @overload":
                next_index += 1
                while next_index < len(lines):
                    if lines[next_index].strip().endswith("..."):
                        next_index += 1
                        break
                    next_index += 1

            skipped_blank_lines = False
            while next_index < len(lines) and lines[next_index] == "":
                skipped_blank_lines = True
                next_index += 1

            next_method_line = lines[next_index] if next_index < len(lines) else ""
            if _method_name(next_method_line) in _AUGMENTED_OVERLOAD_METHODS[current_class]:
                if skipped_blank_lines and normalized and normalized[-1] != "":
                    normalized.append("")
                index = next_index
                continue

        normalized.append(line)
        index += 1

    return normalized


def _restore_method_spacing(lines: list[str]) -> list[str]:
    normalized: list[str] = []

    for index, line in enumerate(lines):
        normalized.append(line)
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        if line == '        """' and next_line.startswith("    def "):
            normalized.append("")

    return normalized


def _method_name(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("def "):
        return None
    return stripped[4:].split("(", 1)[0]


def _diff_message(relative_path: str, bundled: str, typings: str) -> str:
    diff = "".join(
        difflib.unified_diff(
            bundled.splitlines(keepends=True),
            typings.splitlines(keepends=True),
            fromfile=f"src/pycapnp_base_stubs/{relative_path}",
            tofile=f"typings/capnp-stubs/{relative_path}",
        ),
    )
    return f"{relative_path} drifted from typings/capnp-stubs:\n{diff}"


def _runtime_source_doc(runtime_object: object, *, is_class: bool) -> str | None:
    """Recover the authored docstring while dropping Cython's embedded signature."""
    raw_doc = getattr(runtime_object, "__doc__", None)
    if not raw_doc:
        return None

    doc = inspect.cleandoc(raw_doc)
    first_paragraph, separator, remainder = doc.partition("\n\n")
    callable_name, opening_parenthesis, _ = first_paragraph.partition("(")
    starts_with_signature = bool(
        opening_parenthesis
        and callable_name
        and all(name_part.isidentifier() for name_part in callable_name.split("."))
    )

    if starts_with_signature:
        if not separator:
            return None
        doc = inspect.cleandoc(remainder)
    if not is_class and not separator:
        return None
    return "\n".join(line.rstrip() for line in doc.splitlines()) or None


def _stub_declarations(
    body: list[ast.stmt],
    prefix: tuple[str, ...] = (),
) -> list[tuple[tuple[str, ...], ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef]]:
    declarations: list[tuple[tuple[str, ...], ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef]] = []
    for declaration in body:
        if isinstance(declaration, ast.ClassDef):
            qualified_name = (*prefix, declaration.name)
            declarations.append((qualified_name, declaration))
            declarations.extend(_stub_declarations(declaration.body, qualified_name))
        elif isinstance(declaration, (ast.FunctionDef, ast.AsyncFunctionDef)):
            declarations.append(((*prefix, declaration.name), declaration))
    return declarations


def test_bundled_base_stubs_match_typings_module() -> None:
    """Keep the bundled stubs aligned with the checked-in typings module."""
    bundled_files = _stub_files(BUNDLED_STUBS_DIR)
    typings_files = _stub_files(TYPINGS_STUBS_DIR)

    assert bundled_files == typings_files

    for relative_path in sorted(typings_files):
        bundled_content = _normalize_stub(
            relative_path,
            (BUNDLED_STUBS_DIR / relative_path).read_text(encoding="utf8"),
        )
        typings_content = _normalize_stub(
            relative_path,
            (TYPINGS_STUBS_DIR / relative_path).read_text(encoding="utf8"),
        )

        assert bundled_content == typings_content, _diff_message(relative_path, bundled_content, typings_content)


def test_bundled_base_stub_docstrings_match_runtime_source_docs() -> None:
    """Editor help should retain authored pyx docs without adding synthetic documentation."""
    content = (BUNDLED_STUBS_DIR / "lib" / "capnp.pyi").read_text(encoding="utf8")
    tree = ast.parse(content)
    runtime_module = capnp.lib.capnp

    for qualified_name, declaration in _stub_declarations(tree.body):
        runtime_object: object = runtime_module
        try:
            for name_part in qualified_name:
                runtime_object = getattr(runtime_object, name_part)
        except AttributeError:
            continue

        expected = _runtime_source_doc(runtime_object, is_class=isinstance(declaration, ast.ClassDef))
        actual = ast.get_docstring(declaration, clean=True)
        assert actual == expected, f"docstring mismatch for {'.'.join(qualified_name)}"


def test_bundled_base_stubs_do_not_invent_capnp_modules_or_types() -> None:
    """The bundled surface must describe runtime objects instead of typing-only capnp helpers."""
    files = _stub_files(BUNDLED_STUBS_DIR)
    content = (BUNDLED_STUBS_DIR / "lib" / "capnp.pyi").read_text(encoding="utf8")

    assert "_internal.pyi" not in files
    assert "capnp._internal" not in content
    assert "schema_capnp" not in content
    assert "type AnyPointer" not in content
    assert "type Capability" not in content
    assert "CapnpModule" not in content
    assert "CapnpTypesModule" not in content
    assert "__all__" not in content


def test_bundled_base_stub_classes_match_runtime_names_and_inheritance() -> None:
    """Every declared pycapnp class and base class must exist in the 2.2.4 runtime."""
    content = (BUNDLED_STUBS_DIR / "lib" / "capnp.pyi").read_text(encoding="utf8")
    tree = ast.parse(content)
    runtime_module = capnp.lib.capnp

    for declaration in tree.body:
        if not isinstance(declaration, ast.ClassDef):
            continue

        assert hasattr(runtime_module, declaration.name), f"stub-only class: {declaration.name}"
        runtime_class = getattr(runtime_module, declaration.name)
        stub_bases = [ast.unparse(base).split(".")[-1] for base in declaration.bases]
        runtime_bases = [base.__name__ for base in runtime_class.__bases__ if base is not object]
        assert stub_bases == runtime_bases, f"incorrect bases for {declaration.name}"


def test_bundled_base_stub_targets_pycapnp_224_surface() -> None:
    """Keep the bundled surface on the selected 2.2.4 release boundary."""
    content = (BUNDLED_STUBS_DIR / "lib" / "capnp.pyi").read_text(encoding="utf8")

    assert "class _AsyncIoStream:" in content
    assert "class AsyncIoStream:" not in content
    assert "def get_data_as_view(self, field: str) -> memoryview:" in content
    assert "def to_segment_views(" not in content
    assert "class _RemotePromise:" in content
    assert "class _RemotePromise(_Promise):" not in content
    assert "class _DynamicCapabilityClient:" in content
    assert "class _DynamicCapabilityClient(_CapabilityClient):" not in content

    root_content = (BUNDLED_STUBS_DIR / "__init__.pyi").read_text(encoding="utf8")
    assert "from capnp.lib.capnp import _AsyncIoStream\n" in root_content
    assert "AsyncIoStream = _AsyncIoStream" in root_content
    assert "_AsyncIoStream as _AsyncIoStream" not in root_content
    assert "from capnp.lib import capnp as _capnp" not in root_content
    assert "__version__: str" in root_content
    assert "version as _version" not in root_content

    assert "reverse_mapping: dict[str, str]" in content
    assert "class _StructModuleWhich(enum.Enum):" in content
    assert "__hash__: None" in content
    assert re.search(
        r"async def read_async\(.*?\) -> _DynamicStructReader \| None:",
        content,
        re.DOTALL,
    )


def test_bundled_types_stub_matches_runtime_schema_singletons() -> None:
    """Type the real ``capnp.types`` module without introducing a wrapper class."""
    content = (BUNDLED_STUBS_DIR / "types.pyi").read_text(encoding="utf8")
    tree = ast.parse(content)
    declared = {
        statement.target.id
        for statement in tree.body
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name)
    }
    runtime_names = {name for name in vars(capnp.types) if not name.startswith("_")}

    assert declared == runtime_names
    assert all(type(getattr(capnp.types, name)) is capnp.lib.capnp._SchemaType for name in declared)


def test_bundled_root_exports_precise_types_module(tmp_path: Path) -> None:
    """The root re-export should preserve the concrete built-in schema descriptor types."""
    sample = tmp_path / "test_capnp_types.py"
    sample.write_text(
        """from typing import assert_type

import capnp
import capnp.types
from capnp.lib.capnp import _AsyncIoStream, _SchemaType

assert_type(capnp.__version__, str)
assert_type(capnp.AsyncIoStream, type[_AsyncIoStream])
assert_type(capnp.types.Int32, _SchemaType)
assert_type(capnp.types.AnyPointer, _SchemaType)
""",
        encoding="utf8",
    )

    result = run_pyright(sample)
    assert result.returncode == 0, result.stdout


def test_schema_capnp_element_size_matches_runtime_enum_module() -> None:
    """The bundled system-schema stub should expose every runtime ElementSize member."""
    content = (REPO_ROOT / "src" / "schema_capnp" / "__init__.pyi").read_text(encoding="utf8")
    runtime_members = {name for name in vars(schema_capnp.ElementSize) if not name.startswith("_") and name != "schema"}

    assert "class _ElementSizeEnumModule(_EnumModule):" in content
    assert "ElementSize: _ElementSizeEnumModule" in content
    assert runtime_members == {
        "empty",
        "bit",
        "byte",
        "twoBytes",
        "fourBytes",
        "eightBytes",
        "pointer",
        "inlineComposite",
    }
    for member in runtime_members:
        assert f"    {member}: int" in content


def test_bundled_interface_method_stub_is_nongeneric() -> None:
    """Bundled interface method helpers should stay precise without generic base schemas."""
    contents = (
        (BUNDLED_STUBS_DIR / "lib" / "capnp.pyi").read_text(encoding="utf8"),
        (TYPINGS_STUBS_DIR / "lib" / "capnp.pyi").read_text(encoding="utf8"),
    )

    for content in contents:
        assert "TypeVar(" not in content
        assert "Generic[" not in content
        assert "_InterfaceMethod[" not in content
        assert "class _InterfaceMethod:" in content
        assert "@property\n    def param_type(self) -> _StructSchema: ..." in content
        assert "@property\n    def result_type(self) -> _StructSchema: ..." in content
        assert "def methods(self) -> dict[str, _InterfaceMethod]:" in content
        assert "def methods_inherited(self) -> dict[str, _InterfaceMethod]:" in content


def test_bundled_promise_stubs_do_not_advertise_wait() -> None:
    """Bundled promise stubs should not claim support for wait()."""
    contents = (
        (BUNDLED_STUBS_DIR / "lib" / "capnp.pyi").read_text(encoding="utf8"),
        (TYPINGS_STUBS_DIR / "lib" / "capnp.pyi").read_text(encoding="utf8"),
    )

    for content in contents:
        promise_block = re.search(r"class _Promise:.*?(?=\nclass |\Z)", content, re.DOTALL)
        remote_promise_block = re.search(r"class _RemotePromise.*?(?=\nclass |\Z)", content, re.DOTALL)

        assert promise_block is not None
        assert remote_promise_block is not None
        assert "def cancel(" in promise_block.group(0)
        assert "def wait(" not in promise_block.group(0)
        assert "def wait(" not in remote_promise_block.group(0)


def test_typings_snapshot_includes_dynamic_object_builder_overloads() -> None:
    """The augmented capnp-stubs snapshot should add builder-side schema overloads too."""
    content = (TYPINGS_STUBS_DIR / "lib" / "capnp.pyi").read_text(encoding="utf8")

    assert (
        "schema: calculator_capnp.types.modules._CalculatorInterfaceModule._ExpressionStructModule,\n"
        "    ) -> calculator_capnp.types.builders.ExpressionBuilder: ..."
    ) in content
    assert (
        "schema: restorer_capnp.types.modules._AnyTesterInterfaceModule,\n"
        "    ) -> restorer_capnp.types.clients.AnyTesterClient: ..."
    ) in content
    assert (
        "schema: type[single_value_capnp.types.lists._MyStructList],\n"
        "    ) -> single_value_capnp.types.builders.MyStructListBuilder: ..."
    ) in content
