"""Common test helper functions."""

from __future__ import annotations

import argparse

from capnp_stub_generator.run import run


def run_generator(args_list):
    """Helper to convert CLI-style args to run() call."""
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
