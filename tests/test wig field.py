import os
import sys
import pandas as pd

#sys.path.append('C:/Users/VNOPPENA.VITO/PycharmProjects/aquacropOriginal/aquacrop')
from aquacrop.classes import    *
from aquacrop.core import       *

#load file with climate data, yield data, soil data
filepath=get_filepath('C://Users//VNOPPENA//PycharmProjects//wig_aquacrop//tmp//yaIUPoAB3XGj4yrNUHGw//climate//climate.csv')
weatherdata=pd.read_csv(filepath, delimiter=r"\s+")
weatherdata_selectedV=weatherdata[["Day","Month","Year","MINIMUM_TEMPERATURE","MAXIMUM_TEMPERATURE","RAINFALL",'ET0']]
weather_data = prepare_weatherfromfile(weatherdata_selectedV)
print(weather_data)

#Soil for now just test on sandy loam
#CN: CN curve number in SOL file, REW: Readily evaporable water from top layer in SOL file
#Thickness=Thickness, thWP=WP/100
#thFC=FC/100,thS=Sat/100, Ksat=Ksat
#penetrability=default 100 #remark:CRa&CRb parameters from sol files not included, not sure if this has consequences
soil = SoilClass('custom',CN=72,REW=10)
soil.add_layer(thickness=4,thWP=0.069,
                 thFC=0.278,thS=0.438,Ksat=91,
                 penetrability=100)
soil

#Crop !! still need to be checked plantingdate should be adjusted according to information in wig
crop= CropClass('custom', PlantingDate='04/15', CropType=2, PlantMethod=0, CalendarType=1, SwitchGDD=0,
                       Emergence=28, MaxRooting=40, Senescence=85, Maturity=130, HIstart=51,
                       Flowering=-999, GDDmethod=3, YldForm=55, Tbase=2., Tupp=26.,
                       PolHeatStress=0, PolColdStress=0,Tmin_up=8, Tmin_lo=8,
                       TrColdStress=1, GDD_up=8, Zmin=0.3, Zmax=0.8, fshape_r=1.5, SxTopQ=0.07,
                       SxBotQ=0.018,
                       SeedSize=20, PlantPop=40000, CCx=0.9, CDC=0.055, CGC=0.16108, Kcb=1.1, fage=0.15, WP=18.5,
                       WPy=100,
                       fsink=0.75, HI0=85, dHI_pre=2., a_HI=0., b_HI=10., dHI0=5., Determinant=0, p_up1=0.3, p_up2=0.65,
                       p_up3=0.75,
                       p_up4=0.8, p_lo1=0.6, p_lo2=1., p_lo3=1., p_lo4=1., fshape_w1=3., fshape_w2=3., fshape_w3=3.,
                      fshape_w4=0., Aer=15, HIini=0.01)
print(crop)
InitWC = InitWCClass(value=['FC'])

model = AquaCropModel(SimStartTime=f'{2022}/03/01',
                          SimEndTime=f'{2022}/05/15',#need to adjust
                          wdf=weather_data,
                          Soil=soil,
                          Crop=crop,
                          InitWC=InitWC)
dataflux = []
datawater = []
datagrowth = []
datafinal = []

# initilize model
model.initialize()
# run model till termination
model.step(till_termination=True)
model.Outputs.Flux.head()
model.Outputs.Water.head()
model.Outputs.Growth.head()
model.Outputs.Final.head()
outdir= r'C://Users//VNOPPENA//aquacrop.0.2//aquacroptest'
os.makedirs(outdir, exist_ok=True)
outfile = os.path.join(outdir, '2017modelOutputsFlux.csv')
model.Outputs.Flux.to_csv(outfile)
outfile = os.path.join(outdir, '2017modelOutputsWater.csv')
model.Outputs.Water.to_csv(outfile)
outfile = os.path.join(outdir, '2017modelOutputsGrowth.csv')
model.Outputs.Growth.to_csv(outfile)
outfile = os.path.join(outdir, '2017modelOutputsFinal.csv')
model.Outputs.Final.to_csv(outfile)
