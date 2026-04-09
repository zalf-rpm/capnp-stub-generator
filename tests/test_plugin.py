"""Plugin invocation tests for the capnpc entry point."""

import os
import subprocess
import sys
from pathlib import Path


def test_capnpc_plugin_invocation(tmp_path) -> None:
    """Test that capnpc can invoke our plugin."""
    # Create a wrapper script for the plugin
    plugin_name = "capnpc-python"
    plugin_path = tmp_path / plugin_name

    # We need to make sure we use the current python environment and PYTHONPATH
    python_exe = sys.executable
    src_path = Path.cwd() / "src"

    # Create the wrapper script
    with open(plugin_path, "w") as f:
        f.write("#!/bin/sh\n")
        f.write(f"export PYTHONPATH={src_path}:$PYTHONPATH\n")
        f.write(f"exec {python_exe} -m capnp_stub_generator.capnpc_plugin\n")

    plugin_path.chmod(0o755)

    # Add tmp_path to PATH
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"

    # Schema to compile
    schema_path = Path("tests/schemas/basic/dummy.capnp").absolute()

    # Output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Run capnpc
    # capnpc -o python:{output_dir} {schema_path}
    # capnpc will change CWD to output_dir before invoking the plugin

    cmd = ["capnpc", f"-opython:{output_dir}", str(schema_path)]

    result = subprocess.run(cmd, check=False, env=env, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"capnpc stderr:\n{result.stderr}")
    assert result.returncode == 0, f"capnpc failed: {result.stderr}"

    # Check if output was generated
    # The plugin generates dummy_capnp as a package with __init__.pyi
    found_files = list(output_dir.rglob("dummy_capnp/__init__.pyi"))
    assert len(found_files) > 0, f"Output file not found. Files: {list(output_dir.rglob('*'))}"
    expected_output = found_files[0]

    content = expected_output.read_text()
    assert content  # Just check it's not empty (header is present)


def test_capnpc_plugin_bundling_options(tmp_path) -> None:
    """Test that bundling is enabled by default in plugin mode."""
    plugin_name = "capnpc-python"
    plugin_path = tmp_path / plugin_name

    python_exe = sys.executable
    src_path = Path.cwd() / "src"

    with open(plugin_path, "w") as f:
        f.write("#!/bin/sh\n")
        f.write(f"export PYTHONPATH={src_path}:$PYTHONPATH\n")
        f.write(f"exec {python_exe} -m capnp_stub_generator.capnpc_plugin\n")

    plugin_path.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"

    schema_path = tmp_path / "minimal.capnp"
    schema_path.write_text("@0xdbb9ad1f14bf0b36;\nstruct Foo {}\n")

    # Base output directory where capnpc will write
    base_output_dir = tmp_path / "base_output"
    base_output_dir.mkdir()

    # Output directory for stubs
    stubs_dir = base_output_dir / "stubs"
    stubs_dir.mkdir()

    cmd = ["capnpc", "-opython:stubs", str(schema_path)]

    result = subprocess.run(cmd, check=False, env=env, cwd=base_output_dir, capture_output=True, text=True)

    assert result.returncode == 0, f"capnpc failed: {result.stderr}"

    # Check stubs in stubs_dir
    assert stubs_dir.exists()
    found_files = list(stubs_dir.rglob("minimal_capnp/__init__.pyi"))
    assert len(found_files) > 0, "Stub file not found in stubs subdir"

    # Check content
    content = found_files[0].read_text()
    assert content

    # Check bundled dependencies are now in stubs_dir (the output directory)
    # Since bundling is enabled by default, capnp-stubs should be bundled in the output dir
    assert (stubs_dir / "capnp-stubs").exists(), "capnp-stubs not bundled"
    assert (stubs_dir / "schema_capnp").exists(), "schema_capnp not bundled"
    assert (stubs_dir / "schema_capnp" / "__init__.py").exists(), "schema_capnp runtime not bundled"
    assert (stubs_dir / "schema_capnp" / "__init__.pyi").exists(), "schema_capnp stub file not found"
    assert (stubs_dir / "schema_capnp" / "schema.capnp").exists(), "schema.capnp not found"
