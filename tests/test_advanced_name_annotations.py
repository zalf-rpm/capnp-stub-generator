from pathlib import Path

import pytest

from capnp_stub_generator.cli import main

SCHEMA = Path(__file__).parent / "schemas" / "advanced_features.capnp"


@pytest.mark.skip(reason="Generator currently lacks proper name annotation handling")
def test_name_annotations(tmp_path):
    main(["-p", str(SCHEMA), "-o", str(tmp_path)])
    stub = tmp_path / "advanced_features_capnp.pyi"
    assert stub.exists(), "Stub should be generated"
    # Future: parse stub contents for BetterName, goodField, RenamedOops, neo, BetterDeepEnum, etc.
