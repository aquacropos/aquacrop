import os
os.environ['DEVELOPMENT'] = 'True'
import pandas as pd

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement, CO2
from aquacrop.utils import prepare_weather

# Tunis climate
tunis_weather = prepare_weather('C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/tunis_climate.txt')

# Local Tunis soil
tunis_soil = Soil(soil_type='ac_TunisLocal')

# crops
wheat = Crop('WheatGDD', planting_date='10/15')

# IWC
wet_dry = InitialWaterContent(wc_type='Num',
                              method='Depth',
                              depth_layer=[0.3,0.9],
                              value=[0.3,0.15])

# irr management
irr_mngt = IrrigationManagement(irrigation_method=0)

# CO2
co2_data = pd.read_csv(
                    "C:/Users/s10034cb/Dropbox (The University of Manchester)/Manchester Postdoc/aquacrop/aquacrop/data/MaunaLoaCO2.txt",
                    header=1,
                    delim_whitespace=True,
                    names=["year", "ppm"],
    )

model = AquaCropModel(sim_start_time=f'{1979}/10/15',
                      sim_end_time=f'{2002}/03/31',
                      weather_df=tunis_weather,
                      soil=tunis_soil,
                      crop=wheat,
                      irrigation_management=irr_mngt,
                      initial_water_content=wet_dry,
                      co2_concentration=CO2(co2_data=co2_data)
                      )
model.run_model(till_termination=True)

print(model._outputs.final_stats)