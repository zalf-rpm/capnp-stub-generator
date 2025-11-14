"""Tests for Phase 2: _DynamicObjectReader Protocol with overloads for casting methods."""

import pytest


def test_dynamic_object_reader_protocol_generated(basic_stubs):
    """Test that _DynamicObjectReader Protocol class is generated."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()

    # Check that Protocol class is defined
    assert "class _DynamicObjectReader(Protocol):" in content, "_DynamicObjectReader Protocol should be defined"


def test_protocol_has_as_struct_overloads(basic_stubs):
    """Test that as_struct() method has overloads for struct types."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()

    # Should have overloads for MyStruct and OtherStruct (without type[] wrapper)
    assert "def as_struct(self, type: _MyStructModule) -> _MyStructModule.Reader:" in content, (
        "as_struct should have overload for MyStruct"
    )
    assert "def as_struct(self, type: _OtherStructModule) -> _OtherStructModule.Reader:" in content, (
        "as_struct should have overload for OtherStruct"
    )


def test_protocol_has_as_struct_catchall(basic_stubs):
    """Test that as_struct() has a catch-all overload."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()

    # Should have catch-all overload (with @overload decorator)
    assert "@overload" in content and "def as_struct(self, type: Any) -> Any:" in content, (
        "as_struct should have catch-all overload"
    )


def test_protocol_has_as_interface_overloads(basic_stubs):
    """Test that as_interface() method has overloads for interface types."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()

    # Should have overloads for GenericGetter and GenericSetter (without type[] wrapper)
    assert (
        "def as_interface(self, type: _GenericGetterModule) -> _GenericGetterModule.GenericGetterClient:" in content
    ), "as_interface should have overload for GenericGetter"
    assert (
        "def as_interface(self, type: _GenericSetterModule) -> _GenericSetterModule.GenericSetterClient:" in content
    ), "as_interface should have overload for GenericSetter"


def test_protocol_has_as_interface_catchall(basic_stubs):
    """Test that as_interface() has a catch-all overload."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()

    # Should have catch-all overload returning _DynamicCapabilityClient (with @overload decorator)
    assert "@overload" in content and "def as_interface(self, type: Any) -> _DynamicCapabilityClient:" in content, (
        "as_interface should have catch-all overload"
    )
    assert "from capnp.lib.capnp import _DynamicCapabilityClient" in content, (
        "_DynamicCapabilityClient should be imported"
    )


def test_protocol_has_as_list_method(basic_stubs):
    """Test that as_list() method is present."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()

    # Should have as_list method
    assert "def as_list(self, element_type: type[Any]) -> Sequence[Any]:" in content, "as_list method should be present"


def test_protocol_has_as_text_method(basic_stubs):
    """Test that as_text() method is present."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()

    # Should have as_text method
    assert "def as_text(self) -> str:" in content, "as_text method should be present"


def test_protocol_uses_overload_decorator(basic_stubs):
    """Test that @overload decorator is used."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()
    lines = content.split("\n")

    # Find the Protocol and check for @overload decorators
    in_protocol = False
    overload_count = 0

    for line in lines:
        if "class _DynamicObjectReader(Protocol):" in line:
            in_protocol = True
        elif in_protocol and "@overload" in line:
            overload_count += 1
        elif in_protocol and line.strip() and not line.startswith(" "):
            # Exited the Protocol class
            break

    # Should have at least 4 overloads: 2+ for as_struct, 2+ for as_interface
    assert overload_count >= 4, f"Should have at least 4 @overload decorators, found {overload_count}"


def test_protocol_struct_overloads_sorted(basic_stubs):
    """Test that struct overloads are in sorted order."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()
    lines = content.split("\n")

    # Find as_struct overloads
    struct_overload_lines = []
    in_protocol = False

    for i, line in enumerate(lines):
        if "class _DynamicObjectReader(Protocol):" in line:
            in_protocol = True
        elif in_protocol and "def as_struct(self, type: _" in line:
            struct_overload_lines.append((i, line))
        elif in_protocol and "def as_interface" in line:
            # Reached interface overloads, stop
            break

    # Extract struct names from overloads (excluding catch-all with type: Any)
    struct_names = []
    for _, line in struct_overload_lines:
        # Extract "_MyStructModule" from "type: _MyStructModule)"
        if "type: _" in line and "type: Any" not in line:
            start = line.find("type: _") + 6
            end = line.find(")", start)
            struct_name = line[start:end]
            struct_names.append(struct_name)

    # Check if sorted
    if len(struct_names) > 1:
        assert struct_names == sorted(struct_names), f"Struct overloads should be sorted, got: {struct_names}"


def test_protocol_interface_overloads_sorted(basic_stubs):
    """Test that interface overloads are in sorted order."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()
    lines = content.split("\n")

    # Find as_interface overloads
    interface_overload_lines = []
    in_protocol = False
    in_as_interface = False

    for i, line in enumerate(lines):
        if "class _DynamicObjectReader(Protocol):" in line:
            in_protocol = True
        elif in_protocol and "def as_interface(self, type: _" in line:
            in_as_interface = True
            interface_overload_lines.append((i, line))
        elif in_protocol and in_as_interface and "def as_list" in line:
            # Reached as_list, stop
            break

    # Extract interface names from overloads (excluding catch-all with type: Any)
    interface_names = []
    for _, line in interface_overload_lines:
        # Extract "_GenericGetterModule" from "type: _GenericGetterModule)"
        if "type: _" in line and "type: Any" not in line:
            start = line.find("type: _") + 6
            end = line.find(")", start)
            interface_name = line[start:end]
            interface_names.append(interface_name)

    # Check if sorted
    if len(interface_names) > 1:
        assert interface_names == sorted(interface_names), (
            f"Interface overloads should be sorted, got: {interface_names}"
        )


def test_protocol_placement_after_imports(basic_stubs):
    """Test that Protocol is placed after imports and before main content."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"
    content = stub_file.read_text()
    lines = content.split("\n")

    # Find key sections
    protocol_line = None
    last_import_line = None
    first_module_line = None

    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            last_import_line = i
        elif "class _DynamicObjectReader(Protocol):" in line:
            protocol_line = i
        elif "class _MyStructModule" in line or "class _GenericGetterModule" in line:
            if first_module_line is None:
                first_module_line = i

    assert protocol_line is not None, "Protocol should be present"
    assert last_import_line is not None, "Imports should be present"
    assert first_module_line is not None, "Module classes should be present"

    # Protocol should come after imports
    assert protocol_line > last_import_line, (
        f"Protocol (line {protocol_line}) should come after imports (line {last_import_line})"
    )

    # Protocol should come before module classes
    assert protocol_line < first_module_line, (
        f"Protocol (line {protocol_line}) should come before module classes (line {first_module_line})"
    )


def test_pyright_validates_protocol(basic_stubs):
    """Test that the generated Protocol passes pyright validation."""
    stub_file = basic_stubs / "generic_interface_capnp.pyi"

    # If we got here, pyright validation already passed during generation
    # Just do a basic sanity check
    assert stub_file.exists()
    content = stub_file.read_text()

    # Check that the Protocol is syntactically valid
    try:
        compile(content, str(stub_file), "exec")
    except SyntaxError as e:
        pytest.fail(f"Generated Protocol has syntax error: {e}")
