"""Tests for generic AnyPointer and interface generation."""

from pathlib import Path

SCHEMAS_DIR = Path(__file__).parent / "schemas" / "basic"


def _line_window_contains_any(lines: list[str], anchor: str, candidates: tuple[str, ...], *, lookahead: int) -> bool:
    """Return whether lines near an anchor contain any candidate text."""
    for index, line in enumerate(lines):
        if anchor not in line:
            continue
        window_end = min(index + lookahead, len(lines))
        for nearby_line in lines[index:window_end]:
            if any(candidate in nearby_line for candidate in candidates):
                return True
    return False


def _line_window_contains_all(lines: list[str], anchor: str, required: tuple[str, ...], *, lookahead: int) -> bool:
    """Return whether a nearby line contains all required tokens."""
    for index, line in enumerate(lines):
        if anchor not in line:
            continue
        window_end = min(index + lookahead, len(lines))
        for nearby_line in lines[index:window_end]:
            if all(token in nearby_line for token in required):
                return True
    return False


def _class_block_contains_any(lines: list[str], class_name: str, field_tokens: tuple[str, ...]) -> bool:
    """Return whether a class block contains any of the expected field tokens."""
    in_class = False
    for line in lines:
        if f"class {class_name}" in line:
            in_class = True
        elif in_class and "class " in line and class_name not in line:
            in_class = False

        if in_class and any(token in line for token in field_tokens):
            return True
    return False


def test_generics_anypointer_interface(basic_stubs: Path) -> None:
    """Test that generics with AnyPointer, generic instantiations, and interfaces are handled."""
    stub = basic_stubs / "advanced_features_capnp" / "__init__.pyi"
    assert stub.exists(), "Stub should be generated"

    content = stub.read_text()

    # Check for GenericBox struct Protocol
    assert (
        "class _GenericBoxStructModule(_StructModule):" in content
        or "class _GenericBoxStructModule(Generic[T], _StructModule):" in content
    ), "GenericBox _StructModule should exist"
    assert "def value(self) -> _DynamicObjectReader:" in content, (
        "GenericBox.value should be typed as _DynamicObjectReader (from AnyPointer)"
    )
    # Check for module annotation (not TypeAlias)
    assert "GenericBox: _GenericBoxStructModule" in content, "GenericBox annotation should exist"

    # Check for generic instantiations in AdvancedContainer
    assert "def enumBox(self)" in content, "enumBox field should exist"
    assert "def innerBox(self)" in content, "innerBox field should exist"

    # Both should reference GenericBox (via Protocol or TypeAlias)
    lines = content.split("\n")
    generic_box_tokens = ("GenericBox", "_GenericBoxStructModule")
    assert _line_window_contains_any(lines, "def enumBox(self)", generic_box_tokens, lookahead=3), (
        "enumBox should be typed as GenericBox"
    )
    assert _line_window_contains_any(lines, "def innerBox(self)", generic_box_tokens, lookahead=3), (
        "innerBox should be typed as GenericBox"
    )

    # Check for interface (now uses _InterfaceModule pattern)
    assert "class _TestIfaceInterfaceModule(_InterfaceModule):" in content, "TestIface _InterfaceModule should exist"
    assert "TestIface: _TestIfaceInterfaceModule" in content, "TestIface annotation should exist"
    assert "class TestIfaceClient(_DynamicCapabilityClient):" in content, (
        "TestIfaceClient should inherit from _DynamicCapabilityClient"
    )

    # Check interface client methods
    assert "def ping(" in content, "TestIfaceClient should have ping method"
    assert "def stats(" in content, "TestIfaceClient should have stats method"

    # Check for result types
    assert "class PingResult" in content, "PingResult should be defined"
    assert "class StatsResult" in content, "StatsResult should be defined"

    assert _line_window_contains_all(lines, "def ping(", ("count", "int"), lookahead=5), (
        "ping method should have int count parameter"
    )
    assert _class_block_contains_any(lines, "StatsResult", ("value:", "label:")), (
        "StatsResult should have value and label fields"
    )
