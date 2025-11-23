@0x986b312981017e05;

struct TestGroupStruct {
  union {
    struct :group {
      field @0 :UInt32;
    }
    other @1 :Void;
  }
}

struct TestGroupEnum {
  union {
    enum :group {
      field @0 :UInt32;
    }
    other @1 :Void;
  }
}
