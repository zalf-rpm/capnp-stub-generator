import os
import subprocess
import sys
from pathlib import Path


def test_capnpc_plugin_invocation(tmp_path, basic_stubs):
    """Test that capnpc can invoke our plugin."""

    # Create a wrapper script for the plugin
    plugin_name = "capnpc-stub-generator"
    plugin_path = tmp_path / plugin_name

    # We need to make sure we use the current python environment and PYTHONPATH
    python_exe = sys.executable
    cwd = os.getcwd()
    src_path = os.path.join(cwd, "src")

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
    # capnpc -o stub-generator:{output_dir} {schema_path}
    # capnpc will change CWD to output_dir before invoking the plugin

    cmd = ["capnpc", f"-ostub-generator:{output_dir}", str(schema_path)]

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    assert result.returncode == 0, f"capnpc failed: {result.stderr}"

    # Check if output was generated
    # The plugin should generate dummy_capnp.pyi in output_dir
    expected_output = output_dir / "dummy_capnp.pyi"

    # If it's not there, check if it created a subdirectory
    if not expected_output.exists():
        # List files in output_dir to debug
        files = list(output_dir.rglob("*"))
        print(f"Files in output_dir: {files}")

    assert expected_output.exists(), "Output file was not generated"

    content = expected_output.read_text()
    assert "class _TestAllTypesStructModule" in content


def test_capnpc_plugin_env_vars(tmp_path):
    """Test environment variables configuration in the plugin."""

    plugin_name = "capnpc-stub-generator"
    plugin_path = tmp_path / plugin_name

    python_exe = sys.executable
    cwd = os.getcwd()
    src_path = os.path.join(cwd, "src")

    with open(plugin_path, "w") as f:
        f.write("#!/bin/sh\n")
        f.write(f"export PYTHONPATH={src_path}:$PYTHONPATH\n")
        f.write(f"exec {python_exe} -m capnp_stub_generator.capnpc_plugin\n")

    plugin_path.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    env["CAPNP_SKIP_PYRIGHT"] = "1"

    schema_path = Path("tests/schemas/basic/dummy.capnp").absolute()
    output_dir = tmp_path / "output_no_pyright"
    output_dir.mkdir()

    # Pass output directory
    cmd = ["capnpc", f"-ostub-generator:{output_dir}", str(schema_path)]

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    assert result.returncode == 0, f"capnpc failed: {result.stderr}"

    # Check output
    expected_output = output_dir / "dummy_capnp.pyi"
    assert expected_output.exists()
