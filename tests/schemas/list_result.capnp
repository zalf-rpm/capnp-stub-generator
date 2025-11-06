
@0xf0a0b1c2d3e4f502;

struct Item {
    name @0 :Text;
    value @1 :Int32;
}

interface ItemService {
    getItems @0 () -> (items :List(Item));
}
