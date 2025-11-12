"""Test generation of complex list types."""

from __future__ import annotations


def test_complex_lists(basic_stubs):
    """Test that multi-dimensional lists are properly typed with nested Sequence types."""
    stub = basic_stubs / "advanced_features_capnp.pyi"
    assert stub.exists(), "Stub should be generated"

    content = stub.read_text()

    # Check for 2D int list
    assert "def ints2d(self) -> Sequence[Sequence[int]]:" in content, (
        "ints2d should be typed as Sequence[Sequence[int]]"
    )

    # Check for 2D struct list
    assert "def inners2d(" in content, "inners2d field should exist"

    # Find inners2d and check its type includes nested Sequence
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "def inners2d(" in line:
            # Check the next few lines for the return type
            for j in range(i, min(i + 5, len(lines))):
                if "-> Sequence[Sequence[" in lines[j]:
                    assert "Inner" in lines[j], "inners2d should reference Inner type in nested Sequence"
                    break
            break

    # Check for listListInner in Nested struct
    assert "def listListInner(" in content, "listListInner field should exist"

    # Verify nested Sequence typing for listListInner
    found_list_list_inner_type = False
    for line in lines:
        if "def listListInner(" in line:
            # Look for the return type annotation
            for j in range(lines.index(line), min(lines.index(line) + 5, len(lines))):
                if "-> Sequence[Sequence[" in lines[j] and "Inner" in lines[j]:
                    found_list_list_inner_type = True
                    break

    assert found_list_list_inner_type, "listListInner should be typed with nested Sequence[Sequence[Inner...]]"
