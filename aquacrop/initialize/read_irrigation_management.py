import numpy as np
import pandas as pd

from ..entities.irrigationManagement import IrrMngtStruct



def read_irrigation_management(ParamStruct, IrrMngt, ClockStruct):
    """
    initilize irr mngt and turn into jit classes

    *Arguments:*\n

    `ParamStruct` : `ParamStruct` :  Contains model crop and soil paramaters

    `IrrMngt` : `IrrigationManagement` :  irr mngt params object

    `ClockStruct` : `ClockStruct` :  time paramaters


    *Returns:*

    `ParamStruct` : `ParamStruct` :  updated model paramaters



    """
    # If specified, read input irrigation time-series
    if IrrMngt.irrigation_method == 3:

        df = IrrMngt.Schedule.copy()

        # change the index to the date
        df.index = pd.DatetimeIndex(df.Date)

        # create a dateframe containing the daily irrigation to
        # be applied for every day in the simulation
        df = df.reindex(ClockStruct.time_span, fill_value=0).drop("Date", axis=1)

        IrrMngt.Schedule = np.array(df.values, dtype=float).flatten()

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

