from _generated.zalfmas import climate_capnp


class ClimateDataImpl(climate_capnp.Service.Server):
    async def info(self, _context, **kwargs):
        # Return a tuple that pycapnp unpacks into _context.results
        return climate_capnp.Service.Server.InfoResult(
            "climate_data_001", "Climate Data Service", "Provides climate data services."
        )
