"""Extended tests for capnproto stub generator covering multiple schema patterns."""

from __future__ import annotations

import re
from pathlib import Path

here = Path(__file__).parent
generated_dir = here / "_generated" / "basic"


def _read(path: str | Path) -> list[str]:
    with open(path, encoding="utf8") as f:
        return f.readlines()


def _get_stub_path(schema: str) -> Path:
    """Get path to pre-generated stub file."""
    stub_name = f"{Path(schema).stem}_capnp.pyi"
    return generated_dir / stub_name


def test_primitives_and_lists_imports_and_types():
    stub_path = _get_stub_path("primitives.capnp")
    lines = _read(stub_path)
    content = "".join(lines)
    assert "from __future__ import annotations" in content
    # Sequence and MutableSequence appear (list fields) from collections.abc
    assert "from collections.abc import" in content
    assert "Sequence" in content
    assert "MutableSequence" in content
    # Literal now appears for list init overloads, overload appears for typed init methods
    assert "from typing import" in content
    assert "Literal" in content
    assert "overload" in content
    # Basic field annotations present (now as properties)
    assert any("def aBool(self) -> bool" in line for line in lines)
    assert any("def ints(self) -> Sequence[int]" in line for line in lines)


def test_nested_enum_and_literal_and_overload():
    stub_path = _get_stub_path("nested.capnp")
    lines = _read(stub_path)
    # Enum should now be a real Enum class with TypeAlias, not a Protocol
    assert any(re.match(r"^\s*class _KindModule\(Enum\):", line) for line in lines)
    assert any("Kind: TypeAlias = _KindModule" in line for line in lines)
    # Ensure Enum import present
    assert any(line.startswith("from enum import") and "Enum" in line for line in lines)
    # Ensure TypeAlias import present
    assert any(line.startswith("from typing import") and "TypeAlias" in line for line in lines)
    # Sequence import still expected for list fields
    assert any(line.startswith("from collections.abc import") and "Sequence" in line for line in lines)
    # Now overload is expected (for list init overloads)
    assert any("overload" in line for line in lines if line.startswith("from typing import"))


def test_unions_literal_and_overload_and_which():
    stub_path = _get_stub_path("unions.capnp")
    lines = _read(stub_path)
    # Expect Literal import (union which methods)
    assert any(line.startswith("from typing import") and "Literal" in line for line in lines)
    # Overload is only imported when there are multiple init methods (2+)
    # unions.capnp doesn't have multiple init methods, so no overload import
    # 'which' function should appear for discriminantCount > 0
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)


def test_interfaces_protocol_and_any_and_iterator():
    stub_path = _get_stub_path("interfaces.capnp")
    lines = _read(stub_path)
    # Protocol import expected
    assert any(line.startswith("from typing import") and "Protocol" in line for line in lines)
    # Iterator from collections.abc
    assert any(line.startswith("from collections.abc import") and "Iterator" in line for line in lines)
    # Interface methods now have result types
    # greet should have GreetResult return type (not bare str)
    assert any("def greet" in line and "name: str" in line and "GreetResult" in line for line in lines)
    # streamNumbers should have StreamnumbersResult return type
    assert any("def streamNumbers" in line and "count: int" in line and "StreamnumbersResult" in line for line in lines)


def test_imports_cross_module_reference():
    # Use pre-generated stubs from basic directory
    # Both import_base and import_user should already be generated together
    user_stub = generated_dir / "import_user_capnp.pyi"
    user_lines = _read(user_stub)
    # With nested structure, Shared.Reader and Shared.Builder are used
    # Reader class should return Shared.Reader
    assert any("def shared(self) -> _SharedModule.Reader:" in line for line in user_lines), (
        "Reader class should return Shared.Reader"
    )
    # Builder class should narrow to Shared.Builder
    assert any("def shared(self) -> _SharedModule.Builder:" in line for line in user_lines), (
        "Builder class should return Shared.Builder"
    )
    # Ensure import statement for base module types exists (imports Protocol module, not user-facing name)
    assert any(line.startswith("from ") and "import _SharedModule" in line for line in user_lines)
