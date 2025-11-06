"""Test that generated stubs work with union type annotations in user code."""

from __future__ import annotations

from pathlib import Path


def test_union_type_annotation_with_future_import(tmp_path: Path):
    """Test that union types work when __future__ annotations is imported."""
    # Generate stub for a simple schema
    from tests.conftest import generate_stub_from_schema

    stub_dir = generate_stub_from_schema("primitives.capnp", tmp_path)

    # Create a test file that uses union type annotations
    test_file = tmp_path / "test_usage.py"
    test_file.write_text(
        f"""
from __future__ import annotations

import sys
sys.path.insert(0, str('{stub_dir}'))

import primitives_capnp

def process_data(data: primitives_capnp.SimplePrimitives | str | None) -> str:
    '''Function that accepts SimplePrimitives or str or None.'''
    if data is None:
        return "none"
    elif isinstance(data, str):
        return data
    else:
        return "struct"

# This should work without runtime errors
result = process_data(None)
assert result == "none"
"""
    )

    # Run the test file - should work without errors
    import subprocess

    result = subprocess.run(
        ["python", str(test_file)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Failed with: {result.stderr}"


def test_union_type_annotation_without_future_import_fails(tmp_path: Path):
    """Test that union types fail without __future__ annotations (documents current limitation)."""
    from tests.conftest import generate_stub_from_schema

    stub_dir = generate_stub_from_schema("primitives.capnp", tmp_path)

    # Create a test file that does NOT import __future__ annotations
    test_file = tmp_path / "test_usage_no_future.py"
    test_file.write_text(
        f"""
# NOTE: Missing 'from __future__ import annotations'

import sys
sys.path.insert(0, str('{stub_dir}'))

import primitives_capnp

# This will fail at import time because the | operator is evaluated immediately
# on the runtime _StructModule object
def process_data(data: primitives_capnp.SimplePrimitives | str | None) -> str:
    '''Function that accepts SimplePrimitives or str or None.'''
    return "test"
"""
    )

    # Run the test file - should fail with TypeError
    import subprocess

    result = subprocess.run(
        ["python", str(test_file)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    # This is expected to fail
    assert result.returncode != 0
    assert "TypeError" in result.stderr or "unsupported operand type" in result.stderr.lower()


def test_union_type_with_typing_union(tmp_path: Path):
    """Test that typing.Union works as an alternative to | operator."""
    from tests.conftest import generate_stub_from_schema

    stub_dir = generate_stub_from_schema("primitives.capnp", tmp_path)

    # Create a test file that uses typing.Union instead of |
    test_file = tmp_path / "test_usage_union.py"
    test_file.write_text(
        f"""
from typing import Union

import sys
sys.path.insert(0, str('{stub_dir}'))

import primitives_capnp

def process_data(data: Union[primitives_capnp.SimplePrimitives, str, None]) -> str:
    '''Function that accepts SimplePrimitives or str or None using typing.Union.'''
    if data is None:
        return "none"
    elif isinstance(data, str):
        return data
    else:
        return "struct"

# This should work without runtime errors
result = process_data("test")
assert result == "test"
"""
    )

    # Run the test file - should work without errors
    import subprocess

    result = subprocess.run(
        ["python", str(test_file)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Failed with: {result.stderr}"


def test_union_type_in_class_definition(tmp_path: Path):
    """Test that union types work in class method signatures with __future__ import."""
    from tests.conftest import generate_stub_from_schema

    stub_dir = generate_stub_from_schema("primitives.capnp", tmp_path)

    # Create a test file with a class that uses union type annotations
    test_file = tmp_path / "test_class_usage.py"
    test_file.write_text(
        f"""
from __future__ import annotations

import sys
sys.path.insert(0, str('{stub_dir}'))

import primitives_capnp

class DataProcessor:
    def __init__(self):
        self._data = None
    
    def process(
        self,
        data: primitives_capnp.SimplePrimitives | str | None,
    ) -> str | None:
        '''Process data that can be a struct, string, or None.'''
        if data is None:
            return None
        elif isinstance(data, str):
            return data
        else:
            return "struct"

# This should work without runtime errors
processor = DataProcessor()
result = processor.process("test")
assert result == "test"
"""
    )

    # Run the test file - should work without errors
    import subprocess

    result = subprocess.run(
        ["python", str(test_file)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Failed with: {result.stderr}"
