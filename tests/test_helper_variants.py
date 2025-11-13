"""Unit tests for Builder/Reader variant type generation."""

from capnp_stub_generator.helper import _build_variant_type, new_builder, new_builder_flat, new_reader, new_reader_flat


class TestVariantTypeGeneration:
    """Test the _build_variant_type helper and its public wrappers."""

    # Test nested (non-flat) naming
    def test_nested_builder_simple(self):
        assert new_builder("MyStruct") == "MyStruct.Builder"

    def test_nested_reader_simple(self):
        assert new_reader("MyStruct") == "MyStruct.Reader"

    def test_nested_builder_nested_class(self):
        assert new_builder("Outer.Inner") == "Outer.Inner.Builder"

    def test_nested_reader_nested_class(self):
        assert new_reader("Outer.Inner") == "Outer.Inner.Reader"

    def test_nested_builder_generic(self):
        assert new_builder("Env[T]") == "Env[T].Builder"

    def test_nested_reader_generic(self):
        assert new_reader("Env[T]") == "Env[T].Reader"

    def test_nested_builder_multi_param_generic(self):
        assert new_builder("Map[K, V]") == "Map[K, V].Builder"

    # Test flat naming
    def test_flat_builder_simple(self):
        assert new_builder_flat("MyStruct") == "MyStructBuilder"

    def test_flat_reader_simple(self):
        assert new_reader_flat("MyStruct") == "MyStructReader"

    def test_flat_builder_generic(self):
        assert new_builder_flat("Env[T]") == "EnvBuilder[T]"

    def test_flat_reader_generic(self):
        assert new_reader_flat("Env[T]") == "EnvReader[T]"

    def test_flat_builder_multi_param_generic(self):
        assert new_builder_flat("Map[K, V]") == "MapBuilder[K, V]"

    # Test internal helper directly
    def test_build_variant_type_flat_builder(self):
        assert _build_variant_type("Test", "Builder", flat=True) == "TestBuilder"

    def test_build_variant_type_nested_reader(self):
        assert _build_variant_type("Test", "Reader", flat=False) == "Test.Reader"

    def test_build_variant_type_flat_generic(self):
        assert _build_variant_type("Box[T]", "Builder", flat=True) == "BoxBuilder[T]"

    def test_build_variant_type_nested_generic(self):
        assert _build_variant_type("Box[T]", "Reader", flat=False) == "Box[T].Reader"
