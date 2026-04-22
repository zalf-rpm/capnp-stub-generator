"""Server helper types for `restorer.capnp`."""

from . import modules as modules

AnyTesterServer = modules._AnyTesterInterfaceModule.Server

BagServer = modules._BagInterfaceModule.Server

RestorerServer = modules._RestorerInterfaceModule.Server
