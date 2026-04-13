"""Common test helper functions."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from capnp_stub_generator.run import run

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

LOGGER = logging.getLogger(__name__)


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
    """Run pyright against one or more paths."""
    resolved_paths = [os.fspath(path) for path in paths]
    return run_command(["pyright", *resolved_paths], cwd=cwd, env=env)


def run_python_file(
    path: str | Path,
    *,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    """Run a Python file with the current interpreter."""
    return run_command([sys.executable, os.fspath(path)], cwd=cwd, env=env)


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
