"""Test generation of complex list types."""

from __future__ import annotations


def test_complex_lists(basic_stubs):
    """Test that multi-dimensional lists are properly typed with nested Sequence types."""
    stub = basic_stubs / "advanced_features_capnp.pyi"
    assert stub.exists(), "Stub should be generated"

    content = stub.read_text()

    # Check for 2D int list
    # Now uses specific list class alias Int32ListListReader
    assert "def ints2d(self) -> Int32ListListReader:" in content, "ints2d should be typed as Int32ListListReader"

    # Check for 2D struct list
    assert "def inners2d(" in content, "inners2d field should exist"

    # Should be InnerListListReader (or similar)
    # Inner is nested in AdvancedContainer, but we use flat naming for list classes now
    assert "def inners2d(self) -> InnerListListReader:" in content

    # Check for listListInner in Nested struct
    assert "def listListInner(" in content, "listListInner field should exist"

    # Should be InnerListListReader
    assert "def listListInner(self) -> InnerListListReader:" in content
