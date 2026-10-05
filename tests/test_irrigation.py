"""
Tests of the irrigation strategies in AquaCrop (Maize, Champion climate).

Was test_irrigation.py. Each strategy builds and runs its own model; the
shared champion weather is loaded once via the session fixture.
"""
import pandas as pd
import pytest

from aquacrop import (
    AquaCropModel,
    Soil,
    Crop,
    InitialWaterContent,
    IrrigationManagement,
)
from .conftest import MODEL_TOL

SIM_START = "1982/05/01"
SIM_END = "1983/10/30"


def _run(weather, irrigation):
    model = AquaCropModel(
        sim_start_time=SIM_START,
        sim_end_time=SIM_END,
        weather_df=weather,
        soil=Soil(soil_type="SandyLoam"),
        crop=Crop("Maize", planting_date="05/01"),
        initial_water_content=InitialWaterContent(value=["FC"]),
        irrigation_management=irrigation,
    )
    model.run_model(till_termination=True)
    return model.get_simulation_results().head(10)


def test_rainfed_strategy(champion_weather):
    stats = _run(champion_weather, IrrigationManagement(irrigation_method=0))
    assert stats["Dry yield (tonne/ha)"][0] == pytest.approx(10.78, **MODEL_TOL)


def test_threshold_strategy(champion_weather):
    stats = _run(
        champion_weather,
        IrrigationManagement(irrigation_method=1, SMT=[40, 60, 70, 30] * 4),
    )
    assert stats["Dry yield (tonne/ha)"][0] == pytest.approx(12.65, **MODEL_TOL)
    assert stats["Dry yield (tonne/ha)"][1] == pytest.approx(12.96, **MODEL_TOL)


def test_interval_7days_strategy(champion_weather):
    stats = _run(
        champion_weather,
        IrrigationManagement(irrigation_method=2, IrrInterval=7),
    )
    assert stats["Dry yield (tonne/ha)"][0] == pytest.approx(12.65, **MODEL_TOL)
    assert stats["Dry yield (tonne/ha)"][1] == pytest.approx(12.98, **MODEL_TOL)


def test_predefined_schedule_strategy(champion_weather):
    schedule = _create_irrigation_schedule(SIM_START, SIM_END)
    stats = _run(
        champion_weather,
        IrrigationManagement(irrigation_method=3, Schedule=schedule),
    )
    assert stats["Dry yield (tonne/ha)"][0] == pytest.approx(12.13, **MODEL_TOL)
    assert stats["Dry yield (tonne/ha)"][1] == pytest.approx(9.46, **MODEL_TOL)


def test_net_irrigation_strategy(champion_weather):
    stats = _run(
        champion_weather,
        IrrigationManagement(irrigation_method=4, NetIrrSMT=70),
    )
    assert stats["Dry yield (tonne/ha)"][0] == pytest.approx(12.66, **MODEL_TOL)
    assert stats["Dry yield (tonne/ha)"][1] == pytest.approx(12.97, **MODEL_TOL)


def _create_irrigation_schedule(sim_start, sim_end):
    """Irrigate 25 mm on the first Tuesday of each month."""
    all_days = pd.date_range(sim_start, sim_end)
    new_month = True
    dates = []
    for date in all_days:
        if date.is_month_start:
            new_month = True
        if new_month and date.dayofweek == 1:  # Tuesday
            dates.append(date)
            new_month = False
    depths = [25] * len(dates)
    schedule = pd.DataFrame([dates, depths]).T
    schedule.columns = ["Date", "Depth"]
    return schedule
