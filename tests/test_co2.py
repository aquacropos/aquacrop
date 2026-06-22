"""
Test a user-supplied CO2 concentration time series.

Was test_co2_timeseries.py.
"""
import pandas as pd
import pytest

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, CO2
from .conftest import MODEL_TOL


@pytest.fixture(scope="module")
def co2_model_results(tunis_weather):
    co2_data = pd.DataFrame(
        {"year": [1979, 1980, 1981], "ppm": [336.84, 338.76, 340.12]}
    )
    model = AquaCropModel(
        sim_start_time="1979/10/01",
        sim_end_time="1981/05/30",
        weather_df=tunis_weather,
        soil=Soil(soil_type="SandyLoam"),
        crop=Crop("Wheat", planting_date="10/01"),
        initial_water_content=InitialWaterContent(value=["FC"]),
        co2_concentration=CO2(co2_data=co2_data),
    )
    model.run_model(till_termination=True)
    return model.get_simulation_results()


def test_mean_yield(co2_model_results):
    mean_yield = co2_model_results["Dry yield (tonne/ha)"].mean()
    assert mean_yield == pytest.approx(8.627, **MODEL_TOL)
