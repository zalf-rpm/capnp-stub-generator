@0xac57747d36fdd0b1;

struct Setup {
    runId                       @0  :Int64;
    sowingTime                  @1  :Text;
    harvestTime                 @2  :Text;
    cropId                      @3  :Text;
    simJson                     @4  :Text;
    cropJson                    @5  :Text;
    siteJson                    @6  :Text;
    startDate                   @7  :Text;
    endDate                     @8  :Text;
    groundwaterLevel            @9  :Bool;
    impenetrableLayer           @10 :Bool;
    elevation                   @11 :Bool;
    slope                       @12 :Bool;
    latitude                    @13 :Bool;
    landcover                   @14 :Bool;
    fertilization               @15 :Bool;
    nitrogenResponseOn          @16 :Bool;
    irrigation                  @17 :Bool;
    waterDeficitResponseOn      @18 :Bool;
    emergenceMoistureControlOn  @19 :Bool;
    emergenceFloodingControlOn  @20 :Bool;
    leafExtensionModifier       @21 :Bool;
    co2                         @22 :Float32;
    o3                          @23 :Float32;
    fieldConditionModifier      @24 :Float32;
    stageTemperatureSum         @25 :Text;
    useVernalisationFix         @26 :Bool;
    comment                     @27 :Text;
}
