# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportUnknownMemberType=false
"""This is an automatically generated stub for `calculator.capnp`."""

from __future__ import annotations

import base64

import capnp
from capnp.lib.capnp import _EnumModule, _InterfaceModule, _StructModule

import schema_capnp

capnp.remove_import_hook()

# Embedded compiled schemas (base64-encoded)
_SCHEMA_NODES = [
    "EBZQBgb/S9FmcxELFYUAARYAAxEV4hEhFwAD/2NhbGN1bGF0Am9yL2NhbGN1bGF0b3IuY2EHcG5wUQQBAf82zDXfkjOYlwARAVr/Q2FsY3VsYXQAA29y",  # calculator/calculator.capnp
    "EEVQBgb/Nsw135IzmJcAERwD/0vRZnMRCxWFAAABMRaZDTEVOgERJUcAABFdxxHhBwAA/2NhbGN1bGF0A29yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsYz91bGF0b3JREAEB/xWNVPXK1zjUABEZWv/SSO7TNJ3mwwARGTL/lAOElj066O0AERVK/+bf5mF4QJOHABEVSv9FeHByZXNzaQADb24fVmFsdWX/RnVuY3Rpb24AAAD/T3BlcmF0b3IAAABRDAMFAAD/1DZ6VeGqDrsBEaaHWPWjsYERUUoAAhFJBwEB/4ncVkW6vIfyAcjWfARl9CSNET1iAAIRNQcBAv8wxaP0tM6NigEgjMBjd7uP0REpYgACESEH/2V2YWx1YXRlAAAAQAH/ZGVmRnVuY3QAB2lvbkAB/2dldE9wZXJhAAd0b3JAAVABAQ==",  # calculator/calculator.capnp:Calculator
    "EE1QBgb/FY1U9crXONQAUScBAv82zDXfkjOYlwBFAgcEAQQz2gXeBzEVkgERLQcAABEp5wAB/2NhbGN1bGF0BW9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5FeHByZXNzaW8BblABAVEQAwQM//8EAQAAEWFCAABRXAMBUWgCAQ0B/v8UAQEAABFlegAAUWQDAVFwAgENAv3/FAECAAARbVIAAFFsAwFReAIBDQP8/wEB/2aNh9OjIpXZABF1KgACf2xpdGVyYWwBCwACAQsAAf9wcmV2aW91cwA/UmVzdWx0ARH/0kju0zSd5sMAAAEBEQAB/3BhcmFtZXRlAAFyAQgAAgEIAAEPY2FsbA==",  # calculator/calculator.capnp:Calculator.Expression
    "ECBQBgb/0kju0zSd5sMAEScD/zbMNd+SM5iXAAABM+IHEQkxFWoBESkHAAARJUcRTQcAAP9jYWxjdWxhdARvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuVg9hbHVlUAEBUQQDBQAA/1i1jdV0JVPTASLoKhIjZ77mEREqAAIRBQcPcmVhZEABUAEB",  # calculator/calculator.capnp:Calculator.Value
    "EBVQBgb/WLWN1XQlU9MAES0BAAAEBwABMRXKAQAE/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5WYWx1ZS5yZWFkJFBhcmFtcwAA",  # calculator/calculator.capnp:Calculator.Value.read$Params
    "ECVQBgb/IugqEiNnvuYAUS0BAQAABAcAATEV0gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5WYWx1ZS5yZWFkJFJlc3VsdAFzUQQDBAAABAEAABENMgAAUQgDAVEUAgEfdmFsdWUBCwACAQsAAQ==",  # calculator/calculator.capnp:Calculator.Value.read$Results
    "EDhQBgb/Zo2H06MildkAUTIBAv8VjVT1ytc41AAVAgcBAAExFboBAAERJXcAAf9jYWxjdWxhdAVvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuRXhwcmVzc2lvP24uY2FsbFEIAwQAABQBAwAAESlKAABRKAMBUTQCAREBARQBBAAAETE6AABRLAMBUUgCAf9mdW5jdGlvbgAAAAER/5QDhJY9OujtAAABAREAAT9wYXJhbXMBDgABUAMBARD/FY1U9crXONQAAAEBDgAB",  # calculator/calculator.capnp:Calculator.Expression.call
    "ECBQBgb/lAOElj066O0AEScD/zbMNd+SM5iXAAABM/cJqgwxFYIBESkHAAARJUcRTQcAAP9jYWxjdWxhdAVvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuRnVuY3Rpb24AUAEBUQQDBQAA/xd3uHDfYJGxAa3eFGn3q+DAEREqAAIRBQcPY2FsbEABUAEB",  # calculator/calculator.capnp:Calculator.Function
    "EClQBgb/F3e4cN9gkbEAETABAAAFAQcAATEV4gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5GdW5jdGlvbi5jYWxsJFBhcgdhbXNRBAMEAAAEAQAAEQ06AABRCAMBUSQCAT9wYXJhbXMBDgABUAMBAQsAAgEOAAE=",  # calculator/calculator.capnp:Calculator.Function.call$Params
    "ECVQBgb/rd4Uafer4MAAUTABAQAABAcAATEV6gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5GdW5jdGlvbi5jYWxsJFJlcw91bHRzUQQDBAAABAEAABENMgAAUQgDAVEUAgEfdmFsdWUBCwACAQsAAQ==",  # calculator/calculator.capnp:Calculator.Function.call$Results
    "ECdQBgb/5t/mYXhAk4cAEScC/zbMNd+SM5iXAAABM0cNlw0xFYIBESkHAAARJWcAAf9jYWxjdWxhdAVvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuT3BlcmF0b3IAUAEBURABAgAAESkiAAABAREhSgAAAQIRHUoAAAEDERk6AAAHYWRk/3N1YnRyYWN0AAAA/211bHRpcGx5AAAAP2RpdmlkZQ==",  # calculator/calculator.capnp:Calculator.Operator
    "ECVQBgb/1DZ6VeGqDrsAEScBAAAFAQcAATEVugEAARElPwAB/2NhbGN1bGF0BW9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5ldmFsdWF0ZSQ/UGFyYW1zUQQDBAAABAEAABENWgAAUQwDAVEYAgH/ZXhwcmVzc2kAA29uARD/FY1U9crXONQAAAEBEAAB",  # calculator/calculator.capnp:Calculator.evaluate$Params
    "ECRQBgb/EaaHWPWjsYEAEScBAAAFAQcAATEVwgEAARElPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5ldmFsdWF0ZSRSZXN1bHRzAFEEAwQAAAQBAAARDTIAAFEIAwFRFAIBH3ZhbHVlARH/0kju0zSd5sMAAAEBEQAB",  # calculator/calculator.capnp:Calculator.evaluate$Results
    "EDVQBgb/idxWRbq8h/IAUScBAQAABQEHAAExFdIBAAERKXcAAf9jYWxjdWxhdAZvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuZGVmRnVuY3Rpb24kUGFyYW0Bc1EIAwQAAAQBAAARKVoAAFEoAwFRNAIBAQEUAQEAABExKgAAUSwDAVE4AgH/cGFyYW1Db3UAA250AQQAAgEEAAEPYm9keQEQ/xWNVPXK1zjUAAABARAAAQ==",  # calculator/calculator.capnp:Calculator.defFunction$Params
    "ECVQBgb/yNZ8BGX0JI0AEScBAAAFAQcAATEV2gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5kZWZGdW5jdGlvbiRSZXN1bAN0c1EEAwQAAAQBAAARDSoAAFEIAwFRFAIBD2Z1bmMBEf+UA4SWPTro7QAAAQERAAE=",  # calculator/calculator.capnp:Calculator.defFunction$Results
    "ECVQBgb/MMWj9LTOjYoAUScBAQAABAcAATEV0gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5nZXRPcGVyYXRvciRQYXJhbQFzUQQDBAAABAEAABENGgAAUQgDAVEUAgEDb3ABD//m3+ZheECThwAAAQEPAAE=",  # calculator/calculator.capnp:Calculator.getOperator$Params
    "ECVQBgb/IIzAY3e7j9EAEScBAAAFAQcAATEV2gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5nZXRPcGVyYXRvciRSZXN1bAN0c1EEAwQAAAQBAAARDSoAAFEIAwFRFAIBD2Z1bmMBEf+UA4SWPTro7QAAAQERAAE=",  # calculator/calculator.capnp:Calculator.getOperator$Results
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

Calculator = _InterfaceModule(
    _loader.get(0x97983392DF35CC36).as_interface(),
    "Calculator",
)
Calculator.Expression = _StructModule(
    Calculator.schema.methods["evaluate"].param_type.fields["expression"].schema,  # pyright: ignore[reportUnknownArgumentType]
    "Expression",
)
Calculator.Value = _InterfaceModule(
    Calculator.schema.methods["evaluate"].param_type.fields["expression"].schema.fields["previousResult"].schema,  # pyright: ignore[reportUnknownArgumentType]
    "Value",
)
Calculator.Function = _InterfaceModule(
    Calculator.schema.methods["defFunction"].result_type.fields["func"].schema,  # pyright: ignore[reportUnknownArgumentType]
    "Function",
)
Calculator.Operator = _EnumModule(
    Calculator.schema.methods["getOperator"].param_type.fields["op"].schema,  # pyright: ignore[reportUnknownArgumentType]
    "Operator",
)
