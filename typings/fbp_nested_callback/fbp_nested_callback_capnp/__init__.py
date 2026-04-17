# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
"""This is an automatically generated stub for `fbp_nested_callback.capnp`."""

import base64

import capnp
from capnp.lib.capnp import _EnumModule, _InterfaceModule, _StructModule

import schema_capnp

capnp.remove_import_hook()

# Embedded compiled schemas (base64-encoded)
_SCHEMA_NODES = [
    "EBdQBgb/L7LbaEgsYL8AASgAAzEVcgERKRcAA/9mYnBfbmVzdARlZF9jYWxsYmFjay9mYnBfbmVzdGVkX2NhbGxiYWNrLh9jYXBucFEEAQH/6LHyLyvDYpwAEQFCf0NoYW5uZWw=",  # fbp_nested_callback/fbp_nested_callback.capnp
    "ECdQBgb/6LHyLyvDYpwAES4D/y+y22hILGC/AAABMRaFAjEVsgERLRcAABE5RxFpBwAA/2ZicF9uZXN0BWVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2gfYW5uZWxRBAEB/wuSFRgKQzXcABEBcv9TdGF0c0NhbAAfbGJhY2tRBAMFAAD/MxN2ejseEJIBIyxx4NUIav4REbIAAhENB/9yZWdpc3RlcgFTdGF0c0NhbB9sYmFja0ABUAEB",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel
    "ECpQBgb/C5IVGApDNdwAETYD/+ix8i8rw2KcAAABMSzxATEVIgIRNScAABFNRxF1BwAA/2ZicF9uZXN0B2VkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiB2Fja1EIAQH/v114mpyuLqQAEQky/9nRfNd3ify5ABEFWh9TdGF0c/9VbnJlZ2lzdAADZXJRBAMFAAD/Y6GspZjy/IwBnYy7HMqoA64REToAAhEFBz9zdGF0dXNAAVABAQ==",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback
    "EH1QBgb/v114mpyuLqQAUUQBA/8LkhUYCkM13AAFAQcAADGEhgExFVICETkHAAAxNVcBAAH/ZmJwX25lc3QIZWRfY2FsbGJhY2svZmJwX25lc3RlZF9jYWxsYmFjay5jYXBucDpDaGFubmVsLlN0YXRzQ2FsbGJhY2suU3RhdAFzUAEBURgDBAAABAEAABGZmgAAUZwDAVGoAgERAQEUAQEAABGlmgAAUagDAVG0AgERAgEUAQIAABGxegAAUbADAVG8AgERAwIUAQMAABG5qgAAUbwDAVHIAgEBBBQBBAAAEcVSAABRxAMBUdACAREFARQBBQAAEc2aAABR0AMBUdwCAf9ub09mV2FpdAFpbmdXcml0ZQNycwEHAAIBBwAB/25vT2ZXYWl0AWluZ1JlYWRlA3JzAQcAAgEHAAH/bm9PZklwc0kAP25RdWV1ZQEJAAIBCQAB/3RvdGFsTm9PAWZJcHNSZWNlD2l2ZWQBCQACAQkAAf90aW1lc3RhbQABcAEMAAIBDAAB/3VwZGF0ZUluAXRlcnZhbEluA01zAQgAAgEIAAE=",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.Stats
    "ECRQBgb/2dF813eJ/LkAEUQD/wuSFRgKQzXcAAABM4wBzgExFXoCETkHAAARNUcRXQcAAP9mYnBfbmVzdAhlZF9jYWxsYmFjay9mYnBfbmVzdGVkX2NhbGxiYWNrLmNhcG5wOkNoYW5uZWwuU3RhdHNDYWxsYmFjay5VbnJlP2dpc3RlclABAVEEAwUAAP9tnAkonFz1iwGNL4MDvopA8RERMgACEQUHH3VucmVnQAFQAQE=",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.Unregister
    "EBlQBgb/bZwJKJxc9YsAEU8BAAAEBwABMRXiAgAE/2ZicF9uZXN0CmVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiYWNrLlVucmVnaXN0ZXIudW5yZWckUGFyB2Ftcw==",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.Unregister.unreg$Params
    "EClQBgb/jS+DA76KQPEAUU8BAQAABAcAATEV6gIAARE5PwAB/2ZicF9uZXN0CmVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiYWNrLlVucmVnaXN0ZXIudW5yZWckUmVzD3VsdHNRBAMEAAAEAQAAEQ1CAABRCAMBURQCAX9zdWNjZXNzAQEAAgEBAAE=",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.Unregister.unreg$Results
    "EChQBgb/Y6GspZjy/IwAEUQBAAAFAQcAATEVkgIAARE1PwAB/2ZicF9uZXN0CWVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiYWNrLnN0YXR1cyRQYXJhbQFzUQQDBAAABAEAABENMgAAUQgDAVEUAgEfc3RhdHMBEP+/XXianK4upAAAAQEQAAE=",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.status$Params
    "EBhQBgb/nYy7HMqoA64AEUQBAAAEBwABMRWaAgAE/2ZicF9uZXN0CWVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiYWNrLnN0YXR1cyRSZXN1bAN0cw==",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.status$Results
    "EDpQBgb/MxN2ejseEJIAUTYBAQAABQEHAAExFZoCAAERNXcAAf9mYnBfbmVzdAllZF9jYWxsYmFjay9mYnBfbmVzdGVkX2NhbGxiYWNrLmNhcG5wOkNoYW5uZWwucmVnaXN0ZXJTdGF0c0NhbGxiYWNrJFBhcmEDbXNRCAMEAAAEAQAAESlKAABRKAMBUTQCAQEBFAEBAAARMZoAAFE0AwFRQAIB/2NhbGxiYWNrAAAAARH/C5IVGApDNdwAAAEBEQAB/3VwZGF0ZUluAXRlcnZhbEluA01zAQgAAgEIAAE=",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.registerStatsCallback$Params
    "ECpQBgb/Iyxx4NUIav4AETYBAAAFAQcAATEVogIAARE1PwAB/2ZicF9uZXN0CWVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5yZWdpc3RlclN0YXRzQ2FsbGJhY2skUmVzdQdsdHNRBAMEAAAEAQAAEQ2aAABREAMBURwCAf91bnJlZ2lzdAFlckNhbGxiYQNjawER/9nRfNd3ify5AAABAREAAQ==",  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.registerStatsCallback$Results
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

Channel = _InterfaceModule(_loader.get(0x9C62C32B2FF2B1E8).as_interface(), "Channel")
Channel.StatsCallback = _InterfaceModule(
    Channel.schema.methods["registerStatsCallback"].param_type.fields["callback"].schema,
    "StatsCallback",
)
Channel.StatsCallback.Stats = _StructModule(
    Channel.StatsCallback.schema.methods["status"].param_type.fields["stats"].schema,
    "Stats",
)
Channel.StatsCallback.Unregister = _InterfaceModule(
    Channel.schema.methods["registerStatsCallback"].result_type.fields["unregisterCallback"].schema,
    "Unregister",
)
