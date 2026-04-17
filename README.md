# Cap'n Proto Stub Generator for Python

Generates Python stub files (`.pyi`) from Cap'n Proto (`.capnp`) schema files for static type checking with mypy and pyright. Works as a Cap'n Proto compiler plugin to create type stubs alongside your compiled schemas.

## Features

- **Automatic stub generation** via Cap'n Proto compiler plugin
- **Full type coverage** for structs, interfaces, enums, unions, and groups
- **Interface inheritance** and RPC method typing
- **Generic type support** matching pycapnp runtime behavior
- **Import resolution** for complex schema hierarchies
- **Automatic pyright validation** of generated stubs
- **Self-contained output** with bundled dependencies

## Installation

```bash
pip install capnp-stub-generator
```

## Usage

### As Cap'n Proto Compiler Plugin

The recommended way to use this tool is as a Cap'n Proto compiler plugin:

```bash
capnpc -opython:/output/dir schema.capnp
```

This automatically:
1. Compiles your schema with pycapnp
2. Generates `.pyi` stub files as package structures
3. Bundles necessary type dependencies
4. Validates stubs with pyright

### With Multiple Schemas

```bash
capnpc -opython:stubs/ \
    -I/usr/local/include \
    schemas/user.capnp \
    schemas/api/service.capnp
```

The `-I` flag specifies import paths for resolving absolute imports (like `import "/capnp/c++.capnp"`).

## Output Structure

Generated stubs use a package structure:

**Input:**
```
schema.capnp
```

**Output:**
```
schema_capnp/
  ├── __init__.py     # Runtime module
  └── __init__.pyi    # Type stubs
```

This structure allows proper Python module imports and type checking.

## Generated Files Include

- **Type stubs** (`.pyi`) for IDE auto-completion and static analysis
- **Runtime modules** (`.py`) that import compiled pycapnp schemas
- **Bundled dependencies** (`capnp-stubs/`, `schema_capnp/`) for self-contained output
- **Package markers** (`py.typed`, `__init__.py`) for PEP 561 compliance

## Requirements

- Python 3.12-3.13 (or older with up-to-date type checker)
- pycapnp >= 2.2.1, < 3.0.0
- pyright >= 1.1.407 (for validation)

**Note:** Generated stubs are only compatible with pycapnp >= 2.0.0

## Examples

### Basic Schema

```bash
capnpc -opython:output/ myschema.capnp
```

Creates:
```
output/
  ├── myschema_capnp/
  │   ├── __init__.py
  │   └── __init__.pyi
  ├── capnp-stubs/      # Bundled pycapnp stubs
  └── schema_capnp/      # Cap'n Proto schema types
```

### With Imports

```bash
capnpc -opython:output/ \
    -I/usr/local/include \
    myschema.capnp
```

Resolves imports like:
```capnp
using Cxx = import "/capnp/c++.capnp";
```

### Multiple Files with Structure Preservation

```bash
capnpc -opython:output/ \
    schemas/user.capnp \
    schemas/api/v1/service.capnp
```

Preserves directory structure:
```
output/
  ├── user_capnp/
  └── api/
      └── v1/
          └── service_capnp/
```

## Integration with Build Systems

### Makefile

```makefile
SCHEMAS := $(wildcard schemas/**/*.capnp)
STUBS_DIR := generated/stubs

.PHONY: stubs
stubs:
	capnpc -opython:$(STUBS_DIR) -Ischemas $(SCHEMAS)
```

## Type Checking Generated Stubs

The generated stubs work with mypy and pyright:

```python
import myschema_capnp

# Full type checking and IDE completion
message = myschema_capnp.MyStruct.new_message()
message.field = "value"
```

## Repository Dogfooding

When you run the test suite, it refreshes the checked-in `typings/` snapshot from the generated example schemas.

- `typings/addressbook`, `typings/calculator`, `typings/restorer`, and the other example packages come from the generator output
- `typings/capnp-stubs` and `typings/schema_capnp` are refreshed from the bundled base stubs plus the example-specific augmentation

This keeps `src/pycapnp_base_stubs` as the single source of truth for the bundled `capnp` typing surface while still giving editors a ready-to-use dogfooded snapshot for autocompletion.

## Troubleshooting

### Import Resolution

**Problem:** `ImportError` for absolute imports

**Solution:** Use `-I` flag to specify import search paths:
```bash
capnpc -opython:output/ -I/usr/local/include -I./vendor schema.capnp
```

### Pyright Not Found

**Problem:** Validation fails with "pyright not found"

**Solution:** Install pyright globally:
```bash
npm install -g pyright
```

Or install in your project:
```bash
pip install pyright
```

### Missing Type Information

**Problem:** IDE doesn't recognize generated types

**Solution:** Ensure output directory is in Python path:
```python
import sys
sys.path.insert(0, 'path/to/output')
```

## Best Practices

1. **Generate stubs with source compilation** - Use the plugin approach for consistency
2. **Include in build process** - Regenerate stubs when schemas change
3. **Version control schemas only** - Add `*_capnp/` directories to `.gitignore`
4. **Use import paths** - Configure `-I` flags for all schema dependencies
5. **Enable validation** - Keep pyright validation enabled (automatic)

## Advanced Usage

### Bundled Dependencies

The plugin automatically bundles:
- `capnp-stubs/` - Type stubs for pycapnp runtime
- `schema_capnp/` - Cap'n Proto schema types
- `__init__.py` files for package structure

This makes the output self-contained and portable.

### Python Module Annotations

Schemas can specify Python module structure using annotations:

```capnp
@0x123456789abcdef0;

annotation module(file): Text;

$module("my.python.module");

struct MyStruct {
    # ...
}
```

This generates stubs in `my/python/module/` directory structure.

## Bundled Dependencies

This package bundles [pycapnp type stubs](https://github.com/zalf-rpm/pycapnp-stubs) (BSD 2-Clause License) for comprehensive type coverage.

## License

GNU General Public License v3.0 or later (GPL-3.0-or-later)

Copyright (C) 2022 Adrian Figueroa <adrian.figueroa@metirionic.com>
Copyright (C) 2025 Vincent Dlugosch <vincent.dlugosch@zalf.de>

See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please submit a Pull Request.

## Acknowledgments

- **Original Author:** Adrian Figueroa (Metirionic) - Initial implementation
- **Current Maintainer:** Vincent Dlugosch (ZALF) - Enhanced version
