"""Extended tests for capnproto stub generator covering multiple schema patterns."""

from __future__ import annotations

import re
from pathlib import Path

from tests.test_helpers import read_generated_types_lines

here = Path(__file__).parent
generated_dir = here / "_generated" / "basic"


def _get_stub_path(schema: str) -> Path:
    """Get path to a pre-generated schema package."""
    stub_name = f"{Path(schema).stem}_capnp"
    return generated_dir / stub_name


def test_primitives_and_lists_imports_and_types() -> None:
    """Test primitives and lists imports and types."""
    stub_path = _get_stub_path("primitives.capnp")
    lines = read_generated_types_lines(stub_path)
    content = "".join(lines)
    # Note: from __future__ import annotations is not needed with Python 3.10+ type annotations
    # Sequence and MutableSequence appear (list fields) from collections.abc
    # Note: With specific list classes, Sequence is only used for nested lists or setters
    # assert "Sequence" in content
    # assert "MutableSequence" in content
    # Literal now appears for list init overloads, overload appears for typed init methods
    assert "from typing import" in content
    assert "Literal" in content
    assert "overload" in content
    # Basic field annotations present (now as properties)
    assert any("def aBool(self) -> bool" in line for line in lines)
    # List fields use specific list classes
    assert any("def ints(self) -> Int32ListReader" in line for line in lines)


def test_nested_enum_and_literal_and_overload() -> None:
    """Test nested enum and literal and overload."""
    stub_path = _get_stub_path("nested.capnp")
    lines = read_generated_types_lines(stub_path)
    # Enum should now be a simple class with int annotations
    assert any(re.match(r"^\s*class _KindEnumModule:", line) for line in lines)
    assert any("Kind: _KindEnumModule" in line for line in lines)
    # Sequence import still expected for list fields (only for nested lists or setters)
    # Now overload is expected (for list init overloads)
    assert any("overload" in line for line in lines if line.startswith("from typing import"))


def test_unions_literal_and_overload_and_which() -> None:
    """Test unions literal and overload and which."""
    stub_path = _get_stub_path("unions.capnp")
    lines = read_generated_types_lines(stub_path)
    # Expect Literal import (union which methods)
    assert any(line.startswith("from typing import") and "Literal" in line for line in lines)
    # Overload is only imported when there are multiple init methods (2+)
    # unions.capnp doesn't have multiple init methods, so no overload import
    # 'which' function should appear for discriminantCount > 0
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)


def test_interfaces_protocol_and_any_and_iterator() -> None:
    """Test interfaces protocol and any and iterator."""
    stub_path = _get_stub_path("interfaces.capnp")
    lines = read_generated_types_lines(stub_path)
    content = "".join(lines)
    # Protocol import expected
    assert any(line.startswith("from typing import") and "Protocol" in line for line in lines)
    # Interface methods now have result types (may be multi-line)
    # greet should have GreetResult return type
    assert "def greet(" in content
    assert "name: str" in content
    # streamNumbers should have count parameter
    assert "def streamNumbers(" in content
    assert "count: int" in content


def test_imports_cross_module_reference() -> None:
    # Use pre-generated stubs from basic directory
    # Both import_base and import_user should already be generated together
    """Test imports cross module reference."""
    user_lines = read_generated_types_lines(generated_dir / "import_user_capnp")
    # With nested structure, Shared.Reader and Shared.Builder are used
    # Reader class should return Shared.Reader
    # Now we use aliases, so it should be SharedReader
    assert any("def shared(self) -> SharedReader:" in line for line in user_lines) or any(
        "def shared(self) -> _SharedStructModule.Reader:" in line for line in user_lines
    ), "Reader class should return Shared.Reader or SharedReader"
    # Builder class should narrow to Shared.Builder
    assert any("def shared(self) -> SharedBuilder:" in line for line in user_lines) or any(
        "def shared(self) -> _SharedStructModule.Builder:" in line for line in user_lines
    ), "Builder class should return Shared.Builder or SharedBuilder"
    # Ensure import statement for base module types exists (imports Protocol module, not user-facing name)
    # Now we also import aliases
    assert any(line.startswith("from ") and "import _SharedStructModule" in line for line in user_lines) or any(
        line.startswith("from ") and "SharedReader" in line for line in user_lines
    )
