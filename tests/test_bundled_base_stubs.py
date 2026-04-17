"""Regression tests for the bundled base pycapnp stubs."""

from __future__ import annotations

import difflib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLED_STUBS_DIR = REPO_ROOT / "src" / "pycapnp_base_stubs"
TYPINGS_STUBS_DIR = REPO_ROOT / "typings" / "capnp-stubs"
_AUGMENTED_OVERLOAD_METHODS = {
    "_DynamicObjectReader": {"as_interface", "as_struct"},
    "_CapabilityClient": {"cast_as"},
}


def _stub_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def _normalize_stub(relative_path: str, content: str) -> str:
    if relative_path != "lib/capnp.pyi":
        return content

    content = content.replace("from capnp._internal import", "from .._internal import")
    lines = _strip_generated_import_block(content.splitlines())
    lines = _strip_augmented_overload_blocks(lines)
    return "\n".join(lines)


def _strip_generated_import_block(lines: list[str]) -> list[str]:
    marker = "# Generated imports for project-specific types"

    try:
        start = lines.index(marker)
    except ValueError:
        return lines

    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.startswith(("from .._internal import", "from capnp._internal import")):
            break
        end += 1

    prefix = lines[:start]
    suffix = lines[end:]
    if (
        prefix
        and prefix[-1]
        not in ("", "# Type alias for anypointer to reflect what is really allowed for anypointer inputs")
        and suffix
        and suffix[0].startswith("from ")
    ):
        prefix.append("")

    return prefix + suffix


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

            while next_index < len(lines) and lines[next_index] == "":
                next_index += 1

            next_method_line = lines[next_index] if next_index < len(lines) else ""
            if _method_name(next_method_line) in _AUGMENTED_OVERLOAD_METHODS[current_class]:
                index = next_index
                continue

        normalized.append(line)
        index += 1

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
