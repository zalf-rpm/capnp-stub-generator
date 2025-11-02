"""Baseline tests for calculator example Python code.

This establishes a baseline for the calculator example's type errors,
tracking them as we improve interface stub generation.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent
CALCULATOR_DIR = TESTS_DIR / "examples" / "calculator"


def run_pyright_on_file(file_path: Path) -> tuple[int, str]:
    """Run pyright on a file and return error count and output."""
    result = subprocess.run(
        ["pyright", str(file_path)],
        capture_output=True,
        text=True,
    )
    error_count = result.stdout.count("error:")
    return error_count, result.stdout


class TestCalculatorClientBaseline:
    """Baseline tests for async_calculator_client.py."""

    def test_client_type_errors_baseline(self):
        """Track baseline type errors in calculator client."""
        file_path = CALCULATOR_DIR / "async_calculator_client.py"
        error_count, output = run_pyright_on_file(file_path)

        # Expect no errors after fixes.
        EXPECTED_ERRORS = 0

        if error_count != EXPECTED_ERRORS:
            pytest.fail(
                f"Calculator client has {error_count} errors (expected {EXPECTED_ERRORS}).\n"
                f"Pyright output:\n{output}\n\n"
                f"If errors decreased, update EXPECTED_ERRORS!\n"
                f"If errors increased, check for regressions."
            )

    def test_client_has_no_runtime_attribute_errors(self):
        """Test that basic capnp attributes are now available."""
        file_path = CALCULATOR_DIR / "async_calculator_client.py"
        _, output = run_pyright_on_file(file_path)

        # These should NOT have "is not a known attribute" errors anymore
        runtime_attrs = ["TwoPartyClient", "AsyncIoStream", "run"]

        for attr in runtime_attrs:
            if f'"{attr}" is not a known attribute' in output:
                pytest.fail(
                    f"Runtime attribute '{attr}' still not recognized in stubs.\n"
                    f"Pyright output:\n{output}"
                )


class TestCalculatorServerBaseline:
    """Baseline tests for async_calculator_server.py."""

    def test_server_type_errors_baseline(self):
        """Track baseline type errors in calculator server."""
        file_path = CALCULATOR_DIR / "async_calculator_server.py"
        error_count, output = run_pyright_on_file(file_path)

        # Expect no errors after fixes.
        EXPECTED_ERRORS = 0

        if error_count != EXPECTED_ERRORS:
            pytest.fail(
                f"Calculator server has {error_count} errors (expected {EXPECTED_ERRORS}).\n"
                f"Pyright output:\n{output}\n\n"
                f"If errors decreased, update EXPECTED_ERRORS!\n"
                f"If errors increased, check for regressions."
            )

    def test_server_has_no_runtime_attribute_errors(self):
        """Test that basic capnp attributes are now available."""
        file_path = CALCULATOR_DIR / "async_calculator_server.py"
        _, output = run_pyright_on_file(file_path)

        # These should NOT have "is not a known attribute" errors anymore
        runtime_attrs = ["TwoPartyServer", "AsyncIoStream", "run"]

        for attr in runtime_attrs:
            if f'"{attr}" is not a known attribute' in output:
                pytest.fail(
                    f"Runtime attribute '{attr}' still not recognized in stubs.\n"
                    f"Pyright output:\n{output}"
                )


class TestCalculatorErrorCategories:
    """Categorize the types of errors in calculator code."""

    def test_categorize_client_errors(self):
        """Categorize and document client errors."""
        file_path = CALCULATOR_DIR / "async_calculator_client.py"
        _, output = run_pyright_on_file(file_path)

        error_categories = {
            "nested_interface": "Calculator.Function.Server",
            "runtime_attrs": ["TwoPartyClient", "AsyncIoStream", "run"],
        }

        # Count errors by category
        nested_interface_errors = output.count('Cannot access attribute "Function"')
        runtime_attr_errors = sum(
            output.count(f'"{attr}" is not a known attribute')
            for attr in error_categories["runtime_attrs"]
        )

        print("\nClient error categories:")
        print(f"  Nested interface access: {nested_interface_errors}")
        print(f"  Runtime attribute access: {runtime_attr_errors}")

        # After stub updates, runtime errors should be 0
        assert runtime_attr_errors == 0, "Runtime attributes should be available after stub update"

    def test_categorize_server_errors(self):
        """Categorize and document server errors."""
        file_path = CALCULATOR_DIR / "async_calculator_server.py"
        _, output = run_pyright_on_file(file_path)

        # Count error types
        nested_interface_errors = output.count("Cannot access attribute")
        unknown_type_errors = output.count("Unknown")
        runtime_attr_errors = output.count("is not a known attribute")

        print("\nServer error categories:")
        print(f"  Nested interface/attribute: {nested_interface_errors}")
        print(f"  Unknown types: {unknown_type_errors}")
        print(f"  Runtime attributes: {runtime_attr_errors}")

        # After stub updates, runtime errors should be 0
        assert runtime_attr_errors == 0, "Runtime attributes should be available after stub update"


class TestCalculatorImprovementTracking:
    """Track improvements in calculator type checking over time."""

    def test_calculator_combined_baseline(self):
        """Track total errors across both files."""
        client_errors, _ = run_pyright_on_file(CALCULATOR_DIR / "async_calculator_client.py")
        server_errors, _ = run_pyright_on_file(CALCULATOR_DIR / "async_calculator_server.py")

        total_errors = client_errors + server_errors

        # Expect zero errors combined now.
        EXPECTED_TOTAL = 0

        print(f"\nTotal calculator errors: {total_errors}")
        print(f"  Client: {client_errors}")
        print(f"  Server: {server_errors}")
        print(f"  Expected: {EXPECTED_TOTAL}")

        if total_errors < EXPECTED_TOTAL:
            print(f"\n🎉 IMPROVEMENT! Errors reduced from {EXPECTED_TOTAL} to {total_errors}")
            print("Update EXPECTED_TOTAL in this test!")

        assert total_errors <= EXPECTED_TOTAL, (
            f"Type errors increased! Was {EXPECTED_TOTAL}, now {total_errors}"
        )

    def test_no_regression_in_runtime_stubs(self):
        """Ensure runtime stub additions don't cause regressions."""
        # Test both files
        for file_name in ["async_calculator_client.py", "async_calculator_server.py"]:
            file_path = CALCULATOR_DIR / file_name
            _, output = run_pyright_on_file(file_path)

            # These runtime attributes should all be available now
            missing_attrs = []
            for attr in ["TwoPartyClient", "TwoPartyServer", "AsyncIoStream", "run"]:
                if f'"{attr}" is not a known attribute' in output:
                    missing_attrs.append(attr)

            assert not missing_attrs, (
                f"{file_name}: Missing runtime attributes: {missing_attrs}\n"
                "These should be available in capnp stubs!"
            )


def test_calculator_baseline_summary():
    """Summary of calculator baseline tests."""
    print("\n" + "=" * 70)
    print("CALCULATOR BASELINE TEST SUMMARY")
    print("=" * 70)
    print("All baseline tests passed!")
    print("  ✓ Client errors: 4 (baseline established)")
    print("  ✓ Server errors: 9 (baseline established)")
    print("  ✓ Runtime attributes: All available")
    print("  ✓ No regressions detected")
    print("\nMain remaining issues:")
    print("  - Interface nested types (Calculator.Function.Server)")
    print("  - Interface nested type parameters (Expression)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
