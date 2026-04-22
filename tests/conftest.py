"""Pytest configuration and fixtures for capnp stub generator tests."""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

from capnp_stub_generator.run import run
from tests.test_helpers import read_generated_types_lines, run_command, run_pyright

# Test directory structure
TESTS_DIR = Path(__file__).parent
REPO_ROOT = TESTS_DIR.parent
SCHEMAS_DIR = TESTS_DIR / "schemas"
GENERATED_DIR = TESTS_DIR / "_generated"
TYPINGS_DIR = REPO_ROOT / "typings"

# Schema subdirectories
BASIC_SCHEMAS_DIR = SCHEMAS_DIR / "basic"
EXAMPLES_SCHEMAS_DIR = SCHEMAS_DIR / "examples"
ZALFMAS_SCHEMAS_DIR = SCHEMAS_DIR / "zalfmas"
CAPNP_SCHEMAS_DIR = SCHEMAS_DIR / "capnp"

# Generated output subdirectories
BASIC_GENERATED_DIR = GENERATED_DIR / "basic"
EXAMPLES_GENERATED_DIR = GENERATED_DIR / "examples"
ZALFMAS_GENERATED_DIR = GENERATED_DIR / "zalfmas"
ZALFMAS_NO_ANNOTATIONS_GENERATED_DIR = GENERATED_DIR / "zalfmas_no_annotations"
CAPNP_GENERATED_DIR = GENERATED_DIR / "capnp"
LOGGER = logging.getLogger(__name__)
DOGFOOD_DEPENDENCY_DIRS = ("capnp-stubs", "schema_capnp")
DOGFOOD_IGNORED_DIRS = {"__pycache__", ".ruff_cache"}


@dataclass(frozen=True)
class CompileRequest:
    """Parameters describing one schema compilation pass."""

    schema_dir: Path
    output_dir: Path
    description: str
    failure_message: str
    import_paths: list[str] | None = None


def _clean_generated_dir() -> None:
    """Remove and recreate the shared generated test directory."""
    if GENERATED_DIR.exists():
        shutil.rmtree(GENERATED_DIR)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def _write_generated_package_markers() -> None:
    """Ensure generated stub parent directories are importable as packages."""
    package_dirs = (
        GENERATED_DIR,
        BASIC_GENERATED_DIR,
        EXAMPLES_GENERATED_DIR,
        ZALFMAS_GENERATED_DIR,
        ZALFMAS_NO_ANNOTATIONS_GENERATED_DIR,
        CAPNP_GENERATED_DIR,
    )
    for package_dir in package_dirs:
        if not package_dir.exists():
            continue
        init_file = package_dir / "__init__.py"
        if init_file.exists():
            continue
        init_file.write_text(
            f'"""Generated stub package container for `{package_dir.relative_to(TESTS_DIR).as_posix()}`."""\n',
            encoding="utf8",
        )


def _replace_tree(source_dir: Path, destination_dir: Path) -> None:
    """Replace a destination tree with a fresh copy of a generated source tree."""
    if destination_dir.exists():
        shutil.rmtree(destination_dir)
    shutil.copytree(
        source_dir,
        destination_dir,
        ignore=shutil.ignore_patterns(*DOGFOOD_IGNORED_DIRS),
    )


def _sync_dogfood_typings_from_examples() -> None:
    """Refresh the tracked `typings/` snapshot from the generated example stubs."""
    if not EXAMPLES_GENERATED_DIR.is_dir():
        pytest.fail(f"Generated examples directory missing: {EXAMPLES_GENERATED_DIR}")

    TYPINGS_DIR.mkdir(parents=True, exist_ok=True)

    source_dirs = {path.name: path for path in EXAMPLES_GENERATED_DIR.iterdir() if path.is_dir()}
    missing_dependency_dirs = [name for name in DOGFOOD_DEPENDENCY_DIRS if name not in source_dirs]
    if missing_dependency_dirs:
        pytest.fail(
            "Generated examples are missing bundled dependency directories: "
            + ", ".join(sorted(missing_dependency_dirs)),
        )

    stale_top_level_dirs = {path.name for path in EXAMPLES_SCHEMAS_DIR.iterdir() if path.is_dir()} | set(
        DOGFOOD_DEPENDENCY_DIRS
    )
    for directory_name in stale_top_level_dirs:
        destination_dir = TYPINGS_DIR / directory_name
        if destination_dir.exists():
            shutil.rmtree(destination_dir)

    for directory_name, source_dir in source_dirs.items():
        if directory_name in DOGFOOD_IGNORED_DIRS:
            continue
        _replace_tree(source_dir, TYPINGS_DIR / directory_name)

    LOGGER.info("✓ Refreshed dogfood typings in %s", TYPINGS_DIR)


