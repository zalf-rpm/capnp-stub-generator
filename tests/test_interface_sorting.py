"""Unit tests for interface inheritance depth computation and sorting."""

from capnp_stub_generator.run import InterfaceNode, _sort_interfaces_by_inheritance


def test_interface_node_compute_depth_root():
    """Root interfaces have depth 0."""
    node = InterfaceNode("Base", "Base.Client", [])
    assert node.compute_depth({}, {}) == 0


def test_interface_node_compute_depth_single_inheritance():
    """Single inheritance chain has correct depth."""
    base = InterfaceNode("Base", "Base.Client", [])
    derived = InterfaceNode("Derived", "Derived.Client", ["Base.Client"])

    registry = {"Base": base, "Derived": derived}
    client_map = {"Base.Client": "Base", "Derived.Client": "Derived"}

    assert base.compute_depth(registry, client_map) == 0
    assert derived.compute_depth(registry, client_map) == 1


def test_interface_node_compute_depth_multi_level():
    """Multi-level inheritance has correct depths."""
    root = InterfaceNode("Root", "Root.Client", [])
    mid = InterfaceNode("Mid", "Mid.Client", ["Root.Client"])
    leaf = InterfaceNode("Leaf", "Leaf.Client", ["Mid.Client"])

    registry = {"Root": root, "Mid": mid, "Leaf": leaf}
    client_map = {"Root.Client": "Root", "Mid.Client": "Mid", "Leaf.Client": "Leaf"}

    assert root.compute_depth(registry, client_map) == 0
    assert mid.compute_depth(registry, client_map) == 1
    assert leaf.compute_depth(registry, client_map) == 2


def test_interface_node_compute_depth_multiple_bases():
    """Interface with multiple bases uses max depth."""
    base1 = InterfaceNode("Base1", "Base1.Client", [])
    base2 = InterfaceNode("Base2", "Base2.Client", [])
    mid = InterfaceNode("Mid", "Mid.Client", ["Base1.Client"])
    derived = InterfaceNode("Derived", "Derived.Client", ["Base2.Client", "Mid.Client"])

    registry = {"Base1": base1, "Base2": base2, "Mid": mid, "Derived": derived}
    client_map = {
        "Base1.Client": "Base1",
        "Base2.Client": "Base2",
        "Mid.Client": "Mid",
        "Derived.Client": "Derived",
    }

    assert derived.compute_depth(registry, client_map) == 2  # 1 + max(0, 1)


def test_interface_node_compute_depth_circular():
    """Circular dependencies return 0 gracefully."""
    # Simulate circular: A -> B -> A
    a = InterfaceNode("A", "A.Client", ["B.Client"])
    b = InterfaceNode("B", "B.Client", ["A.Client"])

    registry = {"A": a, "B": b}
    client_map = {"A.Client": "A", "B.Client": "B"}

    # Should handle gracefully without infinite recursion
    depth_a = a.compute_depth(registry, client_map)
    depth_b = b.compute_depth(registry, client_map)

    assert depth_a >= 0
    assert depth_b >= 0


def test_interface_node_compute_depth_missing_base():
    """Missing base interfaces are handled gracefully."""
    derived = InterfaceNode("Derived", "Derived.Client", ["MissingBase.Client"])

    registry = {"Derived": derived}
    client_map = {"Derived.Client": "Derived"}

    # Missing base is treated as external (depth 0), so derived has depth 1
    assert derived.compute_depth(registry, client_map) == 1


def test_sort_interfaces_empty():
    """Empty interface dict returns empty list."""
    assert _sort_interfaces_by_inheritance({}) == []


def test_sort_interfaces_single():
    """Single interface works correctly."""
    interfaces = {"Base": ("Base.Client", [])}
    result = _sort_interfaces_by_inheritance(interfaces)
    assert result == [("Base", "Base.Client")]


def test_sort_interfaces_hierarchy():
    """Multi-level hierarchy sorts correctly (most derived first)."""
    interfaces = {
        "Root": ("Root.Client", []),
        "Mid": ("Mid.Client", ["Root.Client"]),
        "Leaf": ("Leaf.Client", ["Mid.Client"]),
    }
    result = _sort_interfaces_by_inheritance(interfaces)

    # Most derived first, then middle, then root
    assert len(result) == 3
    assert result[0] == ("Leaf", "Leaf.Client")
    assert result[1] == ("Mid", "Mid.Client")
    assert result[2] == ("Root", "Root.Client")


def test_sort_interfaces_multiple_roots():
    """Multiple independent hierarchies sort correctly."""
    interfaces = {
        "RootA": ("RootA.Client", []),
        "RootB": ("RootB.Client", []),
        "DerivedA": ("DerivedA.Client", ["RootA.Client"]),
        "DerivedB": ("DerivedB.Client", ["RootB.Client"]),
    }
    result = _sort_interfaces_by_inheritance(interfaces)

    # Extract names for easier testing
    names = [name for name, _ in result]

    # Derived should come before roots
    assert names.index("DerivedA") < names.index("RootA")
    assert names.index("DerivedB") < names.index("RootB")


def test_sort_interfaces_diamond_inheritance():
    """Diamond inheritance pattern sorts correctly."""
    interfaces = {
        "Base": ("Base.Client", []),
        "Left": ("Left.Client", ["Base.Client"]),
        "Right": ("Right.Client", ["Base.Client"]),
        "Bottom": ("Bottom.Client", ["Left.Client", "Right.Client"]),
    }
    result = _sort_interfaces_by_inheritance(interfaces)

    names = [name for name, _ in result]

    # Bottom should be first (depth 2)
    assert names[0] == "Bottom"
    # Base should be last (depth 0)
    assert names[-1] == "Base"
    # Left and Right should be in middle (depth 1)
    assert "Left" in names[1:3]
    assert "Right" in names[1:3]


def test_sort_interfaces_stable_sort():
    """Interfaces with same depth are sorted alphabetically."""
    interfaces = {
        "Zebra": ("Zebra.Client", ["Base.Client"]),
        "Apple": ("Apple.Client", ["Base.Client"]),
        "Base": ("Base.Client", []),
        "Middle": ("Middle.Client", ["Base.Client"]),
    }
    result = _sort_interfaces_by_inheritance(interfaces)

    # Get same-depth interfaces (depth 1)
    depth1_names = [name for name, _ in result[:-1]]  # All except Base

    # Should be alphabetically sorted
    assert depth1_names == sorted(depth1_names)
