@0xbf602c4868dbb22f;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("mas::schema::fbp");

using Go = import "/capnp/go.capnp";
$Go.package("fbp");
$Go.import("github.com/zalf-rpm/mas-infrastructure/capnproto_schemas/gen/go/fbp");

using Persistent = import "persistence.capnp".Persistent;
using SturdyRef = import "persistence.capnp".SturdyRef;
using Common = import "common.capnp";
using Stoppable = import "service.capnp".Stoppable;

struct IP {
  # an FBP information packet

  struct KV {
    key @0 :Text;
    desc 	@1 :Text; # optional human readable info on what value is
    value   @2 :AnyPointer;  # would often be a Common.Value
  }
  attributes @0 :List(KV);
  # key value pair attributes attached to IP additional to main content

  enum Type {
    standard     @0;
    openBracket  @1;
    closeBracket @2;
  }
  type @2 :Type = standard;

  content @1 :AnyPointer;
  # main content of IP
}

struct IIP {
  content @0 :AnyPointer;
  # might often be a Common.Value or common.StructuredText
}

interface Channel(V) extends(Common.Identifiable, Persistent) {
  # a potentially buffered channel to transport values of type V

  enum CloseSemantics {
    fbp   @0; # close channel automatically if there are no writers anymore and buffer is empty = no upstream data
    no    @1; # keep channel open until close message received
  }

  struct Msg {
    union {
      value @0 :V;
      done  @1 :Void;   # done message, no more data will be sent (indicate upstream is done - but semantics up to user)
      noMsg @2 :Void;   # no message available, if readIfMsg is used
    }
  }

  struct StartupInfo {
    # information about the startup of a channel

    bufferSize      @0 :UInt64;
    # size of the buffer

    closeSemantics  @1 :CloseSemantics;
    # semantics of closing the channel

    channelSR       @2 :Text;
    # sturdy reference to the channel

    channel         @5 :Channel(V);
    # capability to started channel

    readerSRs       @3 :List(Text);
    # sturdy references to the readers

    readers         @6 :List(Reader);
    # list of caps to the created Readers

    writerSRs       @4 :List(Text);
    # sturdy references to the writers

    writers         @7 :List(Writer);
    # list of caps to the created Writers
  }

  interface Reader extends(Common.Identifiable, Persistent) $Cxx.name("ChanReader") {
    read          @0 () -> Msg;
    # read blocking until message is available

    readIfMsg     @2 () -> Msg;
    # read non blocking if there is a message available

    close         @1 ();
    # close this reading end of the channel
  }

  interface Writer extends(Common.Identifiable, Persistent) $Cxx.name("ChanWriter") {
    write           @0 Msg;
    # write blocking until message is written

    writeIfSpace    @2 Msg -> (success :Bool);
    # write non blocking if there is space in the buffer

    close           @1 ();
    # close this writing end of the channel
  }

  setBufferSize @0 (size :UInt64 = 1);
  # set buffer size of channel, lowest allowed value = 1, meaning basically no buffer

  reader        @1 () -> (r :Reader);
  # get just a reader

  writer        @2 () -> (w :Writer);
  # get just a writer

  endpoints     @3 () -> (r :Reader, w :Writer);
  # get both endpoints of channel

  setAutoCloseSemantics @4 (cs :CloseSemantics);
  # set semantics when to automatically close this channel

  close         @5 (waitForEmptyBuffer :Bool = true);
  # close this channel
  # wait for empty buffer or kill channel right away
}

interface StartChannelsService extends(Common.Identifiable) {
    # starting channels

    struct Params {
        name            @0 :Text;       # name of channel
        noOfChannels    @1 :UInt16 = 1; # how many channels to create
        noOfReaders     @2 :UInt16 = 1; # no of readers to create per channel
        noOfWriters     @3 :UInt16 = 1; # no of writers to create per channel
        readerSrts      @4 :List(Text); # fixed sturdy ref tokens per reader
        writerSrts      @5 :List(Text); # fixed sturdy ref tokens per writer
        bufferSize      @6 :UInt16 = 1; # how large is the buffer supposed to be
    }
    start @0 Params -> (startupInfos :List(Channel.StartupInfo), stop :Stoppable);
    # create one (or multiple with same properties) channel and return reader and writer sturdy refs to the channel(s)
}

struct PortInfos {
  # information for component to connect to in/out ports

  struct NameAndSR {
    name        @0 :Text;
    union {
        sr      @1 :Text;           # for single ports
        srs     @2 :List(Text);     # for array ports
    }
  }

  inPorts  @0 :List(NameAndSR);
  # reader sturdy refs for the IN ports

  outPorts @1 :List(NameAndSR);
  # writer sturdy refs for the OUT ports
}

struct Component {
    interface Runnable extends(Common.Identifiable) {
      # interface to run remote FBP component

      start @0 (portInfosReaderSr :Text, name :Text) -> (success :Bool);
      # start component with a sturdy ref to a reader of PortInfos
      # the component will use the port infos to connect to the channels
      # and given an optional nam

      stop  @1 () -> (success :Bool);
      # stop the component
    }

    enum ComponentType {
        standard    @0; # standard FBP component
        iip         @1; # initial information packet
        subflow     @2; # represents a subflow
    }

    struct Port {
        enum PortType {
            standard @0; # standard port
        }

        enum ContentType {
            structuredText @0;
        }

        name        @0 :Text; # port name

        contentType @1 :Text;
        # type of content, e.g. common.capnp:StructuredText or geo.capnp:LatLngCoord or Text

        type        @2 :PortType = standard; # port type
    }

    info          @0 :Common.IdInformation; # id, name and description of this FBP component
    type          @1 :ComponentType; # the type of FBP component
    inPorts       @2 :List(Port); # the components allowed input ports
    outPorts      @3 :List(Port); # the components allowed input ports

    run           @4 :Runnable; # if non null, interface to runtime instance of this component

    defaultConfig @5 :Text; # default configuration for component
}

#interface ComponentService extends(Common.Identifiable) {
#    # serving FBP components (meta)data and possibly capability to run a component somehow/somewhere
#
#    struct Entry {
#        categoryId  @0 :Text;
#        component   @1 :Component;
#    }
#
#    categories  @2 () -> (categories :List(Common.IdInformation));
#    # the categories the service offers
#
#    list        @0 () -> (entries :List(Entry));
#    # list all available components
#
#    component   @1 (id :Text) -> (comp :Component);
#    # get a component by it's id
#}
