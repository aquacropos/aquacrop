import pandas as pd
from ..entities.clockStruct import ClockStructClass


def read_clock_paramaters(SimStartTime, SimEndTime, OffSeason=False):
    """
    function to read in start and end simulaiton time and return a `ClockStructClass` object

    *Arguments:*\n

    `SimStartTime` : `str`:  simulation start date

    `SimEndTime` : `str` :  simulation start date

    `OffSeason` : `bool` :  simulate off season true, false

    *Returns:*


    `ClockStruct` : `ClockStructClass` : time paramaters


    """

    # extract data and put into numpy datetime format
    SimStartTime = pd.to_datetime(SimStartTime)
    SimEndTime = pd.to_datetime(SimEndTime)

    # create object
    ClockStruct = ClockStructClass()

    # add variables
    ClockStruct.simulation_start_date = SimStartTime
    ClockStruct.simulation_end_date = SimEndTime

    ClockStruct.n_steps = (SimEndTime - SimStartTime).days + 1
    ClockStruct.time_span = pd.date_range(freq="D", start=SimStartTime, end=SimEndTime)

    ClockStruct.step_start_time = ClockStruct.time_span[0]
    ClockStruct.step_end_time = ClockStruct.time_span[1]

    ClockStruct.sim_off_season = OffSeason

    return ClockStruct

