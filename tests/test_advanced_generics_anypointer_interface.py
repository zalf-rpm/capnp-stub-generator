from pathlib import Path

import pytest

from capnp_stub_generator.cli import main

SCHEMA = Path(__file__).parent / "schemas" / "advanced_features.capnp"


@pytest.mark.skip(reason="Generator not yet supporting generics/anypointer/interface stubs")
def test_generics_anypointer_interface(tmp_path):
    main(["-p", str(SCHEMA), "-o", str(tmp_path)])
    stub = tmp_path / "advanced_features_capnp.pyi"
    assert stub.exists(), "Stub should be generated"
    # Future: assert GenericBox brand instantiations enumBox/innerBox; AnyPointer value typing; interface method signatures.
