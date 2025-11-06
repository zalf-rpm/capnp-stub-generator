
@0xbf602c4868dbb231;

struct IP {
    content @0 :AnyPointer;
}

interface Channel {
    struct Msg {
        union {
            value @0 :IP;
            done  @1 :Void;
        }
    }
    
    interface Reader {
        read        @0 () -> Msg;
        readIfMsg   @1 () -> Msg;
        close       @2 ();
    }
    
    interface Writer {
        write @0 (msg :Msg);
        close @1 ();
    }
    
    reader  @0 () -> (r :Reader);
    writer  @1 () -> (w :Writer);
}
