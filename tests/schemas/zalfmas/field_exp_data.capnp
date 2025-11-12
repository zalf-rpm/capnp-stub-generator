@0xe14a1fcaee034d63;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("mas::schema::data");

using Go = import "/capnp/go.capnp";
$Go.package("data");
$Go.import("github.com/zalf-rpm/mas-infrastructure/capnproto_schemas/gen/go/data");

using TimeSeries = import "/climate.capnp".TimeSeries;
using Date = import "/date.capnp".Date;
using SoilProfile = import "/soil.capnp".Profile;

struct WeatherStation {
  id                                      @0  :Text;            # WST_ID [text] weather station code
  name                                    @1  :Text;            # WST_NAME [text] weather station name
  instituteName                           @2  :Text;            # INST_NAME [text] institute name
  site                                    @3  :Text;            # WST_SITE [text] weather station site
  country                                 @4  :Text;            # WST_LOC_1 [text] weather station location country
  location2ndLevel                        @5  :Text;            # WST_LOC_2 [text] weather station location 2nd level
  location3rdLevel                        @6  :Text;            # WST_LOC_3 [text] weather station location 3rd level
  latitudeInDecDeg                        @7  :Float64 = -9999; # WST_LAT [decimal degrees] weather station latitude
  longitudeInDecDeg                       @8  :Float64 = -9999; # WST_LONG [decimal degrees] weather station longitude
  elevationM                              @9  :Float64 = -9999; # WST_ELEV [m] weather station elevation
  yearlyAvgTempInDegC                     @10 :Float64 = -9999; # TAV [°C] temperature avg year
  amplitudeOfMonthlyAvgTempsInDegC        @11 :Float64 = -9999; # TAMP [°C] temperature amplitude month avg
  tempSensorHeightInM                     @12 :Float64 = -1;    # REFHT [m] reference height weather measurement
  refHeightWeatherMeasurementInM          @13 :Float64 = -1;    # WNDHT [m] reference height windspeed measurement
  refHeightWindspeedMeasurementInM        @14 :Float64 = -1;    # TEMHT [m] temperature sensor height
  annualCO2ConcentrationInPPM             @15 :Float64 = -1;    # CO2Y [ppm] CO2 concentration annual
  notes                                   @16 :Text;            # WST_NOTES [text] weather notes
}

struct SoilMetadata {
  id                            @0  :Text;          # SOIL_ID [text] soil profile id
  name                          @1  :Text;          # SOIL_NAME [text] name of soil
  source                        @2  :Text;          # SL_SOURCE [text] soil source
  depthInCM                     @3  :Int16 = -1;    # SLDP [cm] soil depth
  obstableDepthInCM             @4  :Int16 = -1;    # SLOBS [cm] soil obstacle depth
  depthOfTopsoilInCM            @5  :Int16 = -1;    # SLTOP [cm] depth of topsoil
  drainageRatePerDay            @6  :Float64 = -1;  # SADR [1/day] drainage rate per day
  runoffCureNoSCS               @7  :Float64 = -1;  # SLRO [number] runoff curve no SCS
  soilAvailableWaterContentInCM @8  :Float64 = -1;  # SAWC [cm] soil available water content
  surfaceStoneCoverAsFraction   @9  :Float64 = -1;  # FLST [m2/m2] surface stones (cover)
  soilAlbedo                    @10 :Float64 = -1;  # SALB [] soil albedo
  soilEvaporationLimitInMM      @11 :Float64 = -1;  # SLU1 [mm] soil evaporation limit
  mineralizationFactor          @12 :Float64 = -1;  # SLNF [number] mineralization factor
  soilFertilityOnFoto           @13 :Float64 = -1;  # SLPF [number] soil fertility on foto
  soilClassificationSystem      @14 :Text;          # SL_SYSTEM [text] soil classification system
  soilTexture                   @15 :Text;          # SLTX [code] soil texture
  classification                @16 :Text;          # CLASSIFICATION [text] soil classification
  notes                         @17 :Text;          # SL_NOTES [text] soil notes
  profile                       @18 :SoilProfile;
}

