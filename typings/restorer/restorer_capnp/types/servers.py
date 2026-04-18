"""Runtime placeholder module for server helpers of `restorer.capnp`."""

# pyright: reportUnusedClass=none

from .. import AnyTester, Bag, Restorer

AnyTesterServer = AnyTester.Server
BagServer = Bag.Server
RestorerServer = Restorer.Server