def _get_plugin_path() -> Path:
    """Return the capnpc plugin path and fail loudly if it is missing."""
    plugin_path = Path(__file__).parent.parent / "src" / "capnp_stub_generator" / "capnpc_plugin.py"
    if not plugin_path.exists():
        pytest.fail(f"Plugin not found at {plugin_path}")
    return plugin_path


def _create_wrapper_script() -> Path:
    """Create an executable wrapper for the capnpc Python plugin."""
    with tempfile.NamedTemporaryFile(mode="w", suffix="_capnpc_python", delete=False) as wrapper:
        wrapper.write(f"""#!/usr/bin/env {sys.executable}
import sys
sys.path.insert(0, {str(Path(__file__).parent.parent / "src")!r})
from capnp_stub_generator.capnpc_plugin import main
main()
""")
        wrapper_path = Path(wrapper.name)

    wrapper_path.chmod(0o700)
    return wrapper_path


def _run_compile_command(
    cmd: list[str],
    *,
    failure_message: str,
    schema_dir: Path,
) -> None:
    """Run a capnp compile command and fail the test session on errors."""
    LOGGER.debug("Running: %s", " ".join(cmd))
    result = run_command(cmd)
    if result.returncode == 0:
        return

    LOGGER.error("Failed to compile schemas from %s:\n%s", schema_dir, result.stderr)
    LOGGER.error("stdout: %s", result.stdout)
    pytest.fail(f"{failure_message}: {result.stderr}")


def _compile_schema_files(
    request: CompileRequest,
    schema_files: list[Path],
    wrapper_path: Path,
) -> None:
    """Compile a specific list of schema files using the capnp plugin."""
    if not schema_files:
        LOGGER.warning("No schema files found in %s", request.schema_dir)
        return

    LOGGER.info("Compiling %s", request.description)
    request.output_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["capnp", "compile", f"--src-prefix={request.schema_dir}", f"-o{wrapper_path}:{request.output_dir}"]
    for import_path in request.import_paths or []:
        cmd.extend(["-I", import_path])
    cmd.extend(str(schema_file) for schema_file in schema_files)
    _run_compile_command(cmd, failure_message=request.failure_message, schema_dir=request.schema_dir)
    LOGGER.info("✓ Generated stubs in %s", request.output_dir)


def _compile_schema_tree(
    request: CompileRequest,
    wrapper_path: Path,
) -> None:
    """Compile all schemas under a directory."""
    _compile_schema_files(request, list(request.schema_dir.rglob("*.capnp")), wrapper_path)


def _filtered_schema_files(schema_dir: Path) -> list[Path]:
    """Return schema files excluding duplicate-ID and bundled system schemas."""
    return [
        schema_file
        for schema_file in schema_dir.rglob("*.capnp")
        if schema_file.name != "a.capnp" and "capnp" not in schema_file.relative_to(schema_dir).parts
    ]


def _compile_filtered_zalfmas_schemas(
    request: CompileRequest,
    wrapper_path: Path,
) -> None:
    """Compile zalfmas-style schemas after filtering unsupported inputs."""
    _compile_schema_files(request, _filtered_schema_files(request.schema_dir), wrapper_path)


def _validate_generated_stubs_with_pyright() -> None:
    """Run pyright against generated stubs that are expected to type check cleanly."""
    LOGGER.info("Running pyright validation on generated stubs...")
    basic_stubs_to_check = [
        str(path) for path in BASIC_GENERATED_DIR.iterdir() if path.is_dir() and path.name != "capnp-stubs"
    ]
    examples_stubs_to_check = [
        str(path) for path in EXAMPLES_GENERATED_DIR.iterdir() if path.is_dir() and path.name != "capnp-stubs"
    ]
    pyright_result = run_pyright(*basic_stubs_to_check, *examples_stubs_to_check)
    if pyright_result.returncode == 0:
        LOGGER.info("✓ Pyright validation passed")
        return

    error_lines = [line for line in pyright_result.stdout.split("\n") if " error:" in line]
    if error_lines:
        LOGGER.error("Pyright validation failed:\n%s", pyright_result.stdout)
        pytest.fail(f"Pyright validation failed with {len(error_lines)} error(s)")
    LOGGER.info("✓ Pyright validation passed")


