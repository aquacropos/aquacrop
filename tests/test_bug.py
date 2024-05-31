"""
This test is for bug testing
"""
import os
os.environ['DEVELOPMENT'] = 'True'
import unittest

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, GroundWater
from aquacrop.utils import prepare_weather, get_filepath




class TestModelExceptions(unittest.TestCase):
    """
    Test of what happens if the model does not run.
    """

    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _weather_data["Precipitation"] = (
        _weather_data["Precipitation"] / 10
    )  # too much rain for ground water effect in the original

    _sandy_loam = Soil(soil_type="SandyLoam")
    _wheat = Crop("Wheat", planting_date="10/01")
    _initial_water_content = InitialWaterContent(value=["FC"])
    _model_os = AquaCropModel(
        sim_start_time=f"{1979}/10/01",
        sim_end_time=f"{1981}/05/30",
        weather_df=_weather_data,
        soil=_sandy_loam,
        crop=_wheat,
        initial_water_content=_initial_water_content,
        groundwater=GroundWater(
            water_table="Y", dates=[f"{1979}/10/01"], values=[2.66]
        ),
    )
    _model_os.run_model(till_termination=True)

    def test_anything(self):
        """
        Test any variable
        """
        pass


if __name__ == "__main__":
    unittest.main()