struct Field {
  id                            @0  :Text;            # FIELD_ID [text] field id
  name                          @1  :Text;            # FL_NAME [text] field name
  latitudeInDecDeg              @2  :Float64 = -9999; # FL_LAT[degree] field latitude
  longitudeInDecDeg             @3  :Float64 = -9999; # FL_LONG[degree] field longitude
  elevationInM                  @4  :Float64 = -9999; # FLELE [m] field elevation
  slopeDegreeInDeg              @5  :Float64 = -1;    # FLSL [degree angle] field slope
  drainageType                  @6  :Text;            # FL_DRNTYPE [code] drainage type
  distanceToWeatherStationInKM  @7  :Float64 = -1;    # WST_DIST [km] weather station distance
  country                       @8  :Text;            # FL_LOC_1 [text] field country
  subCountry                    @9  :Text;            # FL_LOC_2 [text] field sub country
  subSubCountry                 @10 :Text;            # FL_LOC_3 [text] field sub sub country
  notes                         @11 :Text;            # FL_NOTES [text] field notes
}

struct ExperimentDescription {
  id                              @0  :Text;            # EID [text] experiment id
  suiteId                         @1  :Text;            # SUITEID [text] suite id
  name                            @2  :Text;            # EXNAME [text] name of experiment
  researchInfrastructureName      @3  :Text;            # INFRANAME [text] research infrastructure name
  instituteName                   @4  :Text;            # INNAME [text] institute name
  researchUnitName                @5  :Text;            # RUNAME [text] research unit name
  experimentalFacilityName        @6  :Text;            # FANAME [text] experimental facility name
  siteName                        @7  :Text;            # SITE_NAME [text] site name
  siteType                        @8  :Text;            # SITE_TYPE [code] site type
  mainExperimentFactor            @9  :Text;            # MAIN_FACTOR [text] main experimental factor
  experimentalFactorCombinations  @10 :Text;            # FACTORS [text] experimental factor combinations
  experimentType                  @11 :Text;            # EXPER_TYPE [code] experiment type
  managementType                  @12 :Text;            # MGMT_TYPE [code] management type
  croppingSystem                  @13 :Text;            # CR_SYSTEM [text] cropping system
  plantingYear                    @14 :Int16 = -1;      # PLYR [year] planting year
  harvestOperationYear            @15 :Int16 = -1;      # HAYR [year] harvest operation year
  notes                           @16 :Text;            # EXP_NOTES [text] experiment notes
  treatments                      @17 :List(Treatment);
}

struct Treatment {
  id                              @0  :Text;            # TREAT_ID [text] treatment id
  experimentId                    @25 :Text;            # EID [text] experiment id
  fieldId                         @26  :Text;           # FIELD_ID [text] field id
  field                           @1  :Field;
  weatherStationId                @27 :Text;           # WST_ID [text] weather station code
  weatherStation                  @2  :WeatherStation;
  weatherStationDataset           @28 :Text;           # WST_DATASET [text] weather file
  weatherStationTimeseries        @3  :TimeSeries;
  name                            @4  :Text;            # TRT_NAME [text] treatment name
  simulationStartDate             @5  :Date;            # SDAT [date] simulation start date
  simulationEndDate               @6  :Date;            # ENDAT [date] simulation end date
  irrigationApplied               @7  :Bool;            # IRRIG [code] irrigatin applied
  fertilizerApplied               @8  :Bool;            # FERTILIZER [code] fertilizer applied
  irrigationLevel                 @9  :Int8 = -1;       # IR [number] irrigation level
  fertilizerLevel                 @10 :Int8 = -1;       # FE [number] fertilizer level
  plantingDateLevel               @11 :Int8 = -1;       # PD [number] planting date level
  environmentalModificationsLevel @12 :Int8 = -1;       # EM [number] environmental modifications level
  initialConditionsLevel          @13 :Int8 = -1;       # IC [number] initial conditions level
  plantingDensityLevel            @14 :Int8 = -1;       # PL [number] planting density level
  numberOfBlocksOrReplicates      @15 :Int8 = -1;       # REP_NO [number] number of replicates
  notes                           @16 :Text;            # TR_NOTES [text] treatment comment
  plots                           @17 :List(Plot);
  residue                         @18 :Residue;
  initialConditionsLayers         @19 :List(InitialConditionsLayer);
  plantingEvents                  @20 :List(PlantingEvent);
  harvestEvents                   @21 :List(HarvestEvent);
  irrigationEvents                @22 :List(IrrigationEvent);
  fertilizerEvents                @23 :List(FertilizerEvent);
  environmentModifications        @24 :List(EnvironmentModification);
}

