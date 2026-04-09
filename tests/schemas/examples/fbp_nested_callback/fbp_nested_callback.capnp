@0xbf602c4868dbb22f;

interface Channel {
  interface StatsCallback {
    # delivers some status information about this channel
    struct Stats {
      noOfWaitingWriters    @0 :UInt16;
      noOfWaitingReaders    @1 :UInt16;
      noOfIpsInQueue        @2 :UInt64;
      totalNoOfIpsReceived  @3 :UInt64;
      timestamp             @4 :Text;
      updateIntervalInMs    @5 :UInt32;
    }

    interface Unregister {
      unreg @0 () -> (success :Bool);
    }

    status @0 (stats :Stats);
  }

  registerStatsCallback @0 (
    callback :StatsCallback,
    updateIntervalInMs :UInt32,
  ) -> (unregisterCallback :StatsCallback.Unregister);
}
