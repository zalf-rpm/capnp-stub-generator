"""Unit tests for Builder/Reader variant type generation."""

from capnp_stub_generator.helper import _build_variant_type, new_builder, new_builder_flat, new_reader_flat


class TestVariantTypeGeneration:
    """Test the _build_variant_type helper and its public wrappers."""

    # Test nested (non-flat) naming
    def test_nested_builder_simple(self) -> None:
        """Test nested builder simple."""
        assert new_builder("MyStruct") == "MyStruct.Builder"

    def test_nested_builder_nested_class(self) -> None:
        """Test nested builder nested class."""
        assert new_builder("Outer.Inner") == "Outer.Inner.Builder"

    def test_nested_builder_generic(self) -> None:
        """Test nested builder generic."""
        assert new_builder("Env[T]") == "Env[T].Builder"

    def test_nested_builder_multi_param_generic(self) -> None:
        """Test nested builder multi param generic."""
        assert new_builder("Map[K, V]") == "Map[K, V].Builder"

    # Test flat naming
    def test_flat_builder_simple(self) -> None:
        """Test flat builder simple."""
        assert new_builder_flat("MyStruct") == "MyStructBuilder"

    def test_flat_reader_simple(self) -> None:
        """Test flat reader simple."""
        assert new_reader_flat("MyStruct") == "MyStructReader"

    def test_flat_builder_generic(self) -> None:
        """Test flat builder generic."""
        assert new_builder_flat("Env[T]") == "EnvBuilder[T]"

    def test_flat_reader_generic(self) -> None:
        """Test flat reader generic."""
        assert new_reader_flat("Env[T]") == "EnvReader[T]"

    def test_flat_builder_multi_param_generic(self) -> None:
        """Test flat builder multi param generic."""
        assert new_builder_flat("Map[K, V]") == "MapBuilder[K, V]"

    # Test internal helper directly
    def test_build_variant_type_flat_builder(self) -> None:
        """Test build variant type flat builder."""
        assert _build_variant_type("Test", "Builder", flat=True) == "TestBuilder"

    def test_build_variant_type_nested_reader(self) -> None:
        """Test build variant type nested reader."""
        assert _build_variant_type("Test", "Reader", flat=False) == "Test.Reader"

    def test_build_variant_type_flat_generic(self) -> None:
        """Test build variant type flat generic."""
        assert _build_variant_type("Box[T]", "Builder", flat=True) == "BoxBuilder[T]"

    def test_build_variant_type_nested_generic(self) -> None:
        """Test build variant type nested generic."""
        assert _build_variant_type("Box[T]", "Reader", flat=False) == "Box[T].Reader"
