"""Cap'n Proto plugin entry point for stub generation."""

import logging
import os
import sys

import capnp

from capnp_stub_generator.run import run_from_modules


class SchemaProxy:
    """Proxy for Schema object to add get_nested support."""

    def __init__(self, schema, loader):
        self._schema = schema
        self._loader = loader

    def __getattr__(self, name):
        return getattr(self._schema, name)

    @property
    def node(self):
        return self._schema.node

    def get_nested(self, name):
        for nested in self._schema.node.nestedNodes:
            if nested.name == name:
                try:
                    nested_schema = self._loader.get(nested.id)
                    return SchemaProxy(nested_schema, self._loader)
                except Exception as e:
                    raise KeyError(f"Failed to load nested node '{name}' (id={nested.id}): {e}")
        raise KeyError(f"Nested node '{name}' not found")

    def as_struct(self):
        return self._schema.as_struct()

    def as_interface(self):
        return self._schema.as_interface()

    def as_enum(self):
        return self._schema.as_enum()

    def as_const_value(self):
        return self._schema.as_const_value()


class MockModule:
    """Mock module object to satisfy Writer expectations."""

    def __init__(self, schema, filename):
        self.schema = schema
        self.__file__ = filename


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

    schema_capnp = load_schema_capnp()

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

    # Read configuration from environment variables
    skip_pyright = os.environ.get("CAPNP_SKIP_PYRIGHT", "0") == "1"
    augment_capnp_stubs = os.environ.get("CAPNP_AUGMENT_STUBS", "0") == "1"

    import_paths_env = os.environ.get("CAPNP_IMPORT_PATHS", "")
    import_paths = import_paths_env.split(":") if import_paths_env else []

    # Load all nodes from the request
    loader = capnp.SchemaLoader()
    for node in request.nodes:
        loader.load_dynamic(node)

    module_registry = {}
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

    # Populate module registry
    for file_id, path in file_id_to_path.items():
        try:
            schema = loader.get(file_id)
            # Wrap schema in proxy to support get_nested
            proxy_schema = SchemaProxy(schema, loader)
            module = MockModule(proxy_schema, path)
            module_registry[file_id] = (path, module)
        except Exception as e:
            logging.warning(f"Failed to load schema for file {path} (id={file_id}): {e}")

    # Calculate common base from requested files to preserve directory structure
    paths = [rf.filename for rf in request.requestedFiles]
    common_base = None
    if paths:
        try:
            common_base = os.path.commonpath(paths)
            # If common_base is a file (single file input), use its directory
            # We can't check os.path.isfile(common_base) because files might not exist relative to CWD
            # But if common_base is in paths, it's a file path
            if common_base in paths:
                common_base = os.path.dirname(common_base)
        except ValueError:
            # Mix of absolute and relative paths or different drives
            common_base = None

    # Run generation
    try:
        run_from_modules(
            module_registry,
            output_dir,
            import_paths,
            skip_pyright,
            augment_capnp_stubs,
            common_base=common_base,
        )
    except Exception as e:
        logging.error(f"Generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
