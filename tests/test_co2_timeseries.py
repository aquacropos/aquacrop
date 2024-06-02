"""
Test exeptions in the model.
"""
import os
os.environ['DEVELOPMENT'] = 'True'
import unittest
import pandas as pd


from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, GroundWater, CO2
from aquacrop.utils import prepare_weather, get_filepath



class TestModelExceptions(unittest.TestCase):
    """
    Test of what happens if the model does not run.
    """

    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _co2_data = pd.DataFrame(
        {
            "year":[1979, 1980, 1981],
            "ppm":[336.84, 338.76, 340.12],
        }
    )
    _co2 = CO2(co2_data=_co2_data)
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
        co2_concentration=_co2,
    )
    _model_os.run_model(till_termination=True)
    def test_yield(self):
        """
        Test yield
        """
        yield_expected = 8.627
        yield_returned = round(
            self._model_os.get_simulation_results()["Dry yield (tonne/ha)"].mean(), 3
        )
        self.assertEqual(yield_expected, yield_returned)

if __name__ == "__main__":
    unittest.main()
