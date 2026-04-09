"""Automatically generated runtime bindings for `schema.capnp`."""

from pathlib import Path

import capnp

capnp.remove_import_hook()
here = Path(__file__).resolve().parent
module_file = here / "schema.capnp"
import_path = [str(here)]
Node = capnp.load(str(module_file), imports=import_path).Node
Annotation = capnp.load(str(module_file), imports=import_path).Annotation
Value = capnp.load(str(module_file), imports=import_path).Value
Brand = capnp.load(str(module_file), imports=import_path).Brand
Type = capnp.load(str(module_file), imports=import_path).Type
ElementSize = capnp.load(str(module_file), imports=import_path).ElementSize
Field = capnp.load(str(module_file), imports=import_path).Field
Enumerant = capnp.load(str(module_file), imports=import_path).Enumerant
Method = capnp.load(str(module_file), imports=import_path).Method
Superclass = capnp.load(str(module_file), imports=import_path).Superclass
CapnpVersion = capnp.load(str(module_file), imports=import_path).CapnpVersion
CodeGeneratorRequest = capnp.load(str(module_file), imports=import_path).CodeGeneratorRequest
