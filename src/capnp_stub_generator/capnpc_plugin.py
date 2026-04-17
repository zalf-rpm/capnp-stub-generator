"""Cap'n Proto plugin entry point for stub generation."""

from __future__ import annotations

import logging
import subprocess
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
    except (capnp.KjException, OSError):
        logger.exception("Failed to read CodeGeneratorRequest")
        sys.exit(1)

    requested_files: list[str] = [str(requested_file.filename) for requested_file in request.requestedFiles]

    if not requested_files:
        logger.warning("No files requested for generation.")
        return

    # capnpc changes the working directory to the output directory.
    output_dir = str(Path.cwd())

    # Enable bundling by default - augment_capnp_stubs is now always on for self-contained output
    skip_pyright = True
    augment_capnp_stubs = True

    # Build import paths from the request
    import_paths: list[str] = []

    # Load all nodes from the request into the schema loader
    loader = capnp.SchemaLoader()
    logger.info("Loading %s nodes from CodeGeneratorRequest", len(request.nodes))
    for node in request.nodes:
        try:
            loader.load_dynamic(node)
            logger.debug("Loaded node: %s (id=%s, which=%s)", node.displayName, hex(node.id), node.which())
        except capnp.KjException as error:
            logger.warning("Failed to load node %s: %s", node.displayName, error)

    # Build mapping of all file IDs to paths (needed for type resolution)
    file_id_to_path: dict[int, str] = {}

    # Track which files were explicitly requested (only these will have stubs generated)
    requested_file_ids: set[int] = set()

    # Map file IDs to paths for all files (requested + imports)
    for requested_file in request.requestedFiles:
        requested_file_id = int(requested_file.id)
        requested_file_name = str(requested_file.filename)
        requested_file_ids.add(requested_file_id)
        file_id_to_path[requested_file_id] = requested_file_name

        # Also map imports for type resolution (but won't generate stubs for them)
        for imported_file in requested_file.imports:
            # Resolve import path relative to the importing file
            imported_name = str(imported_file.name)
            path = (
                imported_name[1:]
                if imported_name.startswith("/")
                else str(Path(requested_file_name).parent / imported_name)
            )
            file_id_to_path[int(imported_file.id)] = path

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
                ruff_config_path=str((Path.cwd() / "pyproject.toml").resolve())
                if (Path.cwd() / "pyproject.toml").is_file()
                else None,
                preserve_path_structure=True,
                file_schemas_only=requested_file_ids,
            ),
        )
    except (capnp.KjException, OSError, subprocess.SubprocessError):
        logger.exception("Generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
