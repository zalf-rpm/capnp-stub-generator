@0xaaaabbbbccccdddd;

# Advanced feature schema to exercise unions, groups, generics, anypointer, interfaces,
# versioning, constants referencing constants, name annotations, and complex nested lists.

using Dummy = import "dummy.capnp";

using Cxx = import "c++.capnp";

# Global constants (base + derived)
const baseInt :UInt32 = 1111;
const baseText :Text = "base";
const baseList :List(UInt16) = [1,2,3];
const derivedList :List(UInt32) = [Dummy.globalInt, 999];
const chainedStruct :Dummy.TestAllTypes = (int32Field = .baseInt, textField = .baseText);

# Generic struct with AnyPointer binding
struct GenericBox {
  value @0 :AnyPointer;
}

struct AdvancedContainer {
  id @0 :UInt64 = 42;
  label @1 :Text = "advanced";
  flags @2 :List(Bool) = [true, false, true];

  # Top-level unions (named)
  firstUnion @3! :union {
    a @4 :Text;
    b @5 :UInt32;
    c @6 :List(UInt8) = [1,2];
  }

  secondUnion @7! :union {
    x @8 :Dummy.TestEnum;
    y @9 :AdvancedContainer.Nested.Inner; # forward nested struct ref
    z @10 :List(Text) = ["x", "y"];
  }

  # Unnamed union interleaved with fields
  before @11 :Text;
  union {
    u @12 :UInt16;
    v @13 :UInt32;
  }
  after @14 :Text = "after";

  # Group with nested union and group inside the union
  complexGroup :group {
    head @15 :UInt8 = 7;
    union {
      g1 @16 :UInt32;
      g2 :group {
        deep @17 :Int32 = -123;
        union {
          deeper @18 :Bool;
          deepest @19 :Text;
        }
      }
    }
    tail @20 :Text = "tail";
  }

  struct Nested {
    note @0 :Text = "nested";
    struct Inner {
      value @0 :Int32 = 1;
    }
    listInner @1 :List(Inner) = [(value = 2),(value = 3)];
    listListInner @2 :List(List(Inner)) = [[(value = 4)],[(value = 5),(value = 6)]];
    enum InnerState {
      start @0;
      mid @1;
      end @2;
    }
    state @3 :InnerState = mid;
    stateList @4 :List(InnerState) = [start, end];
  }

  nested @21 :Nested;

  # Multi-dimensional primitive + struct lists
  ints2d @22 :List(List(Int32)) = [[1,2],[3],[4,5,6]];
  inners2d @23 :List(List(Nested.Inner)) = [[(value = 7)],[(value = 8),(value = 9)]];

  # Generic usage: a box of enum and a box of struct via brand binding
  enumBox @24 :GenericBox;
  innerBox @25 :GenericBox;

  # Version pair embedded
  oldVersion @26 :OldVersion;
  newVersion @27 :NewVersion = (new1 = 999, newText = "newer");

  # Interface reference
  iface @28 :TestIface;
}

# Versioned structs
struct OldVersion { old1 @0 :Int64; }
struct NewVersion { old1 @0 :Int64; new1 @1 :Int64 = 987; newText @2 :Text = "baz"; }

# Interface definition
interface TestIface {
  ping @0 (count :Int32) -> (ok :Bool);
  stats @1 () -> (value :Int64, label :Text);
}

# Name annotation stress
struct BadName $Cxx.name("BetterName") {
  union {
    badField @0 :Bool $Cxx.name("goodField");
    alt @1 :Text;
  }
  enum Oops $Cxx.name("RenamedOops") { first @0; second @1; third @2 $Cxx.name("neo"); }
  renamedEnumField @2 :Oops $Cxx.name("betterEnumField");
  struct Deep $Cxx.name("BetterDeep") {
    enum DeepEnum $Cxx.name("BetterDeepEnum") { alpha @0; beta @1; gamma @2 $Cxx.name("delta"); }
    val @0 :DeepEnum = beta;
  }
  nestedDeep @3 :Deep $Cxx.name("betterDeepField");
}
