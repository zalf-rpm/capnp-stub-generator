from pathlib import Path

SCHEMAS_DIR = Path(__file__).parent / "schemas" / "basic"


def test_generics_anypointer_interface(basic_stubs):
    """Test that generics with AnyPointer, generic instantiations, and interfaces are handled."""
    stub = basic_stubs / "advanced_features_capnp.pyi"
    assert stub.exists(), "Stub should be generated"

    content = stub.read_text()

    # Check for GenericBox struct Protocol
    assert (
        "class _GenericBoxModule(_StructModule):" in content
        or "class _GenericBoxModule(Generic[T], _StructModule):" in content
    ), "GenericBox _StructModule should exist"
    assert "def value(self) -> Any:" in content, "GenericBox.value should be typed as Any (from AnyPointer)"
    # Check for module annotation (not TypeAlias)
    assert "GenericBox: _GenericBoxModule" in content, "GenericBox annotation should exist"

    # Check for generic instantiations in AdvancedContainer
    assert "def enumBox(self)" in content, "enumBox field should exist"
    assert "def innerBox(self)" in content, "innerBox field should exist"

    # Both should reference GenericBox (via Protocol or TypeAlias)
    lines = content.split("\n")
    found_enum_box = False
    found_inner_box = False

    for i, line in enumerate(lines):
        if "def enumBox(self)" in line:
            # Check return type in next few lines - should reference _GenericBoxModule
            for j in range(i, min(i + 3, len(lines))):
                if "GenericBox" in lines[j] or "_GenericBoxModule" in lines[j]:
                    found_enum_box = True
                    break
        if "def innerBox(self)" in line:
            for j in range(i, min(i + 3, len(lines))):
                if "GenericBox" in lines[j] or "_GenericBoxModule" in lines[j]:
                    found_inner_box = True
                    break

    assert found_enum_box, "enumBox should be typed as GenericBox"
    assert found_inner_box, "innerBox should be typed as GenericBox"

    # Check for interface (now uses _InterfaceModule pattern)
    assert "class _TestIfaceModule(_InterfaceModule):" in content, "TestIface _InterfaceModule should exist"
    assert "TestIface: _TestIfaceModule" in content, "TestIface annotation should exist"
    assert "class TestIfaceClient(_DynamicCapabilityClient):" in content, (
        "TestIfaceClient should inherit from _DynamicCapabilityClient"
    )

    # Check interface client methods
    assert "def ping(" in content, "TestIfaceClient should have ping method"
    assert "def stats(" in content, "TestIfaceClient should have stats method"

    # Check for result types
    assert "class PingResult" in content, "PingResult should be defined"
    assert "class StatsResult" in content, "StatsResult should be defined"

    # Verify ping has proper parameter
    found_ping_params = False
    found_stats_result_fields = False

    for i, line in enumerate(lines):
        if "def ping(" in line:
            # Check for count parameter
            for j in range(i, min(i + 5, len(lines))):
                if "count" in lines[j] and "int" in lines[j]:
                    found_ping_params = True
                    break

    # Check StatsResult has the expected fields (value and label)
    # Result fields are direct attributes in Protocol classes
    in_stats_result = False
    for line in lines:
        if "class StatsResult" in line:
            in_stats_result = True
        elif in_stats_result and "class " in line and "StatsResult" not in line:
            in_stats_result = False

        if in_stats_result and ("value:" in line or "label:" in line):
            found_stats_result_fields = True
            break

    assert found_ping_params, "ping method should have int count parameter"
    assert found_stats_result_fields, "StatsResult should have value and label fields"
