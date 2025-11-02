from pathlib import Path

import pytest

from capnp_stub_generator.cli import main

SCHEMA = Path(__file__).parent / "schemas" / "advanced_features.capnp"


@pytest.mark.skip(reason="Generator not yet handling advanced constants/version fields")
def test_advanced_constants_and_version_fields(tmp_path):
    main(["-p", str(SCHEMA), "-o", str(tmp_path)])
    # Basic smoke checks: file created and module importable later
    assert (tmp_path / "advanced_features_capnp.pyi").exists(), (
        "Expected stub file for advanced features"
    )
    # Future: inspect constants (baseInt, derivedList, chainedStruct) and versioned struct fields new1/newText presence.
