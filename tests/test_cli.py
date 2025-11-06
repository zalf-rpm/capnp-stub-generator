"""Comprehensive CLI tests for capnp-stub-generator.

Tests cover:
- Argument parsing and validation
- Path handling (absolute/relative)
- Error handling for invalid inputs
- Output directory creation
- Exclude patterns
- Import paths
- Recursive search
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

import pytest

from capnp_stub_generator.cli import main, setup_parser

# Test directories
TESTS_DIR = Path(__file__).parent
SCHEMAS_DIR = TESTS_DIR / "schemas"


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    yield output_dir
    # Cleanup is automatic with tmp_path


@pytest.fixture
def temp_schema_dir(tmp_path):
    """Create a temporary directory with test schemas."""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()

    # Create a simple test schema
    (schema_dir / "test.capnp").write_text("""
@0xdbb9ad1f14bf0b36;

struct TestStruct {
    field @0 :Text;
}
""")

    # Create a schema with imports
    (schema_dir / "base.capnp").write_text("""
@0xdbb9ad1f14bf0b37;

struct BaseStruct {
    id @0 :UInt32;
}
""")

    (schema_dir / "user.capnp").write_text("""
@0xdbb9ad1f14bf0b38;

using Base = import "base.capnp";

struct UserStruct {
    base @0 :Base.BaseStruct;
}
""")

    # Create subdirectory with schema
    subdir = schema_dir / "subdir"
    subdir.mkdir()
    (subdir / "nested.capnp").write_text("""
@0xdbb9ad1f14bf0b39;

struct NestedStruct {
    name @0 :Text;
}
""")

    yield schema_dir


class TestArgumentParsing:
    """Test argument parsing and validation."""

    def test_parser_setup(self):
        """Test that parser is set up correctly."""
        parser = setup_parser()
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.description is not None

    def test_default_arguments(self):
        """Test default argument values."""
        parser = setup_parser()
        args = parser.parse_args([])

        assert args.paths == ["**/*.capnp"]
        assert args.excludes == []
        assert args.clean == []
        assert args.output_dir == ""
        assert args.import_paths == []
        assert args.recursive is False

    def test_paths_argument(self):
        """Test -p/--paths argument parsing."""
        parser = setup_parser()
        args = parser.parse_args(["-p", "schema1.capnp", "schema2.capnp"])
        assert args.paths == ["schema1.capnp", "schema2.capnp"]

    def test_output_dir_argument(self):
        """Test -o/--output-dir argument parsing."""
        parser = setup_parser()
        args = parser.parse_args(["-o", "/tmp/output"])
        assert args.output_dir == "/tmp/output"

    def test_import_paths_argument(self):
        """Test -I/--import-path argument parsing."""
        parser = setup_parser()
        args = parser.parse_args(["-I", "/usr/include", "/opt/capnp"])
        assert args.import_paths == ["/usr/include", "/opt/capnp"]

    def test_excludes_argument(self):
        """Test -e/--excludes argument parsing."""
        parser = setup_parser()
        args = parser.parse_args(["-e", "test1.capnp", "test2.capnp"])
        assert args.excludes == ["test1.capnp", "test2.capnp"]

    def test_recursive_flag(self):
        """Test -r/--recursive flag."""
        parser = setup_parser()
        args = parser.parse_args(["-r"])
        assert args.recursive is True

    def test_clean_argument(self):
        """Test -c/--clean argument parsing."""
        parser = setup_parser()
        args = parser.parse_args(["-c", "*.pyi", "*.py"])
        assert args.clean == ["*.pyi", "*.py"]

    def test_combined_arguments(self):
        """Test parsing multiple arguments together."""
        parser = setup_parser()
        args = parser.parse_args(
            ["-p", "schemas/", "-o", "output/", "-I", "/usr/include", "-r", "-e", "schemas/test.capnp"]
        )

        assert args.paths == ["schemas/"]
        assert args.output_dir == "output/"
        assert args.import_paths == ["/usr/include"]
        assert args.recursive is True
        assert args.excludes == ["schemas/test.capnp"]


class TestAbsolutePaths:
    """Test handling of absolute paths."""

    def test_absolute_schema_path(self, temp_schema_dir, temp_output_dir):
        """Test generating stubs with absolute schema path."""
        schema_file = temp_schema_dir / "test.capnp"

        args = ["-p", str(schema_file.absolute()), "-o", str(temp_output_dir)]

        result = main(args)
        assert result == 0

        # Verify stub was generated
        stub_file = temp_output_dir / "test_capnp.pyi"
        assert stub_file.exists()
        assert stub_file.stat().st_size > 0

    def test_absolute_output_path(self, temp_schema_dir, temp_output_dir):
        """Test generating stubs with absolute output path."""
        schema_file = temp_schema_dir / "test.capnp"

        args = ["-p", str(schema_file), "-o", str(temp_output_dir.absolute())]

        result = main(args)
        assert result == 0

        stub_file = temp_output_dir / "test_capnp.pyi"
        assert stub_file.exists()

    def test_absolute_import_path(self, temp_schema_dir, temp_output_dir):
        """Test using absolute import paths."""
        # Need to process both files since user.capnp imports base.capnp
        args = [
            "-p",
            str(temp_schema_dir / "base.capnp"),
            str(temp_schema_dir / "user.capnp"),
            "-o",
            str(temp_output_dir),
            "-I",
            str(temp_schema_dir.absolute()),
        ]

        result = main(args)
        assert result == 0

        # Should successfully generate stubs for both
        assert (temp_output_dir / "base_capnp.pyi").exists()
        assert (temp_output_dir / "user_capnp.pyi").exists()


class TestRelativePaths:
    """Test handling of relative paths."""

    def test_relative_schema_path(self, temp_schema_dir, temp_output_dir):
        """Test generating stubs with relative schema path."""
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_schema_dir.parent)

            args = ["-p", "schemas/test.capnp", "-o", "output"]

            result = main(args)
            assert result == 0

            stub_file = Path("output/test_capnp.pyi")
            assert stub_file.exists()
        finally:
            os.chdir(original_cwd)

    def test_relative_output_path(self, temp_schema_dir, temp_output_dir):
        """Test generating stubs with relative output path."""
        schema_file = temp_schema_dir / "test.capnp"

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_schema_dir.parent)

            args = ["-p", str(schema_file), "-o", "output"]

            result = main(args)
            assert result == 0

            stub_file = Path("output/test_capnp.pyi")
            assert stub_file.exists()
        finally:
            os.chdir(original_cwd)

    def test_current_directory_path(self, temp_schema_dir, temp_output_dir):
        """Test using current directory (.) as path."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_schema_dir)

            args = ["-p", ".", "-o", str(temp_output_dir), "-r"]

            result = main(args)
            assert result == 0

            # Should find schemas in current directory
            stubs = list(temp_output_dir.glob("*_capnp.pyi"))
            assert len(stubs) > 0
        finally:
            os.chdir(original_cwd)


