from pathlib import Path

import pytest

from capnp_stub_generator.cli import main

SCHEMA = Path(__file__).parent / "schemas" / "advanced_features.capnp"


@pytest.mark.skip(reason="Generator not yet supporting multi-dimensional list stubs")
def test_complex_lists(tmp_path):
    main(["-p", str(SCHEMA), "-o", str(tmp_path)])
    stub = tmp_path / "advanced_features_capnp.pyi"
    assert stub.exists(), "Stub should be generated"
    # Future: assert ints2d, inners2d, listListInner structure representation.
