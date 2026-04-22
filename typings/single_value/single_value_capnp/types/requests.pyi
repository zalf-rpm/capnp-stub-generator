"""Request helper types for `single_value.capnp`."""

from typing import Protocol

from .results import client as results_client

class GetboolRequest(Protocol):
    def send(self) -> results_client.GetboolResult: ...

class GetintRequest(Protocol):
    def send(self) -> results_client.GetintResult: ...

class GetfloatRequest(Protocol):
    def send(self) -> results_client.GetfloatResult: ...

class GettextRequest(Protocol):
    def send(self) -> results_client.GettextResult: ...

class GetdataRequest(Protocol):
    def send(self) -> results_client.GetdataResult: ...

class GetlistRequest(Protocol):
    def send(self) -> results_client.GetlistResult: ...

class GetstructRequest(Protocol):
    def send(self) -> results_client.GetstructResult: ...

class GetinterfaceRequest(Protocol):
    def send(self) -> results_client.GetinterfaceResult: ...

class GetanyRequest(Protocol):
    def send(self) -> results_client.GetanyResult: ...

class GetliststructRequest(Protocol):
    def send(self) -> results_client.GetliststructResult: ...
