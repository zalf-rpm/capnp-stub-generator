#!/usr/bin/env python3
"""
Example using capnp.load() to load schemas directly.

This approach loads .capnp files at runtime and doesn't require pre-compiled
Python modules. It's simpler for development but requires the schema files
to be present at runtime.

Usage:
    python tests/schemas/examples/registry/registry_with_load.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import capnp

# Path to the schema directory
SCHEMA_DIR = Path(__file__).parent.parent.parent / "zalfmas"
CAPNP_IMPORTS = [str(SCHEMA_DIR), str(SCHEMA_DIR / "capnp")]

# Load schemas using capnp.load()
registry_capnp = capnp.load(str(SCHEMA_DIR / "registry.capnp"), imports=CAPNP_IMPORTS)
common_capnp = capnp.load(str(SCHEMA_DIR / "common.capnp"), imports=CAPNP_IMPORTS)


class Identifiable(common_capnp.Identifiable.Server):
    """Server implementation of Identifiable interface."""

    async def info(self, _context):
        """Return id information."""
        pass


async def main():
    """Create a Registry.Entry message with an Identifiable capability."""
    re = registry_capnp.Registry.Entry.new_message(
        categoryId="cat",
        ref=Identifiable(),
        id="some_id",
        name="some_name",
    )
    print(f"Created Registry.Entry: {re}")
    print(f"  categoryId: {re.categoryId}")
    print(f"  id: {re.id}")
    print(f"  name: {re.name}")


if __name__ == "__main__":
    asyncio.run(capnp.run(main()))
