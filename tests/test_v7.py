import os
os.environ['DEVELOPMENT'] = 'True'
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement, GroundWater
from aquacrop.utils import prepare_weather, get_filepath

filepath=get_filepath('tunis_climate.txt')
weather_data = prepare_weather(filepath)

# soil
sandy_loam = Soil(soil_type='SiltLoam')

# crops
wheat = Crop('Wheat', planting_date='10/01', YldWC=30)

# IWC
InitWC = InitialWaterContent(value=['FC'])

# irr management
irr_mngt = IrrigationManagement(irrigation_method=0)

model = AquaCropModel(sim_start_time=f'{1979}/10/01',
                      sim_end_time=f'{1981}/05/30',
                      weather_df=weather_data,
                      soil=sandy_loam,
                      crop=wheat,
                      irrigation_management=irr_mngt,
                      initial_water_content=InitWC,
                      )
model.run_model(till_termination=True)

fig,ax=plt.subplots(2,1,figsize=(12,14))


# YIELD POTENTIAL TESTS
model._outputs.final_stats=model._outputs.final_stats.set_index('Harvest Date (YYYY/MM/DD)')
final_stats_m=model._outputs.final_stats.melt(value_name='yield', value_vars=['Yield potential (tonne/ha)', 'Dry yield (tonne/ha)'], var_name='yield type', ignore_index=False).reset_index()

sns.barplot(data=final_stats_m, x='Harvest Date (YYYY/MM/DD)', y='yield',hue='yield type', ax=ax[0])

model._outputs.crop_growth=model._outputs.crop_growth.set_index('time_step_counter')
crop_growth_m=model._outputs.crop_growth.melt(value_name='yield', value_vars=['YieldPot', 'DryYield'], var_name='yield type', ignore_index=False).reset_index()

sns.scatterplot(data=crop_growth_m, x='time_step_counter', y='yield',hue='yield type', ax=ax[1])

# FRESH/DRY YIELD TESTS
# model._outputs.final_stats=model._outputs.final_stats.set_index('Harvest Date (YYYY/MM/DD)')
# final_stats_m=model._outputs.final_stats.melt(value_name='yield', value_vars=['Dry yield (tonne/ha)', 'Fresh yield (tonne/ha)'], var_name='yield type', ignore_index=False).reset_index()

# sns.barplot(data=final_stats_m, x='Harvest Date (YYYY/MM/DD)', y='yield',hue='yield type', ax=ax[0])

# model._outputs.crop_growth=model._outputs.crop_growth.set_index('time_step_counter')
# crop_growth_m=model._outputs.crop_growth.melt(value_name='yield', value_vars=['DryYield', 'FreshYield'], var_name='yield type', ignore_index=False).reset_index()

# sns.lineplot(data=crop_growth_m, x='time_step_counter', y='yield',hue='yield type', ax=ax[1])

plt.show()