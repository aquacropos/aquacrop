"""
Tests for date-validation errors raised by AquaCropModel.

Was test_model_exceptions.py. The model is built once (not run) and its date
attributes are mutated to trigger each validation error.
"""
import pytest

from aquacrop import AquaCropModel, Crop, InitialWaterContent


@pytest.fixture
def model(tunis_weather, sandy_loam):
    return AquaCropModel(
        sim_start_time="1979/10/01",
        sim_end_time="1985/05/30",
        weather_df=tunis_weather,
        soil=sandy_loam,
        crop=Crop("Wheat", planting_date="10/01"),
        initial_water_content=InitialWaterContent(value=["FC"]),
    )


def test_bad_sim_start_time_format(model):
    with pytest.raises(Exception) as excinfo:
        model.sim_start_time = "1979-10/01"
    assert "sim_start_time format must be 'YYYY/MM/DD'" in str(excinfo.value)


def test_bad_sim_end_time_format(model):
    with pytest.raises(Exception) as excinfo:
        model.sim_end_time = "1979/13-01"
    assert "sim_end_time format must be 'YYYY/MM/DD'" in str(excinfo.value)


def test_start_before_climate_data(model):
    with pytest.raises(Exception) as excinfo:
        model.sim_start_time = "1970/10/01"
        model.sim_end_time = "1971/05/30"
        model.run_model()
    assert (
        "The first date of the climate data cannot be longer than the start date of the model."
        in str(excinfo.value)
    )


def test_simulation_period_too_long(model):
    with pytest.raises(Exception) as excinfo:
        model.sim_start_time = "1979/10/01"
        model.sim_end_time = "2900/10/01"
        model.run_model()
    assert "Simulation period must be less than 580 years." in str(excinfo.value)


def test_end_after_climate_data(model):
    with pytest.raises(Exception) as excinfo:
        model.sim_start_time = "1979/10/01"
        model.sim_end_time = "2100/10/01"
        model.run_model()
    assert (
        "The model end date cannot be longer than the last date of climate data."
        in str(excinfo.value)
    )
