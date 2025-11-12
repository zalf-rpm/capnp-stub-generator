@0x9e8f8c7d6b5a4231;

# Schema for testing runtime behavior of server methods

struct Info {
    name @0 :Text;
    value @1 :Int32;
}

struct Data {
    content @0 :Text;
    timestamp @1 :Int64;
}

interface TestService {
    # Method returning primitive
    getPrimitive @0 () -> (result :Int32);
    
    # Method returning struct
    getStruct @1 () -> (info :Info);
    
    # Method returning interface
    getInterface @2 () -> (service :SubService);
    
    # Method with multiple return fields
    getMultiple @3 () -> (count :Int32, data :Data);
    
    # Void method
    doNothing @4 ();
    
    interface SubService {
        getValue @0 () -> (value :Float64);
    }
}
