@0x9876543210abcdf1;

interface Bag {
  # A simple capability that holds a value
  getValue @0 () -> (value :Text);
  setValue @1 (value :Text) -> ();
}

interface Restorer {
  # restore a capability from a sturdy ref

  struct RestoreParams {
    localRef @0 :Text;
  }

  restore @0 RestoreParams -> (cap :Capability);
  # restore from the localRef in a transient sturdy ref as live capability

  getAnyTester @1 () -> (tester :AnyTester);
}

interface AnyTester {
  getAnyStruct @0 () -> (s :AnyStruct);
  getAnyList @1 () -> (l :AnyList);
  getAnyPointer @2 () -> (p :AnyPointer);
}
