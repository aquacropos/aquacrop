import pandas as pd

import os
os.environ['DEVELOPMENT'] = 'True'

from aquacrop import (
    AquaCropModel,
    Soil,
    Crop,
    InitialWaterContent,
    IrrigationManagement,
)
from aquacrop.utils import prepare_weather, get_filepath


_sim_start = "1982/05/01"
_sim_end = "1983/10/30"

weather_file_path = get_filepath("champion_climate.txt")

_weather_data = prepare_weather(weather_file_path)

_sandy_loam = Soil(soil_type="SandyLoam")
_wheat = Crop("Maize", planting_date="05/01")
_initial_water_content = InitialWaterContent(value=["FC"])

irrigation = IrrigationManagement(irrigation_method=0)

model_os = AquaCropModel(
    sim_start_time=_sim_start,
    sim_end_time=_sim_end,
    weather_df=_weather_data,
    soil=_sandy_loam,
    crop=_wheat,
    initial_water_content=_initial_water_content,
    irrigation_management=irrigation,
)
# run model till termination
model_os.run_model(till_termination=True)

final_statistics = model_os.get_simulation_results().head(10)
yield_expected = 10.78
yield_returned = round(final_statistics["Dry yield (tonne/ha)"][0], 2)

print(yield_expected)
print(yield_returned)