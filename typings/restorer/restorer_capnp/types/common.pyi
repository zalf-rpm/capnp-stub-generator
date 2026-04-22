"""Common typing aliases for `restorer.capnp`."""

from capnp.lib.capnp import (
    _DynamicCapabilityClient,
    _DynamicCapabilityServer,
    _DynamicListBuilder,
    _DynamicListReader,
    _DynamicObjectBuilder,
    _DynamicObjectReader,
    _DynamicStructBuilder,
    _DynamicStructReader,
)

# Type alias for AnyList parameters
type AnyList = _DynamicListBuilder | _DynamicListReader | _DynamicObjectReader | _DynamicObjectBuilder

# Type alias for AnyPointer parameters (accepts all Cap'n Proto pointer types)
type AnyPointer = (
    str
    | bytes
    | _DynamicStructBuilder
    | _DynamicStructReader
    | _DynamicCapabilityClient
    | _DynamicCapabilityServer
    | _DynamicListBuilder
    | _DynamicListReader
    | _DynamicObjectReader
    | _DynamicObjectBuilder
)

# Type alias for AnyStruct parameters
type AnyStruct = _DynamicStructBuilder | _DynamicStructReader | _DynamicObjectReader | _DynamicObjectBuilder

# Type alias for Capability parameters
type Capability = _DynamicCapabilityClient | _DynamicCapabilityServer | _DynamicObjectReader | _DynamicObjectBuilder
