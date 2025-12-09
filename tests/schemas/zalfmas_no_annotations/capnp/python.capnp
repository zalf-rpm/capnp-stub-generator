# Copyright (c) 2024 capnp-stub-generator contributors
# Licensed under the MIT License

@0x8b6c1e3f2d7a4c90;

annotation module(file): Text;
# Specifies the Python module path for generated stubs
# Example: $Python.module("mas.schema.climate")
# This will generate the stub in mas/schema/climate_capnp.pyi

annotation name(field, enumerant, struct, enum, interface, method, param, group, union): Text;
# Allows renaming of fields, types, etc. in generated Python code
