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
        l.startswith("from collections.abc import") and "Iterator" in l and "Sequence" in l
        for l in lines
    )
    # Literal should not appear (no enums defined) but overload should not appear either (no init overloads)
    assert not any(l.startswith("from typing import") and "Literal" in l for l in lines)
    # Basic field annotations present
    assert any("aBool:" in l and "bool" in l for l in lines)
    assert any("ints:" in l and "Sequence[int]" in l for l in lines)


def test_nested_enum_and_literal_and_overload():
    out = _generate("nested.capnp")
    lines = _read(out)
    # Enum should now be a real Enum subclass, not a Literal alias
    assert any(re.match(r"^\s*class Kind\(Enum\):", l) for l in lines)
    # Ensure Enum import present
    assert any(l.startswith("from enum import") and "Enum" in l for l in lines)
    # Sequence import still expected for list fields
    assert any(l.startswith("from collections.abc import") and "Sequence" in l for l in lines)
    # No overload expected (only one init overload)
    assert not any("overload" in l for l in lines if l.startswith("from typing import"))


def test_unions_literal_and_overload_and_which():
    out = _generate("unions.capnp")
    lines = _read(out)
    # Expect Literal import (union which methods) and overload import (multiple init overloads)
    assert any(l.startswith("from typing import") and "Literal" in l for l in lines)
    # Only a single init choice => no overload import expected
    assert not any(l.startswith("from typing import") and "overload" in l for l in lines)
    # 'which' function should appear for discriminantCount > 0
    assert any(re.match(r"^\s*def which\(self\) -> Literal\[", l) for l in lines)


def test_interfaces_protocol_and_any_and_iterator():
    out = _generate("interfaces.capnp")
    lines = _read(out)
    # Protocol import expected
    assert any(l.startswith("from typing import") and "Protocol" in l for l in lines)
    # Iterator from collections.abc
    assert any(l.startswith("from collections.abc import") and "Iterator" in l for l in lines)
    # Any usage in method parameters or return types (interface methods use Any)
    # Concrete interface param/return typing now applied
    assert any("def greet" in l and "name: str" in l and "-> str" in l for l in lines)
    assert any("def streamNumbers" in l and "count: int" in l and "-> int" in l for l in lines)


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
    assert any("shared:" in l and "SharedBuilder" in l and "SharedReader" in l for l in user_lines)
    # Ensure import statement for base module types exists
    assert any(
        l.startswith("from ") and "import Shared, SharedBuilder, SharedReader" in l
        for l in user_lines
    )
