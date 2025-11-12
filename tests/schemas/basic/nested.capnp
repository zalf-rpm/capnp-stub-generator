@0x96a2ff486aa76036;

struct Outer {
  id @0 :UInt32;
  name @1 :Text;

  struct Inner {
    flag @0 :Bool = true;
    value @1 :Int16 = 42;

    enum Kind {
      alpha @0;
      beta @1;
      gamma @2;
    }

    kind @2 :Kind = beta;
  }

  inner @2 :Inner;
  innerList @3 :List(Inner) = [(flag = false, value = 1, kind = alpha)];
}