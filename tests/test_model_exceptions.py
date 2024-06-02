"""
Test exeptions in the model.
"""
import os
os.environ['DEVELOPMENT'] = 'True'
import unittest


from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
from aquacrop.utils import prepare_weather, get_filepath




class TestModelExceptions(unittest.TestCase):
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

    def test_syntax_err_sim_end_time(self):
        """
        Test error syntax in sim_end_time
        """

        with self.assertRaises(Exception) as context:
            self._model_os.sim_start_time = f"{1979}-10/01"

        self.assertTrue(
            "sim_start_time format must be 'YYYY/MM/DD'" in str(context.exception)
        )

    def test_syntax_err_sim_start_time(self):
        """
        Test error syntax in sim_start_time
        """
        with self.assertRaises(Exception) as context:
            self._model_os.sim_end_time = f"{1979}/13-01"

        self.assertTrue(
            "sim_end_time format must be 'YYYY/MM/DD'" in str(context.exception)
        )

    def test_error_in_date_range(self):
        """
        Test error in date range
        """

        with self.assertRaises(Exception) as context:
            self._model_os.sim_start_time = f"{1970}/10/01"
            self._model_os.sim_end_time = f"{1971}/05/30"
            self._model_os.run_model()

        self.assertTrue(
            "The first date of the climate data cannot be longer than the start date of the model."
            in str(context.exception)
        )

        with self.assertRaises(Exception) as context:
            self._model_os.sim_start_time = f"{1979}/10/01"
            self._model_os.sim_end_time = f"{2900}/10/01"
            self._model_os.run_model()

        self.assertTrue(
            "Simulation period must be less than 580 years." in str(context.exception)
        )

        with self.assertRaises(Exception) as context:
            self._model_os.sim_start_time = f"{1979}/10/01"
            self._model_os.sim_end_time = f"{2100}/10/01"
            self._model_os.run_model()

        self.assertTrue(
            "The model end date cannot be longer than the last date of climate data."
            in str(context.exception)
        )

    # TODO: ADD TEST TO CHECK THE COLUMN OF THE WEATHER_DF


if __name__ == "__main__":
    unittest.main()
