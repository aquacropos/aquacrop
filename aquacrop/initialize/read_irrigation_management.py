import numpy as np
import pandas as pd

from ..entities.irrigationManagement import IrrMngtStruct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.irrigationManagement import IrrigationManagement, IrrMngtStruct
    from aquacrop.entities.paramStruct import ParamStruct


def read_irrigation_management(
    ParamStruct: "ParamStruct",
    IrrMngt: "IrrigationManagement",
    ClockStruct: "ClockStruct") -> "ParamStruct":
    """
    initilize irrigation management and store as IrrMngtStruct object

    Arguments:

        ParamStruct (ParamStruct):  Contains model crop and soil paramaters

        IrrMngt (IrrigationManagement):  irr mngt params object

        ClockStruct (ClockStruct):  time paramaters


    Returns:

        ParamStruct (ParamStruct):  updated model paramaters



    """
    # If specified, read input irrigation time-series
    if IrrMngt.irrigation_method == 3:

        df = IrrMngt.Schedule.copy()
        # change the index to the date
        df.index = pd.DatetimeIndex(df.Date)

        try:
            # create a dateframe containing the daily irrigation to
            # be applied for every day in the simulation
            df = df.reindex(ClockStruct.time_span, fill_value=0).drop("Date", axis=1)

            IrrMngt.Schedule = np.array(df.values, dtype=float).flatten()
            
        except TypeError:
            # older version of pandas with not reindex

            # create new dataframe for whole simulation
            # populate new dataframe with old values
            new_df = pd.DataFrame(data=np.zeros(len(ClockStruct.time_span)),
                index=pd.to_datetime(ClockStruct.time_span),
                columns=['Depth']
                )
                
            # fill in the new dataframe with irrigation schedule
            new_df.loc[df.index]=df.Depth.values

            IrrMngt.Schedule = np.array(new_df.values, dtype=float).flatten()

    else:

        IrrMngt.Schedule = np.zeros(len(ClockStruct.time_span))

    IrrMngt.SMT = np.array(IrrMngt.SMT, dtype=float)

    irr_mngt_struct = IrrMngtStruct(len(ClockStruct.time_span))
    for a, v in IrrMngt.__dict__.items():
        if hasattr(irr_mngt_struct, a):
            irr_mngt_struct.__setattr__(a, v)

    ParamStruct.IrrMngt = irr_mngt_struct
    ParamStruct.FallowIrrMngt = IrrMngtStruct(len(ClockStruct.time_span))

    return ParamStruct

