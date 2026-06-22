"""
Root growth tests with a custom soil profile whose deepest layer has zero
penetrability.

Was test_rootgowth.py (filename typo fixed). Checks that root depth stays
within physical bounds and never decreases through time.
"""
import pytest

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, GroundWater
from .conftest import MODEL_TOL


@pytest.fixture(scope="module")
def root_growth_model(tunis_weather):
    weather = tunis_weather.copy()
    weather["Precipitation"] = weather["Precipitation"] / 10

    soil = Soil(soil_type="custom", cn=46, rew=7)
    for penetrability in (100, 100, 100, 0):
        soil.add_layer(
            thickness=0.1 * 3, thWP=0.24, thFC=0.40, thS=0.50,
            Ksat=155, penetrability=penetrability,
        )

    model = AquaCropModel(
        sim_start_time="1979/10/01",
        sim_end_time="1980/05/30",
        weather_df=weather,
        soil=soil,
        crop=Crop("Wheat", planting_date="10/01"),
        initial_water_content=InitialWaterContent(value=["FC"]),
        groundwater=GroundWater(
            water_table="Y", dates=["1979/10/01"], values=[2.66]
        ),
    )
    model.run_model(till_termination=True)
    return model


def _root_depth_to_harvest(model):
    harvest_step = model._outputs.final_stats["Harvest Date (Step)"].values[0]
    crop_growth = model._outputs.crop_growth
    return crop_growth["z_root"][0:harvest_step]


def test_minimum_root_depth(root_growth_model):
    root_depth = _root_depth_to_harvest(root_growth_model)
    assert root_depth.min() == pytest.approx(0.3, abs=0.05)


def test_maximum_root_depth(root_growth_model):
    """Root depth must not exceed the depth where penetrability becomes 0."""
    root_depth = _root_depth_to_harvest(root_growth_model)
    assert root_depth.max() == pytest.approx(0.9, abs=0.05)


def test_root_depth_non_decreasing(root_growth_model):
    root_depth = _root_depth_to_harvest(root_growth_model)
    for earlier, later in zip(root_depth, root_depth[1:]):
        assert later >= earlier, "Root depth decreased through time"
