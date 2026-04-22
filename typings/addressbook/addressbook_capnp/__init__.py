# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
"""This is an automatically generated stub for `addressbook.capnp`."""

import base64

import capnp
from capnp.lib.capnp import _EnumModule, _StructModule

import schema_capnp

capnp.remove_import_hook()

# Embedded compiled schemas (base64-encoded)
_SCHEMA_NODES = [
    "EBxQBgb/8P8X8Kf+TpMAARgAAxEV8hEhNwAD/2FkZHJlc3NiAm9vay9hZGRyZXNzYm9vay4fY2FwbnBRDAEB/3np4RPaWnGkABERIv+oqbKqadtnpgARDTr/F12NYB041N4AEQliB3F1eD9QZXJzb27/QWRkcmVzc0IAB29vaw==",  # addressbook/addressbook.capnp
    "EBpQBgb/eenhE9pacaQAER4E//D/F/Cn/k6TAAABERYuMRUSARElBwAAUSADAVEsAgEAAP9hZGRyZXNzYgNvb2svYWRkcmVzc2Jvb2suY2FwbnA6cXUBeFABAQEIAAIRCHsAAQ==",  # addressbook/addressbook.capnp:qux
    "EHpQBgb/qKmyqmnbZ6YAUR4BA//w/xfwp/5OkwAFBQcAADEwRAIxFSoBESUXAAAxMY8BAAH/YWRkcmVzc2IDb29rL2FkZHJlc3Nib29rLmNhcG5wOlBlD3Jzb25RBAEB/4upZV3MHMn2ABEBYv9QaG9uZU51bQAHYmVyURwDBAAABAEAABG1GgAAUbADAVG8AgEBARQBAQAAEbkqAABRtAMBUcACARECARQBAgAAEb0yAABRuAMBUcQCAREDAhQBAwAAEcE6AABRvAMBUdgCAQEEAQH/Wl/LUsayUboAEdVaAAIBBQEB/6w0IdDpRMOYABHBUgACEQYEFAELAAARrVIAAFGsAwFRuAIBA2lkAQgAAgEIAAEPbmFtZQEMAAIBDAABH2VtYWlsAQwAAgEMAAE/cGhvbmVzAQ4AAVADAQEQ/4upZV3MHMn2AAABAQ4AAf9lbXBsb3ltZQADbnT/dGVzdEdyb3UAAXD/ZXh0cmFEYXQAAWEBDQACAQ0AAQ==",  # addressbook/addressbook.capnp:Person
    "EDdQBgb/i6llXcwcyfYAUSUBAf+oqbKqadtnpgAFAQcAADGXHQExFYoBES0XAAARNXcAAf9hZGRyZXNzYgVvb2svYWRkcmVzc2Jvb2suY2FwbnA6UGVyc29uLlBob25lTnVtYmVyAABRBAEB/8cl+Qbkk2ChABEBKg9UeXBlUQgDBAAABAEAABEpOgAAUSQDAVEwAgEBARQBAQAAES0qAABRKAMBUTQCAT9udW1iZXIBDAACAQwAAQ90eXBlAQ//xyX5BuSTYKEAAAEBDwAB",  # addressbook/addressbook.capnp:Person.PhoneNumber
    "ECJQBgb/xyX5BuSTYKEAETEC/4upZV3MHMn2AAABMdkZATEVsgERLQcAABEpTwAB/2FkZHJlc3NiBW9vay9hZGRyZXNzYm9vay5jYXBucDpQZXJzb24uUGhvbmVOdW1iZXIfLlR5cGVQAQFRDAECAAARHToAAAEBERUqAAABAhENKgAAP21vYmlsZQ9ob21lD3dvcms=",  # addressbook/addressbook.capnp:Person.PhoneNumber.Type
    "EFNQBgb/Wl/LUsayUboAUSUBA/+oqbKqadtnpgBVBQcBBAECAAAxFYIBAAERIecAAf9hZGRyZXNzYgVvb2svYWRkcmVzc2Jvb2suY2FwbnA6UGVyc29uLmVtcGxveW1lbnQAURADBAz//xQBBAAAEWFaAABRYAMBUWwCAR0B/v8DFAEFAAARaUoAAFFoAwFRdAIBHQL9/wMUAQYAABFxOgAAUWwDAVF4AgENA/z/FAEHAAARdWoAAFF0AwFRgAIB/3VuZW1wbG95AANlZAAG/2VtcGxveWVyAAAAAQwAAgEMAAE/c2Nob29sAQwAAgEMAAH/c2VsZkVtcGwAD295ZWQABg==",  # addressbook/addressbook.capnp:Person.employment
    "EEFQBgb/rDQh0OlEw5gAUSUBA/+oqbKqadtnpgAVBQcBAAExFXoBAAERIa8AAf9hZGRyZXNzYgRvb2svYWRkcmVzc2Jvb2suY2FwbnA6UGVyc29uLnRlcz90R3JvdXBRDAMEEAIUAQgAABFFOgAAUUADAVFMAgERAQMUAQkAABFJOgAAUUQDAVFQAgERAgQUAQoAABFNOgAAUUgDAVFUAgE/ZmllbGQxAQgAAgEIAAE/ZmllbGQyAQgAAgEIAAE/ZmllbGQzAQgAAgEIAAE=",  # addressbook/addressbook.capnp:Person.testGroup
    "EChQBgb/F12NYB041N4AER4B//D/F/Cn/k6TAAUBBwAAM0YCdwIxFVIBESkHAAARJT8AAf9hZGRyZXNzYgRvb2svYWRkcmVzc2Jvb2suY2FwbnA6QWRkcmVzc0JvbwFrUAEBUQQDBAAABAEAABENOgAAUQgDAVEkAgE/cGVvcGxlAQ4AAVADAQEQ/6ipsqpp22emAAABAQ4AAQ==",  # addressbook/addressbook.capnp:AddressBook
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

qux = _loader.get(0xA4715ADA13E1E979).as_const_value()
Person = _StructModule(_loader.get(0xA667DB69AAB2A9A8).as_struct(), "Person")
Person.PhoneNumber = _StructModule(
    Person.schema.fields["phones"].schema.elementType,
    "PhoneNumber",
)
Person.PhoneNumber.Type = _EnumModule(
    Person.PhoneNumber.schema.fields["type"].schema,
    "Type",
)
AddressBook = _StructModule(_loader.get(0xDED4381D608D5D17).as_struct(), "AddressBook")
