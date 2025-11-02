@0xe4c2de84ad1e85cf;

using Base = import "import_base.capnp";

struct UsesImport {
  shared @0 :Base.Shared;
  others @1 :List(Base.Shared);
}