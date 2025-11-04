# Stub-file generator for cap'n proto schemas

Generates Python stubs files from cap'n proto schemas.
Useful for IDE auto-completion and static type checking.

## Usage

Clone and install with pip:

```Python
pip install capnp-stub-generator
```

Run on a set of files:

```
capnp-stub-generator -p "path/to/capnp/schemas/**/*.capnp" \
    -c "path/to/output/directory/**/*_capnp.py" "path/to/output/directory/**/*_capnp.pyi" \
    -e "**/c-capnproto/**/*.capnp" \
    -r
```

where the options are

- `-p` - search paths that contain schema files
- `-c` - cleanup paths (delete matching files before generation)
- `-e` - exclude paths that shall not be converted to stubs
- `-r` - recursive file search
- `-o` - output directory for generated stub files (defaults to adjacent to schema files)
- `-I` - import paths for resolving absolute imports (e.g., `/capnp/c++.capnp`)

### Using Import Paths

When your schemas use absolute imports (imports starting with `/`), you need to specify import paths using the `-I` flag:

```bash
capnp-stub-generator -p schemas/*.capnp -o output/ -I /path/to/imports
```

For example, if your schema has:
```capnp
using Cxx = import "/capnp/c++.capnp";
```

And `/capnp/c++.capnp` is located at `/path/to/imports/capnp/c++.capnp`, then use:
```bash
capnp-stub-generator -p my_schema.capnp -I /path/to/imports
```

Multiple import paths can be specified:
```bash
capnp-stub-generator -p schemas/*.capnp -I /path/to/imports1 -I /path/to/imports2
```

For a runnable example, see the [test generation script](./capnp-stub-generator/tests/test_generation.py).

## Style and packaging

This repository is a fork from a company-internal repository. Issues can be reported here, will be fixed upstream, and backported.
Therefore, this repository does not (yet) contain a style checking and packaging pipeline.

The repository may become independent in the future.
