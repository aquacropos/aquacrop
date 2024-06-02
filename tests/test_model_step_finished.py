import os
os.environ['DEVELOPMENT'] = 'True'
import unittest


from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
from aquacrop.utils import prepare_weather, get_filepath




class TestModelByStepNotFinished(unittest.TestCase):
    """
    Test of the step model without finalisation
    """

    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _sandy_loam = Soil(soil_type="SandyLoam")
    _wheat = Crop("Wheat", planting_date="10/01")
    _initial_water_content = InitialWaterContent(value=["FC"])
    _model_os = AquaCropModel(
        sim_start_time=f"{1982}/10/01",
        sim_end_time=f"{1983}/05/30",
        weather_df=_weather_data,
        soil=_sandy_loam,
        crop=_wheat,
        initial_water_content=_initial_water_content,
    )
    _model_os.run_model(num_steps=5000)

    def test_final_statistics(self):
        """
        Test final statistics
        """
        final_statistics = self._model_os.get_simulation_results().head()
        yied_1_expected = 8.81
        yield_1_returned = round(final_statistics["Dry yield (tonne/ha)"][0], 2)

        self.assertEqual(yied_1_expected, yield_1_returned)

    def test_crop_growth(self):
        """
        Test Crop Growth.

        TODO: This test proves nothing relevant
        """
        crop_growth = self._model_os.get_crop_growth().head()

        gdd_4_expected = 19
        gdd_4_returned = crop_growth["gdd"][4]
        self.assertEqual(gdd_4_expected, gdd_4_returned)

        gd_cum_4_expected = 106.35
        gdd_cum_4_returned = crop_growth["gdd_cum"][4]
        self.assertEqual(gd_cum_4_expected, gdd_cum_4_returned)

    def test_water_flux(self):
        """
        Test water flux
        """
        water_flux = self._model_os.get_water_flux().head()

        wr_4_expected = 56.06
        wr_4_returned = water_flux["Wr"][4]

        self.assertEqual(wr_4_expected, wr_4_returned)

        es_pot_4_expected = 4.29
        es_pot_4_returned = round(water_flux["EsPot"][4], 2)
        self.assertEqual(es_pot_4_expected, es_pot_4_returned)

    def test_water_storage(self):
        """
        Test water storage
        """
        water_storage = self._model_os.get_water_storage().head()

        th1_3_expected = 0.146171
        th1_3_returned = round(water_storage["th1"][3], 6)
        self.assertEqual(th1_3_expected, th1_3_returned)

    def test_aditional_information(self):
        """
        Test aditional information. Model is not finished
        """
        aditional_information = self._model_os.get_additional_information()
        has_model_finished_expected = True
        has_model_finished_returned = aditional_information["has_model_finished"]
        self.assertEqual(has_model_finished_expected, has_model_finished_returned)


if __name__ == "__main__":
    unittest.main()
