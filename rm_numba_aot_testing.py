#import os
#os.environ['DEVELOPMENT'] = 'True'
import sys
import seaborn as sns
import matplotlib.pyplot as plt
sys.setrecursionlimit(2000)
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
                    sep='\s+',
                    names=["year", "ppm"],
    )

model = AquaCropModel(sim_start_time=f'{1979}/10/15',
                      sim_end_time=f'{2001}/03/31',
                      weather_df=tunis_weather,
                      soil=tunis_soil,
                      crop=wheat,
                      irrigation_management=irr_mngt,
                      initial_water_content=wet_dry,
                      co2_concentration=CO2(co2_data=co2_data)
                      )
model.run_model(till_termination=True)
print(model.crop.Name)
water_flux=model.get_water_flux()
crop_growth=model.get_crop_growth()
final_stats = model._outputs.final_stats
water_flux.to_csv('../AquaCrop docs/water_flux.csv')
crop_growth.to_csv('../AquaCrop docs/crop_growth.csv')
print(final_stats)
sns.set_theme(style="whitegrid")  # Set a clean theme for the plots

# List of columns to plot
columns = ['canopy_cover', 'biomass', 'harvest_index', 'z_root']

# Create separate plots for each column
for col in columns:
    plt.figure(figsize=(6, 4))  # Create a new figure
    sns.lineplot(data=crop_growth, x='dap', y=col, color='blue')
    plt.xlabel('Days After Planting (dap)')
    plt.ylabel(col.replace('_', ' ').title())  # Format column name for the label
    plt.title(f'{col.replace("_", " ").title()} vs. DAP')
    plt.tight_layout()
    plt.show()  # Show the plot

