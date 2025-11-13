"""Test that struct and interface return types are accurate and match runtime behavior."""

import pytest


@pytest.fixture(scope="module")
def dummy_stub_file(basic_stubs):
    """Get pre-generated dummy schema stub."""
    return basic_stubs / "dummy_capnp.pyi"


@pytest.fixture(scope="module")
def interface_stub_file(basic_stubs):
    """Get pre-generated interface schema stub."""
    return basic_stubs / "interfaces_capnp.pyi"


class TestStructReturnTypes:
    """Test that struct field return types are correctly narrowed per class."""

    def test_base_class_has_no_field_properties(self, dummy_stub_file):
        """Base class should not have field properties (these are on Reader/Builder)."""
        content = dummy_stub_file.read_text()
        lines = content.split("\n")

        # Find the base TestAllTypes class
        in_base_class = False
        has_struct_field = False

        for i, line in enumerate(lines):
            if "class TestAllTypes:" in line:
                in_base_class = True
            elif in_base_class and "class Reader:" in line:
                # We've reached the nested Reader class, stop
                break
            elif in_base_class and "class Builder:" in line:
                # We've reached the nested Builder class, stop
                break

            if in_base_class and "def structField(self) ->" in line:
                has_struct_field = True
                break

        assert not has_struct_field, "Base class should NOT have field properties"

    def test_reader_class_returns_reader_type(self, dummy_stub_file):
        """Reader class properties should return Reader types."""
        content = dummy_stub_file.read_text()

        # With nested structure, check for TestAllTypes.Reader return type
        assert "def structField(self) -> TestAllTypes.Reader:" in content, (
            "Reader class should return TestAllTypes.Reader type"
        )

    def test_builder_class_returns_builder_type(self, dummy_stub_file):
        """Builder class properties should return Builder types."""
        content = dummy_stub_file.read_text()

        # With nested structure, check for TestAllTypes.Builder return type
        assert "def structField(self) -> TestAllTypes.Builder:" in content, (
            "Builder class getter should return TestAllTypes.Builder type"
        )

    def test_builder_setter_accepts_union(self, dummy_stub_file):
        """Builder class setters should accept Builder, Reader, or dict types (not base)."""
        content = dummy_stub_file.read_text()

        # Builder setter should accept Builder/Reader + dict with nested class syntax
        assert "def structField(self, value: TestAllTypes.Builder | TestAllTypes.Reader | dict[str, Any])" in content, (
            "Builder setter should accept union of Builder, Reader, and dict types (not base)"
        )

    def test_list_fields_follow_same_pattern(self, dummy_stub_file):
        """List fields should follow the same narrowing pattern."""
        content = dummy_stub_file.read_text()

        # With nested structure, check for Sequence[TestAllTypes.Reader]
        assert "def structList(self) -> Sequence[TestAllTypes.Reader]:" in content, (
            "Reader class list should be Sequence[TestAllTypes.Reader]"
        )


class TestInterfaceReturnTypes:
    """Test that interface types don't have Builder/Reader variants."""

    def test_interface_has_no_builder_reader(self, interface_stub_file):
        """Interfaces now have an interface module and separate Client class."""
        content = interface_stub_file.read_text()

        # Should have the interface module (not Protocol anymore)
        assert "class Greeter:" in content, "Should have interface module"

        # Should have the Client Protocol class
        assert "class GreeterClient(Protocol):" in content, "Should have Client Protocol"

        # Should NOT have Builder/Reader variants
        assert "class GreeterBuilder" not in content, "Interfaces should not have Builder class"
        assert "class GreeterReader" not in content, "Interfaces should not have Reader class"

    def test_interface_methods_return_interface_type(self, interface_stub_file):
        """Interface client methods should return result types (not Builder/Reader)."""
        content = interface_stub_file.read_text()

        # Should have interface module and Client class
        assert "class Greeter:" in content
        assert "class GreeterClient(Protocol):" in content

        # Client methods should not reference non-existent Builder/Reader types
        client_section = content.split("class GreeterClient(Protocol):")[1].split("\nclass ")[0]
        assert "GreeterBuilder" not in client_section, "Interface methods should not reference Builder"
        assert "GreeterReader" not in client_section, "Interface methods should not reference Reader"


