import numpy as np
import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.paramStruct import ParamStruct
    from aquacrop.entities.groundWater import GroundWater



def read_groundwater_table(
    ParamStruct: "ParamStruct",
    GwStruct: "GroundWater",
    ClockStruct: "ClockStruct") -> "ParamStruct":
    """
    Function to initialise groundwater parameters

    Arguments:

        ParamStruct (ParamStruct): Contains model paramaters

        GwStruct (GroundWater): groundwater params

        ClockStruct (ClockStruct): time params

    Returns:

        ParamStruct (ParamStruct): updated with GW info

    """

    # assign water table value and method
    WT = GwStruct.water_table
    WTMethod = GwStruct.method

    # check if water table present
    if WT == "N":
        ParamStruct.water_table = 0
        ParamStruct.z_gw = 999 * np.ones(len(ClockStruct.time_span))
        ParamStruct.zGW_dates = ClockStruct.time_span
        ParamStruct.WTMethod = "None"
    elif WT == "Y":
        ParamStruct.water_table = 1

        df = pd.DataFrame([GwStruct.dates, GwStruct.values]).T
        df.columns = ["Date", "Depth(mm)"]

        # get date in correct format
        df.Date = pd.DatetimeIndex(df.Date)
        # print(f'DF length: {len(df)}')
        # print(f'Index length: {len(df.index)}')

        if len(df) == 1:
            
            # if only 1 watertable depth then set that value to be constant
            # accross whole simulation            
            z_gw = pd.DataFrame(
                data=df["Depth(mm)"].iloc[0]*np.ones(len(ClockStruct.time_span)),
                index=pd.to_datetime(ClockStruct.time_span),
                columns=['Depth(mm)']
            )['Depth(mm)']

        elif len(df) > 1:
            # check water table method
            if WTMethod == "Constant":

                # No interpolation between dates

                # create daily depths for each simulation day
                z_gw = pd.Series(
                    np.nan * np.ones(len(ClockStruct.time_span)), index=ClockStruct.time_span
                )

                # assign constant depth for all dates in between
                for row in range(len(df)):
                    date = df.Date.iloc[row]
                    depth = df["Depth(mm)"].iloc[row]
                    z_gw.loc[z_gw.index >= date] = depth
                    if row == 0:
                        z_gw.loc[z_gw.index <= date] = depth

            elif WTMethod == "Variable":

                # Linear interpolation between dates

                # create daily depths for each simulation day
                # fill unspecified days with NaN
                z_gw = pd.Series(
                    np.nan * np.ones(len(ClockStruct.time_span)), index=ClockStruct.time_span
                )

                for row in range(len(df)):
                    date = df.Date.iloc[row]
                    depth = df["Depth(mm)"].iloc[row]
                    z_gw.loc[date] = depth

                # Interpolate daily groundwater depths
                z_gw = z_gw.interpolate()

        # assign values to Paramstruct object
        ParamStruct.z_gw = z_gw.values
        ParamStruct.zGW_dates = z_gw.index.values
        ParamStruct.WTMethod = WTMethod

    return ParamStruct

