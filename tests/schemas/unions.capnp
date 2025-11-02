@0xbc9a76ff34b05179;

struct WithNamedUnion {
  id @0 :UInt16;

  choice @1! :union {
    none  @2 :Void;
    text  @3 :Text;
    nums  @4 :List(Int32);
  }
}

struct WithUnnamedUnion {
  before @0 :Text;

  union {
    small @1 :UInt8;
    big   @2 :UInt64;
  }

  after @3 :Text;
}

struct UnionDefaults {
  u @0 :WithNamedUnion = (id = 1, choice = (text = "hello"));
}