class TestRecursiveSearch:
    """Test recursive schema discovery."""

    def test_recursive_flag_finds_subdirectories(self, temp_schema_dir, temp_output_dir):
        """Test that -r flag finds schemas in subdirectories."""
        args = ["-p", str(temp_schema_dir), "-o", str(temp_output_dir), "-r"]

        result = main(args)
        assert result == 0

        # Should find nested.capnp in subdir/
        nested_stub = temp_output_dir / "subdir" / "nested_capnp.pyi"
        assert nested_stub.exists()

    def test_non_recursive_misses_subdirectories(self, temp_schema_dir, temp_output_dir):
        """Test that without -r, subdirectories are not searched."""
        args = ["-p", str(temp_schema_dir), "-o", str(temp_output_dir)]

        result = main(args)
        assert result == 0

        # Should not find nested.capnp without -r
        nested_stub = temp_output_dir / "subdir" / "nested_capnp.pyi"
        assert not nested_stub.exists()

        # But should find files in root directory
        root_stubs = list(temp_output_dir.glob("*_capnp.pyi"))
        assert len(root_stubs) > 0


class TestExcludePatterns:
    """Test exclude patterns."""

    def test_exclude_specific_file(self, temp_schema_dir, temp_output_dir):
        """Test excluding a specific file."""
        exclude_file = temp_schema_dir / "test.capnp"

        args = ["-p", str(temp_schema_dir), "-o", str(temp_output_dir), "-e", str(exclude_file)]

        result = main(args)
        assert result == 0

        # test.capnp should not be generated
        test_stub = temp_output_dir / "test_capnp.pyi"
        assert not test_stub.exists()

        # But other files should be generated
        base_stub = temp_output_dir / "base_capnp.pyi"
        assert base_stub.exists()

    def test_exclude_multiple_files(self, temp_schema_dir, temp_output_dir):
        """Test excluding multiple files."""
        args = [
            "-p",
            str(temp_schema_dir),
            "-o",
            str(temp_output_dir),
            "-r",
            "-e",
            str(temp_schema_dir / "test.capnp"),
            str(temp_schema_dir / "subdir" / "nested.capnp"),
        ]

        result = main(args)
        assert result == 0

        # Both excluded files should not be generated
        assert not (temp_output_dir / "test_capnp.pyi").exists()
        assert not (temp_output_dir / "subdir" / "nested_capnp.pyi").exists()

        # But base.capnp and user.capnp should be generated
        assert (temp_output_dir / "base_capnp.pyi").exists()
        assert (temp_output_dir / "user_capnp.pyi").exists()

    def test_exclude_with_recursive(self, temp_schema_dir, temp_output_dir):
        """Test exclude patterns with recursive search."""
        args = [
            "-p",
            str(temp_schema_dir),
            "-o",
            str(temp_output_dir),
            "-r",
            "-e",
            str(temp_schema_dir / "subdir" / "nested.capnp"),
        ]

        result = main(args)
        assert result == 0

        # nested.capnp should not be generated
        nested_stub = temp_output_dir / "subdir" / "nested_capnp.pyi"
        assert not nested_stub.exists()

        # But root files should be generated
        assert (temp_output_dir / "test_capnp.pyi").exists()


