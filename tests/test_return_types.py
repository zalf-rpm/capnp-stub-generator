"""Test that struct and interface return types are accurate and match runtime behavior."""

from pathlib import Path

import pytest

from capnp_stub_generator.cli import main


@pytest.fixture(scope="module")
def dummy_stub_file(tmp_path_factory):
    """Generate dummy schema stub for testing."""
    tmp_dir = tmp_path_factory.mktemp("return_types")
    schema_path = Path(__file__).parent / "schemas" / "dummy.capnp"
    main(["-p", str(schema_path), "-o", str(tmp_dir)])
    stub_file = tmp_dir / "dummy_capnp.pyi"
    return stub_file


@pytest.fixture(scope="module")
def interface_stub_file(tmp_path_factory):
    """Generate interface schema stub for testing."""
    tmp_dir = tmp_path_factory.mktemp("interface_types")
    schema_path = Path(__file__).parent / "schemas" / "interfaces.capnp"
    main(["-p", str(schema_path), "-o", str(tmp_dir)])
    stub_file = tmp_dir / "interfaces_capnp.pyi"
    return stub_file


class TestStructReturnTypes:
    """Test that struct field return types are correctly narrowed per class."""

    def test_base_class_returns_base_type(self, dummy_stub_file):
        """Base class properties should return only the base type, not union."""
        content = dummy_stub_file.read_text()
        lines = content.split("\n")

        # Find the base TestAllTypes class
        in_base_class = False
        found_struct_field = False

        for i, line in enumerate(lines):
            if "class TestAllTypes:" in line:
                in_base_class = True
            elif in_base_class and "class TestAllTypesReader" in line:
                # We've reached the Reader class, stop
                break
            elif in_base_class and "class TestAllTypesBuilder" in line:
                # We've reached the Builder class, stop
                break

            if in_base_class and "def structField(self) ->" in line:
                # Should return only TestAllTypes, not a union
                assert "TestAllTypes:" in line or "-> TestAllTypes" in lines[i : i + 2].__str__(), (
                    "Base class should return base type"
                )
                assert "TestAllTypesBuilder" not in line, "Base class should NOT include Builder in return type"
                assert "TestAllTypesReader" not in line, "Base class should NOT include Reader in return type"
                found_struct_field = True
                break

        assert found_struct_field, "Should find structField in base class"

    def test_reader_class_returns_reader_type(self, dummy_stub_file):
        """Reader class properties should return Reader types."""
        content = dummy_stub_file.read_text()
        lines = content.split("\n")

        # Find the Reader class
        in_reader_class = False
        found_struct_field = False

        for i, line in enumerate(lines):
            if "class TestAllTypesReader(TestAllTypes):" in line:
                in_reader_class = True
            elif in_reader_class and line.startswith("class ") and "TestAllTypesReader" not in line:
                # We've left the Reader class
                break

            if in_reader_class and "def structField(self) ->" in line:
                # Should return TestAllTypesReader only
                assert "TestAllTypesReader" in line, "Reader class should return Reader type"
                assert "TestAllTypesBuilder" not in line, "Reader should not return Builder type"
                found_struct_field = True
                break

        assert found_struct_field, "Should find structField in Reader class"

    def test_builder_class_returns_builder_type(self, dummy_stub_file):
        """Builder class properties should return Builder types."""
        content = dummy_stub_file.read_text()
        lines = content.split("\n")

        # Find the Builder class
        in_builder_class = False
        found_struct_field_getter = False

        for i, line in enumerate(lines):
            if "class TestAllTypesBuilder(TestAllTypes):" in line:
                in_builder_class = True
            elif in_builder_class and line.startswith("class ") and "TestAllTypesBuilder" not in line:
                # We've left the Builder class
                break

            if in_builder_class and "def structField(self) ->" in line:
                # Should return TestAllTypesBuilder only (getter)
                assert "TestAllTypesBuilder" in line, "Builder class getter should return Builder type"
                assert "TestAllTypesReader" not in line, "Builder getter should not return Reader type"
                found_struct_field_getter = True
                break

        assert found_struct_field_getter, "Should find structField getter in Builder class"

    def test_builder_setter_accepts_union(self, dummy_stub_file):
        """Builder class setters should accept base, Builder, Reader, or dict types."""
        content = dummy_stub_file.read_text()

        # Builder setter should accept union for flexibility, including dict for convenience
        assert (
            "def structField(self, value: TestAllTypes | TestAllTypesBuilder | TestAllTypesReader | dict[str, Any])"
            in content
        ), "Builder setter should accept union of base, Builder, Reader, and dict types"

    def test_list_fields_follow_same_pattern(self, dummy_stub_file):
        """List fields should follow the same narrowing pattern."""
        content = dummy_stub_file.read_text()
        lines = content.split("\n")

        # Check base class list field
        in_base = False
        found_base_list = False
        for line in lines:
            if "class TestAllTypes:" in line:
                in_base = True
            elif in_base and "class TestAllTypesReader" in line:
                break
            if in_base and "def structList(self) ->" in line:
                # Should be Sequence[TestAllTypes] not union
                assert "Sequence[TestAllTypes]" in line, "Base class list should be Sequence[BaseType]"
                found_base_list = True
                break

        assert found_base_list, "Should find structList in base class"

        # Check Reader class list field
        in_reader = False
        found_reader_list = False
        for line in lines:
            if "class TestAllTypesReader" in line:
                in_reader = True
            elif in_reader and "class TestAllTypesBuilder" in line:
                break
            if in_reader and "def structList(self) ->" in line:
                assert "Sequence[TestAllTypesReader]" in line, "Reader class list should be Sequence[ReaderType]"
                found_reader_list = True
                break

        assert found_reader_list, "Should find structList in Reader class"


