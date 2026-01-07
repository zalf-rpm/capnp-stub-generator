"""Tests for the shared schema loader approach.

This module tests that loading the same schema multiple times via the shared
schema loader (capnp._embedded_schema_loader) doesn't cause problems.

The shared loader is used to ensure capabilities work correctly across
different schema modules that may reference each other.
"""

from __future__ import annotations

import sys

import capnp


class TestSharedSchemaLoader:
    """Tests for the shared schema loader singleton pattern."""

    def test_shared_loader_exists_after_import(self, basic_stubs):
        """Verify that the shared loader is created after importing a generated module."""
        # Add the generated stubs directory to the path
        sys.path.insert(0, str(basic_stubs))

        try:
            # Import a generated module - this should create the shared loader
            import dummy_capnp  # noqa: F401

            # Verify the shared loader was created on the capnp module
            assert hasattr(capnp, "_embedded_schema_loader")
            assert isinstance(capnp._embedded_schema_loader, capnp.SchemaLoader)
        finally:
            # Clean up sys.path
            if str(basic_stubs) in sys.path:
                sys.path.remove(str(basic_stubs))

    def test_reimporting_module_uses_same_loader(self, basic_stubs):
        """Verify that reimporting a module uses the same shared loader."""
        sys.path.insert(0, str(basic_stubs))

        try:
            # First import
            import dummy_capnp  # noqa: F401

            loader_after_first_import = capnp._embedded_schema_loader
            loader_id_first = id(loader_after_first_import)

            # Force reimport by removing from sys.modules and reimporting
            if "dummy_capnp" in sys.modules:
                del sys.modules["dummy_capnp"]

            import dummy_capnp as dummy_capnp_reimported  # noqa: F811, F401

            loader_after_reimport = capnp._embedded_schema_loader
            loader_id_second = id(loader_after_reimport)

            # The loader should be the same instance
            assert loader_id_first == loader_id_second
            assert loader_after_first_import is loader_after_reimport
        finally:
            if str(basic_stubs) in sys.path:
                sys.path.remove(str(basic_stubs))

    def test_multiple_modules_share_same_loader(self, basic_stubs):
        """Verify that multiple schema modules share the same loader instance."""
        sys.path.insert(0, str(basic_stubs))

        try:
            # Import first module
            import dummy_capnp  # noqa: F401

            loader_after_first = capnp._embedded_schema_loader
            loader_id_first = id(loader_after_first)

            # Import a different module
            import channel_capnp  # noqa: F401

            loader_after_second = capnp._embedded_schema_loader
            loader_id_second = id(loader_after_second)

            # Both should use the same loader
            assert loader_id_first == loader_id_second
            assert loader_after_first is loader_after_second
        finally:
            if str(basic_stubs) in sys.path:
                sys.path.remove(str(basic_stubs))

    def test_loading_same_schema_nodes_multiple_times(self, basic_stubs):
        """Test that load_dynamic can be called multiple times with the same schema nodes.

        The SchemaLoader.load_dynamic method should handle duplicate loads gracefully.
        This tests the scenario where the same module is imported multiple times
        or where schemas with shared dependencies are loaded.
        """
        sys.path.insert(0, str(basic_stubs))

        try:
            # Import a module to populate the loader
            import dummy_capnp  # noqa: F401

            loader = capnp._embedded_schema_loader

            # Verify the loader has schemas loaded
            assert loader is not None

            # Try to get a schema by reading the embedded data again
            # This simulates what happens when the module is reimported
            import base64
            import re

            import schema_capnp

            # Read the module file to get the embedded schema data
            module_file = basic_stubs / "dummy_capnp" / "__init__.py"
            content = module_file.read_text()

            # Extract one of the base64-encoded schema nodes
            # Look for lines like:    "EBZQBgb/...",  # schema name
            b64_pattern = re.compile(r'"([A-Za-z0-9+/=]+)",\s*#')
            matches = b64_pattern.findall(content)

            if matches:
                # Try loading the same schema node again - this should not raise
                for schema_b64 in matches[:3]:  # Test with first 3 schemas
                    schema_data = base64.b64decode(schema_b64)
                    node_reader = schema_capnp.Node.from_bytes_packed(schema_data)

                    # This should not raise - load_dynamic should handle duplicates
                    loader.load_dynamic(node_reader)

        finally:
            if str(basic_stubs) in sys.path:
                sys.path.remove(str(basic_stubs))

    def test_schemas_accessible_after_multiple_loads(self, basic_stubs):
        """Verify that schemas remain accessible after being loaded multiple times."""
        sys.path.insert(0, str(basic_stubs))

        try:
            # Import module
            import dummy_capnp

            # Verify we can create messages using the schema
            # This confirms the schema was loaded correctly
            msg = dummy_capnp.TestAllTypes.new_message()
            assert msg is not None

            # Set some fields to verify the schema works
            msg.boolField = True
            msg.int32Field = 42
            msg.textField = "test"

            assert msg.boolField is True
            assert msg.int32Field == 42
            assert msg.textField == "test"

            # Force reimport
            if "dummy_capnp" in sys.modules:
                del sys.modules["dummy_capnp"]

            import dummy_capnp as dummy_reimported  # noqa: F811

            # Verify we can still create and use messages
            msg2 = dummy_reimported.TestAllTypes.new_message()
            msg2.boolField = False
            msg2.int32Field = 123

            assert msg2.boolField is False
            assert msg2.int32Field == 123

        finally:
            if str(basic_stubs) in sys.path:
                sys.path.remove(str(basic_stubs))

    def test_loader_get_returns_consistent_schemas(self, basic_stubs):
        """Verify that loader.get() returns consistent schema objects."""
        sys.path.insert(0, str(basic_stubs))

        try:
            import dummy_capnp  # noqa: F401

            loader = capnp._embedded_schema_loader

            # Read the module to find schema IDs
            module_file = basic_stubs / "dummy_capnp" / "__init__.py"
            content = module_file.read_text()

            # Find hex IDs like _loader.get(0xABCD1234)
            import re

            id_pattern = re.compile(r"_loader\.get\((0x[0-9A-Fa-f]+)\)")
            hex_ids = id_pattern.findall(content)

            if hex_ids:
                # Get the same schema multiple times
                schema_id = int(hex_ids[0], 16)

                schema1 = loader.get(schema_id)
                schema2 = loader.get(schema_id)

                # Should return the same schema object
                assert schema1.node.id == schema2.node.id
                assert schema1.node.displayName == schema2.node.displayName

        finally:
            if str(basic_stubs) in sys.path:
                sys.path.remove(str(basic_stubs))


class TestCrossModuleCapabilities:
    """Tests for capability handling across modules using shared loader."""

    def test_interface_schemas_share_loader(self, basic_stubs):
        """Verify that interface schemas from different modules share the loader."""
        sys.path.insert(0, str(basic_stubs))

        try:
            # Import modules with interfaces
            import channel_capnp
            import interfaces_capnp  # noqa: F401

            # Both should use the same loader
            loader = capnp._embedded_schema_loader
            assert loader is not None

            # Verify the Channel interface is accessible via the loader
            # The Channel interface should be in the loader from channel_capnp
            assert channel_capnp.Channel is not None

        finally:
            if str(basic_stubs) in sys.path:
                sys.path.remove(str(basic_stubs))
