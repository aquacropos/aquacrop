
import os
os.environ['DEVELOPMENT'] = 'True'
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath

filepath=get_filepath('tunis_climate.txt')

weather_data = prepare_weather(filepath)
weather_data

# soils
tunis = Soil(soil_type='ac_TunisLocal')
sandy_loam = Soil(soil_type='SandyLoam')
soil_custom1 = Soil(soil_type='custom',cn=46,rew=7)
soil_custom1.add_layer( thickness=.1*12,thWP=0.24,
                        thFC=0.40,thS=0.50,Ksat=155,
                        penetrability=100)
soil_custom2 = Soil(soil_type='custom',cn=46,rew=7)
soil_custom2.add_layer( thickness=.1*6,thWP=0.24,
                        thFC=0.40,thS=0.50,Ksat=155,
                        penetrability=100)
soil_custom2.add_layer(thickness=.1*6,thWP=0.24,
                        thFC=0.40,thS=0.50,Ksat=155,
                        penetrability=100)

# crops
wheat = Crop('Wheat', planting_date='10/01')
maize = Crop('Maize', planting_date='05/01')


InitWC = InitialWaterContent(value=['FC'])

# test custom initial water content:
customWC = InitialWaterContent(wc_type = 'Pct',
                               method = 'Layer',
                               depth_layer= [1],
                               value = [60])

# default wc
defaultWC = InitialWaterContent(wc_type = 'Prop',
                               method = 'Layer',
                               depth_layer= [1],
                               value = ['FC'])

# multi WC
multiWC = InitialWaterContent(wc_type = 'Prop',
                              method = 'Layer',
                              depth_layer= [1,2],
                              value = ['FC', 'FC'])

# create irr management
irr_mngt = IrrigationManagement(irrigation_method=0)

# combine into aquacrop model and specify start and end simulation date
model_custom = AquaCropModel(sim_start_time=f'{1979}/10/01',
                      sim_end_time=f'{1985}/05/30',
                      weather_df=weather_data,
                      soil=soil_custom2,
                      crop=maize,
                      irrigation_management=irr_mngt,
                      initial_water_content=InitialWaterContent(value=['FC']))

# run model till termination
model_custom.run_model(till_termination=True)

print('Custom model:')
print(model_custom._outputs.water_flux.head())
print(model_custom._outputs.water_storage.head())
print(model_custom._outputs.crop_growth.head())
print(model_custom._outputs.final_stats.head())

# combine into aquacrop model and specify start and end simulation date
model_default = AquaCropModel(sim_start_time=f'{1979}/10/01',
                      sim_end_time=f'{1985}/05/30',
                      weather_df=weather_data,
                      soil=soil_custom1,
                      crop=maize,
                      irrigation_management=IrrigationManagement(irrigation_method=0),
                      initial_water_content=defaultWC)

model_default.run_model(till_termination=True)

print('Default model:')
print(model_default._outputs.water_flux.head())
print(model_default._outputs.water_storage.head())
print(model_default._outputs.crop_growth.head())
print(model_default._outputs.final_stats.head())

names=['Custom','Default']

#combine our two output files
dflist=[model_custom._outputs.final_stats,
        model_default._outputs.final_stats] 

outlist=[]
for i in range(len(dflist)): # go through our two output files
    temp = pd.DataFrame(dflist[i]['Yield (tonne/ha)']) # extract the seasonal yield data
    temp['label']=names[i] # add the soil type label
    outlist.append(temp) # save processed results

# combine results
all_outputs = pd.concat(outlist,axis=0)

#create figure
fig,ax=plt.subplots(1,1,figsize=(10,7),)

# create box plot
sns.boxplot(data=all_outputs,x='label',y='Yield (tonne/ha)',ax=ax,)

# labels and font sizes
ax.tick_params(labelsize=15)
ax.set_xlabel(' ')
ax.set_ylabel('Yield (tonne/ha)',fontsize=18)

