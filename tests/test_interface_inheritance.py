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
ZALFMAS_DIR = TESTS_DIR / "schemas" / "zalfmas"
IDENTIFIABLE_DIR = TESTS_DIR / "schemas" / "examples" / "identifiable"
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
        ZALFMAS_DIR / "crop.capnp",
        ZALFMAS_DIR / "registry.capnp",
        ZALFMAS_DIR / "persistence.capnp",
        ZALFMAS_DIR / "service.capnp",
        ZALFMAS_DIR / "date.capnp",
        ZALFMAS_DIR / "geo.capnp",
    ]

    schema_paths = [str(f) for f in schema_files]
    args = ["-p"] + schema_paths + ["-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    # Check the generated stub (in zalfmas subdirectory due to structure preservation)
    stub_file = generated_dir / "zalfmas" / "model_capnp.pyi"
    assert stub_file.exists(), f"Stub file was not generated at {stub_file}"

    content = stub_file.read_text()

    # Check that ClimateInstance interface exists as Protocol
    assert "class _ClimateInstanceModule(" in content, "ClimateInstance Protocol module should exist"
    assert "ClimateInstance: _ClimateInstanceModule" in content, "ClimateInstance annotation should exist"

    # Check that ClimateInstanceClient extends IdentifiableClient (nested in Protocol)
    # The Client inherits from the full Protocol path
    assert "class ClimateInstanceClient(_IdentifiableModule.IdentifiableClient)" in content, (
        "ClimateInstanceClient should extend _IdentifiableModule.IdentifiableClient"
    )

    # Check that _ClimateInstanceModule.Server extends _IdentifiableModule.Server
    # The Server class should be nested inside _ClimateInstanceModule
    lines = content.split("\n")
    in_climate_instance = False
    found_server_inheritance = False

    for i, line in enumerate(lines):
        if "class _ClimateInstanceModule(" in line:
            in_climate_instance = True
        elif in_climate_instance and "class Server(" in line and "_IdentifiableModule.Server" in line:
            found_server_inheritance = True
            break
        elif in_climate_instance and line.startswith("class _") and "ClimateInstanceModule" not in line:
            # We've moved to a different top-level class
            break

    assert found_server_inheritance, "_ClimateInstanceModule.Server should extend _IdentifiableModule.Server"


def test_multiple_interface_inheritance(generated_dir):
    """Test that an interface extending multiple interfaces shows all inheritance.

    IdentifiableHolder extends both Identifiable and Holder(T), so:
    - class IdentifiableHolder:
    - class Server(Identifiable.Server, Holder.Server):
    """
    # Generate stub for common.capnp
    schema_file = ZALFMAS_DIR / "common.capnp"
    args = ["-p", str(schema_file), "-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    stub_file = generated_dir / "zalfmas" / "common_capnp.pyi"
    assert stub_file.exists(), "Stub file was not generated"

    content = stub_file.read_text()

    # Check that IdentifiableHolder exists as Protocol
    assert "class _IdentifiableHolderModule(" in content, "IdentifiableHolder Protocol module should exist"
    assert "IdentifiableHolder: _IdentifiableHolderModule" in content, "IdentifiableHolder annotation should exist"

    # Check that IdentifiableHolderClient extends both IdentifiableClient and HolderClient
    assert (
        "class IdentifiableHolderClient(_IdentifiableModule.IdentifiableClient, _HolderModule.HolderClient)" in content
    ), (
        "IdentifiableHolderClient should extend both _IdentifiableModule.IdentifiableClient and _HolderModule.HolderClient"
    )

    # Check that IdentifiableHolder.Server extends both base Servers
    lines = content.split("\n")
    in_identifiable_holder = False
    found_server_inheritance = False

    for i, line in enumerate(lines):
        if "class _IdentifiableHolderModule(" in line:
            in_identifiable_holder = True
        elif in_identifiable_holder and "class Server(_IdentifiableModule.Server, _HolderModule.Server)" in line:
            found_server_inheritance = True
            break
        elif in_identifiable_holder and line.startswith("class _") and "IdentifiableHolderModule" not in line:
            break

    assert found_server_inheritance, (
        "_IdentifiableHolderModule.Server should extend both _IdentifiableModule.Server and _HolderModule.Server"
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

    stub_file = generated_dir / "zalfmas" / "climate_capnp.pyi"
    assert stub_file.exists(), "Stub file was not generated"

    content = stub_file.read_text()

    # Check that Service extends both Identifiable and Persistent (no longer needs Protocol suffix)
    assert "class _ServiceModule(_IdentifiableModule, _PersistentModule):" in content, (
        "Service Module should extend both Identifiable and Persistent"
    )

    # Check Server class inheritance - Service.Server should extend both base Servers
    lines = content.split("\n")
    in_service = False
    found_server_inheritance = False

    for i, line in enumerate(lines):
        if "class _ServiceModule(" in line:
            in_service = True
        elif in_service and "class Server(_IdentifiableModule.Server, _PersistentModule.Server)" in line:
            found_server_inheritance = True
            break
        elif in_service and line.startswith("class _") and "ServiceModule" not in line and "Server" not in line:
            break

    assert found_server_inheritance, (
        "_ServiceModule.Server should extend both _IdentifiableModule.Server and _PersistentModule.Server"
    )


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

    stub_file = generated_dir / "zalfmas" / "cluster_admin_service_capnp.pyi"
    assert stub_file.exists(), "Stub file was not generated"

    content = stub_file.read_text()

    # Check nested interfaces extend Identifiable (no longer needs Protocol suffix)
    assert "class _AdminMasterModule(_IdentifiableModule):" in content, (
        "AdminMaster Module should extend Identifiable"
    )
    assert "class _UserMasterModule(_IdentifiableModule):" in content, (
        "UserMaster Module should extend Identifiable"
    )
    assert "class _RuntimeModule(_IdentifiableModule):" in content, (
        "Runtime Module should extend Identifiable"
    )

    # Check that all Server classes extend _IdentifiableModule.Server
    # Count how many times we see "class Server(_IdentifiableModule.Server"
    server_inheritance_count = content.count("class Server(_IdentifiableModule.Server")

    # We should find at least 3 Server classes extending _IdentifiableModule.Server
    # (one for each of AdminMaster, UserMaster, and Runtime)
    assert server_inheritance_count >= 3, (
        f"Should have at least 3 Server classes extending _IdentifiableModule.Server, found {server_inheritance_count}"
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
        ZALFMAS_DIR / "crop.capnp",
        ZALFMAS_DIR / "registry.capnp",
        ZALFMAS_DIR / "persistence.capnp",
        ZALFMAS_DIR / "service.capnp",
        ZALFMAS_DIR / "date.capnp",
        ZALFMAS_DIR / "geo.capnp",
    ]

    schema_paths = [str(f) for f in schema_files]
    args = ["-p"] + schema_paths + ["-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    # Read both stub files
    model_stub = (generated_dir / "zalfmas" / "model_capnp.pyi").read_text()
    common_stub = (generated_dir / "zalfmas" / "common_capnp.pyi").read_text()

    # Verify Identifiable has info() method
    # This should be in the IdentifiableClient class
    assert "class IdentifiableClient(_DynamicCapabilityClient):" in common_stub, "Should have IdentifiableClient"
    assert "def info(self)" in common_stub, "Identifiable should have info() method"

    # Verify ClimateInstance interface exists and ClimateInstanceClient extends IdentifiableClient
    assert "class _ClimateInstanceModule(" in model_stub, "ClimateInstance Module should exist"
    assert "class ClimateInstanceClient(_IdentifiableModule.IdentifiableClient)" in model_stub, (
        "ClimateInstanceClient should extend _IdentifiableModule.IdentifiableClient"
    )

    # The actual info() method will be inherited from IdentifiableClient via inheritance
    # Python's Protocol mechanism handles this - we don't need to repeat the method


def test_empty_interface_with_inheritance(generated_dir):
    """Test that interfaces with no methods but with inheritance work correctly.

    IdentifiableHolder has no methods of its own, but extends two other interfaces.
    """
    schema_file = ZALFMAS_DIR / "common.capnp"
    args = ["-p", str(schema_file), "-o", str(generated_dir), "-I", str(ZALFMAS_DIR)]
    main(args)

    stub_file = generated_dir / "zalfmas" / "common_capnp.pyi"
    assert stub_file.exists(), "Stub file was not generated"

    content = stub_file.read_text()

    # Find _IdentifiableHolderModule class
    lines = content.split("\n")
    in_identifiable_holder = False
    holder_content = []

    for line in lines:
        if "class _IdentifiableHolderModule(" in line:
            in_identifiable_holder = True
            holder_content.append(line)
        elif in_identifiable_holder:
            if line.startswith("class _") and "Server" not in line and "IdentifiableHolderModule" not in line:
                break
            holder_content.append(line)

    holder_text = "\n".join(holder_content)

    # Should have inheritance but minimal body
    assert "class _IdentifiableHolderModule(" in holder_text
    assert "..." in holder_text  # Should have ellipsis for empty body
    assert "class Server(_IdentifiableModule.Server, _HolderModule.Server)" in holder_text
