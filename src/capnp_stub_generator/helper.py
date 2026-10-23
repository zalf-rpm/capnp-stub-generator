"""Helper functionality that is used in other modules of this package."""

from __future__ import annotations

import ast
import builtins
import keyword
import typing
from copy import copy
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from collections.abc import Sequence

    from capnp_stub_generator.capnp_types import SchemaType

BUILDER_NAME = "Builder"
READER_NAME = "Reader"

_BASE_CAPNP_STUB = Path(__file__).resolve().parent.parent / "pycapnp_base_stubs" / "lib" / "capnp.pyi"
_STRUCT_READER_CLASS = "_DynamicStructReader"


def sanitize_name(name: str) -> str:
    """Sanitize a name to avoid Python keywords.

    If the name is a Python keyword, append an underscore.
    E.g. 'lambda' becomes 'lambda_', 'class' becomes 'class_'.

    Args:
        name (str): The original name.

    Returns:
        str: The sanitized name.

    """
    if keyword.iskeyword(name):
        return f"{name}_"
    return name


def _build_variant_type(type_name: str, variant: str, *, flat: bool = False) -> str:
    """Build Builder or Reader variant of a type name.

    Handles both flat naming (MyClassBuilder) and nested naming (MyClass.Builder).
    Properly handles generic types by preserving type parameters.

    Args:
        type_name: The base type name (e.g., "MyClass", "Outer.Inner", "Env[T]")
        variant: Either "Builder" or "Reader"
        flat: If True, use flat naming (MyClassBuilder), else nested (MyClass.Builder)

    Returns:
        The variant type name with proper syntax

    Examples:
        >>> _build_variant_type("MyStruct", "Builder", flat=False)
        'MyStruct.Builder'
        >>> _build_variant_type("MyStruct[T]", "Builder", flat=False)
        'MyStruct[T].Builder'
        >>> _build_variant_type("MyStruct", "Builder", flat=True)
        'MyStructBuilder'
        >>> _build_variant_type("MyStruct[T]", "Builder", flat=True)
        'MyStructBuilder[T]'

    """
    if flat:
        # Flat naming: MyClass -> MyClassBuilder, MyClass[T] -> MyClassBuilder[T]
        if "[" in type_name:
            base_name, generic_part = type_name.split("[", 1)
            return f"{base_name}{variant}[{generic_part}"
        return f"{type_name}{variant}"
    # Nested naming: MyClass -> MyClass.Builder, MyClass[T] -> MyClass[T].Builder
    # Generic parameters stay with the parent: MyClass[T].Builder, not MyClass.Builder[T]
    # This is the correct Python typing pattern for nested generic classes
    return f"{type_name}.{variant}"


def new_builder_flat(type_name: str) -> str:
    """Convert a type name to its builder variant using flat naming.

    E.g. `MyClass` becomes `MyClassBuilder`.
    For generic types like `MyClass[T]`, becomes `MyClassBuilder[T]`.

    Args:
        type_name (str): The original type name.

    Returns:
        str: The builder variant.

    """
    return _build_variant_type(type_name, BUILDER_NAME, flat=True)


def new_reader_flat(type_name: str) -> str:
    """Convert a type name to its reader variant using flat naming.

    E.g. `MyClass` becomes `MyClassReader`.
    For generic types like `MyClass[T]`, becomes `MyClassReader[T]`.

    Args:
        type_name (str): The original type name.

    Returns:
        str: The reader variant.

    """
    return _build_variant_type(type_name, READER_NAME, flat=True)


def new_builder(type_name: str) -> str:
    """Convert a type name to its builder variant using nested class syntax.

    E.g. `MyClass` becomes `MyClass.Builder`.
    E.g. `Outer.Inner` becomes `Outer.Inner.Builder`.
    For generic types like `MyClass[T]`, becomes `MyClass[T].Builder`.

    Args:
        type_name (str): The original type name.

    Returns:
        str: The builder variant.

    """
    return _build_variant_type(type_name, BUILDER_NAME, flat=False)


@dataclass
class TypeHint:
    """A class that captures a type hint."""

    name: str
    scopes: list[str] = field(default_factory=list)
    affix: str = ""
    primary: bool = False
    flat_alias: bool = False  # If True, name is already a flat alias and affix is only for lookup

    @override
    def __str__(self) -> str:
        """Return the string representation of the type hint.

        This is composed of the scopes (if any), the name of the hint, and the affix (if any).
        For generic types like `MyClass[T]`, the affix comes after: `MyClass[T].Builder`.
        Affixes are treated as nested classes (e.g., MyClass.Builder instead of MyClassBuilder).
        If flat_alias is True, the name already contains the full type and affix is not appended.
        """
        # If using flat alias, don't append the affix
        if self.flat_alias:
            full_name = self.name
        # Handle affixes for generic types: MyClass[T] + Builder -> MyClass[T].Builder
        elif (self.affix and "[" in self.name) or self.affix:
            full_name = f"{self.name}.{self.affix}"
        else:
            full_name = self.name

        if not self.scopes:
            return full_name
        return f"{'.'.join(self.scopes)}.{full_name}"


