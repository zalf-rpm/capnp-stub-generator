"""This is an automatically generated stub for `schema.capnp`."""

import os

import capnp

capnp.remove_import_hook()
here = os.path.dirname(os.path.abspath(__file__))
module_file = os.path.abspath(os.path.join(here, "schema.capnp"))
import_path = [here]
Node = capnp.load(module_file, imports=import_path).Node
Annotation = capnp.load(module_file, imports=import_path).Annotation
Value = capnp.load(module_file, imports=import_path).Value
Brand = capnp.load(module_file, imports=import_path).Brand
Type = capnp.load(module_file, imports=import_path).Type
ElementSize = capnp.load(module_file, imports=import_path).ElementSize
Field = capnp.load(module_file, imports=import_path).Field
Enumerant = capnp.load(module_file, imports=import_path).Enumerant
Method = capnp.load(module_file, imports=import_path).Method
Superclass = capnp.load(module_file, imports=import_path).Superclass
CapnpVersion = capnp.load(module_file, imports=import_path).CapnpVersion
CodeGeneratorRequest = capnp.load(module_file, imports=import_path).CodeGeneratorRequest
