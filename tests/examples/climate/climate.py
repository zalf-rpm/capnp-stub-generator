from _generated_zalfmas import climate_capnp, common_capnp


class ClimateDataImpl(climate_capnp.Service.Server):
    async def info(self, **kwargs):
        return common_capnp.IdInformation.new_message(
            id="climate_data_001", name="Climate Data Service", description="Provides climate data services."
        )
