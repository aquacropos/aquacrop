import sys
_=[sys.path.append(i) for i in ['.', '..']]
from aquacrop.core import *
from aquacrop.classes import *

def compile_func():
    wdf = prepare_weather(get_filepath('tunis_climate.txt'))
    wdf.Date.min(),wdf.Date.max()

    soil = SoilClass('ac_TunisLocal',CalcCN=0)
    crop = CropClass('Wheat',PlantingDate= '10/15',HarvestDate= '05/30' )
    iwc = InitWCClass('Num','Depth',[0.3,0.9],[0.3,0.15])
    model = AquaCropModel('1981/10/15','1982/05/31',wdf,soil,crop,InitWC=iwc)
    model.initialize()
    model.step(till_termination=True)
    return model
    
model = compile_func()



__version__ = "0.2"
