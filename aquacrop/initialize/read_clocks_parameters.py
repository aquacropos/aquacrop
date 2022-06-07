"""
Inititalize clocks parameters
"""
import pandas as pd
from ..entities.clockStruct import ClockStruct


def read_clock_paramaters(sim_start_time, sim_end_time, off_season=False):
    """
    Function to read in start and end simulaiton time and return a ClockStruct object

        Arguments:

            sim_start_time : `str`
                    simulation start date

            sim_end_time : `str`
                    simulation start date

            off_season : `bool`
                    simulate off season true, false

        Returns:

            clock_sctruct : ClockStruct object
                    time paramaters


    """
    check_max_simulation_days(sim_start_time, sim_end_time)

    # Extract data and put into pandas datetime format
    pandas_sim_start_time = pd.to_datetime(sim_start_time)
    pandas_sim_end_time = pd.to_datetime(sim_end_time)

    # create ClockStruct object
    clock_sctruct = ClockStruct()

    # Add variables
    clock_sctruct.simulation_start_date = pandas_sim_start_time
    clock_sctruct.simulation_end_date = pandas_sim_end_time

    clock_sctruct.n_steps = (pandas_sim_end_time - pandas_sim_start_time).days + 1
    clock_sctruct.time_span = pd.date_range(
        freq="D", start=pandas_sim_start_time, end=pandas_sim_end_time
    )

    clock_sctruct.step_start_time = clock_sctruct.time_span[0]
    clock_sctruct.step_end_time = clock_sctruct.time_span[1]

    clock_sctruct.sim_off_season = off_season

    return clock_sctruct


def check_max_simulation_days(sim_start_time, sim_end_time):
    """
    Check that the date range of the simulation is less than 580 years.
    In pandas this cannot happen due to the size of the variable
    """
    start_year = int(sim_start_time.split("/")[0])
    end_year = int(sim_end_time.split("/")[0])
    if (end_year - start_year) > 580:
        raise ValueError("Simulation period must be less than 580 years.")