class TestOutputDirectory:
    """Test output directory handling."""

    def test_output_dir_created_if_missing(self, temp_schema_dir, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "new_output" / "nested" / "deep"
        schema_file = temp_schema_dir / "test.capnp"

        args = ["-p", str(schema_file), "-o", str(output_dir)]

        result = main(args)
        assert result == 0

        assert output_dir.exists()
        assert (output_dir / "test_capnp.pyi").exists()

    def test_preserve_directory_structure(self, temp_schema_dir, temp_output_dir):
        """Test that directory structure is preserved with -r."""
        args = ["-p", str(temp_schema_dir), "-o", str(temp_output_dir), "-r"]

        result = main(args)
        assert result == 0

        # Check structure is preserved
        assert (temp_output_dir / "test_capnp.pyi").exists()
        assert (temp_output_dir / "subdir" / "nested_capnp.pyi").exists()

    def test_no_output_dir_places_stubs_alongside_schemas(self, temp_schema_dir):
        """Test that without -o, stubs are placed next to schemas."""
        schema_file = temp_schema_dir / "test.capnp"

        args = ["-p", str(schema_file)]

        result = main(args)
        assert result == 0

        # Stub should be next to schema
        stub_file = temp_schema_dir / "test_capnp.pyi"
        assert stub_file.exists()

        # Cleanup
        stub_file.unlink()
        (temp_schema_dir / "test_capnp.py").unlink(missing_ok=True)


class TestImportPaths:
    """Test import path handling."""

    def test_import_path_resolves_dependencies(self, temp_schema_dir, temp_output_dir):
        """Test that import paths allow resolving schema dependencies."""
        # user.capnp imports base.capnp - need to include both
        args = [
            "-p",
            str(temp_schema_dir / "base.capnp"),
            str(temp_schema_dir / "user.capnp"),
            "-o",
            str(temp_output_dir),
            "-I",
            str(temp_schema_dir),
        ]

        result = main(args)
        assert result == 0

        # Should successfully generate stub for user.capnp
        stub_file = temp_output_dir / "user_capnp.pyi"
        assert stub_file.exists()

        # Check that import is present in stub
        content = stub_file.read_text()
        assert "BaseStruct" in content or "base_capnp" in content

    def test_multiple_import_paths(self, temp_schema_dir, temp_output_dir, tmp_path):
        """Test multiple import paths."""
        # Create another directory with schemas
        extra_dir = tmp_path / "extra"
        extra_dir.mkdir()
        (extra_dir / "extra.capnp").write_text("""
@0xdbb9ad1f14bf0b40;

struct ExtraStruct {
    data @0 :Text;
}
""")

        args = [
            "-p",
            str(temp_schema_dir / "test.capnp"),
            "-o",
            str(temp_output_dir),
            "-I",
            str(temp_schema_dir),
            str(extra_dir),
        ]

        result = main(args)
        assert result == 0

    def test_import_path_with_absolute_imports(self, temp_schema_dir, temp_output_dir):
        """Test import paths work with absolute-style imports."""
        # Use an existing schema from the test directory if available
        cpp_schema = SCHEMAS_DIR / "c++.capnp"
        if not cpp_schema.exists():
            pytest.skip("c++.capnp not found in test schemas")

        args = ["-p", str(cpp_schema), "-o", str(temp_output_dir), "-I", str(SCHEMAS_DIR)]

        result = main(args)
        assert result == 0

        # Verify stub was generated
        assert (temp_output_dir / "c++_capnp.pyi").exists()


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_nonexistent_schema_file(self, temp_output_dir):
        """Test handling of nonexistent schema file."""
        args = ["-p", "/nonexistent/path/to/schema.capnp", "-o", str(temp_output_dir)]

        # Should not raise exception, but might not generate anything
        result = main(args)
        assert result == 0

        # No stubs should be generated
        stubs = list(temp_output_dir.glob("*_capnp.pyi"))
        assert len(stubs) == 0

    def test_empty_directory(self, temp_output_dir, tmp_path):
        """Test handling of empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        args = ["-p", str(empty_dir), "-o", str(temp_output_dir), "-r"]

        result = main(args)
        assert result == 0

        # No stubs should be generated
        stubs = list(temp_output_dir.glob("*_capnp.pyi"))
        assert len(stubs) == 0


class TestCleanArgument:
    """Test the clean argument functionality."""

    def test_clean_removes_old_stubs(self, temp_schema_dir, temp_output_dir):
        """Test that -c removes old stub files."""
        # First generate some stubs
        args = ["-p", str(temp_schema_dir / "test.capnp"), "-o", str(temp_output_dir)]
        main(args)

        stub_file = temp_output_dir / "test_capnp.pyi"
        py_file = temp_output_dir / "test_capnp.py"
        assert stub_file.exists()
        assert py_file.exists()

        # Create old stub that should be cleaned
        old_stub = temp_output_dir / "old_capnp.pyi"
        old_stub.write_text("# Old stub")

        # Run again with clean
        args = [
            "-c",
            str(temp_output_dir / "*.pyi"),
            str(temp_output_dir / "*.py"),
            "-p",
            str(temp_schema_dir / "base.capnp"),
            "-o",
            str(temp_output_dir),
        ]
        main(args)

        # Old files should be removed
        assert not stub_file.exists()
        assert not py_file.exists()
        assert not old_stub.exists()

        # New stub should exist
        assert (temp_output_dir / "base_capnp.pyi").exists()


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_generate_from_existing_schemas(self, temp_output_dir):
        """Test generating stubs from actual test schemas."""
        if not SCHEMAS_DIR.exists():
            pytest.skip("Test schemas directory not found")

        # Use existing test schemas
        args = ["-p", str(SCHEMAS_DIR / "primitives.capnp"), "-o", str(temp_output_dir)]

        result = main(args)
        assert result == 0

        stub_file = temp_output_dir / "primitives_capnp.pyi"
        assert stub_file.exists()

        # Verify stub has expected content
        content = stub_file.read_text()
        assert "import" in content
        assert "class" in content or "def" in content

    def test_batch_generation_with_imports(self, temp_output_dir):
        """Test generating multiple interdependent schemas."""
        if not SCHEMAS_DIR.exists():
            pytest.skip("Test schemas directory not found")

        schemas = [SCHEMAS_DIR / "import_base.capnp", SCHEMAS_DIR / "import_user.capnp"]

        # Filter to existing schemas
        existing_schemas = [s for s in schemas if s.exists()]
        if len(existing_schemas) < 2:
            pytest.skip("Import test schemas not found")

        args = ["-p"] + [str(s) for s in existing_schemas] + ["-o", str(temp_output_dir), "-I", str(SCHEMAS_DIR)]

        result = main(args)
        assert result == 0

        # Both stubs should be generated
        for schema in existing_schemas:
            stub_name = schema.stem + "_capnp.pyi"
            assert (temp_output_dir / stub_name).exists()

    def test_large_directory_recursive(self, temp_output_dir):
        """Test recursive generation on a larger directory."""
        if not SCHEMAS_DIR.exists():
            pytest.skip("Test schemas directory not found")

        args = ["-p", str(SCHEMAS_DIR), "-o", str(temp_output_dir), "-I", str(SCHEMAS_DIR), "-r"]

        result = main(args)
        assert result == 0

        # Should generate multiple stubs
        stubs = list(temp_output_dir.glob("**/*_capnp.pyi"))
        assert len(stubs) > 0


class TestCLIInvocation:
    """Test CLI invocation through subprocess."""

    def test_cli_help(self):
        """Test that --help works."""
        # Try to find the installed command
        result = subprocess.run(
            ["capnp-stub-generator", "--help"], capture_output=True, text=True, cwd=str(TESTS_DIR.parent)
        )

        if result.returncode != 0 and "not found" in result.stderr:
            pytest.skip("capnp-stub-generator command not in PATH")

        assert result.returncode == 0
        # Output goes to stderr for argparse --help
        output = result.stdout + result.stderr
        assert "usage:" in output.lower()
        assert "capnp" in output.lower()

    def test_cli_via_subprocess(self, temp_schema_dir, temp_output_dir):
        """Test invoking CLI through subprocess."""
        schema_file = temp_schema_dir / "test.capnp"

        cmd = ["capnp-stub-generator", "-p", str(schema_file), "-o", str(temp_output_dir)]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(temp_schema_dir.parent))

        if result.returncode != 0 and "not found" in (result.stderr + result.stdout):
            pytest.skip("capnp-stub-generator command not in PATH")

        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")

        assert result.returncode == 0
        assert (temp_output_dir / "test_capnp.pyi").exists()
