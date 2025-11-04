from pathlib import Path

from capnp_stub_generator.cli import main

SCHEMAS_DIR = Path(__file__).parent / "schemas"
SCHEMA = SCHEMAS_DIR / "advanced_features.capnp"
DUMMY_SCHEMA = SCHEMAS_DIR / "dummy.capnp"


def test_generics_anypointer_interface(tmp_path):
    """Test that generics with AnyPointer, generic instantiations, and interfaces are handled."""
    # Need to load dummy.capnp as well since advanced_features imports it
    main(["-p", str(DUMMY_SCHEMA), str(SCHEMA), "-o", str(tmp_path)])
    stub = tmp_path / "advanced_features_capnp.pyi"
    assert stub.exists(), "Stub should be generated"

    content = stub.read_text()

    # Check for GenericBox struct with AnyPointer
    assert "class GenericBox:" in content, "GenericBox struct should exist"
    assert "def value(self) -> Any:" in content, "GenericBox.value should be typed as Any (from AnyPointer)"

    # Check for generic instantiations in AdvancedContainer
    assert "def enumBox(self)" in content, "enumBox field should exist"
    assert "def innerBox(self)" in content, "innerBox field should exist"

    # Both should reference GenericBox
    lines = content.split("\n")
    found_enum_box = False
    found_inner_box = False

    for i, line in enumerate(lines):
        if "def enumBox(self)" in line:
            # Check return type in next few lines
            for j in range(i, min(i + 3, len(lines))):
                if "GenericBox" in lines[j]:
                    found_enum_box = True
                    break
        if "def innerBox(self)" in line:
            for j in range(i, min(i + 3, len(lines))):
                if "GenericBox" in lines[j]:
                    found_inner_box = True
                    break

    assert found_enum_box, "enumBox should be typed as GenericBox"
    assert found_inner_box, "innerBox should be typed as GenericBox"

    # Check for interface
    assert "class TestIface(Protocol):" in content, "TestIface should be a Protocol"

    # Check interface methods
    assert "def ping(" in content, "TestIface should have ping method"
    assert "def stats(" in content, "TestIface should have stats method"

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