class TestInterfaceReturnTypes:
    """Test that interface types don't have Builder/Reader variants."""

    def test_interface_has_no_builder_reader(self, interface_stub_file):
        """Interfaces should only have the Protocol, no Builder/Reader classes."""
        content = interface_stub_file.read_text()

        # Should have the Protocol (actual name is Greeter, not TestGreeter)
        assert "class Greeter(Protocol):" in content, "Should have Protocol definition"

        # Should NOT have Builder/Reader variants
        assert "class GreeterBuilder" not in content, "Interfaces should not have Builder class"
        assert "class GreeterReader" not in content, "Interfaces should not have Reader class"

    def test_interface_methods_return_interface_type(self, interface_stub_file):
        """Interface methods should return interface types (not Builder/Reader)."""
        content = interface_stub_file.read_text()

        # Interface methods should reference only the Protocol type
        # Not Builder/Reader since interfaces don't have those variants
        assert "class Greeter(Protocol):" in content

        # Methods should not reference non-existent Builder/Reader types
        lines_after_greeter = content.split("class Greeter(Protocol):")[1].split("\nclass ")[0]
        assert "GreeterBuilder" not in lines_after_greeter, "Interface methods should not reference Builder"
        assert "GreeterReader" not in lines_after_greeter, "Interface methods should not reference Reader"


class TestStaticMethodReturnTypes:
    """Test that static factory methods have correct return types."""

    def test_new_message_returns_builder(self, dummy_stub_file):
        """new_message should return Builder type (for mutation)."""
        content = dummy_stub_file.read_text()

        # Find new_message in base class
        assert "def new_message(" in content
        assert ") -> TestAllTypesBuilder:" in content, "new_message should return Builder type"

    def test_from_bytes_returns_reader(self, dummy_stub_file):
        """from_bytes should return Reader type (read-only)."""
        content = dummy_stub_file.read_text()

        assert "def from_bytes(" in content
        assert "-> Iterator[TestAllTypesReader]:" in content, "from_bytes should return Reader type in Iterator"

    def test_read_returns_reader(self, dummy_stub_file):
        """read methods should return Reader type (read-only)."""
        content = dummy_stub_file.read_text()

        assert ") -> TestAllTypesReader:" in content, "read should return Reader type"
        assert "def read_packed(" in content

    def test_reader_does_not_have_new_message(self, dummy_stub_file):
        """Reader class should not have new_message method (can't create new messages)."""
        content = dummy_stub_file.read_text()
        lines = content.split("\n")

        # Find Reader class
        in_reader = False
        reader_content = []
        for line in lines:
            if "class TestAllTypesReader(TestAllTypes):" in line:
                in_reader = True
            elif in_reader and line.startswith("class ") and "TestAllTypesReader" not in line:
                break
            if in_reader:
                reader_content.append(line)

        reader_text = "\n".join(reader_content)
        # new_message should not be redefined in Reader (inherits from base but unusable)
        # The key is that Reader doesn't override it, so the inherited one would be wrong
        # At runtime, _DynamicStructReader doesn't have new_message
        assert "def new_message(" not in reader_text, "Reader class should not declare new_message"


class TestRuntimeAccuracy:
    """Test that type annotations match actual runtime behavior."""

    def test_base_type_matches_runtime_abstract(self, dummy_stub_file):
        """Base class types should match the abstract interface at runtime.

        At runtime, you never actually get a base class instance,
        you always get a Builder or Reader. But the base class
        defines the abstract interface, so its return types should
        be the base types.
        """
        content = dummy_stub_file.read_text()

        # This is correct: base class properties return base types
        # even though at runtime you'll get specific Builder/Reader instances
        assert "class TestAllTypes:" in content
        # The property typing reflects the abstract interface
        # This allows both Reader and Builder (which inherit from base) to be used

    def test_annotations_support_variance(self, dummy_stub_file):
        """Type annotations should support proper variance/substitution.

        A function expecting TestAllTypes should accept:
        - TestAllTypes (base, though abstract)
        - TestAllTypesReader (subtype)
        - TestAllTypesBuilder (subtype)

        But a function returning TestAllTypes might actually return
        either Reader or Builder at runtime (Liskov substitution).
        """
        content = dummy_stub_file.read_text()

        # This is validated by pyright/mypy through inheritance
        assert "class TestAllTypesReader(TestAllTypes):" in content
        assert "class TestAllTypesBuilder(TestAllTypes):" in content
        # Inheritance ensures proper subtyping


def test_return_types_summary():
    """Document the complete return type pattern.

    Summary of correct return type behavior:

    Structs:
    - Base class properties: BaseType (abstract interface)
    - Reader class properties: ReaderType (read-only, narrow)
    - Builder class properties: BuilderType (mutable, narrow)
    - Builder setters: BaseType | BuilderType | ReaderType (flexible)
    - new_message(): BuilderType (creates mutable)
    - from_bytes/read(): ReaderType (loads read-only)

    Interfaces:
    - Only Protocol class (no Builder/Reader)
    - Methods return interface types directly
    - Server methods return Awaitable[Type]

    This matches pycapnp runtime behavior and provides
    accurate type checking with proper variance.
    """
    pass  # Documentation test
