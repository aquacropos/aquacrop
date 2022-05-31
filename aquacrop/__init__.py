import os
import logging


from .scripts.checkIfPackageIsCompiled import compile_all_AOT_files


# Important: This code is necessary to check if the AOT files are compiled.
if os.getenv("DEVELOPMENT"):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logging.info("Running the simulation in development mode.")
else:
    compile_all_AOT_files()

from aquacrop.core import AquaCropModel
from aquacrop.entities.soil import Soil
from aquacrop.entities.crop import  Crop
from aquacrop.entities.inititalWaterContent import InitialWaterContent
from aquacrop.entities.irrigationManagement import IrrigationManagement
from aquacrop.entities.fieldManagement import FieldMngt
from aquacrop.entities.groundWater import  GroundWater
from aquacrop.utils.prepare_weather import prepare_weather
from aquacrop.utils.data import get_filepath