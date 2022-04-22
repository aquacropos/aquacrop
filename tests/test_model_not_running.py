import unittest

from aquacrop.utils.data import get_filepath
from aquacrop.utils.prepare_weather import prepare_weather
from aquacrop.core import AquaCropModel
from aquacrop.entities.soil import Soil
from aquacrop.entities.crop import Crop
from aquacrop.entities.inititalWaterContent import InitialWaterContent


class TestModelByStepNotFinished(unittest.TestCase):
    """
    Test of what happens if the model does not run.
    """

    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _sandy_loam = Soil(soil_type="SandyLoam")
    _wheat = Crop("Wheat", planting_date="10/01")
    _initial_water_content = InitialWaterContent(value=["FC"])
    _model_os = AquaCropModel(
        sim_start_time=f"{1979}/10/01",
        sim_end_time=f"{1985}/05/30",
        weather_df=_weather_data,
        soil=_sandy_loam,
        crop=_wheat,
        initial_water_content=_initial_water_content,
    )

    def test_final_statistics(self):
        """
        Test if an exception occurs when the model does not run before getting the results
        """

        with self.assertRaises(Exception) as context:
            self._model_os.get_simulation_results()

        self.assertTrue(
            "You cannot get results without running the model. Please execute the run_model() method."
            in str(context.exception)
        )

    def test_crop_growth(self):
        """
        Test if an exception occurs when the model does not run before getting the results
        """

        with self.assertRaises(Exception) as context:
            self._model_os.get_crop_growth()

        self.assertTrue(
            "You cannot get results without running the model. Please execute the run_model() method."
            in str(context.exception)
        )

    def test_water_storage(self):
        """
        Test if an exception occurs when the model does not run before getting the results
        """

        with self.assertRaises(Exception) as context:
            self._model_os.get_water_storage()

        self.assertTrue(
            "You cannot get results without running the model. Please execute the run_model() method."
            in str(context.exception)
        )

    def test_water_flux(self):
        """
        Test if an exception occurs when the model does not run before getting the results
        """

        with self.assertRaises(Exception) as context:
            self._model_os.get_water_flux()

        self.assertTrue(
            "You cannot get results without running the model. Please execute the run_model() method."
            in str(context.exception)
        )

    def test_additional_information(self):
        """
        Test if an exception occurs when the model does not run before getting the results
        """

        with self.assertRaises(Exception) as context:
            self._model_os.get_additional_information()

        self.assertTrue(
            "You cannot get results without running the model. Please execute the run_model() method."
            in str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
