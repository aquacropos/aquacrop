"""
This test is for bug testing
"""
import os
os.environ['DEVELOPMENT'] = 'True'
import unittest

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, GroundWater
from aquacrop.utils import prepare_weather, get_filepath




class TestModelExceptions(unittest.TestCase):
    """
    Test of what happens if the model does not run.
    """

    _weather_file_path = get_filepath("tunis_climate.txt")

    _weather_data = prepare_weather(_weather_file_path)

    _weather_data["Precipitation"] = (
        _weather_data["Precipitation"] / 10
    )  # too much rain for ground water effect in the original

    # create a custom soil that has a layer with penetrability = 0
    soil_custom3 = Soil(soil_type='custom', cn=46, rew=7)
    soil_custom3.add_layer(thickness=.1*3,thWP=0.24,
                            thFC=0.40,thS=0.50,Ksat=155,
                            penetrability=100)
    soil_custom3.add_layer(thickness=.1*3,thWP=0.24,
                            thFC=0.40,thS=0.50,Ksat=155,
                            penetrability=100)
    soil_custom3.add_layer(thickness=.1*3,thWP=0.24,
                            thFC=0.40,thS=0.50,Ksat=155,
                            penetrability=100)
    soil_custom3.add_layer(thickness=.1*3,thWP=0.24,
                            thFC=0.40,thS=0.50,Ksat=155,
                            penetrability=0)
    print(soil_custom3.profile) 
    _wheat = Crop("Wheat", planting_date="10/01")
    _initial_water_content = InitialWaterContent(value=["FC"])
    _model_os = AquaCropModel(
        sim_start_time=f"{1979}/10/01",
        sim_end_time=f"{1981}/05/30",
        weather_df=_weather_data,
        soil=soil_custom3,
        crop=_wheat,
        initial_water_content=_initial_water_content,
        groundwater=GroundWater(
            water_table="Y", dates=[f"{1979}/10/01"], values=[2.66]
        ),
    )
    _model_os.run_model(till_termination=True)

    def test_minimum_root_depth(self):
        """
        Test that minimum root depth is not below 0
        """
        root_depth = self._model_os._outputs.crop_growth["z_root"]
    
        min_rooting_depth_expected = 0
        min_rooting_depth_returned = round(root_depth.min(), 1)
        self.assertEqual(min_rooting_depth_expected, min_rooting_depth_returned)
    
    def test_maximum_root_depth(self):
        """
        Test that minimum root depth is not below 0
        """
        root_depth = self._model_os._outputs.crop_growth["z_root"]
    
        max_rooting_depth_expected = 0.9
        max_rooting_depth_returned = round(root_depth.max(), 1)
        self.assertEqual(max_rooting_depth_expected, max_rooting_depth_returned)
    
    def test_root_depth(self):
        """
        Test that root depth does not decrease through time
        """
        root_depth = self._model_os._outputs.crop_growth["z_root"]
    
        for earlier,later in zip(root_depth, root_depth[1:]):
            self.assertGreaterEqual(later, earlier, "Root depth decreased through time")

if __name__ == "__main__":
    unittest.main()