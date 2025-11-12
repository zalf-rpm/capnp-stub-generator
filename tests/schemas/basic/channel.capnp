@0xf0a0b1c2d3e4f501;

struct Msg {
    content @0 :Text;
    timestamp @1 :Int64;
}

interface Channel {
    interface Reader {
        read @0 () -> (msg :Msg);  # Returns a Msg struct, not just Data
        close @1 () -> ();
    }
    
    interface Writer {
        write @0 (msg :Msg) -> ();  # Takes a Msg struct
        close @1 () -> ();
    }
    
    getReader @0 () -> (reader :Reader);
    getWriter @1 () -> (writer :Writer);
}
