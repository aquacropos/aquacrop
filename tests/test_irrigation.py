"""
Test file for irrigation
"""
import os
os.environ['DEVELOPMENT'] = 'True'
import unittest
import pandas as pd

from aquacrop import (
    AquaCropModel,
    Soil,
    Crop,
    InitialWaterContent,
    IrrigationManagement,
)
from aquacrop.utils import prepare_weather, get_filepath


class TestIrrigation(unittest.TestCase):
    """
    Tests of different irrigation methodologies in AquaCrop.
    """

    _sim_start = "1982/05/01"
    _sim_end = "1983/10/30"

    weather_file_path = get_filepath("champion_climate.txt")

    _weather_data = prepare_weather(weather_file_path)

    _sandy_loam = Soil(soil_type="SandyLoam")
    _wheat = Crop("Maize", planting_date="05/01")
    _initial_water_content = InitialWaterContent(value=["FC"])

    def test_rainfed_strategy(self):
        """
        Rainfed methodology
        """
        irrigation = IrrigationManagement(irrigation_method=0)

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigation,
        )
        # run model till termination
        model_os.run_model(till_termination=True)

        final_statistics = model_os.get_simulation_results().head(10)
        yield_expected = 10.78
        yield_returned = round(final_statistics["Dry yield (tonne/ha)"][0], 2)

        self.assertEqual(yield_expected, yield_returned)

    def test_threshold4_irrigate_strategy(self):
        """
        Threshold methodology
        """
        irrigation = IrrigationManagement(irrigation_method=1, SMT=[40, 60, 70, 30] * 4)

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigation,
        )
        # run model till termination
        model_os.run_model(till_termination=True)

        final_statistics = model_os.get_simulation_results().head(10)

        yied_1_expected = 12.65
        yield_1_returned = round(final_statistics["Dry yield (tonne/ha)"][0], 2)

        yied_2_expected = 12.96
        yield_2_retruned = round(final_statistics["Dry yield (tonne/ha)"][1], 2)

        self.assertEqual(yied_1_expected, yield_1_returned)

        self.assertEqual(yied_2_expected, yield_2_retruned)

    def test_interval_7days__strategy(self):
        """
        7 days interval methodology
        """

        irrigation = IrrigationManagement(irrigation_method=2, IrrInterval=7)

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigation,
        )
        # run model till termination
        model_os.run_model(till_termination=True)

        final_statistics = model_os.get_simulation_results().head(10)

        yield_1_expected = 12.65
        yield_1_returned = round(final_statistics["Dry yield (tonne/ha)"][0], 2)

        yield_2_expected = 12.98
        yield_2_returned = round(final_statistics["Dry yield (tonne/ha)"][1], 2)

        self.assertEqual(yield_1_expected, yield_1_returned)
        self.assertEqual(yield_2_expected, yield_2_returned)

    def test_predefined_schedule_strategy(self):
        """
        Predefined schedule methodology
        """
        irrigation_schedule_df = create_pandas_irrigation_schedule(
            self._sim_start, self._sim_end
        )
        # print(irrigationSchedule)
        irrigate_schedule = IrrigationManagement(
            irrigation_method=3, Schedule=irrigation_schedule_df
        )

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigate_schedule,
        )

        # run model till termination
        model_os.run_model(till_termination=True)

        final_statistics = model_os.get_simulation_results().head(10)

        yield_1_expected = 12.13
        yield_1_returned = round(final_statistics["Dry yield (tonne/ha)"][0], 2)

        yield_2_expected = 9.46
        yield_2_returned = round(final_statistics["Dry yield (tonne/ha)"][1], 2)

        self.assertEqual(yield_1_expected, yield_1_returned)
        self.assertEqual(yield_2_expected, yield_2_returned)

    def test_net_irrigation_strategy(self):
        """
        Net methodology
        """
        irrigation = IrrigationManagement(irrigation_method=4, NetIrrSMT=70)

        model_os = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._sandy_loam,
            crop=self._wheat,
            initial_water_content=self._initial_water_content,
            irrigation_management=irrigation,
        )

        # run model till termination
        model_os.run_model(till_termination=True)

        final_statistics = model_os.get_simulation_results().head(10)

        yield_1_expected = 12.66
        yield_1_returned = round(final_statistics["Dry yield (tonne/ha)"][0], 2)

        yield_2_expected = 12.97
        yield_2_returned = round(final_statistics["Dry yield (tonne/ha)"][1], 2)

        self.assertEqual(yield_1_expected, yield_1_returned)
        self.assertEqual(yield_2_expected, yield_2_returned)


def create_pandas_irrigation_schedule(sim_start, sim_end):
    """
    This function create a irrigation schedule
    """
    all_days = pd.date_range(
        sim_start, sim_end
    )  # list of all dates in simulation period

    new_month = True
    dates = []
    # iterate through all simulation days
    for date in all_days:
        # check if new month
        if date.is_month_start:
            new_month = True

        if new_month:
            # check if tuesday (dayofweek=1)
            if date.dayofweek == 1:
                # save date
                dates.append(date)
                new_month = False
    depths = [25] * len(dates)  # depth of irrigation applied
    schedule = pd.DataFrame([dates, depths]).T  # create pandas DataFrame
    schedule.columns = ["Date", "Depth"]  # name columns

    return schedule


if __name__ == "__main__":
    unittest.main()
