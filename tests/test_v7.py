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
# CHANGE THESE PLOTS (COMBINED BAR AND COMBINED LINE, 2 total)
model._outputs.final_stats=model._outputs.final_stats.set_index('Harvest Date (YYYY/MM/DD)')
# model._outputs.final_stats=model._outputs.final_stats.reset_index()
final_stats_m=model._outputs.final_stats.melt(value_name='yield', value_vars=['Dry yield (tonne/ha)', 'Fresh yield (tonne/ha)'], var_name='yield type', ignore_index=False).reset_index()
print(final_stats_m.head())

sns.barplot(data=final_stats_m, x='Harvest Date (YYYY/MM/DD)', y='yield',hue='yield type', ax=ax[0])

model._outputs.crop_growth=model._outputs.crop_growth.set_index('time_step_counter')
crop_growth_m=model._outputs.crop_growth.melt(value_name='yield', value_vars=['DryYield', 'FreshYield'], var_name='yield type', ignore_index=False).reset_index()
print(crop_growth_m.head())

sns.lineplot(data=crop_growth_m, x='time_step_counter', y='yield',hue='yield type', ax=ax[1])

# sns.boxplot(data=pd.DataFrame(model._outputs.final_stats),x='Harvest Date (YYYY/MM/DD)',y='Dry yield (tonne/ha)',ax=ax[0,0])
# sns.boxplot(data=pd.DataFrame(model._outputs.final_stats),x='Harvest Date (YYYY/MM/DD)',y='Fresh yield (tonne/ha)',ax=ax[1,0])
# sns.boxplot(data=pd.DataFrame(model._outputs.crop_growth),x='time_step_counter',y='DryYield',ax=ax[0,1])
# sns.boxplot(data=pd.DataFrame(model._outputs.crop_growth),x='time_step_counter',y='FreshYield',ax=ax[1,1])

plt.show()