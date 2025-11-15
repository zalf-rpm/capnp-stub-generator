"""Quick test to verify init method uses type aliases."""
from capnp_stub_generator.writer import Writer

# Create a minimal test
writer = Writer(None, None, None)

# Mock the necessary attributes
writer._all_type_aliases = {"EntryBuilder", "EntryReader"}

# Test _get_flat_builder_alias
result = writer._get_flat_builder_alias("_MetadataModule._EntryModule")
print(f"Flat builder alias: {result}")
assert result == "EntryBuilder", f"Expected 'EntryBuilder', got '{result}'"

result2 = writer._get_flat_builder_alias("_SomeModule._OtherModule")  
print(f"Flat builder alias for non-existent: {result2}")
assert result2 is None, f"Expected None for non-existent alias, got '{result2}'"

print("✅ All tests passed!")
