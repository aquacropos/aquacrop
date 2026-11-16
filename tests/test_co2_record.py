"""
Tests for the default CO2 record: Mauna Loa observations, then an SSP pathway.
"""
import warnings

import pandas as pd
import pytest

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, CO2
from aquacrop.entities.co2 import acfp


def _ppm(fname):
    return pd.read_csv(f"{acfp}/data/co2/{fname}", header=1, sep=r"\s+",
                       names=["year", "ppm"]).set_index("year")["ppm"]


def _model(co2, start, end):
    dates = pd.date_range(f"{start}-01-01", f"{end}-12-31", freq="D")
    weather = pd.DataFrame({"MinTemp": 12.0, "MaxTemp": 28.0, "Precipitation": 3.0,
                            "ReferenceET": 5.0, "Date": dates})
    return AquaCropModel(
        sim_start_time=f"{start}/01/01", sim_end_time=f"{end}/12/31",
        weather_df=weather, soil=Soil("SandyLoam"), crop=Crop("Maize", planting_date="05/01"),
        initial_water_content=InitialWaterContent(value=["FC"]), co2_concentration=co2)


def test_default_is_observed_then_ssp245():
    co2 = CO2()
    record = co2.co2_data.set_index("year")["ppm"]
    assert record.loc[:co2.observed_end].equals(_ppm("MaunaLoaCO2.txt"))
    future = _ppm("CO2_SSP2-4.5.txt").loc[co2.observed_end + 1:]
    assert record.loc[co2.observed_end + 1:].equals(future)
    assert co2.default_scenario


def test_scenario_follows_observed_record():
    co2 = CO2(scenario="SSP5-8.5")
    record = co2.co2_data.set_index("year")["ppm"]
    future = _ppm("CO2_SSP5-8.5.txt").loc[co2.observed_end + 1:]
    assert record.loc[co2.observed_end + 1:].equals(future)
    assert record.index.is_monotonic_increasing
    assert not co2.default_scenario


def test_unknown_scenario_raises():
    with pytest.raises(ValueError):
        CO2(scenario="rcp85")


def test_custom_data_unchanged():
    data = pd.DataFrame({"year": [2000, 2001], "ppm": [370.0, 371.0]})
    co2 = CO2(co2_data=data)
    assert co2.co2_data is data
    assert not co2.default_scenario


def test_default_warns_past_observed_record():
    co2 = CO2()
    model = _model(co2, co2.observed_end, co2.observed_end + 1)
    with pytest.warns(UserWarning, match=r"CO2\(scenario=\.\.\.\)"):
        model._initialize()


@pytest.mark.parametrize("scenario, offset", [(None, -1), ("ssp585", 1)])
def test_no_warning_within_record_or_with_scenario(scenario, offset):
    co2 = CO2(scenario=scenario)
    end = co2.observed_end
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        _model(co2, end + min(offset, 0), end + max(offset, 0))._initialize()
