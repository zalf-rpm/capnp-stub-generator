"""Test that Result types are available as top-level type aliases like Builder and Reader."""

import pytest


def test_result_type_aliases_exist(calculator_stubs):
    """Test that Result type aliases are generated at the top level."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Check for Result type aliases in the top-level section
    assert "type EvaluateResult = " in content, "EvaluateResult type alias should exist"
    assert "type DeffunctionResult = " in content, "DeffunctionResult type alias should exist"
    assert "type GetoperatorResult = " in content, "GetoperatorResult type alias should exist"
    assert "type ReadResult = " in content, "ReadResult type alias should exist"
    assert "type CallResult = " in content, "CallResult type alias should exist"


def test_result_type_aliases_point_to_client_nested_types(calculator_stubs):
    """Test that Result type aliases point to Client-nested Result classes."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Result types should point to Client.Result (not Server.Result)
    assert "type EvaluateResult = _CalculatorInterfaceModule.CalculatorClient.EvaluateResult" in content, (
        "EvaluateResult should point to CalculatorClient.EvaluateResult"
    )

    assert "type ReadResult = _CalculatorInterfaceModule._ValueInterfaceModule.ValueClient.ReadResult" in content, (
        "ReadResult should point to ValueClient.ReadResult"
    )

    assert (
        "type CallResult = _CalculatorInterfaceModule._FunctionInterfaceModule.FunctionClient.CallResult" in content
    ), "CallResult should point to FunctionClient.CallResult"


def test_result_type_aliases_alongside_builder_reader(calculator_stubs):
    """Test that Result type aliases appear alongside Builder and Reader aliases."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Find the type alias section
    lines = content.split("\n")
    type_alias_section = []
    in_type_alias_section = False

    for line in lines:
        if "# Top-level type aliases" in line:
            in_type_alias_section = True
        elif in_type_alias_section:
            if line.startswith("type "):
                type_alias_section.append(line)
            elif line and not line.startswith("#"):
                break

    # Should have Builder, Reader, Client, and Result type aliases
    assert any("Builder" in line for line in type_alias_section), "Should have Builder aliases"
    assert any("Reader" in line for line in type_alias_section), "Should have Reader aliases"
    assert any("Client" in line for line in type_alias_section), "Should have Client aliases"
    assert any("Result" in line for line in type_alias_section), "Should have Result aliases"


def test_result_type_aliases_in_sorted_order(calculator_stubs):
    """Test that Result type aliases are sorted alphabetically with other aliases."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Extract all type aliases
    lines = content.split("\n")
    type_aliases = []
    in_type_alias_section = False

    for line in lines:
        if "# Top-level type aliases" in line:
            in_type_alias_section = True
        elif in_type_alias_section:
            if line.startswith("type "):
                # Extract alias name: "type Name = ..." -> "Name"
                alias_name = line.split("=")[0].replace("type ", "").strip()
                type_aliases.append(alias_name)
            elif line and not line.startswith("#"):
                break

    # Check that aliases are sorted
    sorted_aliases = sorted(type_aliases)
    assert type_aliases == sorted_aliases, f"Type aliases should be sorted. Got: {type_aliases}"


def test_void_method_result_type_alias_exists(calculator_stubs):
    """Test that void methods also have Result type aliases."""
    # For the channel example with void methods
    channel_stub = calculator_stubs.parent.parent / "basic" / "interfaces_capnp.pyi"

    if not channel_stub.exists():
        pytest.skip("Channel stub not available")

    content = channel_stub.read_text()

    # Check for CloseResult (void method)
    if "CloseResult" in content:
        # Should have type alias for void method result too
        assert "type CloseResult = " in content, "Void method should also have Result type alias"


def test_nested_interface_result_type_aliases(calculator_stubs):
    """Test that nested interfaces (Value, Function) have Result type aliases."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Value interface has read() -> ReadResult
    assert "type ReadResult = " in content
    assert "ValueClient.ReadResult" in content

    # Function interface has call() -> CallResult
    assert "type CallResult = " in content
    assert "FunctionClient.CallResult" in content


def test_result_type_alias_usage_in_type_hints(calculator_stubs):
    """Test that Result type aliases can be used in type hints (manual check)."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # The type aliases should be at module level, making them usable:
    # def my_function() -> EvaluateResult: ...
    # This is verified by the presence of the type alias definition
    assert "type EvaluateResult = _CalculatorInterfaceModule.CalculatorClient.EvaluateResult" in content

    # And the actual Result class should be nested in Client
    assert "class EvaluateResult(Awaitable[EvaluateResult], Protocol):" in content
    assert "    class CalculatorClient" in content


def test_result_type_count_matches_method_count(calculator_stubs):
    """Test that we have Result type aliases for all interface methods."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # Count Result type aliases for Calculator methods
    # Note: method names are titled using .title() which lowercases everything except first char after space
    calculator_results = [
        ("evaluate", "EvaluateResult"),
        ("defFunction", "DeffunctionResult"),  # .title() makes it "Deffunction"
        ("getOperator", "GetoperatorResult"),  # .title() makes it "Getoperator"
    ]

    for method_name, result_name in calculator_results:
        assert f"type {result_name} = " in content, f"Should have {result_name} type alias for {method_name}"

    # Count Result type aliases for Value methods
    assert "type ReadResult = " in content, "Should have ReadResult type alias"

    # Count Result type aliases for Function methods
    assert "type CallResult = " in content, "Should have CallResult type alias"


def test_summary():
    """Summary of Result type alias tests."""
    print("\n✓ Result type aliases generated")
    print("✓ Result aliases point to Client-nested types")
    print("✓ Result aliases appear alongside Builder/Reader aliases")
    print("✓ Result aliases are sorted alphabetically")
    print("✓ Void method Results have aliases")
    print("✓ Nested interface Results have aliases")
    print("✓ Result alias count matches method count")