struct Cultivar {
  id                  @0  :Text;        # CUL_ID [text] cultivar identifier
  name                @1  :Text;        # CUL_NAME [text] cultivar name
  accessionId         @2  :Text;        # ACCES_ID [number] accession id
  accessionLocation   @3  :Text;        # ACCES_LOC [text] accession location
  cropIdentifierICASA @4  :Text;        # CRID [code] crop identifier ICASA
  seedLot             @5  :Text;        # SEED_LOT [text] seed lot
  breedingProgram     @6  :Text;        # BREED_PRG [text] breeding program
  originalName        @7  :Text;        # CUL_ORIG [text] cultivar name orig
  releaseYear         @8  :Int16 = -1;  # CUL_YEAR [year] cultivar release year
  synonym             @9  :Text;        # CUL_SYN [text] cultivar synonym
  notes               @10 :Text;        # CUL_NOTES [text] cultivar notes
}

struct Plot {
  id              @0  :Text;      # PLTID [text] plot id
  experimentId    @10 :Text;      # EID [text] experiment id
  treatmentId     @11 :Text;      # TREAT_ID [text] treatment id
  cultivarId      @12 :Text;      # CUL_ID [text] cultivar identifier
  cultivar        @1  :Cultivar;
  soilId          @13  :Text;      # SOIL_ID [text] soil profile id
  soil            @2  :SoilMetadata;
  blockNumber     @3  :Int8 = -1; # BLOCK [number] block number
  plotNumber      @4  :Int8 = -1; # PLOTno [number] plot number
  replicateNumber @5  :Int8 = -1; # RP [number] replicate number
  rowNumber       @6  :Int8 = -1; # PLOT_X [number] plot row number
  columnNumber    @7  :Int8 = -1; # PLOT_Y [number] plot column number
  harvestMethod   @8  :Text;      # PLTHM [code] harvest method plot
  notes           @9  :Text;      # PLOT_NOTES [text] plot notes
}

struct InitialConditionsLayer {
  experimentId            @9  :Text;          # EID [text] experiment id
  treatmentId             @10 :Text;          # TREAT_ID [text] treatment id
  date                    @0  :Date;          # ICDAT [date] initial conditions date
  soilLayerTopDepthInCM   @1  :Int16 = -1;    # ICTL [cm] soil layer top depth
  soilLayerBaseDepthInCM  @2  :Int16 = -1;    # ICBL [cm] soil layer base depth
  waterConcentration      @3  :Float64 = -1;  # ICH2O [mm3/mm3] initial water concentration by layer
  totalNInKGperHA         @4  :Float64 = -1;  # ICN_TOT [kg[N]/ha] initial Ntot layer
  massNH4InKGperHA        @5  :Float64 = -1;  # ICNH4M [kg[N]/ha] initial NH4 mass layer
  massNO3InKGperHA        @6  :Float64 = -1;  # ICNO3M [kg[N]/ha] initial NO3 mass layer
  concNH4InPPM            @7  :Float64 = -1;  # ICNH4 [ppm] initial NH4 concentration layer
  concNO3InPPM            @8  :Float64 = -1;  # ICNO3 [ppm] initial NO3 concentration layer
}

struct PlantingEvent {
  experimentId                                @10 :Text;            # EID [text] experiment id
  treatmentId                                 @11 :Text;            # TREAT_ID [text] treatment id
  plantingDistribution                        @0  :Text;            # PLDS [code] planting distribution
  rowSpacingInCM                              @1  :Float64 = -1;    # PLRS [cm] row spacing
  rowDirectionInArcDeg                        @2  :Float64 = -9999; # PLRD [arc degrees] row direction
  plantingDepthInMM                           @3  :Int16 = -1;      # PLDP [mm] planting depth
  plotLayout                                  @4  :Text;            # PLLAY [text] plot layout
  plantingDate                                @5  :Date;            # PDATE [date] planting date
  plantPopulationAtPlantingInNoPerM2          @6  :Int16 = -1;      # PLPOP [number/m2] plant population at planting
  averageEmergenceDate                        @7  :Date;            # APLDAE [date] average emergence date
  averagePlantPopulationAtEmergenceInNoPerM2  @8  :Int16 = -1;      # APLPOE [number/m2] average plant population at emergence
  notes                                       @9  :Text;            # PL_NOTES [text] planting notes
}

