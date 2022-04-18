import unittest
import pandas as pd
import time

from aquacrop.core import AquaCropModel, get_filepath, prepare_weather
from aquacrop.entities.soil import SoilClass
from aquacrop.entities.crop import CropClass
from aquacrop.entities.inititalWaterContent import InitialWaterContent


class TestAquacropOs(unittest.TestCase):
    def test_model_Os(self):

        weather_file_path = get_filepath("tunis_climate.txt")

        weather_data = prepare_weather(weather_file_path)

        sandy_loam = SoilClass(soilType="SandyLoam")
        wheat = CropClass("Wheat", planting_date="10/01")
        initial_water_content = InitialWaterContent(value=["FC"])
        start_function_execution = time.time()
        model_os = AquaCropModel(
            sim_start_time=f"{1979}/10/01",
            sim_end_time=f"{1985}/05/30",
            weather_df=weather_data,
            soil=sandy_loam,
            crop=wheat,
            initial_water_content=initial_water_content,
        )

        # run model till termination
        model_results = model_os.run_model(till_termination=True)["results"]
        final_statistics = model_results.final_stats.head(10)
        end_function_execution = time.time()
        print(
            "Function execution time is = ",
            end_function_execution - start_function_execution,
        )
        print(final_statistics)

        yied_1_result = 8.940139992051638
        yield1 = final_statistics["Yield (tonne/ha)"][0]

        yied_5_result = 8.682660046213236
        yield5 = final_statistics["Yield (tonne/ha)"][4]

        self.assertEqual(yield1, yied_1_result)
        self.assertEqual(yield5, yied_5_result)


if __name__ == "__main__":
    unittest.main()
