"""
Inititalize clocks parameters
"""
import pandas as pd
from ..entities.clockStruct import ClockStruct


def read_clock_parameters(
    sim_start_time: str,
    sim_end_time: str,
    off_season: bool=False) -> ClockStruct:
    """
    Function to read in start and end simulation time and return a ClockStruct object

    Arguments:

        sim_start_time (str): simulation start date

        sim_end_time (str): simulation start date

        off_season (bool): True, simulate off season
                          False, skip ahead to next season post-harvest

    Returns:

        clock_struct (ClockStruct): simulation time paramaters


    """
    check_max_simulation_days(sim_start_time, sim_end_time)

    # Extract data and put into pandas datetime format
    pandas_sim_start_time = pd.to_datetime(sim_start_time)
    pandas_sim_end_time = pd.to_datetime(sim_end_time)

    # create ClockStruct object
    clock_struct = ClockStruct()

    # Add variables
    clock_struct.simulation_start_date = pandas_sim_start_time
    clock_struct.simulation_end_date = pandas_sim_end_time

    clock_struct.n_steps = (pandas_sim_end_time - pandas_sim_start_time).days + 1
    clock_struct.time_span = pd.date_range(
        freq="D", start=pandas_sim_start_time, end=pandas_sim_end_time
    )

    clock_struct.step_start_time = clock_struct.time_span[0]
    clock_struct.step_end_time = clock_struct.time_span[1]

    clock_struct.sim_off_season = off_season

    return clock_struct


def check_max_simulation_days(
    sim_start_time: str,
    sim_end_time: str):
    """
    Check that the date range of the simulation is less than 580 years.
    In pandas this cannot happen due to the size of the variable

    Arguments:

        sim_start_time (str): simulation start date YYYY/MM/DD

        sim_end_time (str): simulation start date YYYY/MM/DD

    """
    start_year = int(sim_start_time.split("/")[0])
    end_year = int(sim_end_time.split("/")[0])
    if (end_year - start_year) > 580:
        raise ValueError("Simulation period must be less than 580 years.")