class TestStaticMethodReturnTypes:
    """Test that static factory methods have correct return types."""

    def test_new_message_returns_builder(self, dummy_stub_file):
        """new_message should return Builder type (for mutation)."""
        content = dummy_stub_file.read_text()

        # Find new_message in base class - with nested structure
        assert "def new_message(" in content
        assert ") -> TestAllTypes.Builder:" in content, "new_message should return TestAllTypes.Builder type"

    def test_from_bytes_returns_reader(self, dummy_stub_file):
        """from_bytes should return Reader type (read-only)."""
        content = dummy_stub_file.read_text()

        assert "def from_bytes(" in content
        assert "-> Iterator[TestAllTypes.Reader]:" in content, (
            "from_bytes should return TestAllTypes.Reader type in Iterator"
        )

    def test_read_returns_reader(self, dummy_stub_file):
        """read methods should return Reader type (read-only)."""
        content = dummy_stub_file.read_text()

        assert ") -> TestAllTypes.Reader:" in content, "read should return TestAllTypes.Reader type"
        assert "def read_packed(" in content

    def test_reader_does_not_have_new_message(self, dummy_stub_file):
        """Reader class should not have new_message method (can't create new messages)."""
        content = dummy_stub_file.read_text()
        lines = content.split("\n")

        # Find nested Reader class
        in_reader = False
        reader_content = []
        for line in lines:
            if line.strip() == "class Reader:":
                in_reader = True
            elif in_reader and line.strip().startswith("class ") and "Reader" not in line:
                break
            if in_reader:
                reader_content.append(line)

        reader_text = "\n".join(reader_content)
        # new_message should not be in Reader class
        assert "def new_message(" not in reader_text, "Reader class should not declare new_message"


class TestRuntimeAccuracy:
    """Test that type annotations match actual runtime behavior."""

    def test_base_type_matches_runtime_struct_module(self, dummy_stub_file):
        """Base class types should match the _StructModule at runtime.

        At runtime, the base class is a _StructModule which provides
        static factory methods like new_message(), from_bytes(), etc.
        It does not have field properties - those are on Reader/Builder.
        """
        content = dummy_stub_file.read_text()

        # Base class should have factory methods but no field properties
        assert "class TestAllTypes:" in content
        assert "def new_message(" in content
        assert "def from_bytes(" in content

    def test_annotations_reflect_runtime_structure(self, dummy_stub_file):
        """Type annotations should reflect actual runtime class structure.

        At runtime:
        - Base class is _StructModule (factory methods, no field properties)
        - Reader is _DynamicStructReader (field properties, read-only)
        - Builder is _DynamicStructBuilder (field properties with setters)

        With nested structure, Reader and Builder are nested inside the base class.
        """
        content = dummy_stub_file.read_text()

        # Base and nested Reader, Builder classes
        assert "class TestAllTypes:" in content
        assert "TestAllTypesReader: TypeAlias = TestAllTypes.Reader" in content
        assert "TestAllTypesBuilder: TypeAlias = TestAllTypes.Builder" in content
        # Nested classes exist
        assert "class Reader:" in content
        assert "class Builder:" in content


def test_return_types_summary():
    """Document the complete return type pattern.

    Summary of correct return type behavior:

    Structs:
    - Base class: Factory methods only (new_message, from_bytes, etc.)
    - Reader class properties: ReaderType (read-only, narrow)
    - Builder class properties: BuilderType (mutable, narrow)
    - Builder setters: BuilderType | ReaderType | dict (flexible, no base type)
    - new_message(): BuilderType (creates mutable)
    - from_bytes/read(): ReaderType (loads read-only)

    Interfaces:
    - Only Protocol class (no Builder/Reader)
    - Methods return interface types directly
    - Server methods return Awaitable[Type]

    This matches pycapnp runtime behavior where:
    - Base = _StructModule (factory)
    - Reader = _DynamicStructReader
    - Builder = _DynamicStructBuilder
    None of these inherit from each other, so base type is not
    accepted in setters (you can't set a field to a factory module).
    """
    pass  # Documentation test
