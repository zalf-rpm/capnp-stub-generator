"""Test interface inheritance in generated stubs.

This module tests that interfaces that extend other interfaces
correctly reflect the inheritance in the generated Python stubs.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from capnp_stub_generator.cli import main

# Test directories
TESTS_DIR = Path(__file__).parent
ZALFMAS_DIR = TESTS_DIR / "zalfmas_capnp_schemas"
IDENTIFIABLE_DIR = TESTS_DIR / "examples" / "identifiable"
GENERATED_DIR = TESTS_DIR / "_generated" / "interface_inheritance"


@pytest.fixture(scope="module")
def generated_dir():
    """Ensure the generated directory exists and is clean."""
    if GENERATED_DIR.exists():
        shutil.rmtree(GENERATED_DIR)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    yield GENERATED_DIR

    # Keep generated files for inspection
    # shutil.rmtree(GENERATED_DIR)


def test_simple_interface_inheritance(generated_dir):
    """Test that an interface extending another interface shows inheritance.

    ClimateInstance extends Identifiable, so the generated stub should show:
    - class ClimateInstance(Identifiable, Protocol):
    - class Server(Identifiable.Server):
    """
    # Generate stubs for model.capnp which has ClimateInstance extends Identifiable
    schema_files = [
        ZALFMAS_DIR / "model.capnp",
        ZALFMAS_DIR / "common.capnp",
        ZALFMAS_DIR / "climate.capnp",
        ZALFMAS_DIR / "soil.capnp",
        ZALFMAS_DIR / "management.capnp",
        ZALFMAS_DIR / "persistence.capnp",
        ZALFMAS_DIR / "service.capnp",
        ZALFMAS_DIR / "date.capnp",
        ZALFMAS_DIR / "geo.capnp",
    ]

    schema_paths = [str(f) for f in schema_files]
    args = ["-p"] + schema_paths + ["-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    # Check the generated stub
    stub_file = generated_dir / "model_capnp.pyi"
    assert stub_file.exists(), "Stub file was not generated"

    content = stub_file.read_text()

    # Check that ClimateInstance extends Identifiable
    assert "class ClimateInstance(Identifiable, Protocol):" in content, "ClimateInstance should extend Identifiable"

    # Check that ClimateInstance.Server extends Identifiable.Server
    # The Server class should be nested, so we need to find it in context
    lines = content.split("\n")
    in_climate_instance = False
    found_server_inheritance = False

    for i, line in enumerate(lines):
        if "class ClimateInstance(Identifiable, Protocol):" in line:
            in_climate_instance = True
        elif in_climate_instance and "class Server(Identifiable.Server):" in line:
            found_server_inheritance = True
            break
        elif in_climate_instance and line.startswith("class ") and "ClimateInstance" not in line:
            # We've moved to a different top-level class
            break

    assert found_server_inheritance, "ClimateInstance.Server should extend Identifiable.Server"


def test_multiple_interface_inheritance(generated_dir):
    """Test that an interface extending multiple interfaces shows all inheritance.

    IdentifiableHolder extends both Identifiable and Holder(T), so:
    - class IdentifiableHolder(Identifiable, Holder, Protocol):
    - class Server(Identifiable.Server, Holder.Server):
    """
    # Generate stub for common.capnp
    schema_file = ZALFMAS_DIR / "common.capnp"
    args = ["-p", str(schema_file), "-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    stub_file = generated_dir / "common_capnp.pyi"
    assert stub_file.exists(), "Stub file was not generated"

    content = stub_file.read_text()

    # Check that IdentifiableHolder extends both Identifiable and Holder
    assert "class IdentifiableHolder(Identifiable, Holder, Protocol):" in content, (
        "IdentifiableHolder should extend both Identifiable and Holder"
    )

    # Check that IdentifiableHolder.Server extends both base Servers
    lines = content.split("\n")
    in_identifiable_holder = False
    found_server_inheritance = False

    for i, line in enumerate(lines):
        if "class IdentifiableHolder(Identifiable, Holder, Protocol):" in line:
            in_identifiable_holder = True
        elif in_identifiable_holder and "class Server(Identifiable.Server, Holder.Server):" in line:
            found_server_inheritance = True
            break
        elif in_identifiable_holder and line.startswith("class ") and "IdentifiableHolder" not in line:
            break

    assert found_server_inheritance, (
        "IdentifiableHolder.Server should extend both Identifiable.Server and Holder.Server"
    )


def test_interface_with_persistent_inheritance(generated_dir):
    """Test interfaces that extend Persistent.

    Service in climate.capnp extends Identifiable and Persistent.
    We use Service instead of Dataset due to Dataset having complex dependency issues.
    """
    schema_files = [
        ZALFMAS_DIR / "climate.capnp",
        ZALFMAS_DIR / "common.capnp",
        ZALFMAS_DIR / "persistence.capnp",
        ZALFMAS_DIR / "date.capnp",
        ZALFMAS_DIR / "geo.capnp",
    ]

    schema_paths = [str(f) for f in schema_files]
    args = ["-p"] + schema_paths + ["-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    stub_file = generated_dir / "climate_capnp.pyi"
    assert stub_file.exists(), "Stub file was not generated"

    content = stub_file.read_text()

    # Check that Service extends both Identifiable and Persistent
    assert "class Service(Identifiable, Persistent, Protocol):" in content, (
        "Service should extend both Identifiable and Persistent"
    )

    # Check Server class inheritance - Service.Server should extend both base Servers
    lines = content.split("\n")
    in_service = False
    found_server_inheritance = False

    for i, line in enumerate(lines):
        if "class Service(Identifiable, Persistent, Protocol):" in line:
            in_service = True
        elif in_service and "class Server(Identifiable.Server, Persistent.Server):" in line:
            found_server_inheritance = True
            break
        elif in_service and line.startswith("class ") and "Service" not in line and "Server" not in line:
            break

    assert found_server_inheritance, "Service.Server should extend both Identifiable.Server and Persistent.Server"


def test_interface_inheritance_in_nested_interfaces(generated_dir):
    """Test that nested interfaces that extend other interfaces show inheritance.

    In cluster_admin_service.capnp, AdminMaster, UserMaster, and Runtime
    all extend Identifiable.
    """
    schema_files = [
        ZALFMAS_DIR / "cluster_admin_service.capnp",
        ZALFMAS_DIR / "common.capnp",
    ]

    schema_paths = [str(f) for f in schema_files]
    args = ["-p"] + schema_paths + ["-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    stub_file = generated_dir / "cluster_admin_service_capnp.pyi"
    assert stub_file.exists(), "Stub file was not generated"

    content = stub_file.read_text()

    # Check nested interfaces extend Identifiable
    assert "class AdminMaster(Identifiable, Protocol):" in content, "AdminMaster should extend Identifiable"
    assert "class UserMaster(Identifiable, Protocol):" in content, "UserMaster should extend Identifiable"
    assert "class Runtime(Identifiable, Protocol):" in content, "Runtime should extend Identifiable"

    # Check that all Server classes extend Identifiable.Server
    # Count how many times we see "class Server(Identifiable.Server):"
    # within the context of AdminMaster, UserMaster, or Runtime
    server_inheritance_count = content.count("class Server(Identifiable.Server):")

    # We should find at least 3 Server classes extending Identifiable.Server
    # (one for each of AdminMaster, UserMaster, and Runtime)
    assert server_inheritance_count >= 3, (
        f"Should have at least 3 Server classes extending Identifiable.Server, found {server_inheritance_count}"
    )


def test_interface_method_inheritance_visibility(generated_dir):
    """Test that methods from parent interfaces are accessible via inheritance.

    When ClimateInstance extends Identifiable, users should be able to:
    1. See Identifiable's methods through type checking
    2. Implement ClimateInstance.Server by also implementing Identifiable.Server methods
    """
    # Generate stubs
    schema_files = [
        ZALFMAS_DIR / "model.capnp",
        ZALFMAS_DIR / "common.capnp",
        ZALFMAS_DIR / "climate.capnp",
        ZALFMAS_DIR / "soil.capnp",
        ZALFMAS_DIR / "management.capnp",
        ZALFMAS_DIR / "persistence.capnp",
        ZALFMAS_DIR / "service.capnp",
        ZALFMAS_DIR / "date.capnp",
        ZALFMAS_DIR / "geo.capnp",
    ]

    schema_paths = [str(f) for f in schema_files]
    args = ["-p"] + schema_paths + ["-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    # Read both stub files
    model_stub = (generated_dir / "model_capnp.pyi").read_text()
    common_stub = (generated_dir / "common_capnp.pyi").read_text()

    # Verify Identifiable has info() method
    assert "def info(self)" in common_stub, "Identifiable should have info() method"

    # Verify ClimateInstance extends Identifiable (and thus inherits info())
    assert "class ClimateInstance(Identifiable, Protocol):" in model_stub, "ClimateInstance should extend Identifiable"

    # The actual info() method will be inherited from Identifiable via Protocol inheritance
    # Python's Protocol mechanism handles this - we don't need to repeat the method


def test_empty_interface_with_inheritance(generated_dir):
    """Test that interfaces with no methods but with inheritance work correctly.

    IdentifiableHolder has no methods of its own, but extends two other interfaces.
    """
    schema_file = ZALFMAS_DIR / "common.capnp"
    args = ["-p", str(schema_file), "-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    stub_file = generated_dir / "common_capnp.pyi"
    assert stub_file.exists(), "Stub file was not generated"

    content = stub_file.read_text()

    # Find IdentifiableHolder class
    lines = content.split("\n")
    in_identifiable_holder = False
    holder_content = []

    for line in lines:
        if "class IdentifiableHolder(Identifiable, Holder, Protocol):" in line:
            in_identifiable_holder = True
            holder_content.append(line)
        elif in_identifiable_holder:
            if line.startswith("class ") and "Server" not in line:
                break
            holder_content.append(line)

    holder_text = "\n".join(holder_content)

    # Should have inheritance but minimal body
    assert "class IdentifiableHolder(Identifiable, Holder, Protocol):" in holder_text
    assert "..." in holder_text  # Should have ellipsis for empty body
    assert "class Server(Identifiable.Server, Holder.Server):" in holder_text