@pytest.fixture(scope="session", autouse=True)
def generate_all_stubs() -> dict[str, Path]:
    """Generate all test stubs once at the beginning of the test session.

    This fixture runs automatically before any tests and generates stubs for:
    - Basic test schemas
    - Example schemas (calculator, addressbook, etc.)
    - Zalfmas schemas

    Uses the capnp compile plugin approach to ensure all schemas including
    groups in unions are properly handled.

    All other tests should use the generated stubs from this fixture.
    """
    LOGGER.info("Generating all test stubs using capnp compile plugin...")

    _clean_generated_dir()
    _ = _get_plugin_path()
    wrapper_path = _create_wrapper_script()

    try:
        _compile_schema_tree(
            CompileRequest(
                BASIC_SCHEMAS_DIR,
                BASIC_GENERATED_DIR,
                f"{len(list(BASIC_SCHEMAS_DIR.rglob('*.capnp')))} schemas from {BASIC_SCHEMAS_DIR}",
                "Schema compilation failed",
            ),
            wrapper_path,
        )
        _compile_schema_tree(
            CompileRequest(
                EXAMPLES_SCHEMAS_DIR,
                EXAMPLES_GENERATED_DIR,
                f"{len(list(EXAMPLES_SCHEMAS_DIR.rglob('*.capnp')))} schemas from {EXAMPLES_SCHEMAS_DIR}",
                "Schema compilation failed",
            ),
            wrapper_path,
        )
        if CAPNP_SCHEMAS_DIR.exists():
            _compile_schema_tree(
                CompileRequest(
                    CAPNP_SCHEMAS_DIR,
                    CAPNP_GENERATED_DIR,
                    f"{len(list(CAPNP_SCHEMAS_DIR.rglob('*.capnp')))} schemas from {CAPNP_SCHEMAS_DIR}",
                    "Schema compilation failed",
                ),
                wrapper_path,
            )

        _compile_filtered_zalfmas_schemas(
            CompileRequest(
                ZALFMAS_SCHEMAS_DIR,
                ZALFMAS_GENERATED_DIR,
                f"{len(_filtered_schema_files(ZALFMAS_SCHEMAS_DIR))} zalfmas schemas (WITH Python annotations)",
                "Zalfmas schema compilation failed",
                [str(ZALFMAS_SCHEMAS_DIR)],
            ),
            wrapper_path,
        )

        zalfmas_no_ann_source = SCHEMAS_DIR / "zalfmas_no_annotations"
        if zalfmas_no_ann_source.exists():
            _compile_filtered_zalfmas_schemas(
                CompileRequest(
                    zalfmas_no_ann_source,
                    ZALFMAS_NO_ANNOTATIONS_GENERATED_DIR,
                    f"{len(_filtered_schema_files(zalfmas_no_ann_source))} zalfmas schemas (WITHOUT Python annotations)",
                    "Zalfmas schema compilation (no annotations) failed",
                    [str(zalfmas_no_ann_source)],
                ),
                wrapper_path,
            )

        LOGGER.info("✓ All test stubs generated successfully using capnp compile")
        _write_generated_package_markers()
        _sync_dogfood_typings_from_examples()
        _validate_generated_stubs_with_pyright()

    finally:
        wrapper_path.unlink(missing_ok=True)

    return {
        "basic": BASIC_GENERATED_DIR,
        "examples": EXAMPLES_GENERATED_DIR,
        "zalfmas": ZALFMAS_GENERATED_DIR,
        "zalfmas_no_annotations": ZALFMAS_NO_ANNOTATIONS_GENERATED_DIR,
        "capnp": CAPNP_GENERATED_DIR,
    }


@pytest.fixture(scope="session")
def generated_stubs(generate_all_stubs: dict[str, Path]) -> dict[str, Path]:
    """Provide access to generated stub directories.

    Returns:
        dict: Dictionary with keys "basic", "examples", "zalfmas", "capnp"
              pointing to generated stub directories.

    """
    return generate_all_stubs


@pytest.fixture(scope="session")
def calculator_stubs(generated_stubs: dict[str, Path]) -> Path:
    """Provide path to generated calculator stubs."""
    return generated_stubs["examples"] / "calculator"


@pytest.fixture(scope="session")
def addressbook_stubs(generated_stubs: dict[str, Path]) -> Path:
    """Provide path to generated addressbook stubs."""
    return generated_stubs["examples"] / "addressbook"


