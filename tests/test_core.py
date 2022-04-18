import unittest

from aquacrop.core import AquaCropModel, get_filepath, prepare_weather
from aquacrop.entities.soil import Soil
from aquacrop.entities.crop import Crop
from aquacrop.entities.inititalWaterContent import InitialWaterContent


class TestAquacropOs(unittest.TestCase):
    def test_model_till_termination(self):
    
        weather_file_path = get_filepath("tunis_climate.txt")

        weather_data = prepare_weather(weather_file_path)

        sandy_loam = Soil(soilType="SandyLoam")
        wheat = Crop("Wheat", planting_date="10/01")
        initial_water_content = InitialWaterContent(value=["FC"])
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
        final_statistics = model_results.final_stats.head()
        print(final_statistics)
        # print(model_os.outputs.water_storage)

        yied_1_result = 8.940139992051638
        yield1 = final_statistics["Yield (tonne/ha)"][0]

        yied_5_result = 8.682660046213236
        yield5 = final_statistics["Yield (tonne/ha)"][4]

        self.assertEqual(yield1, yied_1_result)
        self.assertEqual(yield5, yied_5_result)

    def test_model_stepts(self):

        weather_file_path = get_filepath("tunis_climate.txt")

        weather_data = prepare_weather(weather_file_path)

        sandy_loam = Soil(soilType="SandyLoam")
        wheat = Crop("Wheat", planting_date="10/01")
        initial_water_content = InitialWaterContent(value=["FC"])
        model_os = AquaCropModel(
            sim_start_time=f"{1979}/10/01",
            sim_end_time=f"{1985}/05/30",
            weather_df=weather_data,
            soil=sandy_loam,
            crop=wheat,
            initial_water_content=initial_water_content,
        )
        # run model till termination
        model_results = model_os.run_model(num_steps=2)["results"]
        # final_statistics = model_results.final_stats.head(10)
        # print(final_statistics.values)
        # np.set_printoptions(threshold=np.inf)
        gdd_result = model_results.crop_growth["GDD"].iloc[0]

        self.assertEqual(21.5, gdd_result)



if __name__ == "__main__":
    unittest.main()
