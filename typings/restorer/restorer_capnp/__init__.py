# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportUnknownMemberType=false
"""This is an automatically generated stub for `restorer.capnp`."""

from __future__ import annotations

import base64

import capnp
from capnp.lib.capnp import _InterfaceModule, _StructModule

import schema_capnp

capnp.remove_import_hook()

# Embedded compiled schemas (base64-encoded)
_SCHEMA_NODES = [
    "EBxQBgb/8c2rEDJUdpgAARIAAxEVwhEdNwAD/3Jlc3RvcmVyAi9yZXN0b3Jlci5jYXBucABRDAEB/+32VV8MfNGYABERIv+Ts+QdgP3F1QARDUr/ZuOu7GhISo0AEQ1SB0JhZ/9SZXN0b3JlcgAAAP9BbnlUZXN0ZQABcg==",  # restorer/restorer.capnp
    "ECpQBgb/7fZVXwx80ZgAERgD//HNqxAyVHaYAAABERaYERXiESEHAAARHYcRdQcAAP9yZXN0b3JlcgIvcmVzdG9yZXIuY2FwbnA6B0JhZ1ABAVEIAwUAAP8ZIzcsKrijwAGCCbHB0gaB4BExSgACESkHAQH/zPH8ARX1RbUBFbuRiFg5o/IRHUoAAhEVB/9nZXRWYWx1ZQAAAEAB/3NldFZhbHVlAAAAQAFQAQE=",  # restorer/restorer.capnp:Bag
    "EBNQBgb/GSM3LCq4o8AAERwBAAAEBwABMRViAQAE/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpCYWcuZ2V0VmFsdWUkUGFyB2Ftcw==",  # restorer/restorer.capnp:Bag.getValue$Params
    "ECNQBgb/ggmxwdIGgeAAERwBAAAFAQcAATEVagEAAREhPwAB/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpCYWcuZ2V0VmFsdWUkUmVzD3VsdHNRBAMEAAAEAQAAEQ0yAABRCAMBURQCAR92YWx1ZQEMAAIBDAAB",  # restorer/restorer.capnp:Bag.getValue$Results
    "ECNQBgb/zPH8ARX1RbUAERwBAAAFAQcAATEVYgEAAREhPwAB/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpCYWcuc2V0VmFsdWUkUGFyB2Ftc1EEAwQAAAQBAAARDTIAAFEIAwFRFAIBH3ZhbHVlAQwAAgEMAAE=",  # restorer/restorer.capnp:Bag.setValue$Params
    "EBNQBgb/FbuRiFg5o/IAERwBAAAEBwABMRVqAQAE/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpCYWcuc2V0VmFsdWUkUmVzD3VsdHM=",  # restorer/restorer.capnp:Bag.setValue$Results
    "EC5QBgb/k7PkHYD9xdUAERgD//HNqxAyVHaYAAABMZq7ATEVCgERJRcAABExhxGFBwAA/3Jlc3RvcmVyAy9yZXN0b3Jlci5jYXBucDpSZXN0b3JlcgAAUQQBAf+I533fUlHa1AARAXL/UmVzdG9yZVAAH2FyYW1zUQgDBQAA/4jnfd9SUdrUAQ6Rh2SC/S67ETFCAAIRJQcBAf+w0PDrVEtD0wGrfICBYSP1tBEZagACEREHf3Jlc3RvcmVAAf9nZXRBbnlUZQAPc3RlckABUAEB",  # restorer/restorer.capnp:Restorer
    "ECVQBgb/iOd931JR2tQAESEB/5Oz5B2A/cXVAAUBBwAAMd0OATEVegERKQcAABElPwAB/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpSZXN0b3Jlci5SZXN0b3JlP1BhcmFtc1ABAVEEAwQAAAQBAAARDUoAAFEMAwFRGAIB/2xvY2FsUmVmAAAAAQwAAgEMAAE=",  # restorer/restorer.capnp:Restorer.RestoreParams
    "ECRQBgb/DpGHZIL9LrsAESEBAAAFAQcAATEVigEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpSZXN0b3Jlci5yZXN0b3JlJFJlc3VsdHMAAFEEAwQAAAQBAAARDSIAAFEIAwFRFAIBB2NhcAESBAMAAQESAAE=",  # restorer/restorer.capnp:Restorer.restore$Results
    "EBRQBgb/sNDw61RLQ9MAESEBAAAEBwABMRWqAQAE/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpSZXN0b3Jlci5nZXRBbnlUZXN0ZXIkUGEPcmFtcw==",  # restorer/restorer.capnp:Restorer.getAnyTester$Params
    "ECRQBgb/q3yAgWEj9bQAESEBAAAFAQcAATEVsgEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpSZXN0b3Jlci5nZXRBbnlUZXN0ZXIkUmUfc3VsdHNRBAMEAAAEAQAAEQ06AABRCAMBURQCAT90ZXN0ZXIBEf9m467saEhKjQAAAQERAAE=",  # restorer/restorer.capnp:Restorer.getAnyTester$Results
    "EEFQBgb/ZuOu7GhISo0AERgD//HNqxAyVHaYAAABM70BdAIxFRIBESUHAAAxIQcBEdEHAAD/cmVzdG9yZXIDL3Jlc3RvcmVyLmNhcG5wOkFueVRlc3RlAXJQAQFREAMFAAD/cwUPF904R/4BDXduw2jWKvQRcWoAAhFpBwEB/+RtNPtP9+yjAZt094WszVqqEV1aAAIRVQcBAv+hxyK+IElBiwGUNYEtIfDPsxFJcgACEUEHAQP/VbI9oj7+CP8BPGhdKea/JugRNXIAAhEtB/9nZXRBbnlTdAAPcnVjdEAB/2dldEFueUxpAANzdEAB/2dldEFueVBvAB9pbnRlckAB/3NldEFueVBvAB9pbnRlckABUAEB",  # restorer/restorer.capnp:AnyTester
    "EBRQBgb/cwUPF904R/4AESIBAAAEBwABMRWyAQAE/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55U3RydWN0JFAfYXJhbXM=",  # restorer/restorer.capnp:AnyTester.getAnyStruct$Params
    "ECRQBgb/DXduw2jWKvQAESIBAAAFAQcAATEVugEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55U3RydWN0JFI/ZXN1bHRzUQQDBAAABAEAABENEgAAUQgDAVEUAgEBcwESBAEAAQESAAE=",  # restorer/restorer.capnp:AnyTester.getAnyStruct$Results
    "EBRQBgb/5G00+0/37KMAESIBAAAEBwABMRWiAQAE/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55TGlzdCRQYXIHYW1z",  # restorer/restorer.capnp:AnyTester.getAnyList$Params
    "ECRQBgb/m3T3hazNWqoAESIBAAAFAQcAATEVqgEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55TGlzdCRSZXMPdWx0c1EEAwQAAAQBAAARDRIAAFEIAwFRFAIBAWwBEgQCAAEBEgAB",  # restorer/restorer.capnp:AnyTester.getAnyList$Results
    "EBRQBgb/occiviBJQYsAESIBAAAEBwABMRW6AQAE/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55UG9pbnRlciQ/UGFyYW1z",  # restorer/restorer.capnp:AnyTester.getAnyPointer$Params
    "ECRQBgb/lDWBLSHwz7MAESIBAAAFAQcAATEVwgEAARElPwAB/3Jlc3RvcmVyBi9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55UG9pbnRlciRSZXN1bHRzAFEEAwQAAAQBAAARDRIAAFEIAwFRFAIBAXABEgACARIAAQ==",  # restorer/restorer.capnp:AnyTester.getAnyPointer$Results
    "ECRQBgb/VbI9oj7+CP8AESIBAAAFAQcAATEVugEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuc2V0QW55UG9pbnRlciQ/UGFyYW1zUQQDBAAABAEAABENEgAAUQgDAVEUAgEBcAESAAIBEgAB",  # restorer/restorer.capnp:AnyTester.setAnyPointer$Params
    "EBRQBgb/PGhdKea/JugAESIBAAAEBwABMRXCAQAE/3Jlc3RvcmVyBi9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuc2V0QW55UG9pbnRlciRSZXN1bHRzAA==",  # restorer/restorer.capnp:AnyTester.setAnyPointer$Results
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

Bag = _InterfaceModule(
    _loader.get(0x98D17C0C5F55F6ED).as_interface(),
    "Bag",
)
Restorer = _InterfaceModule(
    _loader.get(0xD5C5FD801DE4B393).as_interface(),
    "Restorer",
)
Restorer.RestoreParams = _StructModule(
    Restorer.schema.methods["restore"].param_type,  # pyright: ignore[reportUnknownArgumentType]
    "RestoreParams",
)
AnyTester = _InterfaceModule(
    _loader.get(0x8D4A4868ECAEE366).as_interface(),
    "AnyTester",
)
