@0xbf602c4868dbb230;

# Simplified FBP schema to test the actual return type pattern

struct Msg {
    union {
        value @0 :Text;
        done  @1 :Void;
        noMsg @2 :Void;
    }
}

interface Channel {
    interface Reader {
        read @0 () -> Msg;
        # NOTE: This returns Msg directly, not (msg :Msg)
        # The return type IS Msg, not a result struct with a msg field
        
        close @1 ();
    }
    
    interface Writer {
        write @0 (msg :Msg);
        close @1 ();
    }
    
    reader @0 () -> (r :Reader);
    writer @1 () -> (w :Writer);
}
