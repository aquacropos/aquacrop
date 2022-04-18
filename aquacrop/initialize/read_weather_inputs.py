

def read_weather_inputs(ClockStruct, weather_df):
    """
    clip weather to start and end simulation dates

    *Arguments:*\n

    `ClockStruct` : `ClockStructClass` : time paramaters

    `weather_df` : `pd.DataFrame` :  weather data

    *Returns:*

    `weather_df` : `pd.DataFrame`: clipped weather data

    """

    # get the start and end dates of simulation
    start_date = ClockStruct.simulation_start_date
    end_date = ClockStruct.simulation_end_date

    assert weather_df.Date.iloc[0] <= start_date
    assert weather_df.Date.iloc[-1] >= end_date

    # remove weather data outside of simulation dates
    weather_df = weather_df[weather_df.Date >= start_date]
    weather_df = weather_df[weather_df.Date <= end_date]

    return weather_df
