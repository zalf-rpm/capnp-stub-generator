"""Regression tests for builder-vs-reader typing on unconstrained pointers."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tests.test_helpers import read_generated_types_file

if TYPE_CHECKING:
    from pathlib import Path


def _class_block(content: str, class_name: str) -> str:
    """Extract a top-level class block from one generated helper stub file."""
    match = re.search(rf"class {re.escape(class_name)}\b.*?(?=\nclass |\Z)", content, re.DOTALL)
    assert match, f"{class_name} not found"
    return match.group(0)


class TestBuilderOwnedPointerFields:
    """Builder-owned unconstrained pointer fields should expose object builders."""

    def test_anyholder_builder_uses_dynamic_object_builder_for_all_unconstrained_kinds(
        self,
        basic_stubs: Path,
    ) -> None:
        """AnyPointer, AnyStruct, and AnyList builder getters should all be object builders."""
        content = read_generated_types_file(basic_stubs / "any_pointer_capnp", "builders.pyi")
        block = _class_block(content, "AnyHolderBuilder")

        assert "def any(self) -> _DynamicObjectBuilder: ..." in block
        assert "def s(self) -> _DynamicObjectBuilder: ..." in block
        assert "def l(self) -> _DynamicObjectBuilder: ..." in block

    def test_generic_parameter_builder_uses_dynamic_object_builder(
        self,
        zalfmas_stubs: Path,
    ) -> None:
        """Generic pointer fields on builders should use object builders too."""
        content = read_generated_types_file(zalfmas_stubs / "mas/schema/common/common_capnp", "builders.pyi")
        block = _class_block(content, "PairBuilder")

        assert "def fst(self) -> _DynamicObjectBuilder: ..." in block
        assert "def snd(self) -> _DynamicObjectBuilder: ..." in block


class TestInterfacePointerSurfaces:
    """RPC helper surfaces should distinguish reader-owned and builder-owned access."""

    def test_client_entry_points_keep_alias_inputs(self, generated_stubs: dict[str, Path]) -> None:
        """Client call surfaces should keep the broad semantic alias for inputs."""
        package_dir = generated_stubs["examples"] / "restorer" / "restorer_capnp"
        content = read_generated_types_file(package_dir, "clients.pyi")

        assert (
            "def setAnyPointer(self, p: common.AnyPointer | None = None) -> results_client.SetanypointerResult: ..."
            in content
        )
        assert (
            "def setAnyPointer_request(self, p: common.AnyPointer | None = None) -> requests.SetanypointerRequest: ..."
            in content
        )

    def test_request_properties_use_builder_getters_and_alias_setters(
        self,
        generated_stubs: dict[str, Path],
    ) -> None:
        """Request objects should expose mutable builder getters but broad setter aliases."""
        package_dir = generated_stubs["examples"] / "restorer" / "restorer_capnp"
        content = read_generated_types_file(package_dir, "requests.pyi")
        block = _class_block(content, "SetanypointerRequest")

        assert "def p(self) -> _DynamicObjectBuilder: ..." in block
        assert "def p(self, value: common.AnyPointer) -> None: ..." in block

    def test_server_inputs_use_reader_types(self, generated_stubs: dict[str, Path]) -> None:
        """Server method params and CallContext.params should stay reader-facing."""
        package_dir = generated_stubs["examples"] / "restorer" / "restorer_capnp"
        contexts_content = read_generated_types_file(package_dir, "contexts.pyi")
        params_block = _class_block(contexts_content, "SetanypointerParams")
        assert "p: _DynamicObjectReader" in params_block

        modules_content = read_generated_types_file(package_dir, "modules.pyi")
        match = re.search(r"def setAnyPointer\(\s*self,\s*p: (?P<type>[^,\n]+),", modules_content, re.DOTALL)
        assert match, "setAnyPointer server signature not found"
        assert match.group("type") == "_DynamicObjectReader"

    def test_server_results_use_builder_getters_and_alias_setters(
        self,
        generated_stubs: dict[str, Path],
    ) -> None:
        """Server result helpers should expose mutable builders for unconstrained pointers."""
        package_dir = generated_stubs["examples"] / "restorer" / "restorer_capnp"
        content = read_generated_types_file(package_dir, "results", "server.pyi")

        any_struct_block = _class_block(content, "GetanystructServerResult")
        assert "def s(self) -> _DynamicObjectBuilder: ..." in any_struct_block
        assert "def s(self, value: common.AnyStruct) -> None: ..." in any_struct_block

        any_list_block = _class_block(content, "GetanylistServerResult")
        assert "def l(self) -> _DynamicObjectBuilder: ..." in any_list_block
        assert "def l(self, value: common.AnyList) -> None: ..." in any_list_block

        any_pointer_block = _class_block(content, "GetanypointerServerResult")
        assert "def p(self) -> _DynamicObjectBuilder: ..." in any_pointer_block
        assert "def p(self, value: common.AnyPointer) -> None: ..." in any_pointer_block

        capability_block = _class_block(content, "RestoreServerResult")
        assert "def cap(self) -> _DynamicObjectBuilder: ..." in capability_block
        assert "def cap(self, value: common.Capability) -> None: ..." in capability_block
