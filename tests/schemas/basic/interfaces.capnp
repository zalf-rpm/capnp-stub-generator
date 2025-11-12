@0xa1b2c3d4e5f60708;

interface Greeter {
  greet @0 (name :Text) -> (reply :Text);
  streamNumbers @1 (count :UInt32) -> (first :UInt32);
}

struct Holder {
  greeter @0 :Greeter;
  optionalGreeter @1 :Greeter;
}