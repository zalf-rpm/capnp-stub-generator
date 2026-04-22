"""Test that struct and interface return types are accurate and match runtime behavior."""

from pathlib import Path

import pytest

from tests.test_helpers import read_generated_types_combined, read_generated_types_file


@pytest.fixture(scope="module")
def dummy_stub_content(basic_stubs: Path) -> str:
    """Get pre-generated dummy schema helper content."""
    return read_generated_types_combined(basic_stubs / "dummy_capnp")


@pytest.fixture(scope="module")
def interface_stub_content(basic_stubs: Path) -> str:
    """Get pre-generated interface schema helper content."""
    return read_generated_types_combined(basic_stubs / "interfaces_capnp")


@pytest.fixture(scope="module")
def dummy_modules_content(basic_stubs: Path) -> str:
    """Get the dummy module-helper stub content."""
    return read_generated_types_file(basic_stubs / "dummy_capnp", "modules.pyi")


@pytest.fixture(scope="module")
def dummy_readers_content(basic_stubs: Path) -> str:
    """Get the dummy reader-helper stub content."""
    return read_generated_types_file(basic_stubs / "dummy_capnp", "readers.pyi")


class TestStructReturnTypes:
    """Test that struct field return types are correctly narrowed per class."""

    def test_base_class_has_no_field_properties(self, dummy_modules_content: str) -> None:
        """Module helper should not expose struct fields directly (these live on Reader/Builder)."""
        lines = dummy_modules_content.split("\n")

        in_base_class = False
        has_struct_field = False

        for _i, line in enumerate(lines):
            if "class _TestAllTypesStructModule(_StructModule):" in line:
                in_base_class = True
            elif in_base_class and line.startswith("class ") and "_TestAllTypesStructModule" not in line:
                break

            if in_base_class and line.startswith("    def structField(self) ->"):
                has_struct_field = True
                break

        assert not has_struct_field, "Module helper should NOT have direct field properties"

    def test_reader_class_returns_reader_type(self, dummy_readers_content: str) -> None:
        """Reader class properties should return Reader types."""
        assert "def structField(self) -> TestAllTypesReader:" in dummy_readers_content, (
            "Reader class should return TestAllTypesReader type"
        )

    def test_builder_class_returns_builder_type(self, dummy_stub_content: str) -> None:
        """Builder class properties should return Builder types."""
        assert "def structField(self) -> TestAllTypesBuilder:" in dummy_stub_content, (
            "Builder class getter should return TestAllTypesBuilder type"
        )

    def test_builder_setter_accepts_union(self, dummy_stub_content: str) -> None:
        """Builder class setters should accept Builder, Reader, or dict types (not base)."""
        assert "@structField.setter" in dummy_stub_content
        assert "value: TestAllTypesBuilder | readers.TestAllTypesReader | dict[str, Any]" in dummy_stub_content, (
            "Builder setter should accept union of Builder, Reader, and dict types (not base)"
        )

    def test_list_fields_follow_same_pattern(self, dummy_stub_content: str) -> None:
        """List fields should follow the same narrowing pattern."""
        assert "def structList(self) -> TestAllTypesListReader:" in dummy_stub_content, (
            "Reader class list should be TestAllTypesListReader"
        )


class TestInterfaceReturnTypes:
    """Test that interface types don't have Builder/Reader variants."""

    def test_interface_has_no_builder_reader(self, interface_stub_content: str) -> None:
        """Interfaces now have an interface module and separate Client class."""
        assert "class _GreeterInterfaceModule(_InterfaceModule):" in interface_stub_content, (
            "Should have interface module"
        )
        assert "class GreeterClient(_DynamicCapabilityClient):" in interface_stub_content, "Should have Client class"
        assert "class GreeterBuilder" not in interface_stub_content, "Interfaces should not have Builder class"
        assert "class GreeterReader" not in interface_stub_content, "Interfaces should not have Reader class"

    def test_interface_methods_return_interface_type(self, interface_stub_content: str) -> None:
        """Interface client methods should return result types (not Builder/Reader)."""
        assert "class _GreeterInterfaceModule(_InterfaceModule):" in interface_stub_content
        assert "class GreeterClient(_DynamicCapabilityClient):" in interface_stub_content
        client_section = interface_stub_content.split("class GreeterClient(_DynamicCapabilityClient):")[1].split(
            "\nclass ", maxsplit=1
        )[0]
        assert "GreeterBuilder" not in client_section, "Interface methods should not reference Builder"
        assert "GreeterReader" not in client_section, "Interface methods should not reference Reader"


class TestStaticMethodReturnTypes:
    """Test that static factory methods have correct return types."""

    def test_new_message_returns_builder(self, dummy_modules_content: str) -> None:
        """new_message should return Builder type alias (for readability)."""
        assert "def new_message(" in dummy_modules_content
        assert ") -> builders.TestAllTypesBuilder:" in dummy_modules_content, (
            "new_message should return the builder helper type"
        )

    def test_reader_does_not_have_new_message(self, dummy_readers_content: str) -> None:
        """Reader class should not have new_message method (can't create new messages)."""
        assert "def new_message(" not in dummy_readers_content, "Reader class should not declare new_message"


class TestRuntimeAccuracy:
    """Test that type annotations match actual runtime behavior."""