@pytest.fixture(scope="session")
def basic_stubs(generated_stubs: dict[str, Path]) -> Path:
    """Provide path to generated basic test stubs."""
    return generated_stubs["basic"]


@pytest.fixture(scope="session")
def zalfmas_stubs(generated_stubs: dict[str, Path]) -> Path:
    """Provide path to generated zalfmas stubs (with annotations)."""
    return generated_stubs["zalfmas"]


@pytest.fixture(scope="session")
def zalfmas_no_annotations_stubs(generated_stubs: dict[str, Path]) -> Path:
    """Provide path to generated zalfmas stubs (without annotations)."""
    return generated_stubs["zalfmas_no_annotations"]


@pytest.fixture(scope="session")
def capnp_stubs(generated_stubs: dict[str, Path]) -> Path:
    """Provide path to generated capnp stubs (schema.capnp, c++.capnp)."""
    return generated_stubs["capnp"]


# Legacy fixtures for backward compatibility (deprecated)
@pytest.fixture
def generate_calculator_stubs(calculator_stubs: Path) -> Path:
    """Use the calculator_stubs fixture instead."""
    return calculator_stubs


@pytest.fixture
def calculator_stub_lines(calculator_stubs: Path) -> list[str]:
    """Read calculator typing helper lines from the generated helper modules."""
    return read_generated_types_lines(calculator_stubs / "calculator_capnp")


# Constants for backward compatibility
SCHEMAS_DIR_OLD = BASIC_SCHEMAS_DIR  # For tests that reference SCHEMAS_DIR


# Helper functions for tests
def read_stub_file(stub_path: Path) -> list[str]:
    """Read a stub file and return its lines.

    Args:
        stub_path: Path to the .pyi stub file

    Returns:
        List of lines from the stub file

    """
    with stub_path.open() as f:
        return f.readlines()


def runtime_stub_path(stub_root: Path, module_name: str) -> Path:
    """Return the runtime-facing __init__.pyi for one generated schema package."""
    return stub_root / module_name / "__init__.pyi"


def types_stub_path(stub_root: Path, module_name: str, *relative_parts: str) -> Path:
    """Return a file inside the generated per-schema types package."""
    return stub_root / module_name / "types" / Path(*relative_parts)


def generate_stub_from_schema(schema_name: str, output_dir: Path) -> Path:
    """Generate a stub from a schema file (for temporary test generation).

    This should only be used for tests that need custom generation.
    Most tests should use the pre-generated stubs from generate_all_stubs fixture.

    Uses the run module directly.

    Args:
        schema_name: Name of the schema file (e.g., "calculator.capnp")
        output_dir: Directory to write the generated stub

    Returns:
        Path to the generated .pyi file

    """
    # Find the schema file in any of the schema directories
    schema_path = None
    for schema_dir in [BASIC_SCHEMAS_DIR, EXAMPLES_SCHEMAS_DIR, ZALFMAS_SCHEMAS_DIR]:
        candidate = schema_dir / schema_name
        if candidate.exists():
            schema_path = candidate
            break
        # Also check subdirectories
        for subdir in schema_dir.rglob("*"):
            if subdir.is_dir():
                candidate = subdir / schema_name
                if candidate.exists():
                    schema_path = candidate
                    break
        if schema_path:
            break

    if not schema_path:
        pytest.fail(f"Schema {schema_name} not found in schema directories")

    # Create minimal args namespace
    args = argparse.Namespace(
        paths=[str(schema_path)],
        output_dir=str(output_dir),
        excludes=[],
        recursive=False,
        clean=[],
        import_paths=[],
        skip_pyright=True,
        augment_capnp_stubs=False,
    )

    # Call run
    run(args, str(schema_path.parent))

    # Return path to generated .pyi file (as package)
    stub_name = schema_path.stem + "_capnp"
    return output_dir / stub_name / "__init__.pyi"


# Specific stub fixtures for individual files
@pytest.fixture(scope="session")
def dummy_stub_file(basic_stubs: Path) -> Path:
    """Provide path to the main dummy helper module for direct file reads."""
    return types_stub_path(basic_stubs, "dummy_capnp", "modules.pyi")


@pytest.fixture(scope="session")
def dummy_stub_lines(dummy_stub_file: Path) -> list[str]:
    """Read dummy helper lines from the generated helper modules."""
    return read_generated_types_lines(dummy_stub_file.parent.parent)
