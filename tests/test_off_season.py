
import os
os.environ['DEVELOPMENT'] = 'True'
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement, FieldMngt
from aquacrop.utils import prepare_weather, get_filepath

filepath=get_filepath('champion_climate.txt')

weather_data = prepare_weather(filepath)

# soil
sandy_loam = Soil(soil_type='SandyLoam')

# crops
wheat = Crop('Maize', planting_date='10/01')

# IWC
InitWC = InitialWaterContent(value=['FC'])

# irr management
irr_mngt = IrrigationManagement(irrigation_method=0)

# fallow field management
fal_fld = FieldMngt(mulches=True,
                    mulch_pct=100,
                    bunds=True,
                    bund_water=10,
                    z_bund=1)

y_axis = 'Wr' # canopy_cover, surface_storage, Runoff, Es, Infl

# combine into aquacrop model and specify start and end simulation date
model1 = AquaCropModel(sim_start_time=f'{1982}/10/01',
                      sim_end_time=f'{1985}/05/30',
                      weather_df=weather_data,
                      soil=sandy_loam,
                      crop=wheat,
                      irrigation_management=irr_mngt,
                      initial_water_content=InitWC,
                      off_season=True)

# run model till termination
model1.run_model(till_termination=True)

# print(model1._outputs.crop_growth)

model2 = AquaCropModel(sim_start_time=f'{1982}/10/01',
                      sim_end_time=f'{1985}/05/30',
                      weather_df=weather_data,
                      soil=sandy_loam,
                      crop=wheat,
                      irrigation_management=irr_mngt,
                      initial_water_content=InitWC,
                      fallow_field_management=fal_fld,
                      off_season=True)

model2.run_model(till_termination=True)

# fig,ax=plt.subplots(2,1,figsize=(12,14))

# sns.scatterplot(data=pd.DataFrame(model1._outputs.water_flux),x='time_step_counter',y=y_axis, ax=ax[0])
# sns.scatterplot(data=pd.DataFrame(model2._outputs.water_flux),x='time_step_counter',y=y_axis, ax=ax[1])
model_out=pd.DataFrame(model2._outputs.water_flux)

# Test all outputs
all_water_flux = [
                "Wr",
                "z_gw",
                "surface_storage",
                "IrrDay",
                "Infl",
                "Runoff",
                "DeepPerc",
                "CR",
                "GwIn",
                "Es",
                "EsPot",
                "Tr",
                "TrPot",
            ]

for y_var in all_water_flux:
    plt.figure()
    plot=sns.scatterplot(data=model_out,
                        x='time_step_counter',
                        y=y_var)
    fig=plot.get_figure()
    fig.savefig(f'../plots/off_season/{y_var}_2.png')
