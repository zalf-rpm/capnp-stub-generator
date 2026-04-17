"""Regression tests for the bundled base pycapnp stubs."""

from __future__ import annotations

import difflib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLED_STUBS_DIR = REPO_ROOT / "src" / "pycapnp_base_stubs"
TYPINGS_STUBS_DIR = REPO_ROOT / "typings" / "capnp-stubs"
_AUGMENTED_OVERLOAD_METHODS = {
    "_DynamicObjectReader": {"as_interface", "as_list", "as_struct"},
    "_CapabilityClient": {"cast_as"},
}


def _stub_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def _normalize_stub(relative_path: str, content: str) -> str:
    if relative_path != "lib/capnp.pyi":
        return content

    content = content.replace("from capnp._internal import", "from .._internal import")
    lines = _strip_project_specific_imports(content.splitlines())
    lines = _normalize_capnp_preamble(lines)
    lines = _strip_augmented_overload_blocks(lines)
    lines = _restore_method_spacing(lines)
    return "\n".join(lines)


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
