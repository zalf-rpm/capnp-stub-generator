@0xd2c0a4b7e1f35a68;

# A parameter named like a pycapnp struct reader member (`schema`) is shadowed by that member at runtime.
interface Registry {
  lookup @0 (key :Text, schema :Text) -> (found :Bool);
}
