"""Cap'n Proto plugin entry point for stub generation."""

from __future__ import annotations

import logging
import os
import sys

import capnp

import schema_capnp
from capnp_stub_generator.run import run_from_schemas


def main():
    """Entry point for the capnpc plugin."""
    logging.basicConfig(level=logging.INFO)

    try:
        request = schema_capnp.CodeGeneratorRequest.read(sys.stdin)
    except Exception as e:
        logging.exception(f"Failed to read CodeGeneratorRequest: {e}")
        sys.exit(1)

    requested_files = [f.filename for f in request.requestedFiles]

    if not requested_files:
        logging.warning("No files requested for generation.")
        return

    # capnpc changes the working directory to the output directory.
    output_dir = os.getcwd()

    # Enable bundling by default - augment_capnp_stubs is now always on for self-contained output
    skip_pyright = True
    augment_capnp_stubs = True

    # Build import paths from the request
    import_paths = []

    # Load all nodes from the request into the schema loader
    loader = capnp.SchemaLoader()
    logging.info(f"Loading {len(request.nodes)} nodes from CodeGeneratorRequest")
    for node in request.nodes:
        try:
            loader.load_dynamic(node)
            logging.debug(f"Loaded node: {node.displayName} (id={hex(node.id)}, which={node.which()})")
        except Exception as e:
            logging.warning(f"Failed to load node {node.displayName}: {e}")

    # Build mapping of all file IDs to paths (needed for type resolution)
    file_id_to_path = {}

    # Track which files were explicitly requested (only these will have stubs generated)
    requested_file_ids = set()

    # Map file IDs to paths for all files (requested + imports)
    for rf in request.requestedFiles:
        requested_file_ids.add(rf.id)
        file_id_to_path[rf.id] = rf.filename

        # Also map imports for type resolution (but won't generate stubs for them)
        for imp in rf.imports:
            # Resolve import path relative to the importing file
            if imp.name.startswith("/"):
                # Absolute import (relative to search path root)
                path = imp.name[1:]
            else:
                # Relative import
                path = os.path.normpath(os.path.join(os.path.dirname(rf.filename), imp.name))
            file_id_to_path[imp.id] = path

    logging.info(
        f"Will generate stubs for {len(requested_file_ids)} requested files (out of {len(file_id_to_path)} total including imports)",
    )

    # Run generation
    try:
        # Only generate stubs for explicitly requested files (not imports)
        # file_id_to_path contains all files for type resolution
        # requested_file_ids filters which ones actually get generated
        run_from_schemas(
            loader,
            file_id_to_path,  # All files for type resolution
            output_dir,
            import_paths,
            skip_pyright,
            augment_capnp_stubs,
            preserve_path_structure=True,
            file_schemas_only=requested_file_ids,  # Only generate requested files
        )
    except Exception as e:
        logging.error(f"Generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
