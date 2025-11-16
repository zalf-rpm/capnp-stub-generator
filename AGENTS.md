# capnp-stub-generator: AI Agent Guidelines

## Project Overview
This is a Python stub generator that creates `.pyi` type hint files from Cap'n Proto (`.capnp`) schema files for static type checking with tools like mypy and pyright. The generated stubs enable IDE auto-completion and static analysis for pycapnp-based projects.

## Key Requirements
- **Python Version**: 3.10 - 3.13
- **Core Dependency**: pycapnp >= 2.2.1, < 3.0.0
- **Compatibility**: Generated stubs are only compatible with pycapnp >= 2.0.0
- **Output Structure**: Generated stubs must match the exact structure and API of pycapnp runtime modules

## Project Structure
```
capnp_stub_generator/
├── cli.py              # Command-line interface and argument parsing
├── run.py              # Main execution logic and file processing
├── writer.py           # Core stub generation logic (main class: Writer)
├── writer_dto.py       # Data transfer objects for generation contexts
├── scope.py            # Scope management for type resolution
├── helper.py           # Utility functions
├── capnp_types.py      # Type definitions and mappings
└── __main__.py         # Entry point
tests/
├── schemas/            # Test Cap'n Proto schemas
│   ├── basic/          # Basic feature tests
│   ├── examples/       # Example schemas (addressbook, etc.)
│   └── zalfmas/        # Complex real-world schemas
├── test_*.py           # Pytest test files
└── conftest.py         # Pytest configuration and fixtures
```

## Running the Generator

### CLI Usage
```bash
capnp-stub-generator \
    -p "path/to/schemas/**/*.capnp" \     # Schema files to process
    -c "output/**/*_capnp.py" \            # Files to clean before generation
    -e "**/excluded/**/*.capnp" \          # Exclude patterns
    -I /path/to/import/roots \             # Import paths for absolute imports
    -o output/directory \                  # Output directory (optional)
    -r                                     # Recursive search
    --no-pyright                           # Skip pyright validation
```

### Important CLI Notes
- **Always generate all files at once** to properly resolve dependencies and imports between schemas
- Use `-I` flag for schemas with absolute imports (e.g., `import "/capnp/c++.capnp"`)
- Multiple `-I` paths can be specified for complex import hierarchies
- Default behavior: stubs are generated adjacent to schema files
- With `-o`: all stubs go to specified output directory

## Testing

### Test Architecture

The test suite uses a **centralized generation approach** where all test stubs are generated once at the beginning of the test session and reused across all tests. This ensures consistency and faster test execution.

