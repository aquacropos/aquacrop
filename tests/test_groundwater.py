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
sandy_loam = Soil(soil_type='SandyLoam')

# crops
wheat = Crop('Wheat', planting_date='10/01')

# IWC
InitWC = InitialWaterContent(value=['FC'])

# irr management
irr_mngt = IrrigationManagement(irrigation_method=0)

y_axis = 'Infl' # canopy_cover

# SINGLE MODEL TESTING
# model1 = AquaCropModel(sim_start_time=f'{1979}/10/01',
#                       sim_end_time=f'{1985}/05/30',
#                       weather_df=weather_data,
#                       soil=sandy_loam,
#                       crop=wheat,
#                       irrigation_management=irr_mngt,
#                       initial_water_content=InitWC)

# # run model till termination
# model1.run_model(till_termination=True)

# print(model1._outputs.water_storage)

# SINGLE MODEL SINGLE PLOT
# sns.boxplot(data=pd.DataFrame(model1._outputs.water_flux),x='time_step_counter',y='Infl')

# SINGLE MODEL MULTI-PLOT
# fig,ax=plt.subplots(2,2,figsize=(12,14))

# sns.boxplot(data=pd.DataFrame(model1._outputs.water_storage),x='time_step_counter',y='th1',ax=ax[0,0])
# sns.boxplot(data=pd.DataFrame(model1._outputs.water_storage),x='time_step_counter',y='th2',ax=ax[0,1])
# sns.boxplot(data=pd.DataFrame(model1._outputs.water_storage),x='time_step_counter',y='th3',ax=ax[1,0])
# sns.boxplot(data=pd.DataFrame(model1._outputs.water_storage),x='time_step_counter',y='th4',ax=ax[1,1])

# MULTIMODEL TESTING
# model1 = AquaCropModel(sim_start_time=f'{1979}/10/01',
#                       sim_end_time=f'{1985}/05/30',
#                       weather_df=weather_data,
#                       soil=sandy_loam,
#                       crop=wheat,
#                       irrigation_management=irr_mngt,
#                       initial_water_content=InitWC,
#                       groundwater=GroundWater(method="Constant", water_table='Y',
#                                               dates=[f'{1979}/10/01'], values = [2]))
# model1.run_model(till_termination=True)
model2 = AquaCropModel(sim_start_time=f'{1979}/10/01',
                      sim_end_time=f'{1985}/05/30',
                      weather_df=weather_data,
                      soil=sandy_loam,
                      crop=wheat,
                      irrigation_management=irr_mngt,
                      initial_water_content=InitWC,
                      groundwater=GroundWater(method="Variable", water_table='Y',
                                              dates=[f'{1979}/10/01', f'{1983}/04/30'], values = [0.5,2]))
model2.run_model(till_termination=True)

# MULTIMODEL 2 PLOT
fig,ax=plt.subplots(2,1,figsize=(12,14))

sns.boxplot(data=pd.DataFrame(model2._outputs.water_flux),x='time_step_counter',y='GwIn',ax=ax[0])
sns.boxplot(data=pd.DataFrame(model2._outputs.water_flux),x='time_step_counter',y='z_gw',ax=ax[1])

# MULTIMODEL 4 PLOT
# fig,ax=plt.subplots(2,2,figsize=(12,14))

# sns.boxplot(data=pd.DataFrame(model1._outputs.water_flux),x='time_step_counter',y='z_gw',ax=ax[0,0])
# sns.boxplot(data=pd.DataFrame(model2._outputs.water_flux),x='time_step_counter',y='z_gw',ax=ax[1,0])
# sns.boxplot(data=pd.DataFrame(model1._outputs.water_flux),x='time_step_counter',y='GwIn',ax=ax[0,1])
# sns.boxplot(data=pd.DataFrame(model2._outputs.water_flux),x='time_step_counter',y='GwIn',ax=ax[1,1])
