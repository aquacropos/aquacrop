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
wheat = Crop('Wheat', planting_date='10/01')

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

fig,ax=plt.subplots(2,2,figsize=(12,14))

sns.boxplot(data=pd.DataFrame(model._outputs.final_stats),x='Harvest Date (YYYY/MM/DD)',y='DryYield',ax=ax[0,0])
sns.boxplot(data=pd.DataFrame(model._outputs.final_stats),x='Harvest Date (YYYY/MM/DD)',y='FreshYield',ax=ax[1,0])
sns.boxplot(data=pd.DataFrame(model._outputs.growth_outputs),x='time_step_counter',y='DryYield',ax=ax[0,1])
sns.boxplot(data=pd.DataFrame(model._outputs.growth_outputs),x='time_step_counter',y='FreshYield',ax=ax[1,1])

plt.show()