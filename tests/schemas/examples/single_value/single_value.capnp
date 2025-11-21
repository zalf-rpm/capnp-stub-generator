@0x9823749823749823;

interface SingleValue {
  getBool @0 () -> (val: Bool);
  getInt @1 () -> (val: Int32);
  getFloat @2 () -> (val: Float64);
  getText @3 () -> (val: Text);
  getData @4 () -> (val: Data);
  getList @5 () -> (val: List(Int32));
  getStruct @6 () -> (val: MyStruct);
  getInterface @7 () -> (val: SingleValue);
  getAny @8 () -> (val: AnyPointer);
  getListStruct @9 () -> (val: List(MyStruct));
}

struct MyStruct {
  id @0 :Int32;
}
