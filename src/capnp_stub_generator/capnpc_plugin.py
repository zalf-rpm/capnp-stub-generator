"""Cap'n Proto plugin entry point for stub generation."""

from __future__ import annotations

import logging
import os
import sys

import capnp
from capnp.lib.capnp import SchemaLoader, _Schema

from capnp_stub_generator.run import run_from_schemas
from schema import schema_capnp


class SchemaProxy:
    """Proxy for Schema object to add get_nested support.

    This wraps a _Schema object to add get_nested() method support,
    making it behave like a _ParsedSchema for the Writer.
    """

    def __init__(self, schema: _Schema, loader: SchemaLoader):
        self._schema: _Schema = schema
        self._loader: SchemaLoader = loader

    def __getattr__(self, name: str):
        """Delegate attribute access to the underlying _Schema object."""
        return getattr(self._schema, name)

    def __isinstance__(self, cls):
        """Make isinstance checks work with the underlying _Schema."""
        return isinstance(self._schema, cls)

    @property
    def node(self):
        """Return the underlying schema node."""
        return self._schema.node

    def get_proto(self):
        """Return the proto (NodeReader) for this schema."""
        return self._schema.get_proto()

    def get_nested(self, name: str):
        """Get a nested schema by name.

        This method makes _Schema objects behave like _ParsedSchema objects
        by allowing access to nested schemas.
        """
        for nested in self._schema.get_proto().nestedNodes:
            if nested.name == name:
                try:
                    nested_schema = self._loader.get(nested.id)
                    return SchemaProxy(nested_schema, self._loader)
                except Exception as e:
                    raise KeyError(f"Failed to load nested node '{name}' (id={nested.id}): {e}")
        raise KeyError(f"Nested node '{name}' not found")

    def as_struct(self):
        """Return this schema as a struct schema."""
        return self._schema.as_struct()

    def as_interface(self):
        """Return this schema as an interface schema."""
        return self._schema.as_interface()

    def as_enum(self):
        """Return this schema as an enum schema."""
        return self._schema.as_enum()

    def as_const_value(self):
        """Return this schema as a const value."""
        return self._schema.as_const_value()


def load_schema_capnp():
    """Load the schema.capnp file from the capnp package."""
    try:
        schema_path = os.path.join(os.path.dirname(capnp.__file__), "schema.capnp")
        site_packages = os.path.dirname(os.path.dirname(capnp.__file__))
        return capnp.load(schema_path, imports=[site_packages])
    except Exception as e:
        logging.error(f"Failed to load schema.capnp: {e}")
        sys.exit(1)


def main():
    """Entry point for the capnpc plugin."""
    logging.basicConfig(level=logging.INFO)

    try:
        request = schema_capnp.CodeGeneratorRequest.read(sys.stdin)
    except Exception as e:
        logging.error(f"Failed to read CodeGeneratorRequest: {e}")
        sys.exit(1)

    requested_files = [f.filename for f in request.requestedFiles]

    if not requested_files:
        logging.warning("No files requested for generation.")
        return

    # capnpc changes the working directory to the output directory.
    output_dir = os.getcwd()

    # Enable bundling by default and disable pyright validation
    skip_pyright = True
    augment_capnp_stubs = True

    import_paths = []

    # Load all nodes from the request into the schema loader
    # This includes all nested types from all files
    loader = capnp.SchemaLoader()
    logging.info(f"Loading {len(request.nodes)} nodes from CodeGeneratorRequest")
    for node in request.nodes:
        try:
            loader.load_dynamic(node)
            logging.info(f"Loaded node: {node.displayName} (id={hex(node.id)}, which={node.which()})")
        except Exception as e:
            logging.warning(f"Failed to load node {node.displayName}: {e}")

    schema_registry = {}
    file_id_to_path = {}

    # Map requested files and their imports to paths
    for rf in request.requestedFiles:
        file_id_to_path[rf.id] = rf.filename
        for imp in rf.imports:
            # Resolve import path relative to the importing file
            if imp.name.startswith("/"):
                # Absolute import (relative to search path root)
                path = imp.name[1:]
            else:
                # Relative import
                path = os.path.normpath(os.path.join(os.path.dirname(rf.filename), imp.name))

            file_id_to_path[imp.id] = path

    # Populate schema registry with (path, schema) tuples
    # The schema is wrapped in SchemaProxy to provide get_nested() support
    for file_id, path in file_id_to_path.items():
        try:
            schema = loader.get(file_id)
            logging.info(f"Retrieved schema for {path}: {schema.node.displayName} (id={hex(file_id)})")
            logging.debug(f"  Schema type: {type(schema)}, has {len(schema.node.nestedNodes)} nested nodes")
            # Wrap schema in proxy to support get_nested
            proxy_schema = SchemaProxy(schema, loader)
            schema_registry[file_id] = (path, proxy_schema)
        except Exception as e:
            logging.warning(f"Failed to load schema for file {path} (id={file_id}): {e}")

    # Run generation
    try:
        run_from_schemas(
            schema_registry,
            output_dir,
            import_paths,
            skip_pyright,
            augment_capnp_stubs,
            preserve_path_structure=True,
        )
    except Exception as e:
        logging.error(f"Generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
