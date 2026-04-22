"""Schema helper types for `restorer.capnp`."""

from . import modules as modules

type _AnyTesterSchema = modules._AnyTesterInterfaceModule._AnyTesterSchema

type _BagSchema = modules._BagInterfaceModule._BagSchema

type _RestorerRestoreParamsSchema = modules._RestorerInterfaceModule._RestoreParamsStructModule._RestoreParamsSchema

type _RestorerSchema = modules._RestorerInterfaceModule._RestorerSchema