@dataclass
class TypeHintedVariable:
    """A class that represents a type hinted variable."""

    name: str
    type_hints: list[TypeHint]
    default: str = ""
    nesting_depth: int = 0
    raw_list_input_type: str | None = None
    is_generic_param: bool = field(default=False, init=False)
    is_any_pointer: bool = field(default=False, init=False)
    is_any_list: bool = field(default=False, init=False)
    is_any_struct: bool = field(default=False, init=False)
    is_capability: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Sanity check for provided type hints."""
        primary_type_hint_count = 0

        for type_hint in self.type_hints:
            if type_hint.primary:
                primary_type_hint_count += 1

        if primary_type_hint_count != 1:
            msg = f"There can only be exactly one primary type hint. Found {primary_type_hint_count}"
            raise ValueError(msg)

    @override
    def __str__(self) -> str:
        """Return the string representation of this object.

        Returns:
            str: The string representation.

        """
        return self.typed_variable_with_full_hints

    def _nest(self, unnested_type_name: str) -> str:
        if self.nesting_depth > 0:
            return f"{self.nesting_depth * 'Sequence['}{unnested_type_name}{self.nesting_depth * ']'}"

        return unnested_type_name

    @property
    def typed_variable_with_full_hints(self) -> str:
        """Returns the typed variable string, hinted will all available type hints."""
        return self._generate_typed_variable(self.full_type)

    @property
    def primary_type_hint(self) -> TypeHint:
        """Returns the primary type hint."""
        for type_hint in self.type_hints:
            if type_hint.primary:
                return type_hint

        msg = "Primary type hint not found."
        raise RuntimeError(msg)

    def _generate_typed_variable(self, type_name: str) -> str:
        """Generate the typed variable string for a chosen type name.

        Args:
            type_name (str): The type name to use.

        Returns:
            str: The typed variable string.

        """
        nested_type_name = self._nest(type_name)
        typed_variable = f"{self.name}: {nested_type_name}"

        if self.default:
            typed_variable = f"{typed_variable} = {self.default}"

        return typed_variable

    def _get_type_hints_for_affixes(self, affixes: list[str]) -> list[TypeHint]:
        return [self.get_type_hint_for_affix(affix) for affix in affixes]

    def _join_type_hints(self, type_hints: list[TypeHint]) -> str:
        return " | ".join(str(type_hint) for type_hint in type_hints)

    @property
    def full_type(self) -> str:
        """The full type string of the hinted variable."""
        return self._join_type_hints(self.type_hints)

    @property
    def full_type_nested(self) -> str:
        """The full type string with nesting applied (e.g., Sequence[...] for lists)."""
        return self._nest(self.full_type)

    @property
    def primary_type_nested(self) -> str:
        """The primary type string with nesting applied."""
        return self._nest(str(self.primary_type_hint))

    def get_type_with_affixes(self, affixes: list[str]) -> str:
        """Get just the type string (no variable name) with the selected type hint affixes.

        Args:
            affixes (list[str]): The affixes to select for type hints.

        Returns:
            str: The type string with nesting applied.

        """
        type_hints_for_affixes = self._get_type_hints_for_affixes(affixes)
        type_str = self._join_type_hints(type_hints_for_affixes)
        return self._nest(type_str)

    def add_type_hint(self, new_type_hint: TypeHint) -> None:
        """Add a type hint to the hinted variable.

        Args:
            new_type_hint (TypeHint): The type hint to add.

        """
        for type_hint in self.type_hints:
            if type_hint == new_type_hint:
                msg = "Type hint already exists."
                raise ValueError(msg)

        if new_type_hint.primary:
            msg = "There can only be one primary type."
            raise ValueError(msg)

        self.type_hints.append(new_type_hint)

    def get_type_hint_for_affix(self, affix: str) -> TypeHint:
        """Return the type hint that uses the provided affix.

        Args:
            affix (str | None): The affix to look for.

        Returns:
            TypeHint: The type hint that was found.

        """
        for type_hint in self.type_hints:
            if type_hint.affix == affix:
                return type_hint

        msg = f"Affix '{affix}' is not present in any recorded type hint."
        raise KeyError(msg)

    def has_type_hint_with_affix(self, affix: str) -> bool:
        """Assess, whether or not the variable has a type hint with the provided affix."""
        return any(type_hint.affix == affix for type_hint in self.type_hints)

    @property
    def has_type_hint_with_builder_affix(self) -> bool:
        """Whether the variable holds a type hint with a builder affix."""
        return self.has_type_hint_with_affix(BUILDER_NAME)

    @property
    def has_type_hint_with_reader_affix(self) -> bool:
        """Whether the variable holds a type hint with a reader affix."""
        return self.has_type_hint_with_affix(READER_NAME)

    def add_builder_from_primary_type(self) -> None:
        """Add a type hint with builder affix, based on the primary type."""
        self.add_type_hint(
            TypeHint(
                self.primary_type_hint.name,
                copy(self.primary_type_hint.scopes),
                BUILDER_NAME,
            ),
        )

    def add_reader_from_primary_type(self) -> None:
        """Add a type hint with builder affix, based on the primary type."""
        self.add_type_hint(
            TypeHint(
                self.primary_type_hint.name,
                copy(self.primary_type_hint.scopes),
                READER_NAME,
            ),
        )


def replace_capnp_suffix(original: str) -> str:
    """If found, replaces the .capnp suffix in a string with _capnp and converts hyphens to underscores.

    This matches the behavior of pycapnp which converts hyphens to underscores in module names
    to create valid Python identifiers.

    For example, `some-module.capnp` becomes `some_module_capnp`.

    Args:
        original (str): The string to replace the suffix in.

    Returns:
        str: The string with the replaced suffix and hyphens converted to underscores.

    """
    result = original
    if result.endswith(".capnp"):
        result = result.replace(".capnp", "_capnp")

    # Replace hyphens with underscores to create valid Python identifiers
    return result.replace("-", "_")


def join_parameters(parameters: Sequence[TypeHintedVariable | str] | None) -> str:
    """Join parameters with `, `.

    Args:
        parameters (Sequence[HintedVariable | str] | None): The parameters to join.

    Returns:
        str: The joined parameters.

    """
    if parameters:
        return ", ".join(str(p) for p in parameters if p)

    return ""


@dataclass(frozen=True)
class StructReaderMember:
    """One non-dunder member of pycapnp's `_DynamicStructReader`, rendered as stub lines.

    Attributes:
        name: Member name, e.g. `_has`.
        lines: Unindented stub lines declaring the member (decorators included, docstrings stripped).
        referenced_names: Names used in the member's annotations that need to be importable.

    """

    name: str
    lines: tuple[str, ...]
    referenced_names: frozenset[str]


def _strip_docstring_body(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.FunctionDef | ast.AsyncFunctionDef:
    """Return a copy of a function whose body is just `...`."""
    stripped = copy(node)
    stripped.body = [ast.Expr(value=ast.Constant(value=...))]
    return stripped


def _annotation_names(node: ast.AST) -> frozenset[str]:
    """Collect every name referenced from the annotations inside `node`."""
    annotations: list[ast.expr] = []
    if isinstance(node, ast.AnnAssign):
        annotations.append(node.annotation)
    elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
        arguments = node.args
        all_args = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs, arguments.vararg, arguments.kwarg]
        annotations.extend(arg.annotation for arg in all_args if arg is not None and arg.annotation is not None)
        if node.returns is not None:
            annotations.append(node.returns)

    return frozenset(
        name.id for annotation in annotations for name in ast.walk(annotation) if isinstance(name, ast.Name)
    )


def _render_stub_member(node: ast.stmt) -> tuple[str, ...]:
    """Render a class-body statement as stub lines, folding a lone `...` body onto the signature line."""
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
        node = _strip_docstring_body(node)

    lines = ast.unparse(node).splitlines()
    if len(lines) >= 2 and lines[-1].strip() == "..." and lines[-2].endswith(":"):  # noqa: PLR2004
        lines[-2:] = [f"{lines[-2]} ..."]
    return tuple(lines)


@cache
def struct_reader_members() -> tuple[StructReaderMember, ...]:
    """Return the runtime surface of pycapnp's `_DynamicStructReader` as stub declarations.

    The bundled base stubs mirror the pycapnp runtime, so deriving the members from them keeps every generated
    type that stands in for a `_DynamicStructReader` in sync with the runtime without a hand-maintained list.
    `__getattr__` and the other dunders are left out on purpose: the generated types declare the schema's fields
    explicitly, and a catch-all `__getattr__` would hide misspelled field names from the type checker.

    Returns:
        The attribute and method declarations in their original order.

    Raises:
        LookupError: If the bundled stubs do not declare `_DynamicStructReader`.

    """
    tree = ast.parse(_BASE_CAPNP_STUB.read_text(encoding="utf8"))
    reader_class = next(
        (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == _STRUCT_READER_CLASS),
        None,
    )
    if reader_class is None:
        msg = f"{_STRUCT_READER_CLASS} not found in {_BASE_CAPNP_STUB}"
        raise LookupError(msg)

    members: list[StructReaderMember] = []
    for node in reader_class.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            name = node.name
        else:
            continue

        if name.startswith("__") and name.endswith("__"):
            continue

        members.append(StructReaderMember(name, _render_stub_member(node), _annotation_names(node)))

    return tuple(members)


def classify_stub_import(name: str) -> str | None:
    """Return where a name used in a copied stub annotation has to be imported from.

    Returns:
        `"typing"` for names from the typing module, `"capnp"` for pycapnp types, `None` for builtins.

    """
    if hasattr(builtins, name):
        return None
    if name in typing.__all__:
        return "typing"
    return "capnp"


def new_group(name: str, members: list[str]) -> str:
    """Create a string for a group name and its members.

    For example, when the group name is 'Type', and the parameters are 'str', and 'int',
    the output will be 'Type[str, int]'.

    Args:
        name (str): The name of the group.
        members (list[str]): The members of the group

    Returns:
        str: The resulting group string.

    """
    return f"{name}[{join_parameters(members)}]"


def new_type_group(name: str, types: list[str]) -> str:
    """Create a string for a parameter with types.

    Uses `new_group` internally.

    Args:
        name (str): The name of the parameter.
        types (list[str]): The list of types to that this parameter can have.

    Returns:
        str: The resulting parameter string.

    """
    return new_group(name, types)


def new_function(
    name: str,
    parameters: Sequence[TypeHintedVariable | str] | None = None,
    return_type: str | None = None,
) -> str:
    """Create a string for a function.

    Args:
        name (str): The function name.
        parameters (Sequence[HintedVariable | str] | None, optional): The function parameters, if any. Defaults to None.
        return_type (str | None, optional): The function's return type. Defaults to None.

    Returns:
        str: The function string.

    """
    if return_type is None:
        return_type = "None"

    arguments = join_parameters(parameters)
    return f"def {name}({arguments}) -> {return_type}: ..."


def new_decorator(name: str, parameters: Sequence[TypeHintedVariable | str] | None = None) -> str:
    """Create a new decorator.

    Args:
        name (str): The name of the decorator.
        parameters (Sequence[HintedVariable | str] | None, optional): The parameters (args, kwargs) of the decorator,
            if any. Defaults to None.

    Returns:
        str: The decorator string.

    """
    if parameters:
        return f"@{name}({join_parameters(parameters)})"

    return f"@{name}"


def new_property(
    name: str,
    return_type: str,
    *,
    with_setter: bool = False,
    setter_type: str | None = None,
    add_override: bool = False,
) -> list[str]:
    """Create a property declaration.

    Includes special handling for reserved pycapnp runtime introspection names.

    Args:
        name (str): The property name.
        return_type (str): The property's return type.
        with_setter (bool): Whether to include a setter.
        setter_type (str | None): The setter's parameter type (if different from return_type).
        add_override (bool): Whether to add @override decorator (placed after @property).

    Returns:
        list[str]: Lines to be added (decorator + function, and optionally setter).

    """
    lines: list[str] = []

    lines.append("@property")
    if add_override:
        lines.append("@override")
    lines.append(f"def {name}(self) -> {return_type}: ...")

    if with_setter:
        lines.append(f"@{name}.setter")
        if add_override:
            lines.append("@override")
        param_type = setter_type if setter_type is not None else return_type
        lines.append(f"def {name}(self, value: {param_type}) -> None: ...")

    return lines


def new_class_declaration(name: str, parameters: Sequence[str] | None = None) -> str:
    """Create a class declaration string.

    For example, for a name of 'SomeClass' and a list of parameters that is 'str, Type[str, int]', the output
    will be 'SomeClass (str, Type[str, int]):'.

    If no parameters are provided, the output is just 'SomeClass:'.

    Args:
        name (str): The class name.
        parameters (Sequence[str] | None, optional):
            A list of parameters that are part of the class declaration. Defaults to None.

    Returns:
        str: The class declaration.

    """
    if parameters:
        return f"class {name}({join_parameters(parameters)}):"
    return f"class {name}:"


def get_display_name(schema: SchemaType) -> str:
    """Extract the display name from a schema.

    Args:
        schema (Any): The schema to get the display name from.

    Returns:
        str: The display name of the schema.

    """
    return schema.node.displayName[schema.node.displayNamePrefixLength :]
