"""Common test helper functions."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from capnp_stub_generator.run import run

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

LOGGER = logging.getLogger(__name__)
GENERATED_TYPES_COMBINED_ORDER = (
    "modules.pyi",
    "schemas.pyi",
    "lists.pyi",
    "builders.pyi",
    "readers.pyi",
    "clients.pyi",
    "requests.pyi",
    "contexts.pyi",
    "common.pyi",
    "servers.pyi",
    "enums.pyi",
    "results/client.pyi",
    "results/server.pyi",
    "results/tuples.pyi",
)


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Captured result of an external command execution."""

    returncode: int
    stdout: str
    stderr: str


def resolve_executable(name: str) -> str:
    """Resolve an executable name to an absolute path."""
    executable = shutil.which(name)
    if executable is None:
        msg = f"{name} command not found"
        raise FileNotFoundError(msg)
    return executable


def _normalize_command(command: Sequence[str | os.PathLike[str]]) -> list[str]:
    """Convert a command sequence to strings and resolve its executable."""
    normalized = [os.fspath(part) for part in command]
    executable = normalized[0]
    if os.sep not in executable and not Path(executable).is_absolute():
        normalized[0] = resolve_executable(executable)
    return normalized


async def _run_command_async(
    command: Sequence[str | os.PathLike[str]],
    *,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    """Run a command and capture its output."""
    normalized = _normalize_command(command)
    process = await asyncio.create_subprocess_exec(
        *normalized,
        cwd=os.fspath(cwd) if cwd is not None else None,
        env=dict(env) if env is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return CommandResult(
        returncode=process.returncode or 0,
        stdout=stdout.decode(),
        stderr=stderr.decode(),
    )


def run_command(
    command: Sequence[str | os.PathLike[str]],
    *,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    """Run a command synchronously and capture its output."""
    return asyncio.run(_run_command_async(command, cwd=cwd, env=env))


def run_pyright(
    *paths: str | Path,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    """Run basedpyright against explicit paths without project exclusions."""
    resolved_paths = [os.fspath(path) for path in paths]
    project_root = Path(__file__).parent.parent.resolve()
    execution_root = Path(cwd).resolve() if cwd is not None else Path.cwd().resolve()
    requested_paths = [Path(raw_path).resolve() for raw_path in paths if Path(raw_path).exists()]
    requested_roots = {str(path if path.is_dir() else path.parent) for path in requested_paths}
    if requested_paths:
        common_root = Path(os.path.commonpath([str(path) for path in requested_paths]))
        requested_roots.add(str(common_root if common_root.is_dir() else common_root.parent))
    python_path_roots = {
        str(Path(path).resolve()) for path in (env or os.environ).get("PYTHONPATH", "").split(os.pathsep) if path
    }
    extra_paths = {
        str(project_root / "src"),
        str(project_root / "tests" / "_generated" / "basic"),
        str(project_root / "tests" / "_generated" / "examples"),
        str(project_root / "tests" / "_generated" / "zalfmas"),
        str(project_root / "typings"),
        str(execution_root),
        *requested_roots,
        *python_path_roots,
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "pyrightconfig.json"
        config_path.write_text(
            json.dumps(
                {
                    "extraPaths": sorted(extra_paths),
                    "reportMissingTypeStubs": "warning",
                    "reportPrivateUsage": "none",
                    "stubPath": str(project_root / "typings"),
                    "typeCheckingMode": "strict",
                },
            ),
            encoding="utf8",
        )
        return run_command(
            ["basedpyright", "--project", config_path, *resolved_paths],
            cwd=cwd,
            env=env,
        )


def run_python_file(
    path: str | Path,
    *,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    """Run a Python file with the current interpreter."""
    return run_command([sys.executable, os.fspath(path)], cwd=cwd, env=env)


def read_generated_types_file(package_dir: Path, *relative_parts: str) -> str:
    """Read one generated helper stub file from a schema package."""
    return (package_dir / "types" / Path(*relative_parts)).read_text()


def read_generated_types_combined(package_dir: Path) -> str:
    """Read generated helper stubs as one combined view for assertion-heavy tests."""
    type_dir = package_dir / "types"
    contents: list[str] = []
    runtime_stub = package_dir / "__init__.pyi"
    if runtime_stub.exists():
        contents.append(runtime_stub.read_text())
    contents.extend(
        (type_dir / relative_path).read_text()
        for relative_path in GENERATED_TYPES_COMBINED_ORDER
        if (type_dir / relative_path).exists()
    )

    return "\n\n".join(contents)


def read_generated_types_lines(package_dir: Path) -> list[str]:
    """Read generated helper stubs as combined lines."""
    return read_generated_types_combined(package_dir).splitlines(keepends=True)


def log_summary(title: str, lines: Sequence[str]) -> None:
    """Log a human-readable test summary."""
    divider = "=" * 70
    body = "\n".join(lines)
    LOGGER.info("\n%s\n%s\n%s\n%s\n%s", divider, title, divider, body, divider)


def run_generator(args_list: Sequence[str]) -> None:
    """Convert CLI-style args to a `run()` call."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--paths", nargs="+", default=[])
    parser.add_argument("-o", "--output-dir", type=str, default="")
    parser.add_argument("-r", "--recursive", action="store_true", default=False)
    parser.add_argument("-e", "--excludes", nargs="+", default=[])
    parser.add_argument("-c", "--clean", nargs="+", default=[])
    parser.add_argument("-I", "--import-path", dest="import_paths", nargs="+", default=[])
    parser.add_argument("--no-pyright", dest="skip_pyright", action="store_true", default=False)
    parser.add_argument("--no-augment-capnp-stubs", dest="augment_capnp_stubs", action="store_false", default=True)

    args = parser.parse_args(args_list)
    run(args, ".")
