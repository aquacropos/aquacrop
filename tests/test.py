from aquacrop.classes import    *
from aquacrop.core import       *

# locate built in weather file
filepath=get_filepath('tunis_climate.txt')

weather_data = prepare_weather(filepath)

print(weather_data.head())
# ## Soil

sandy_loam = SoilClass(soilType='SandyLoam')
sandy_loam

crop = CropClass('Wheat',PlantingDate='10/01')

InitWC = InitWCClass(value=['FC'])

# combine into aquacrop model and specify start and end simulation date
model = AquaCropModel(SimStartTime=f'{1979}/10/01',
                      SimEndTime=f'{1985}/05/30',
                      wdf=weather_data,
                      Soil=sandy_loam,
                      Crop=crop,
                      InitWC=InitWC)


# initilize model
model.initialize()
# run model till termination
model.step(till_termination=True)

print(model.Outputs.Flux.head())
print(model.Outputs.Water.head())
print(model.Outputs.Growth.head())
print(model.Outputs.Final.head())