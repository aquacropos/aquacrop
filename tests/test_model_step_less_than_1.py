import os
os.environ['DEVELOPMENT'] = 'True'
import unittest


from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
from aquacrop.utils import prepare_weather, get_filepath




class TestModelStepLessThan1(unittest.TestCase):
    """
    Test when AquaCrop model steps are less than 1
    """

    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _sandy_loam = Soil(soil_type="SandyLoam")
    _wheat = Crop("Wheat", planting_date="10/01")
    _initial_water_content = InitialWaterContent(value=["FC"])
    _model_os = AquaCropModel(
        sim_start_time=f"{1979}/10/01",
        sim_end_time=f"{1980}/05/30",
        weather_df=_weather_data,
        soil=_sandy_loam,
        crop=_wheat,
        initial_water_content=_initial_water_content,
    )

    def test_numstep_less_1(self):
        """
        If the number of steps in the execution model is less than 1, an error occurs.
        """

        with self.assertRaises(Exception) as context:
            self._model_os.run_model(num_steps=-1)

        self.assertTrue(
            "num_steps must be equal to or greater than 1." in str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
