import pandas as pd


def prepare_weather(weather_file_path):
    """
    function to read in weather data and return a dataframe containing
    the weather data

    Arguments:\n

FileLocations): `FileLocationsClass`:  input File Locations

weather_file_path): `str):  file location of weather data



    Returns:

weather_df (pandas.DataFrame):  weather data for simulation period

    """

    weather_df = pd.read_csv(weather_file_path, header=0, delim_whitespace=True)

    assert len(weather_df.columns) == 7

    # rename the columns
    weather_df.columns = str(
        "Day Month Year MinTemp MaxTemp Precipitation ReferenceET").split()

    # put the weather dates into datetime format
    weather_df["Date"] = pd.to_datetime(weather_df[["Year", "Month", "Day"]])

    # drop the day month year columns
    weather_df = weather_df.drop(["Day", "Month", "Year"], axis=1)

    # set limit on ET0 to avoid divide by zero errors
    weather_df.ReferenceET.clip(lower=0.1, inplace=True)

    return weather_df

