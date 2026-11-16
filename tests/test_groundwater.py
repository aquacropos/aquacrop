"""
Groundwater table tests.

Consolidates test_groundwater_table.py (yield check with a shallow water table)
and test_bug.py (a regression scenario that previously only checked the model
ran without error).
"""
import pytest

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, GroundWater
from .conftest import MODEL_TOL


def _build_groundwater_model(weather, sim_end):
    # The original tests scale precipitation down so the water table has a
    # visible effect (the unscaled series is too wet).
    weather = weather.copy()
    weather["Precipitation"] = weather["Precipitation"] / 10
    return AquaCropModel(
        sim_start_time="1979/10/01",
        sim_end_time=sim_end,
        weather_df=weather,
        soil=Soil(soil_type="SandyLoam"),
        crop=Crop("Wheat", planting_date="10/01"),
        initial_water_content=InitialWaterContent(value=["FC"]),
        groundwater=GroundWater(
            water_table="Y", dates=["1979/10/01"], values=[2.66]
        ),
    )


@pytest.fixture(scope="module")
def groundwater_model(tunis_weather):
    model = _build_groundwater_model(tunis_weather, "1980/05/30")
    model.run_model(till_termination=True)
    return model


def test_yield_with_water_table(groundwater_model):
    yield_value = groundwater_model.get_simulation_results()["Dry yield (tonne/ha)"][0]
    assert yield_value == pytest.approx(7.987, **MODEL_TOL)


def test_multi_year_run_completes(tunis_weather):
    """Regression scenario (was test_bug.py): a multi-year groundwater run
    should complete without error."""
    model = _build_groundwater_model(tunis_weather, "1981/05/30")
    model.run_model(till_termination=True)
    assert model.get_additional_information()["has_model_finished"] is True
