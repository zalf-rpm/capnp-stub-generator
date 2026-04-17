# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
"""This is an automatically generated stub for `single_value.capnp`."""

import base64

import capnp
from capnp.lib.capnp import _EnumModule, _InterfaceModule, _StructModule

import schema_capnp

capnp.remove_import_hook()

# Embedded compiled schemas (base64-encoded)
_SCHEMA_NODES = [
    "EBpQBgb/I5h0I5h0I5gAARoAAzEVAgERIScAA/9zaW5nbGVfdgNhbHVlL3NpbmdsZV92YWx1ZS5jYXBucABRCAEB/953UmMUzp20ABEJYv+XW9AlnoVjigARCUr/U2luZ2xlVmEAB2x1Zf9NeVN0cnVjdAAAAA==",  # single_value/single_value.capnp
    "EH5QBgb/3ndSYxTOnbQAESAD/yOYdCOYdCOYAAABMRahATEVYgERKQcAADElhwITxQEHAAD/c2luZ2xlX3YEYWx1ZS9zaW5nbGVfdmFsdWUuY2FwbnA6U2luZ2xlVmEHbHVlUAEBUSgDBQAA/1un8HFAvJyfAatvxfMPTbWfEzEBQgACEyUBBwEB/0v/4VFLsufhASlUKGfem46rExkBOgACEw0BBwEC/2mUdrR0EQvNAYEFxlTVqu7lEwEBSgACEfkHAQP/dHVnqj+OLIkBTlaHwpvqBbYR7UIAAhHhBwEE/4M5OHNgHFGrAZ4gdfiekGfBEdVCAAIRyQcBBf9UtLPJzJYF9gGQHwsz0TRYvBG9QgACEbEHAQb/RD+08q9hhKUB2aVm9DKAYtURpVIAAhGdBwEH/55m/sL4wOaEAXKfK7lJAonkEZFqAAIRiQcBCP+4DgYGA/xY5gH75TIfUvkK6BF9OgACEXEHAQn/dBpHfhQqSMMBouAFRUJXCbURZXIAAhFdB39nZXRCb29sQAE/Z2V0SW50QAH/Z2V0RmxvYXQAAABAAX9nZXRUZXh0QAF/Z2V0RGF0YUABf2dldExpc3RAAf9nZXRTdHJ1YwABdEAB/2dldEludGVyAA9mYWNlQAE/Z2V0QW55QAH/Z2V0TGlzdFMAH3RydWN0QAFQAQE=",  # single_value/single_value.capnp:SingleValue
    "EBVQBgb/W6fwcUC8nJ8AESwBAAAEBwABMRXaAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEJvb2wkUGFyYQNtcw==",  # single_value/single_value.capnp:SingleValue.getBool$Params
    "ECVQBgb/q2/F8w9NtZ8AUSwBAQAABAcAATEV4gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEJvb2wkUmVzdQdsdHNRBAMEAAAEAQAAEQ0iAABRCAMBURQCAQd2YWwBAQACAQEAAQ==",  # single_value/single_value.capnp:SingleValue.getBool$Results
    "EBVQBgb/S//hUUuy5+EAESwBAAAEBwABMRXSAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEludCRQYXJhbQFz",  # single_value/single_value.capnp:SingleValue.getInt$Params
    "ECVQBgb/KVQoZ96bjqsAUSwBAQAABAcAATEV2gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEludCRSZXN1bAN0c1EEAwQAAAQBAAARDSIAAFEIAwFRFAIBB3ZhbAEEAAIBBAAB",  # single_value/single_value.capnp:SingleValue.getInt$Results
    "EBVQBgb/aZR2tHQRC80AESwBAAAEBwABMRXiAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEZsb2F0JFBhcgdhbXM=",  # single_value/single_value.capnp:SingleValue.getFloat$Params
    "ECVQBgb/gQXGVNWq7uUAUSwBAQAABAcAATEV6gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEZsb2F0JFJlcw91bHRzUQQDBAAABAEAABENIgAAUQgDAVEUAgEHdmFsAQsAAgELAAE=",  # single_value/single_value.capnp:SingleValue.getFloat$Results
    "EBVQBgb/dHVnqj+OLIkAESwBAAAEBwABMRXaAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldFRleHQkUGFyYQNtcw==",  # single_value/single_value.capnp:SingleValue.getText$Params
    "ECVQBgb/TlaHwpvqBbYAESwBAAAFAQcAATEV4gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldFRleHQkUmVzdQdsdHNRBAMEAAAEAQAAEQ0iAABRCAMBURQCAQd2YWwBDAACAQwAAQ==",  # single_value/single_value.capnp:SingleValue.getText$Results
    "EBVQBgb/gzk4c2AcUasAESwBAAAEBwABMRXaAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldERhdGEkUGFyYQNtcw==",  # single_value/single_value.capnp:SingleValue.getData$Params
    "ECVQBgb/niB1+J6QZ8EAESwBAAAFAQcAATEV4gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldERhdGEkUmVzdQdsdHNRBAMEAAAEAQAAEQ0iAABRCAMBURQCAQd2YWwBDQACAQ0AAQ==",  # single_value/single_value.capnp:SingleValue.getData$Results
    "EBVQBgb/VLSzycyWBfYAESwBAAAEBwABMRXaAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldExpc3QkUGFyYQNtcw==",  # single_value/single_value.capnp:SingleValue.getList$Params
    "EClQBgb/kB8LM9E0WLwAESwBAAAFAQcAATEV4gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldExpc3QkUmVzdQdsdHNRBAMEAAAEAQAAEQ0iAABRCAMBUSQCAQd2YWwBDgABUAMBAQQAAgEOAAE=",  # single_value/single_value.capnp:SingleValue.getList$Results
    "EBVQBgb/RD+08q9hhKUAESwBAAAEBwABMRXqAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldFN0cnVjdCRQYQ9yYW1z",  # single_value/single_value.capnp:SingleValue.getStruct$Params
    "ECVQBgb/2aVm9DKAYtUAESwBAAAFAQcAATEV8gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldFN0cnVjdCRSZR9zdWx0c1EEAwQAAAQBAAARDSIAAFEIAwFRFAIBB3ZhbAEQ/5db0CWehWOKAAABARAAAQ==",  # single_value/single_value.capnp:SingleValue.getStruct$Results
    "ECRQBgb/l1vQJZ6FY4oAUSABAf8jmHQjmHQjmAAEBwAAM6MBxgExFUoBESkHAAARJT8AAf9zaW5nbGVfdgRhbHVlL3NpbmdsZV92YWx1ZS5jYXBucDpNeVN0cnVjdAAAUAEBUQQDBAAABAEAABENGgAAUQgDAVEUAgEDaWQBBAACAQQAAQ==",  # single_value/single_value.capnp:MyStruct
    "EBVQBgb/nmb+wvjA5oQAESwBAAAEBwABMRUCAgAE/3NpbmdsZV92B2FsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEludGVyZmFjZSRQYXJhbXMA",  # single_value/single_value.capnp:SingleValue.getInterface$Params
    "ECZQBgb/cp8ruUkCieQAESwBAAAFAQcAATEVCgIAAREtPwAB/3NpbmdsZV92B2FsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEludGVyZmFjZSRSZXN1bHRzAABRBAMEAAAEAQAAEQ0iAABRCAMBURQCAQd2YWwBEf/ed1JjFM6dtAAAAQERAAE=",  # single_value/single_value.capnp:SingleValue.getInterface$Results
    "EBVQBgb/uA4GBgP8WOYAESwBAAAEBwABMRXSAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEFueSRQYXJhbQFz",  # single_value/single_value.capnp:SingleValue.getAny$Params
    "ECVQBgb/++UyH1L5CugAESwBAAAFAQcAATEV2gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEFueSRSZXN1bAN0c1EEAwQAAAQBAAARDSIAAFEIAwFRFAIBB3ZhbAESAAIBEgAB",  # single_value/single_value.capnp:SingleValue.getAny$Results
    "EBZQBgb/dBpHfhQqSMMAESwBAAAEBwABMRUKAgAE/3NpbmdsZV92B2FsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldExpc3RTdHJ1Y3QkUGFyYW1zAAA=",  # single_value/single_value.capnp:SingleValue.getListStruct$Params
    "ECpQBgb/ouAFRUJXCbUAESwBAAAFAQcAATEVEgIAAREtPwAB/3NpbmdsZV92B2FsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldExpc3RTdHJ1Y3QkUmVzdWx0AXNRBAMEAAAEAQAAEQ0iAABRCAMBUSQCAQd2YWwBDgABUAMBARD/l1vQJZ6FY4oAAAEBDgAB",  # single_value/single_value.capnp:SingleValue.getListStruct$Results
]

# Load schemas and build module structure
# Use a shared loader stored on capnp module so capabilities work across schema modules
if not hasattr(capnp, "_embedded_schema_loader"):
    capnp._embedded_schema_loader = capnp.SchemaLoader()
_loader = capnp._embedded_schema_loader
for _schema_b64 in _SCHEMA_NODES:
    _schema_data = base64.b64decode(_schema_b64)
    _node_reader = schema_capnp.Node.from_bytes_packed(_schema_data)
    _loader.load_dynamic(_node_reader)

# Build module structure inline

SingleValue = _InterfaceModule(_loader.get(0xB49DCE14635277DE).as_interface(), "SingleValue")
MyStruct = _StructModule(_loader.get(0x8A63859E25D05B97).as_struct(), "MyStruct")