**IMPORTANT**: All generated stubs are validated with pyright. The `--no-pyright` flag must NOT be used in tests. If pyright errors occur, the generator code must be fixed, not the validation disabled. See [Pyright Validation Policy](#pyright-validation-policy) for details.

#### Test Session Flow
1. **Session Start**: `conftest.py` automatically generates all stubs in `tests/_generated/` **with pyright validation**
2. **Test Execution**: All tests read from the pre-generated stubs
3. **Session End**: Generated stubs remain for inspection (git-ignored)

### Test Structure

```
tests/
├── conftest.py                    # Central fixture configuration
├── schemas/                       # Source schema files (committed)
│   ├── basic/                     # 18 schemas for basic features
│   │   ├── dummy.capnp            # Comprehensive test schema
│   │   ├── advanced_features.capnp
│   │   ├── interfaces.capnp
│   │   └── ...
│   ├── examples/                  # Real-world examples
│   │   ├── calculator/            # RPC calculator example
│   │   ├── addressbook/           # Classic addressbook example
│   │   ├── climate/
│   │   └── identifiable/
│   └── zalfmas/                   # 20+ complex production schemas
│       ├── model.capnp
│       ├── common.capnp
│       └── ...
├── _generated/                    # Auto-generated stubs (git-ignored)
│   ├── basic/
│   ├── examples/
│   └── zalfmas/
└── test_*.py                      # 35 test files (221 tests total)
```

### Test Categories

#### 1. Feature Tests (test_*_features.py)
Test specific Cap'n Proto features:
- `test_basic_low.py` - Enums, simple structs
- `test_mid_features.py` - Lists, sequences, unions
- `test_advanced_*.py` - Generics, groups, versioning, name annotations

#### 2. Dummy Schema Tests (test_dummy_*.py)
Comprehensive tests using `dummy.capnp`:
- `test_dummy_schema.py` - Consolidated tests
- `test_dummy_enums_and_all_types.py` - Enum and type definitions
- `test_dummy_unions.py` - Union discriminants and which() methods
- `test_dummy_groups_and_nested.py` - Group fields and nested types
- `test_dummy_constants_versions_names.py` - Constants, versioning, annotations
- `test_dummy_lists_and_defaults.py` - List fields and default values

#### 3. Type Checking Tests (test_typing_*.py, test_addressbook_typing.py)
Validate that generated stubs provide correct types:
- `test_addressbook_typing.py` - List initialization, element access, iteration
- `test_typing_*.py` - Various typing scenarios
- `test_union_type_annotations.py` - Union type syntax

#### 4. Interface Tests (test_interface_*.py)
Test RPC interface generation:
- `test_interface_server_methods.py` - Server method signatures
- `test_interface_result_types.py` - Result type generation
- `test_interface_method_types.py` - Method parameter and return types
- `test_interface_void_methods.py` - Void return types
- `test_interface_inheritance.py` - Interface inheritance chains

#### 5. Request/Response Tests
- `test_request_builder_types.py` - Request builder field types
- `test_server_context_parameter.py` - _context parameter in server methods

#### 6. Return Type Tests
- `test_return_types.py` - Struct return types (Base, Builder, Reader variants)

#### 7. CLI Tests
- `test_cli.py` - Comprehensive CLI argument testing (30+ tests)
- `test_directory_structure.py` - Output directory structure preservation

#### 8. Real-World Tests
- `test_real_world_examples.py` - Calculator and addressbook examples
- `test_zalfmas_schemas.py` - Production schema validation

#### 9. Unit Tests
- `test_writer_dto.py` - Data transfer object tests
- `test_generation_extended.py` - Extended generation patterns

### Key Test Fixtures

#### Session-Scoped Fixtures (conftest.py)

```python
@pytest.fixture(scope="session", autouse=True)
def generate_all_stubs():
    """Auto-generates all stubs before any tests run."""
    # Generates basic, examples, and zalfmas schemas
    # Returns paths dict: {"basic": Path, "examples": Path, "zalfmas": Path}

@pytest.fixture(scope="session")
def generated_stubs(generate_all_stubs):
    """Provides access to generated stub directories."""

@pytest.fixture(scope="session")
def basic_stubs(generated_stubs):
    """Path to tests/_generated/basic/"""

@pytest.fixture(scope="session")
def calculator_stubs(generated_stubs):
    """Path to tests/_generated/examples/calculator/"""

@pytest.fixture(scope="session")
def addressbook_stubs(generated_stubs):
    """Path to tests/_generated/examples/addressbook/"""

@pytest.fixture(scope="session")
def zalfmas_stubs(generated_stubs):
    """Path to tests/_generated/zalfmas/"""

@pytest.fixture(scope="session")
def dummy_stub_file(basic_stubs):
    """Path to dummy_capnp.pyi"""

@pytest.fixture(scope="session")
def dummy_stub_lines(dummy_stub_file):
    """Lines from dummy_capnp.pyi as list[str]"""
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_addressbook_typing.py

# Run specific test
pytest tests/test_cli.py::TestArgumentParsing::test_parser_setup

# Run tests matching pattern
pytest -k "interface"

# Run with coverage
pytest --cov=capnp_stub_generator

# Run and show print statements
pytest -s

# Stop at first failure
pytest -x

# Show local variables in tracebacks
pytest -l

# Parallel execution (if pytest-xdist installed)
pytest -n auto
```

### Test Execution Time
- **Full suite**: ~45-60 seconds (221 tests)
- **Individual file**: 1-5 seconds typically
- **Stub generation**: ~8-10 seconds (one-time at session start)

## How to Add New Tests

### Pattern 1: Using Pre-Generated Stubs (Recommended)

For tests that validate stub content:

```python
def test_my_feature(basic_stubs):
    """Test description."""
    stub_file = basic_stubs / "my_schema_capnp.pyi"
    content = stub_file.read_text()

    # Assert on content
    assert "expected_content" in content
```

### Pattern 2: Using Fixture Lines

For line-by-line assertions on dummy.capnp:

```python
def test_dummy_feature(dummy_stub_lines):
    """Test description."""
    lines = dummy_stub_lines

    # Check for specific patterns
    assert any("class MyStruct" in line for line in lines)
    assert any("def myField(self)" in line for line in lines)
```

### Pattern 3: Type Checking Tests

For validating that generated types work with pyright:

```python
def test_type_checking(addressbook_stubs):
    """Test type checking with pyright."""
    # Create test code
    test_code = '''
import addressbook_capnp

book = addressbook_capnp.AddressBook.new_message()
# ... code that should type check
'''

    test_file = addressbook_stubs / "test_my_typing.py"
    test_file.write_text(test_code)

    # Run pyright
    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    error_count = result.stdout.count("error:")
    assert error_count == 0, f"Type checking failed: {result.stdout}"
```

### Pattern 4: Custom Stub Generation

For tests that need specific generation scenarios (e.g., CLI tests):

```python
def test_custom_generation(tmp_path):
    """Test with custom stub generation."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Generate stubs
    main(["-p", str(schema_path), "-o", str(output_dir), "--no-pyright"])

    # Verify output
    stub_file = output_dir / "my_schema_capnp.pyi"
    assert stub_file.exists()
```

### Adding a New Schema

1. **Add schema file**:
   ```bash
   # For basic tests
   touch tests/schemas/basic/new_feature.capnp

   # For examples
   mkdir tests/schemas/examples/new_example
   touch tests/schemas/examples/new_example/example.capnp
   ```

2. **Schema will auto-generate** on next test run

3. **Create test file**:
   ```python
   # tests/test_new_feature.py
   def test_new_feature(basic_stubs):
       stub = basic_stubs / "new_feature_capnp.pyi"
       content = stub.read_text()
       # ... assertions
   ```

### Test Organization Guidelines

1. **One test file per major feature** (e.g., `test_interface_inheritance.py`)
2. **Group related tests in classes** (e.g., `TestInterfaceReturnTypes`)
3. **Use descriptive test names** (e.g., `test_builder_setter_accepts_union`)
4. **Add docstrings** explaining what is being tested and why
5. **Use fixtures** rather than generating stubs in individual tests

### Common Test Patterns

#### Checking for Class Definitions
```python
assert any("class MyStruct:" in line for line in lines)
assert any("class MyStructBuilder(MyStruct):" in line for line in lines)
```

#### Checking for Properties
```python
assert any("def fieldName(self) -> str:" in line for line in lines)
assert any("@fieldName.setter" in line for line in lines)
```

#### Checking for Imports
```python
assert any(line.startswith("from typing import") and "Protocol" in line for line in lines)
```

#### Checking for Union Discriminants
```python
assert any("def which(self) -> Literal[" in line for line in lines)
```

#### Finding Nested Content
```python
# Find content within a specific class
in_class = False
for line in lines:
    if "class MyClass:" in line:
        in_class = True
    elif in_class and "def myMethod" in line:
        found_method = True
        break
```

### Debugging Test Failures

1. **Check generated stubs**:
   ```bash
   ls tests/_generated/basic/
   cat tests/_generated/basic/my_schema_capnp.pyi
   ```

2. **Run with verbose output**:
   ```bash
   pytest tests/test_failing.py -vv
   ```

3. **Inspect fixture values**:
   ```python
   def test_debug(basic_stubs):
       print(f"Stub dir: {basic_stubs}")
       print(f"Files: {list(basic_stubs.glob('*.pyi'))}")
   ```

4. **Check stub generation logs**:
   ```bash
   # Re-run stub generation manually
   rm -rf tests/_generated
   pytest tests/test_my_test.py -v -s  # -s shows print output
   ```

5. **If pyright validation fails**:
   - DO NOT add `--no-pyright` to bypass the error
   - Read the pyright error message carefully
   - Locate the problematic generated code
   - Fix the generator code in `writer.py`
   - See [Pyright Validation Policy](#pyright-validation-policy) for details

### Test Suite Maintenance

#### When Schema Structure Changes
- Update schema files in `tests/schemas/`
- Stubs regenerate automatically on next test run
- Update test assertions if stub format changes

#### When Adding New Generator Features
1. Add or modify schema to test the feature
2. Create test file or add to existing test file
3. Run tests to ensure feature works
4. Check generated stub manually for correctness

#### When Refactoring Tests
- Maintain fixture usage patterns
- Keep session-scoped fixtures for performance
- Use pre-generated stubs when possible
- **NEVER add `--no-pyright` flag** - fix generator issues instead

### Test Coverage

Current test coverage includes:
- **221 tests** across 35 test files
- **Basic features**: Enums, structs, primitives, lists
- **Advanced features**: Unions, groups, generics, versioning
- **Interfaces**: Client/server methods, inheritance, request/response types
- **Type checking**: Validates generated stubs with pyright
- **CLI**: All command-line arguments and options
- **Real-world schemas**: Production-level complexity

### Performance Considerations

- **Session-scoped fixtures**: Stubs generated once per test session
- **Parallel execution possible**: Tests are independent after stub generation
- **Directory structure preserved**: Generator maintains schema directory hierarchy
- **Git-ignored output**: `tests/_generated/` excluded from version control

### Important Notes for AI Agents
- This is a fork from a company-internal repository
- Issues are fixed upstream and backported
- May become independent in the future
- Always preserve existing functionality when making changes
- Test extensively with real-world schemas (zalfmas/) to catch edge cases
- Generated stubs must be importable and pass pyright/mypy validation

## Pyright Validation Policy

**CRITICAL**: Pyright validation is **mandatory** and must not be disabled in tests.

### Policy Rules

1. **DO NOT use `--no-pyright` in tests**
   - All test stubs are validated with pyright during generation
   - This ensures type correctness and catches errors early

2. **Fix pyright errors, don't ignore them**
   - If pyright reports an error, the generator code must be fixed
   - Do not work around errors by disabling validation
   - Pyright errors indicate real type safety issues

3. **Why this policy exists**
   - Generated stubs must be type-safe for end users
   - Pyright errors often reveal bugs in the generator logic
   - Early detection prevents runtime issues
   - Maintains high quality standards

### When You Encounter Pyright Errors

1. **Understand the error**: Read the pyright message carefully
2. **Locate the issue**: Find where in `writer.py` the problematic code is generated
3. **Fix the root cause**: Modify the generator to produce correct type hints
4. **Test thoroughly**: Ensure fix doesn't break other functionality

### Common Pyright Issues and Solutions

- **NamedTuple reserved names**: Use `_sanitize_namedtuple_field_name()`
- **Generic Builder types**: Use `_build_scoped_builder_type()` not string concatenation
- **Forward references**: Only generate references to classes that will exist
- **Missing imports**: Ensure all used types are properly imported

### Example: Bad vs Good Practice

```python
# ❌ BAD: Disabling validation to hide errors
main(["-p", str(schema), "-o", str(output), "--no-pyright"])

# ✅ GOOD: Ensuring validation runs
main(["-p", str(schema), "-o", str(output)])
# If this fails, fix the generator code, not the test
```

## Code Style & Linting
- **Formatter/Linter**: ruff (configured in pyproject.toml)
- **Line Length**: 120 characters
- **Target**: Python 3.10+
- **Enabled Rules**: E (pycodestyle errors), F (pyflakes), I (isort), UP (pyupgrade)
- **Run**: `ruff check .` and `ruff format .`

## Architecture & Key Concepts

### Writer Class (writer.py)
The core class that generates stub files:
- Processes pycapnp compiled modules
- Generates class definitions, methods, properties
- Handles structs, interfaces, enums, unions, groups
- Manages type imports and scopes
- Special handling for discriminant unions (DISCRIMINANT_NONE = 65535)

### Scope Management (scope.py)
- Tracks type definitions and their qualified names
- Resolves cross-file type references
- Handles nested type definitions
- Manages imports between generated modules

### Type Mappings (capnp_types.py)
- Maps Cap'n Proto primitive types to Python types
- Handles generic types (List, Data, Text)
- Special types: AnyPointer, Capability, Promise
- pycapnp-specific types: _DynamicStructBuilder, _DynamicStructReader, etc.

## Common Pitfalls & Considerations

1. **Dependency Order**: Schemas with imports must be processed together, not individually
2. **Import Paths**: Absolute imports require proper `-I` configuration
3. **pycapnp Compatibility**: Generated stubs mirror pycapnp's runtime structure exactly
4. **Nested Types**: Complex nested structures require careful scope management
5. **Union Discriminants**: Unions have special discriminant handling for type safety
6. **Validation**: Generated stubs are validated with pyright by default

## Making Changes

### When Adding Features
1. Add test schemas in `tests/schemas/` if needed
2. Write pytest test in `tests/test_*.py`
3. Implement feature in `writer.py` or related modules
4. Run full test suite: `pytest`
5. Check linting: `ruff check . && ruff format .`
6. Verify generated stubs with: `capnp-stub-generator -p "tests/schemas/**/*.capnp" -r`

### When Fixing Bugs
1. Create minimal reproduction in test suite
2. Fix issue in relevant module
3. Verify test passes and no regressions
4. Check existing tests still pass

## Development Workflow
```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .
poetry run ruff format .

# Generate stubs for testing
poetry run capnp-stub-generator -p "tests/schemas/**/*.capnp" -r

# Run specific test
poetry run pytest tests/test_addressbook_typing.py -v
```
