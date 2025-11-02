@0xabcddcbaabcddcba;

# Low complexity schema: single struct, enum, lists of primitives.

enum Color {
  red @0;
  green @1;
  blue @2;
}

struct BasicLow {
  id @0 :UInt32;
  name @1 :Text;
  isActive @2 :Bool;
  favoriteColor @3 :Color;
  scores @4 :List(Int32);
  tags @5 :List(Text);
}
