import unittest

import pandas as pd

from aquacrop.core import AquaCropModel, _weather_data_current_timestep
from aquacrop.solution.growing_degree_day import growing_degree_day


class TestWeatherColumnOrder(unittest.TestCase):
    def test_weather_columns_are_normalized_before_timestep_extraction(self):
        # A valid DataFrame may put Date before the numeric weather columns.
        weather_df = pd.DataFrame(
            {
                "Date": pd.to_datetime(["2000-01-01"]),
                "MinTemp": [10.0],
                "MaxTemp": [25.0],
                "Precipitation": [0.0],
                "ReferenceET": [3.0],
            }
        )
        model = object.__new__(AquaCropModel)
        model.weather_df = weather_df

        weather_step = _weather_data_current_timestep(model.weather_df.values, 0)
        gdd = growing_degree_day(2, 30.0, 8.0, weather_step[1], weather_step[0])

        self.assertEqual(weather_step[:4].tolist(), [10.0, 25.0, 0.0, 3.0])
        self.assertEqual(gdd, 9.5)


if __name__ == "__main__":
    unittest.main()
