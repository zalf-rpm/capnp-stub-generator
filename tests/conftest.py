"""Central pytest configuration and shared fixtures for capnp-stub-generator tests.

This module provides:
- Centralized stub generation with proper ordering
- Shared fixtures for all tests
- Common helper functions
- Proper setup and teardown
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

# Test directories
TESTS_DIR = Path(__file__).parent
SCHEMAS_DIR = TESTS_DIR / "schemas"
EXAMPLES_DIR = TESTS_DIR / "examples"
ZALFMAS_DIR = TESTS_DIR / "zalfmas_capnp_schemas"

# Generated output directories (centralized)
GENERATED_DIR = TESTS_DIR / "_generated"
GENERATED_EXAMPLES_DIR = TESTS_DIR / "_generated_examples"
GENERATED_ADDRESSBOOK_DIR = TESTS_DIR / "_generated_addressbook_typing"
GENERATED_ZALFMAS_DIR = TESTS_DIR / "_generated_zalfmas"


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "stub_generation: mark test as requiring stub generation")
    config.addinivalue_line(
        "markers", "pyright_validation: mark test as requiring pyright validation"
    )
    config.addinivalue_line("markers", "order(n): specify test execution order")


@pytest.fixture(scope="session", autouse=True)
def cleanup_generated_dirs():
    """Clean up all generated directories before and after test session."""
    # Setup: ensure clean slate
    generated_dirs = [
        GENERATED_DIR,
        GENERATED_EXAMPLES_DIR,
        GENERATED_ADDRESSBOOK_DIR,
        GENERATED_ZALFMAS_DIR,
    ]

    for gen_dir in generated_dirs:
        if gen_dir.exists():
            shutil.rmtree(gen_dir)
        gen_dir.mkdir(parents=True, exist_ok=True)

    yield

    # Teardown: optionally keep generated files for inspection
    # Uncomment to clean up after tests
    # for gen_dir in generated_dirs:
    #     if gen_dir.exists():
    #         shutil.rmtree(gen_dir)


@pytest.fixture(scope="session")
def generate_core_stubs():
    """Generate stubs for core test schemas (dummy.capnp, etc.) once per session."""
    from capnp_stub_generator.cli import main

    # Generate all core schema stubs in one go
    schema_files = [
        SCHEMAS_DIR / "dummy.capnp",
        SCHEMAS_DIR / "primitives.capnp",
        SCHEMAS_DIR / "nested.capnp",
        SCHEMAS_DIR / "unions.capnp",
        SCHEMAS_DIR / "interfaces.capnp",
        SCHEMAS_DIR / "advanced_features.capnp",
    ]

    existing_schemas = [str(s) for s in schema_files if s.exists()]

    if existing_schemas:
        main(["-p"] + existing_schemas + ["-o", str(GENERATED_DIR)])

    return GENERATED_DIR


@pytest.fixture(scope="session")
def generate_import_stubs():
    """Generate stubs for import test schemas."""
    from capnp_stub_generator.cli import main

    import_base = SCHEMAS_DIR / "import_base.capnp"
    import_user = SCHEMAS_DIR / "import_user.capnp"

    if import_base.exists() and import_user.exists():
        main(["-p", str(import_base), str(import_user), "-o", str(GENERATED_DIR)])

    return GENERATED_DIR


@pytest.fixture(scope="session")
def generate_addressbook_stubs():
    """Generate stubs for addressbook example."""
    from capnp_stub_generator.cli import main

    addressbook_schema = EXAMPLES_DIR / "addressbook" / "addressbook.capnp"

    if addressbook_schema.exists():
        main(["-p", str(addressbook_schema), "-o", str(GENERATED_ADDRESSBOOK_DIR)])

    return GENERATED_ADDRESSBOOK_DIR


@pytest.fixture(scope="session")
def generate_calculator_stubs():
    """Generate stubs for calculator example."""
    from capnp_stub_generator.cli import main

    calculator_schema = EXAMPLES_DIR / "calculator" / "calculator.capnp"
    calculator_output = GENERATED_EXAMPLES_DIR / "calculator"

    if calculator_schema.exists():
        calculator_output.mkdir(parents=True, exist_ok=True)
        main(["-p", str(calculator_schema), "-o", str(calculator_output)])
        # Copy the .capnp file to the output directory so it can be loaded
        shutil.copy(calculator_schema, calculator_output / "calculator.capnp")

    return calculator_output


@pytest.fixture(scope="session")
def generate_all_example_stubs():
    """Generate stubs for all example schemas."""
    from capnp_stub_generator.cli import main

    examples = ["addressbook", "calculator"]
    generated = {}

    for example in examples:
        schema_path = EXAMPLES_DIR / example / f"{example}.capnp"
        output_dir = GENERATED_EXAMPLES_DIR / example

        if schema_path.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            main(["-p", str(schema_path), "-o", str(output_dir)])
            generated[example] = output_dir

    return generated


# Helper functions


def read_stub_file(stub_path: Path) -> list[str]:
    """Read a stub file and return lines."""
    with open(stub_path, encoding="utf-8") as f:
        return f.readlines()


def generate_stub_from_schema(schema_name: str, output_dir: Path | None = None) -> Path:
    """Generate a stub from a schema file and return the stub path."""
    from capnp_stub_generator.cli import main

    if output_dir is None:
        output_dir = GENERATED_DIR

    output_dir.mkdir(parents=True, exist_ok=True)
    schema_path = SCHEMAS_DIR / schema_name

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    main(["-p", str(schema_path), "-o", str(output_dir)])

    stub_name = schema_name.replace(".capnp", "_capnp.pyi")
    return output_dir / stub_name


def run_pyright(file_path: Path, cwd: Path | None = None) -> tuple[int, str]:
    """Run pyright on a file and return error count and output."""
    if cwd is None:
        cwd = TESTS_DIR

    result = subprocess.run(
        ["pyright", str(file_path)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )
    error_count = result.stdout.count("error:")
    return error_count, result.stdout


def run_pyright_on_directory(dir_path: Path) -> tuple[int, str]:
    """Run pyright on all files in a directory."""
    result = subprocess.run(
        ["pyright", str(dir_path)],
        capture_output=True,
        text=True,
    )
    error_count = result.stdout.count("error:")
    return error_count, result.stdout


# Test ordering hook
def pytest_collection_modifyitems(config, items):
    """Order tests based on dependencies and markers."""
    # Define test order groups
    order_groups = {
        # 1. Core stub generation tests (no dependencies)
        "generation": [
            "test_generation_extended",
            "test_basic_low",
            "test_mid_features",
        ],
        # 2. Dummy schema tests (depend on core generation)
        "dummy": [
            "test_dummy_enums_and_all_types",
            "test_dummy_lists_and_defaults",
            "test_dummy_groups_and_nested",
            "test_dummy_unions",
            "test_dummy_constants_versions_names",
        ],
        # 3. Advanced feature tests
        "advanced": [
            "test_advanced_unions",
            "test_advanced_groups",
            "test_advanced_versioning_constants",
            "test_advanced_name_annotations",
            "test_advanced_complex_lists",
            "test_advanced_generics_anypointer_interface",
        ],
        # 4. Typing validation tests
        "typing": [
            "test_init_list_typing",
            "test_enum_literal_validation",
            "test_addressbook_typing",
        ],
        # 5. Example tests
        "examples": [
            "test_calculator_baseline",
            "test_calculator_nesting",
            "test_real_world_examples",
        ],
        # 6. Runtime and integration tests
        "runtime": [
            "test_capnp_stubs",
            "test_pyright_validation",
        ],
    }

    # Create order mapping
    order_map = {}
    for order_idx, (group_name, modules) in enumerate(order_groups.items()):
        for module_idx, module_name in enumerate(modules):
            order_map[module_name] = (order_idx, module_idx)

    # Add zalfmas tests at the end (but before unknown tests)
    zalfmas_order = (len(order_groups), 0)

    # Sort items by order
    def get_order(item):
        module_name = item.module.__name__.replace("tests.", "").replace("test_", "test_")
        
        # Zalfmas tests go near the end
        if "zalfmas" in module_name:
            return zalfmas_order
        
        # Extract just the test file name without test_ prefix
        for key in order_map:
            if key in module_name or module_name.endswith(key):
                return order_map[key]
        # Unknown tests go last
        return (999, 999)

    items.sort(key=get_order)
