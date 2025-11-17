# Stub-file generator for cap'n proto schemas

Generates Python stub files (`.pyi`) from Cap'n Proto (`.capnp`) schema files for static type checking with tools like mypy and pyright. The generated stubs enable IDE auto-completion and static analysis for pycapnp-based projects.

## Features

- **Full Python 3.12-3.13 support** with modern type hints(You can use older python versions if your type checker is up to date)
- **Comprehensive type coverage** for structs, interfaces, enums, unions, and groups
- **Interface inheritance** and RPC method typing
- **Generic type support** matching pycapnp runtime behavior
- **Import resolution** for complex schema hierarchies with absolute/relative imports
- **Automatic pyright validation** of generated stubs
- **Directory structure preservation** when using output directory
- **Production-ready** with extensive test coverage (221 tests)

## Installation

Install via pip:

```bash
pip install capnp-stub-generator
```

## Usage

### Basic Command Structure

```bash
capnp-stub-generator [OPTIONS]
```

### Quick Start Examples

**Generate stubs next to schema files:**
```bash
capnp-stub-generator -p "schemas/**/*.capnp" -r
```

**Generate stubs to a specific output directory:**
```bash
capnp-stub-generator -p "schemas/**/*.capnp" -o output/ -r
```

**Clean existing stubs before generation:**
```bash
capnp-stub-generator \
    -p "schemas/**/*.capnp" \
    -c "output/**/*_capnp.py" "output/**/*_capnp.pyi" \
    -o output/ \
    -r
```

**Exclude specific schemas:**
```bash
capnp-stub-generator \
    -p "schemas/**/*.capnp" \
    -e "**/test/**/*.capnp" "**/deprecated/**/*.capnp" \
    -o output/ \
    -r
```

## Command-Line Options

### Required Options

#### `-p, --paths PATHS [PATHS ...]`
Path or glob expressions that match `*.capnp` files for stub generation.

**Examples:**
```bash
# Single file
-p schemas/addressbook.capnp

# Multiple files
-p schemas/user.capnp schemas/product.capnp

# Glob pattern (requires -r for recursive)
-p "schemas/**/*.capnp" -r

# Multiple glob patterns
-p "schemas/core/**/*.capnp" "schemas/api/**/*.capnp" -r
```

**Default:** `**/*.capnp` (searches current directory recursively when `-r` is used)

### Optional Options

#### `-o, --output-dir OUTPUT_DIR`
Directory to write all generated stub outputs. If omitted, stubs are generated alongside each schema file.

**Behavior:**
- **With `-o`**: All stubs written to specified directory, preserving subdirectory structure
- **Without `-o`**: Each `.pyi` file placed next to its corresponding `.capnp` file

**Examples:**
```bash
# Generate to output/ preserving structure
-p "schemas/**/*.capnp" -o output/ -r

# schemas/core/user.capnp → output/core/user_capnp.pyi
# schemas/api/v1/types.capnp → output/api/v1/types_capnp.pyi
```

#### `-c, --clean CLEAN [CLEAN ...]`
Path or glob expressions matching files to delete before stub generation. Useful for cleaning up old generated files.

**Examples:**
```bash
# Clean Python modules and stubs
-c "output/**/*_capnp.py" "output/**/*_capnp.pyi"

# Clean specific directory
-c "output/*"
```

#### `-e, --excludes EXCLUDES [EXCLUDES ...]`
Path or glob expressions to exclude from path matches. Files matching these patterns are not processed.

**Examples:**
```bash
# Exclude test schemas
-e "**/test/**/*.capnp"

# Exclude multiple patterns
-e "**/test/**/*.capnp" "**/deprecated/**/*.capnp" "**/internal/**/*.capnp"
```

#### `-I, --import-path IMPORT_PATHS [IMPORT_PATHS ...]`
Additional import paths for resolving absolute imports (imports starting with `/`).

When your schemas use absolute imports like `import "/capnp/c++.capnp"`, you must specify where to find these files.

**Examples:**
```bash
# Single import path
-I /usr/local/include

# Multiple import paths (searched in order)
-I /usr/local/include -I /opt/capnp/include

# If schema has: using Cxx = import "/capnp/c++.capnp";
# And file is at: /usr/local/include/capnp/c++.capnp
# Then use: -I /usr/local/include
```

#### `-r, --recursive`
Recursively search for `*.capnp` files when using glob patterns. Required for patterns with `**`.

**Examples:**
```bash
# Search recursively
-p "schemas/**/*.capnp" -r

# Without -r, only searches specified directory
-p "schemas/*.capnp"  # Only direct children of schemas/
```

#### `--no-pyright`
Skip pyright validation of generated stubs. By default, all generated stubs are validated with pyright to ensure type correctness.

**Warning:** Only use this option if pyright is not installed. Pyright validation helps catch type errors early.

**Examples:**
```bash
# Skip validation (not recommended)
capnp-stub-generator -p schemas/*.capnp --no-pyright
```

#### `--augment-capnp-stubs`
Augment the bundled `capnp-stubs` package with `cast_as()` overloads for generated interfaces. This provides enhanced type checking when casting capabilities.

The augmented stubs are placed in a `capnp-stubs/` directory beside your output directory.

**Examples:**
```bash
# Generate enhanced stubs for interface casting
capnp-stub-generator -p schemas/*.capnp -o output/ --augment-capnp-stubs
```

