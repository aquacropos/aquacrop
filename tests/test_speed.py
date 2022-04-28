import unittest
import time

from aquacrop.utils.prepare_weather import prepare_weather
from aquacrop.utils.data import get_filepath
from aquacrop.core import AquaCropModel
from aquacrop.entities.soil import SoilClass
from aquacrop.entities.crop import CropClass
from aquacrop.entities.inititalWaterContent import InitialWaterContent


class TestAquacropOs(unittest.TestCase):
    """
    Speed tests of the aquacrop model
    """

    def test_model_os(self):
        """
        Speed test normal aquacrop model
        """

        weather_file_path = get_filepath("tunis_climate.txt")

        weather_data = prepare_weather(weather_file_path)

        sandy_loam = SoilClass(soil_type="SandyLoam")
        wheat = CropClass("Wheat", planting_date="10/01")
        initial_water_content = InitialWaterContent(value=["FC"])
        start_function_execution = time.time()
        model_os = AquaCropModel(
            sim_start_time=f"{1979}/10/01",
            sim_end_time=f"{1980}/05/30",
            weather_df=weather_data,
            soil=sandy_loam,
            crop=wheat,
            initial_water_content=initial_water_content,
        )

        # run model till termination
        model_os.run_model(till_termination=True)

        final_statistics = model_os.get_simulation_results().head(10)
        print(final_statistics)
        end_function_execution = time.time()
        print(
            "Function execution time is = ",
            end_function_execution - start_function_execution,
        )


if __name__ == "__main__":
    unittest.main()
