import sys
if not '-m' in sys.argv:
    from .core import AquaCropModel
    from .entities.soil import Soil
    from .entities.crop import  Crop
    from .entities.inititalWaterContent import InitialWaterContent
    from .entities.irrigationManagement import IrrigationManagement
    from .entities.fieldManagement import FieldMngt
    from .entities.groundWater import  GroundWater
    from .entities.co2 import  CO2
