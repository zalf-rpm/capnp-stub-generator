"""Command-line interface for generating type hints for *.capnp schemas.

Notes:
    - The outputs of this generator are only compatible with pycapnp version >= 1.1.1.
"""

from __future__ import annotations

import argparse
import logging
import os.path
from collections.abc import Sequence

from capnp_stub_generator.run import run

logger = logging.getLogger(__name__)


def _add_recursive_argument(parser: argparse.ArgumentParser):
    """Add a recursive argument to a parser.

    Args:
        parser (argparse.ArgumentParser): The parser to add the argument to.
    """
    parser.add_argument(
        "-r",
        "--recursive",
        dest="recursive",
        default=False,
        action="store_true",
        help="recursively search for *.capnp files with a given glob expression.",
    )


def setup_parser() -> argparse.ArgumentParser:
    """Setup for the parser.

    Returns:
        argparse.ArgumentParser: The parser after setup.
    """
    parser = argparse.ArgumentParser(description="Generate type hints for capnp schema files.")

    parser.add_argument(
        "-c",
        "--clean",
        type=str,
        nargs="+",
        default=[],
        help="path or glob expressions that match files to clean up before stub generation.",
    )

    parser.add_argument(
        "-p",
        "--paths",
        type=str,
        nargs="+",
        default=["**/*.capnp"],
        help="path or glob expressions that match *.capnp files for stub generation.",
    )

    parser.add_argument(
        "-e",
        "--excludes",
        type=str,
        nargs="+",
        default=[],
        help="path or glob expressions to exclude from path matches.",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default="",
        help="directory to write all generated stub outputs; defaults to alongside each schema if omitted.",
    )

    parser.add_argument(
        "-I",
        "--import-path",
        dest="import_paths",
        type=str,
        nargs="+",
        default=[],
        help="additional import paths for resolving absolute imports (e.g., /capnp/c++.capnp).",
    )

    parser.add_argument(
        "--no-pyright",
        dest="skip_pyright",
        default=False,
        action="store_true",
        help="skip pyright validation of generated stubs.",
    )

    _add_recursive_argument(parser)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point of the stub generator.

    Args:
        argv (Sequence[str] | None, optional): Run arguments. Defaults to None.

    Returns:
        int: Error code.
    """
    logging.basicConfig(level=logging.INFO)

    root_directory = os.getcwd()
    logging.info("Working from root directory: %s", root_directory)

    parser = setup_parser()
    args = parser.parse_args(argv)

    run(args, root_directory)

    return 0
