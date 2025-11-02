@0xabcdabcdabcdabcd;

# Mid complexity schema focusing on nested structs, enums, simple union, defaults,
# and list usage.

enum TopEnum {
  alpha @0;
  beta  @1;
  gamma @2;
}

struct MidFeatureContainer {
  id @0 :UInt32;
  name @1 :Text = "container";
  mode @2 :TopEnum = beta;

  struct Nested {
    flag @0 :Bool = true;
    count @1 :Int16 = 7;

    enum State {
      start @0;
      running @1;
      done @2;
    }

    state @2 :State = running;
  }

  nested @3 :Nested;
  nestedList @4 :List(Nested) = [(flag = false, count = 1, state = start)];

  choice @5! :union {
    none  @6 :Void;
    text  @7 :Text;
    nums  @8 :List(Int32) = [1,2,3];
  }

  enumList @9 :List(TopEnum) = [alpha, gamma];
  stateList @10 :List(Nested.State) = [start, running, done];
}
