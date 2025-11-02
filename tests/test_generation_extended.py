"""Extended tests for capnproto stub generator covering multiple schema patterns."""

from __future__ import annotations

import os
import re

from capnp_stub_generator.cli import main

here = os.path.dirname(__file__)


def _read(path: str) -> list[str]:
    with open(path, encoding="utf8") as f:
        return f.readlines()


def _generate(schema: str) -> str:
    out_dir = os.path.join(here, "_generated")
    os.makedirs(out_dir, exist_ok=True)
    main(["-p", os.path.join(here, "schemas", schema), "-o", out_dir])
    return os.path.join(out_dir, f"{os.path.splitext(schema)[0]}_capnp.pyi")


def test_primitives_and_lists_imports_and_types():
    out = _generate("primitives.capnp")
    lines = _read(out)
    header = "".join(lines[:15])
    assert "from __future__ import annotations" in header
    # Iterator appears (for from_bytes) and Sequence appears (list fields) from collections.abc
    assert any(
        line.startswith("from collections.abc import") and "Iterator" in line and "Sequence" in line
        for line in lines
    )
    # Literal now appears for list init overloads, overload appears for typed init methods
    assert any(
        line.startswith("from typing import") and "Literal" in line and "overload" in line
        for line in lines
    )
    # Basic field annotations present
    assert any("aBool:" in line and "bool" in line for line in lines)
    assert any("ints:" in line and "Sequence[int]" in line for line in lines)


def test_nested_enum_and_literal_and_overload():
    out = _generate("nested.capnp")
    lines = _read(out)
    # Enum should now be a real Enum subclass, not a Literal alias
    assert any(re.match(r"^\s*class Kind\(Enum\):", line) for line in lines)
    # Ensure Enum import present
    assert any(line.startswith("from enum import") and "Enum" in line for line in lines)
    # Sequence import still expected for list fields
    assert any(
        line.startswith("from collections.abc import") and "Sequence" in line for line in lines
    )
    # Now overload is expected (for list init overloads)
    assert any("overload" in line for line in lines if line.startswith("from typing import"))


def test_unions_literal_and_overload_and_which():
    out = _generate("unions.capnp")
    lines = _read(out)
    # Expect Literal import (union which methods) and overload import (for init overloads including lists)
    assert any(line.startswith("from typing import") and "Literal" in line for line in lines)
    # Overload is now expected for list init methods
    assert any(line.startswith("from typing import") and "overload" in line for line in lines)
    # 'which' function should appear for discriminantCount > 0
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", line) for line in lines)


def test_interfaces_protocol_and_any_and_iterator():
    out = _generate("interfaces.capnp")
    lines = _read(out)
    # Protocol import expected
    assert any(line.startswith("from typing import") and "Protocol" in line for line in lines)
    # Iterator from collections.abc
    assert any(
        line.startswith("from collections.abc import") and "Iterator" in line for line in lines
    )
    # Any usage in method parameters or return types (interface methods use Any)
    # Concrete interface param/return typing now applied
    assert any("def greet" in line and "name: str" in line and "-> str" in line for line in lines)
    assert any(
        "def streamNumbers" in line and "count: int" in line and "-> int" in line for line in lines
    )


def test_imports_cross_module_reference():
    # Generate base first then user module to ensure registry contains imported types
    # Generate both modules together so registry contains both
    out_dir = os.path.join(here, "_generated")
    os.makedirs(out_dir, exist_ok=True)
    main(
        [
            "-p",
            os.path.join(here, "schemas", "import_base.capnp"),
            os.path.join(here, "schemas", "import_user.capnp"),
            "-o",
            out_dir,
        ]
    )
    user_out = os.path.join(out_dir, "import_user_capnp.pyi")
    user_lines = _read(user_out)
    # Imported type reference should include builders/readers in a union style annotation
    assert any(
        "shared:" in line and "SharedBuilder" in line and "SharedReader" in line
        for line in user_lines
    )
    # Ensure import statement for base module types exists
    assert any(
        line.startswith("from ") and "import Shared, SharedBuilder, SharedReader" in line
        for line in user_lines
    )
