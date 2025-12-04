"""Cap'n Proto plugin entry point for stub generation."""

from __future__ import annotations

import logging
import os
import sys

import capnp

from capnp_stub_generator.run import run_from_schemas
from schema import schema_capnp


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

    # Build import paths from the request
    import_paths = []

    # Load all nodes from the request into the schema loader
    # This provides access to all schemas by ID without needing source files
    loader = capnp.SchemaLoader()
    logging.info(f"Loading {len(request.nodes)} nodes from CodeGeneratorRequest")
    for node in request.nodes:
        try:
            loader.load_dynamic(node)
            logging.debug(f"Loaded node: {node.displayName} (id={hex(node.id)}, which={node.which()})")
        except Exception as e:
            logging.warning(f"Failed to load node {node.displayName}: {e}")

    schema_registry = {}
    file_id_to_path = {}

    # Map file IDs to paths for the registry
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

    # Populate schema registry with ALL nodes (including nested types)
    # This is critical: the Writer needs all schemas in the registry to build its ID mapping
    # Since SchemaLoader doesn't support get_nested(), we must pre-populate everything
    for node in request.nodes:
        try:
            schema = loader.get(node.id)
            # Use the node's displayName to construct a path
            # For nested types, displayName is like "file.capnp:Struct.NestedType"
            if node.id in file_id_to_path:
                # This is a file-level schema
                path = file_id_to_path[node.id]
            else:
                # This is a nested schema - find its parent file
                display_name = node.displayName
                if ":" in display_name:
                    file_part = display_name.split(":")[0]
                    # Find a file that matches this
                    path = file_part  # Fallback
                    for file_id, file_path in file_id_to_path.items():
                        if file_path.endswith(file_part):
                            path = file_path
                            break
                else:
                    path = display_name

            schema_registry[node.id] = (path, schema)
            logging.debug(f"Added schema {node.displayName} (id={hex(node.id)}) to registry")
        except Exception as e:
            logging.debug(f"Could not add schema for node {node.displayName} (id={hex(node.id)}): {e}")

    logging.info(f"Schema registry has {len(schema_registry)} total schemas")
    logging.info(f"Will generate stubs for {len(file_id_to_path)} files")

    # Run generation
    try:
        # Only generate stubs for file-level schemas, not nested types
        file_schema_ids = set(file_id_to_path.keys())

        run_from_schemas(
            schema_registry,
            output_dir,
            import_paths,
            skip_pyright,
            augment_capnp_stubs,
            preserve_path_structure=True,
            file_schemas_only=file_schema_ids,
        )
    except Exception as e:
        logging.error(f"Generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
