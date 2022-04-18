import numpy as np
import pandas as pd



def read_groundwater_table(ParamStruct, GwStruct, ClockStruct):
    """
    Function to read input files and initialise groundwater parameters

    *Arguments:*\n

    `ParamStruct` : `ParamStructClass` :  Contains model paramaters

    `GwStruct` : `GwClass` :  groundwater params

    `ClockStruct` : `ClockStructClass` :  time params

    *Returns:*

    `ParamStruct` : `ParamStructClass` :  updated with GW info

    """

    # assign water table value and method
    WT = GwStruct.WaterTable
    WTMethod = GwStruct.Method

    # check if water table present
    if WT == "N":
        ParamStruct.WaterTable = 0
        ParamStruct.zGW = 999 * np.ones(len(ClockStruct.time_span))
        ParamStruct.zGW_dates = ClockStruct.time_span
        ParamStruct.WTMethod = "None"
    elif WT == "Y":
        ParamStruct.WaterTable = 1

        df = pd.DataFrame([GwStruct.dates, GwStruct.values]).T
        df.columns = ["Date", "Depth(mm)"]

        # get date in correct format
        df.Date = pd.DatetimeIndex(df.Date)

        if len(df) == 1:

            # if only 1 watertable depth then set that value to be constant
            # accross whole simulation
            zGW = df.reindex(ClockStruct.time_span, fill_value=df["Depth(mm)"].iloc[0],).drop(
                "Date", axis=1
            )["Depth(mm)"]

        elif len(df) > 1:
            # check water table method
            if WTMethod == "Constant":

                # No interpolation between dates

                # create daily depths for each simulation day
                zGW = pd.Series(
                    np.nan * np.ones(len(ClockStruct.time_span)), index=ClockStruct.time_span
                )

                # assign constant depth for all dates in between
                for row in range(len(df)):
                    date = df.Date.iloc[row]
                    depth = df["Depth(mm)"].iloc[row]
                    zGW.loc[zGW.index >= date] = depth
                    if row == 0:
                        zGW.loc[zGW.index <= date] = depth

            elif WTMethod == "Variable":

                # Linear interpolation between dates

                # create daily depths for each simulation day
                # fill unspecified days with NaN
                zGW = pd.Series(
                    np.nan * np.ones(len(ClockStruct.time_span)), index=ClockStruct.time_span
                )

                for row in range(len(df)):
                    date = df.Date.iloc[row]
                    depth = df["Depth(mm)"].iloc[row]
                    zGW.loc[date] = depth

                # Interpolate daily groundwater depths
                zGW = zGW.interpolate()

        # assign values to Paramstruct object
        ParamStruct.zGW = zGW.values
        ParamStruct.zGW_dates = zGW.index.values
        ParamStruct.WTMethod = WTMethod

    return ParamStruct

