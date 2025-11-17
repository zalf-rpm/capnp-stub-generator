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

        # With flat type aliases, check for TestAllTypesReader return type
        assert "def structField(self) -> TestAllTypesReader:" in content, (
            "Reader class should return TestAllTypesReader type"
        )

    def test_builder_class_returns_builder_type(self, dummy_stub_file):
        """Builder class properties should return Builder types."""
        content = dummy_stub_file.read_text()

        # With flat type aliases, check for TestAllTypesBuilder return type
        assert "def structField(self) -> TestAllTypesBuilder:" in content, (
            "Builder class getter should return TestAllTypesBuilder type"
        )

    def test_builder_setter_accepts_union(self, dummy_stub_file):
        """Builder class setters should accept Builder, Reader, or dict types (not base)."""
        content = dummy_stub_file.read_text()

        # Builder setter should accept Builder/Reader + dict (may be formatted across multiple lines)
        assert "@structField.setter" in content
        assert "value: TestAllTypesBuilder | TestAllTypesReader | dict[str, Any]" in content, (
            "Builder setter should accept union of Builder, Reader, and dict types (not base)"
        )

    def test_list_fields_follow_same_pattern(self, dummy_stub_file):
        """List fields should follow the same narrowing pattern."""
        content = dummy_stub_file.read_text()

        # With flat type aliases, check for Sequence[TestAllTypesReader]
        assert "def structList(self) -> Sequence[TestAllTypesReader]:" in content, (
            "Reader class list should be Sequence[TestAllTypesReader]"
        )


class TestInterfaceReturnTypes:
    """Test that interface types don't have Builder/Reader variants."""

    def test_interface_has_no_builder_reader(self, interface_stub_file):
        """Interfaces now have an interface module and separate Client class."""
        content = interface_stub_file.read_text()

        # Should have the interface module inheriting from _InterfaceModule
        assert "class _GreeterModule(_InterfaceModule):" in content, "Should have interface module"

        # Should have the Client class inheriting from _DynamicCapabilityClient
        assert "class GreeterClient(_DynamicCapabilityClient):" in content, "Should have Client class"

        # Should NOT have Builder/Reader variants
        assert "class GreeterBuilder" not in content, "Interfaces should not have Builder class"
        assert "class GreeterReader" not in content, "Interfaces should not have Reader class"

    def test_interface_methods_return_interface_type(self, interface_stub_file):
        """Interface client methods should return result types (not Builder/Reader)."""
        content = interface_stub_file.read_text()

        # Should have interface module and Client class
        assert "class _GreeterModule(_InterfaceModule):" in content
        assert "class GreeterClient(_DynamicCapabilityClient):" in content

        # Client methods should not reference non-existent Builder/Reader types
        client_section = content.split("class GreeterClient(_DynamicCapabilityClient):")[1].split("\nclass ")[0]
        assert "GreeterBuilder" not in client_section, "Interface methods should not reference Builder"
        assert "GreeterReader" not in client_section, "Interface methods should not reference Reader"


class TestStaticMethodReturnTypes:
    """Test that static factory methods have correct return types."""

    def test_new_message_returns_builder(self, dummy_stub_file):
        """new_message should return Builder type alias (for readability)."""
        content = dummy_stub_file.read_text()

        # Find new_message in base class - should use flat type alias
        assert "def new_message(" in content
        assert ") -> TestAllTypesBuilder:" in content, "new_message should return TestAllTypesBuilder type alias"

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
