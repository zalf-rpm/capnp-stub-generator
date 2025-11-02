@0x9b1b6b6c6f9a4f7d;

struct SimplePrimitives {
  aBool @0 :Bool;
  anInt @1 :Int32;
  aLong @2 :Int64;
  aUInt @3 :UInt32;
  aFloat @4 :Float32;
  aDouble @5 :Float64;
  aText @6 :Text;
  aData @7 :Data;
}

struct PrimitiveLists {
  bools @0 :List(Bool);
  ints  @1 :List(Int32);
  texts @2 :List(Text);
  datas @3 :List(Data);
}