struct HarvestEvent {
  experimentId  @5 :Text;         # EID[text] experiment id
  treatmentId   @6 :Text;         # TREAT_ID [text] tre atment id
  date          @0 :Date;         # HADAT [date] harvest operations date
  harvestMethod @1 :Text;         # HARM [code] harvest method
  harvestArea   @2 :Float64 = -1; # HAREA [cm2] harvest area
  notes         @3 :Text;         # HA_NOTES [text] harvest notes
  comments      @4 :Text;         # HA_COMMENTS[text] harvest comments
}

struct IrrigationEvent {
  experimentId              @6 :Text; # EID [text] experiment id
  treatmentId               @7 :Text; # TREAT_ID [text] treatment id
  date                      @0 :Date; # IDATE [date] irrigation date
  operation                 @1 :Text; # IROP [code] irrigation operation
  applicationDepth          @2 :Int16 = -9999; # IRADP [cm] irrigation application depth
  amount                    @3 :Int16 = -1; # IRVAL [mm] irrigation amount
  waterNConcentrationInPerc @4 :Float64 = -1; # IRNPC [%] irrigation H2O N concentration
  notes                     @5 :Text; # IR_NOTES [text] irrigation notes
}

struct FertilizerEvent {
  experimentId          @8 :Text;       # EID [text] experiment id
  treatmentId           @9 :Text;       # TREAT_ID [text] treatment id
  date                  @0 :Date;       # FEDATE [date] fertilization date
  applicationMethod     @1 :Text;       # FEACD [code] fertilizer application method
  applicationDepthInCM  @2 :Int16 = -1; # FEDEP [cm] application depth fertilizer
  material              @3 :Text;       # FECD [code] fertilizer material
  appliedNInKGNPerHA    @4 :Int16 = -1; # FEAMN [kg[N]/ha] N in applied fertilizer
  appliedNO3InKGNperHA  @5 :Int16 = -1; # FENO3 [kg[N]/ha] NO3 in applied fertilizer
  appliedNH4InKGNperHA  @6 :Int16 = -1; # FENH4 [kg[N]/ha] NH4 in applied fertilizer
  notes                 @7 :Text;       # FE_NOTES [text] fertilizer notes
}

struct Residue {
  experimentId                    @7 :Text;         # EID [text] experiment id
  treatmentId                     @8 :Text;         # TREAT_ID [text] treatment id
  initialMeasureDate              @0 :Date;         # ICRDAT [date] initial residue measure date
  incorporationDepth              @1 :Int16 = -1;   # ICRDP [cm] residue incorporation depth
  percentIncorporated             @2 :Float64 = -1; # ICRIP [%] residue incorporated
  prevCropCode                    @3 :Text;         # ICPCR [code] residue nature prev crop
  aboveGroundWeight               @4 :Float64 = -1; # ICRAG [kg[dry matter]/ha] residue above-ground weight
  aboveGroundNConcentrationInPerc @5 :Float64 = -1; # ICRN [%] residue above-ground N concentration
  rootWeightPreviousCrop          @6 :Float64 = -1; # ICRT [kg[dry matter]/ha] root weight previous crop
}

struct EnvironmentModification {
  experimentId  @4 :Text;       # EID [text] experiment id
  treatmentId   @5 :Text;       # TREAT_ID [text] treatment id
  date          @0 :Date;       # EMDATE [date] environment modification date
  codeCO2       @1 :Text;       # ECCO2 [code] environment modification code CO2
  valueCO2      @2 :Int16 = -1; # EMCO2 [ppm] environment modification CO2
  notes         @3 :Text;       # EM_NOTES [text] environment modification notes
}

