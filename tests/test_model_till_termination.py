import unittest

from aquacrop.utils.prepare_weather import prepare_weather
from aquacrop.utils.data import get_filepath
from aquacrop.core import AquaCropModel
from aquacrop.entities.soil import Soil
from aquacrop.entities.crop import Crop
from aquacrop.entities.inititalWaterContent import InitialWaterContent


class TestModelTillTermination(unittest.TestCase):
    """
    Simple test of AquacropModel
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
    _model_os.run_model(till_termination=True)

    def test_final_statistics(self):
        """
        Test final statistics
        """
        final_statistics = self._model_os.get_simulation_results().head()
        yied_1_result = 8.940139992051638
        yield1 = final_statistics["Yield (tonne/ha)"][0]

        yied_5_result = 8.682660046213236
        yield5 = final_statistics["Yield (tonne/ha)"][4]

        self.assertEqual(yield1, yied_1_result)
        self.assertEqual(yield5, yied_5_result)

    def test_crop_growth(self):
        """
        Test Crop Growth
        """
        crop_growth = self._model_os.get_crop_growth().head()

        gdd_4_expected = 22.5
        gdd_4_returned = crop_growth["gdd"][4]
        self.assertEqual(gdd_4_expected, gdd_4_returned)

        gd_cum_d_4_expected = 104
        gdd_4_cum_returned = crop_growth["gdd_cum"][4]
        self.assertEqual(gd_cum_d_4_expected, gdd_4_cum_returned)

    def test_water_flux(self):
        """
        Test water flux
        """
        water_flux = self._model_os.get_water_flux().head()

        wr_4_expected = 57.56
        wr_4_returned = water_flux["Wr"][4]

        self.assertEqual(wr_4_expected, wr_4_returned)

        es_pot_4_expected = 3.96
        es_pot_4_returned = round(water_flux["EsPot"][4], 2)
        self.assertEqual(es_pot_4_expected, es_pot_4_returned)

    def test_water_storage(self):
        """
        Test water storage
        """
        water_storage = self._model_os.get_water_storage().head()

        th1_3_expected = 0.146497
        th1_3_returned = round(water_storage["th1"][3], 6)
        self.assertEqual(th1_3_expected, th1_3_returned)

    def test_aditional_information(self):
        """
        Test aditional information
        """
        aditional_information = self._model_os.get_additional_information()
        has_model_finished_expected = True
        has_model_finished_returned = aditional_information["has_model_finished"]
        self.assertEqual(has_model_finished_expected, has_model_finished_returned)


if __name__ == "__main__":
    unittest.main()
