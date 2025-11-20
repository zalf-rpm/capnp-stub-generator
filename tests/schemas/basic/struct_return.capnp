@0xabcd1234567890ab;

struct Nested {
    val @0 :Int32;
}

struct IdInformation {
    id @0 :Text;
    name @1 :Text;
    description @2 :Text;
    nested @3 :Nested;
}

interface Identifiable {
    info @0 () -> IdInformation;
    # Note: This is direct struct return, not (result :IdInformation)
}
