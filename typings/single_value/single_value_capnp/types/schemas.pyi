"""Schema helper types for `single_value.capnp`."""

from . import modules as modules

type _MyStructSchema = modules._MyStructStructModule._MyStructSchema

type _SingleValueSchema = modules._SingleValueInterfaceModule._SingleValueSchema
