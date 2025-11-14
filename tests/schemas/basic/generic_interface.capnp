@0xa1b2c3d4e5f60709;

# Test schema for AnyPointer returns in interfaces

struct MyStruct {
  field @0 :Int32;
  name @1 :Text;
}

struct OtherStruct {
  value @0 :Float64;
}

interface GenericGetter {
  # Methods returning AnyPointer (generic types)
  get @0 () -> (result :AnyPointer);
  getById @1 (id :UInt32) -> (value :AnyPointer);
  getMultiple @2 () -> (first :AnyPointer, second :AnyPointer);
}

interface GenericSetter {
  set @0 (value :AnyPointer) -> (success :Bool);
}

struct Container {
  getter @0 :GenericGetter;
  setter @1 :GenericSetter;
}
