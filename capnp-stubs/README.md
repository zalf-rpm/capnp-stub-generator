# capnp-stubs

Type stubs for [pycapnp](https://github.com/capnproto/pycapnp).

This package provides type information for the pycapnp library, enabling
static type checkers like mypy and Pyright to understand the Cap'n Proto
Python bindings.

## Installation for Development

Since stub files need to be installed alongside the actual pycapnp package,
use the provided install script:

```bash
./install_stubs.sh
```

This script copies the `.pyi` stub files into the pycapnp installation directory,
making them available to type checkers without interfering with runtime behavior.

## Installation for Production

```bash
pip install capnp-stubs
```

Note: The package will install stub files directly into the `capnp` package directory.

## Usage

Once installed, type checkers will automatically discover and use these stubs
when analyzing code that imports `capnp`.

```python
import capnp  # Now fully typed!

parser = capnp.SchemaParser()
module = parser.load("schema.capnp")
```

## Structure

The stub package provides:
- `capnp/__init__.pyi` - Main module stubs
- `capnp/lib/__init__.pyi` - Lib submodule stubs
- `capnp/lib/capnp.pyi` - Implementation class stubs
- `capnp/py.typed` - PEP 561 marker file
