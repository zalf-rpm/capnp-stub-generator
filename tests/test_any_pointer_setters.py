from __future__ import annotations

import subprocess


def test_any_pointer_setters(basic_stubs):
    """Test that AnyPointer fields accept various types in setters."""
    stub_file = basic_stubs / "any_pointer_capnp.pyi"
    content = stub_file.read_text()

    # Check for AnyPointer type alias
    assert "type AnyPointer =" in content

    # Check AnyHolder Builder setters
    # any setter should accept AnyPointer
    assert "def any(self, value: AnyPointer) -> None: ..." in content

    # s setter should accept struct builder/reader/dict
    assert "def s(self, value: _DynamicStructBuilder | _DynamicObjectReader | dict[str, Any]) -> None: ..." in content

    # l setter should accept list builder/reader/Sequence
    assert "def l(self, value: _DynamicListBuilder | _DynamicObjectReader | Sequence[Any]) -> None: ..." in content

    # Check new_message
    assert "any: AnyPointer | None = None" in content


def test_any_pointer_type_checking(basic_stubs):
    """Test type checking for AnyPointer assignments."""
    test_code = """
from typing import Any
import any_pointer_capnp

def test_assignments():
    builder = any_pointer_capnp.AnyHolder.new_message()
    
    # AnyPointer assignments
    builder.any = "some text"
    builder.any = b"some data"
    # builder.any = 123  # Should fail (int not in AnyPointer)
    
    # AnyStruct assignments
    builder.s = {"some": "dict"}
    
    # AnyList assignments
    builder.l = ["some", "list"]
    
    # new_message with AnyPointer
    b2 = any_pointer_capnp.AnyHolder.new_message(any="text")
"""

    test_file = basic_stubs / "test_any_pointer_usage.py"
    test_file.write_text(test_code)

    # Run pyright
    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)

    assert result.returncode == 0, f"Type checking failed: {result.stdout}"
