"""Private compiled schema bundle for generated capnp modules."""

from collections.abc import Sequence

from capnp.lib.capnp import _Schema

def get_schema_by_id(schema_id: int) -> _Schema: ...
def load_capnp_file(path: str, imports: Sequence[str] = ...) -> object: ...
