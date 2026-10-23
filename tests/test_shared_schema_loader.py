"""Tests for generated schema bundle helpers."""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import capnp

INITIAL_INT32_VALUE = 42
REIMPORTED_INT32_VALUE = 123


def _remove_generated_modules(*module_names: str) -> None:
    for module_name in module_names:
        sys.modules.pop(module_name, None)
    for module_name in list(sys.modules):
        if module_name.startswith("_capnp_schema_bundle_"):
            sys.modules.pop(module_name, None)


def _first_loader_schema_id(module_file: Path) -> int:
    match = re.search(r"_loader\.get\((0x[0-9A-Fa-f]+)\)", module_file.read_text(encoding="utf8"))
    assert match is not None
    return int(match.group(1), 16)


class TestSchemaBundleHelpers:
    """Tests for the generated schema bundle singleton pattern."""

    def test_generated_module_exposes_schema_helpers_without_polluting_capnp(self, basic_stubs: Path) -> None:
        """Generated modules should expose helpers without adding attributes to capnp."""
        if hasattr(capnp, "_embedded_schema_loader"):
            delattr(capnp, "_embedded_schema_loader")
        sys.path.insert(0, str(basic_stubs))

        try:
            dummy_capnp = importlib.import_module("dummy_capnp")

            assert hasattr(dummy_capnp, "get_schema_by_id")
            assert hasattr(dummy_capnp, "load_capnp_file")
            assert not hasattr(capnp, "_embedded_schema_loader")
        finally:
            _remove_generated_modules("dummy_capnp")
            sys.path.remove(str(basic_stubs))

    def test_reimporting_module_uses_same_bundle_schema_lookup(self, basic_stubs: Path) -> None:
        """Reimporting a generated module should keep schema lookup stable."""
        sys.path.insert(0, str(basic_stubs))

        try:
            dummy_capnp = importlib.import_module("dummy_capnp")
            schema_id = _first_loader_schema_id(basic_stubs / "dummy_capnp" / "__init__.py")

            schema_after_first_import = dummy_capnp.get_schema_by_id(schema_id)

            sys.modules.pop("dummy_capnp", None)
            dummy_reimported = importlib.import_module("dummy_capnp")
            schema_after_reimport = dummy_reimported.get_schema_by_id(schema_id)

            assert schema_after_first_import.node.id == schema_after_reimport.node.id
            assert schema_after_first_import.node.displayName == schema_after_reimport.node.displayName
        finally:
            _remove_generated_modules("dummy_capnp")
            sys.path.remove(str(basic_stubs))

    def test_get_schema_by_id_can_access_unimported_bundle_schema(self, basic_stubs: Path) -> None:
        """One generated module should resolve schemas from another module before it is imported."""
        sys.path.insert(0, str(basic_stubs))

        try:
            dummy_capnp = importlib.import_module("dummy_capnp")
            channel_schema_id = _first_loader_schema_id(basic_stubs / "channel_capnp" / "__init__.py")

            assert "channel_capnp" not in sys.modules
            channel_schema = dummy_capnp.get_schema_by_id(channel_schema_id)

            assert channel_schema.node.id == channel_schema_id
            assert "channel.capnp" in channel_schema.node.displayName
            assert "channel_capnp" not in sys.modules
        finally:
            _remove_generated_modules("dummy_capnp", "channel_capnp")
            sys.path.remove(str(basic_stubs))

    def test_schemas_accessible_after_multiple_imports(self, basic_stubs: Path) -> None:
        """Generated modules should remain usable after repeated imports."""
        sys.path.insert(0, str(basic_stubs))

        try:
            dummy_capnp = importlib.import_module("dummy_capnp")

            msg = dummy_capnp.TestAllTypes.new_message()
            msg.boolField = True
            msg.int32Field = INITIAL_INT32_VALUE
            msg.textField = "test"

            assert msg.boolField is True
            assert msg.int32Field == INITIAL_INT32_VALUE
            assert msg.textField == "test"

            sys.modules.pop("dummy_capnp", None)
            dummy_reimported = importlib.import_module("dummy_capnp")

            msg2 = dummy_reimported.TestAllTypes.new_message()
            msg2.boolField = False
            msg2.int32Field = REIMPORTED_INT32_VALUE

            assert msg2.boolField is False
            assert msg2.int32Field == REIMPORTED_INT32_VALUE
        finally:
            _remove_generated_modules("dummy_capnp")
            sys.path.remove(str(basic_stubs))

    def test_load_capnp_file_appends_external_schema(self, basic_stubs: Path, tmp_path: Path) -> None:
        """Generated helper should append a runtime-loaded .capnp file to the same loader."""
        schema_file = tmp_path / "external.capnp"
        schema_file.write_text(
            """
@0xd901a1f719acbf44;

struct External {
  value @0 :Int32;
}
""".lstrip(),
            encoding="utf8",
        )
        sys.path.insert(0, str(basic_stubs))

        try:
            dummy_capnp = importlib.import_module("dummy_capnp")
            external_module = dummy_capnp.load_capnp_file(str(schema_file))
            external_schema = dummy_capnp.get_schema_by_id(external_module.schema.node.id)

            assert external_schema.node.id == external_module.schema.node.id
            assert external_schema.node.displayName.endswith("external.capnp")
        finally:
            _remove_generated_modules("dummy_capnp")
            sys.path.remove(str(basic_stubs))

    def test_load_capnp_file_deduplicates_imported_bundle_schema(
        self,
        basic_stubs: Path,
        tmp_path: Path,
    ) -> None:
        """Runtime-loaded imports should reuse bundled schema IDs already in the loader."""
        schema_file = tmp_path / "external.capnp"
        schema_file.write_text(
            """
@0xcafebabecafed123;

using Basic = import "/basic_low.capnp";

struct UsesBasic {
  value @0 :Basic.BasicLow;
}
""".lstrip(),
            encoding="utf8",
        )
        sys.path.insert(0, str(basic_stubs))

        try:
            basic_low_capnp = importlib.import_module("basic_low_capnp")

            basic_schema_id = basic_low_capnp.BasicLow.schema.node.id
            before = basic_low_capnp.get_schema_by_id(basic_schema_id)
            first_external = basic_low_capnp.load_capnp_file(
                str(schema_file),
                imports=[str((Path("tests/schemas/basic")).resolve())],
            )
            after_first = basic_low_capnp.get_schema_by_id(basic_schema_id)
            second_external = basic_low_capnp.load_capnp_file(
                str(schema_file),
                imports=[str((Path("tests/schemas/basic")).resolve())],
            )
            after_second = basic_low_capnp.get_schema_by_id(basic_schema_id)

            uses_basic = first_external.schema.get_nested("UsesBasic")
            value_schema_id = uses_basic.as_struct().fields["value"].schema.as_struct().node.id

            assert before.node.displayName == "basic_low.capnp:BasicLow"
            assert after_first.node.displayName == before.node.displayName
            assert after_second.node.displayName == before.node.displayName
            assert value_schema_id == basic_schema_id
            assert first_external.schema.node.id == second_external.schema.node.id
            assert basic_low_capnp.get_schema_by_id(first_external.schema.node.id).node.displayName.endswith(
                "external.capnp",
            )
        finally:
            _remove_generated_modules("basic_low_capnp")
            sys.path.remove(str(basic_stubs))


class TestCrossModuleCapabilities:
    """Tests for capability handling across generated modules."""

    def test_interface_schemas_are_importable_with_shared_bundle(self, basic_stubs: Path) -> None:
        """Interface modules should remain usable when loaded through the bundle."""
        sys.path.insert(0, str(basic_stubs))

        try:
            channel_capnp = importlib.import_module("channel_capnp")
            importlib.import_module("interfaces_capnp")

            channel_schema = channel_capnp.get_schema_by_id(channel_capnp.Channel.schema.node.id)

            assert channel_schema.node.id == channel_capnp.Channel.schema.node.id
            assert channel_capnp.Channel is not None
        finally:
            _remove_generated_modules("channel_capnp", "interfaces_capnp")
            sys.path.remove(str(basic_stubs))
