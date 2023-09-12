import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
from aquacrop.utils import prepare_weather, get_filepath

filepath=get_filepath('tunis_climate.txt')

weather_data = prepare_weather(filepath)
weather_data

sandy_loam = Soil(soil_type='SandyLoam')
wheat = Crop('Wheat', planting_date='10/01')
InitWC = InitialWaterContent(value=['FC'])

# test custom initial water content:
customWC = InitialWaterContent(wc_type = 'Pct',
                               method = 'Layer',
                               depth_layer= [1],
                               value = [60])

# test scheduling with irri type 3

# combine into aquacrop model and specify start and end simulation date
model = AquaCropModel(sim_start_time=f'{1979}/10/01',
                      sim_end_time=f'{1985}/05/30',
                      weather_df=weather_data,
                      soil=sandy_loam,
                      crop=wheat,
                      initial_water_content=customWC)

# run model till termination
model.run_model(till_termination=True)

print(model._outputs.water_flux.head())
print(model._outputs.water_storage.head())
print(model._outputs.crop_growth.head())
print(model._outputs.final_stats.head())

# combine into aquacrop model and specify start and end simulation date
model_default = AquaCropModel(sim_start_time=f'{1979}/10/01',
                      sim_end_time=f'{1985}/05/30',
                      weather_df=weather_data,
                      soil=Soil('SandyLoam'),
                      crop=wheat,
                      initial_water_content=InitWC)

model_default.run_model(till_termination=True)


names=['Custom','Default']

#combine our two output files
dflist=[model._outputs.final_stats,
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


