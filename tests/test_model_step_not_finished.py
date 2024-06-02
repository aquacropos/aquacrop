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
        sim_start_time=f"{1979}/10/01",
        sim_end_time=f"{1980}/05/30",
        weather_df=_weather_data,
        soil=_sandy_loam,
        crop=_wheat,
        initial_water_content=_initial_water_content,
    )
    _model_os.run_model(num_steps=3,process_outputs=True)

    def test_final_statistics(self):
        """
        Test Final Statistics. It should be False
        """
        final_statistics_returned = self._model_os.get_simulation_results()
        final_statistics_expected = False

        self.assertEqual(final_statistics_expected, final_statistics_returned)

    def test_crop_growth(self):
        """
        Test Crop Growth
        """
        crop_growth = self._model_os.get_crop_growth().head()
        gdd_2_expected = 20
        gdd_2_returned = crop_growth["gdd"][2]
        self.assertEqual(gdd_2_expected, gdd_2_returned)

        gd_cum_d_4_expected = 0.0
        gdd_4_cum_returned = crop_growth["gdd_cum"][4]
        self.assertEqual(gd_cum_d_4_expected, gdd_4_cum_returned)

    def test_water_flux(self):
        """
        Test Water Flux
        """
        water_flux = self._model_os.get_water_flux().head()

        wr_2_expected = 59.98
        wr_2_returned = round(water_flux["Wr"][2], 2)

        self.assertEqual(wr_2_expected, wr_2_returned)

        es_2_expected = 3.19
        es_2_returned = round(water_flux["EsPot"][2], 2)
        self.assertEqual(es_2_expected, es_2_returned)

    def test_water_storage(self):
        """
        Test Water Storage
        """
        water_storage = self._model_os.get_water_storage().head()
        th1_2_expected = 0.16
        th1_2_returned = round(water_storage["th1"][2], 2)
        self.assertEqual(th1_2_expected, th1_2_returned)

    def test_aditional_information(self):
        """
        Test aditional information. Model is not finished
        """
        aditional_information = self._model_os.get_additional_information()
        has_model_finished_expected = False
        has_model_finished_returned = aditional_information["has_model_finished"]
        self.assertEqual(has_model_finished_expected, has_model_finished_returned)


if __name__ == "__main__":
    unittest.main()