## Complete Examples

### Example 1: Simple Project
```bash
capnp-stub-generator -p "schemas/*.capnp" -o stubs/
```
- Processes all `.capnp` files in `schemas/` (non-recursive)
- Writes stubs to `stubs/` directory
- Validates with pyright

### Example 2: Complex Project with Subdirectories
```bash
capnp-stub-generator \
    -p "src/schemas/**/*.capnp" \
    -e "**/test/**/*.capnp" \
    -o build/stubs/ \
    -r
```
- Recursively finds all schemas in `src/schemas/`
- Excludes test schemas
- Preserves directory structure in `build/stubs/`
- Example: `src/schemas/api/v1/user.capnp` → `build/stubs/api/v1/user_capnp.pyi`

### Example 3: With Absolute Imports
```bash
capnp-stub-generator \
    -p "schemas/**/*.capnp" \
    -I /usr/local/include \
    -I ./vendor/capnp \
    -o output/ \
    -r
```
- Handles schemas with absolute imports like `import "/capnp/c++.capnp"`
- Searches import paths in order: `/usr/local/include`, then `./vendor/capnp`

### Example 4: Clean and Regenerate
```bash
capnp-stub-generator \
    -p "schemas/**/*.capnp" \
    -c "output/**/*_capnp.py" "output/**/*_capnp.pyi" \
    -o output/ \
    -r
```
- Deletes all old generated files before generation
- Ensures clean output directory

### Example 5: Interface Casting Support
```bash
capnp-stub-generator \
    -p "schemas/**/*.capnp" \
    -o stubs/ \
    --augment-capnp-stubs \
    -r
```
- Generates type-safe `cast_as()` and `_DynamicObjectReader` method overloads for capabilities
- Creates enhanced `capnp-stubs/` directory beside `stubs/`

## Output Files

The generator creates two files for each schema:

1. **`<schema_name>_capnp.pyi`** - Type stub file for IDE and type checkers
2. **`<schema_name>_capnp.py`** - Runtime module (imports from compiled pycapnp module)

Additionally, a `py.typed` marker file is created in each output directory to mark packages as typed (PEP 561).

### Generated Structure Example

**Input:**
```
schemas/
  ├── user.capnp
  └── api/
      └── service.capnp
```

**Output with `-o output/`:**
```
output/
  ├── py.typed
  ├── user_capnp.pyi
  ├── user_capnp.py
  └── api/
      ├── service_capnp.pyi
      └── service_capnp.py
```

## Requirements

- Python 3.12-3.13
- pycapnp >= 2.2.1, < 3.0.0
- pyright (optional, for validation)

**Note:** Generated stubs are only compatible with pycapnp >= 2.0.0

### Installing Pyright

For stub validation (recommended):
```bash
npm install -g pyright
```

Or skip validation with `--no-pyright` flag.

## Troubleshooting

### Import Resolution Issues

**Problem:** `ImportError` or schemas with absolute imports not found

**Solution:** Use `-I` flag to specify import paths:
```bash
capnp-stub-generator -p schemas/*.capnp -I /usr/local/include -I ./vendor
```

### Directory Structure Not Preserved

**Problem:** All stubs generated in flat structure

**Solution:** Ensure you're using `-r` with glob patterns:
```bash
# Wrong (flat output)
capnp-stub-generator -p "schemas/**/*.capnp" -o output/

# Correct (preserves structure)
capnp-stub-generator -p "schemas/**/*.capnp" -o output/ -r
```

### Pyright Validation Failures

**Problem:** Pyright reports errors in generated stubs

**Solutions:**
1. Update to latest capnp-stub-generator version
2. Report issue with minimal reproduction example
3. Temporarily use `--no-pyright` (not recommended)

### Generated Files Not Type-Checked

**Problem:** IDE/mypy not recognizing generated types

**Solutions:**
1. Ensure `py.typed` marker exists in output directory
2. Add output directory to Python path
3. Restart IDE/language server

## Best Practices

1. **Always generate all schemas together** - This ensures proper dependency resolution and imports between schemas
2. **Use `-c` to clean before regenerating** - Prevents stale files from old generations
3. **Keep pyright validation enabled** - Catches type errors early (default behavior)
4. **Use `-o` for better organization** - Separates generated files from source schemas
5. **Version control `.capnp` files only** - Add generated `*_capnp.py` and `*_capnp.pyi` to `.gitignore`

### Bundled Dependencies

This package bundles [pycapnp type stubs](https://github.com/zalf-rpm/pycapnp-stubs) for the `--augment-capnp-stubs` feature, which generates enhanced type stubs with proper interface casting. The bundled stubs are licensed under BSD 2-Clause License.

## License

This project is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

Copyright (C) 2022 Adrian Figueroa <adrian.figueroa@metirionic.com>
Copyright (C) 2025 Vincent Dlugosch <vincent.dlugosch@zalf.de>

This is a derivative work based on the original capnp-stub-generator developed at Metirionic.
The modifications include extensive enhancements for Python 3.10-3.13 compatibility,
comprehensive test coverage, improved type system support, and production-ready features.

See the [LICENSE](LICENSE) file for the full license text.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- **Original Author:** Adrian Figueroa (Metirionic) - Initial implementation (2022-2023)
- **Current Maintainer:** Vincent Dlugosch (ZALF) - Enhanced version (2025)
