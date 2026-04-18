"""Runtime placeholder package for result helpers of `single_value.capnp`."""

# pyright: reportUnusedClass=none

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import client as client
    from . import server as server
    from . import tuples as tuples

__all__ = ["client", "server", "tuples"]
