"""Cap'n Proto plugin entry point for stub generation."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import capnp

import schema_capnp
from capnp_stub_generator.run import RunFromSchemasOptions, run_from_schemas

logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point for the capnpc plugin."""
    logging.basicConfig(level=logging.INFO)

    try:
        request = schema_capnp.CodeGeneratorRequest.read(sys.stdin)
    except Exception:
        logger.exception("Failed to read CodeGeneratorRequest")
        sys.exit(1)

    requested_files = [f.filename for f in request.requestedFiles]

    if not requested_files:
        logger.warning("No files requested for generation.")
        return

    # capnpc changes the working directory to the output directory.
    output_dir = str(Path.cwd())

    # Enable bundling by default - augment_capnp_stubs is now always on for self-contained output
    skip_pyright = True
    augment_capnp_stubs = True

    # Build import paths from the request
    import_paths = []

    # Load all nodes from the request into the schema loader
    loader = capnp.SchemaLoader()
    logger.info("Loading %s nodes from CodeGeneratorRequest", len(request.nodes))
    for node in request.nodes:
        try:
            loader.load_dynamic(node)
            logger.debug("Loaded node: %s (id=%s, which=%s)", node.displayName, hex(node.id), node.which())
        except Exception as error:
            logger.warning("Failed to load node %s: %s", node.displayName, error)

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
            path = imp.name[1:] if imp.name.startswith("/") else str(Path(rf.filename).parent / imp.name)
            file_id_to_path[imp.id] = path

    logger.info(
        "Will generate stubs for %s requested files (out of %s total including imports)",
        len(requested_file_ids),
        len(file_id_to_path),
    )

    # Run generation
    try:
        # Only generate stubs for explicitly requested files (not imports)
        # file_id_to_path contains all files for type resolution
        # requested_file_ids filters which ones actually get generated
        run_from_schemas(
            loader,
            file_id_to_path,  # All files for type resolution
            RunFromSchemasOptions(
                output_dir=output_dir,
                import_paths=import_paths,
                skip_pyright=skip_pyright,
                augment_capnp_stubs=augment_capnp_stubs,
                preserve_path_structure=True,
                file_schemas_only=requested_file_ids,
            ),
        )
    except Exception:
        logger.exception("Generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
