"""
Update time function
"""
from .reset_initial_conditions import reset_initial_conditions

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from numpy import ndarray
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.initParamVariables import InitialCondition
    from aquacrop.entities.paramStruct import ParamStruct
    from aquacrop.entities.crop import Crop

def update_time(
    clock_struct: "ClockStruct",
    init_cond: "InitialCondition",
    param_struct: "ParamStruct",
    weather: "ndarray",
    crop: "Crop",
    ) -> Tuple["ClockStruct","InitialCondition", "ParamStruct"]:
    """
    Function to update current time in model.

    Arguments:

        clock_struct (ClockStruct):  model time paramaters

        init_cond (InitialCondition):  containing sim variables+counters

        param_struct (ParamStruct):  containing model paramaters

        weather (numpy.array):  weather data for simulation period

    Returns:

        clock_struct (ClockStruct):  model time paramaters

        init_cond (InitialCondition):  containing reset model paramaters

        param_struct (ParamStruct):  containing model paramaters
    """
    # Update time
    if clock_struct.model_is_finished is False:
        if (init_cond.harvest_flag is True) and (
            (clock_struct.sim_off_season is False)
        ):
            # TODO: sim_off_season will always be False.

            # End of growing season has been reached and not simulating
            # off-season soil water balance. Advance time to the start of the
            # next growing season.
            # Check if in last growing season
            if clock_struct.season_counter < clock_struct.n_seasons - 1:
                # Update growing season counter
                clock_struct.season_counter = clock_struct.season_counter + 1
                # Update time-step counter

                clock_struct.time_step_counter = clock_struct.time_span.get_loc(
                    clock_struct.planting_dates[clock_struct.season_counter]
                )
                # Update start time of time-step
                clock_struct.step_start_time = clock_struct.time_span[
                    clock_struct.time_step_counter
                ]
                # Update end time of time-step
                clock_struct.step_end_time = clock_struct.time_span[
                    clock_struct.time_step_counter + 1
                ]
                # Reset initial conditions for start of growing season
                init_cond, param_struct = reset_initial_conditions(
                    clock_struct, init_cond, param_struct, weather, crop
                )

        else:
            # Simulation considers off-season, so progress by one time-step
            # (one day)
            # Time-step counter
            clock_struct.time_step_counter = clock_struct.time_step_counter + 1
            # Start of time step (beginning of current day)
            # clock_struct.time_span = pd.Series(clock_struct.time_span)
            clock_struct.step_start_time = clock_struct.time_span[
                clock_struct.time_step_counter
            ]
            # End of time step (beginning of next day)
            clock_struct.step_end_time = clock_struct.time_span[
                clock_struct.time_step_counter + 1
            ]
            # Check if it is not the last growing season
            if clock_struct.season_counter < clock_struct.n_seasons - 1:
                # Check if upcoming day is the start of a new growing season
                if (
                    clock_struct.step_start_time
                    == clock_struct.planting_dates[clock_struct.season_counter + 1]
                ):
                    # Update growing season counter
                    clock_struct.season_counter = clock_struct.season_counter + 1
                    # Reset initial conditions for start of growing season
                    init_cond, param_struct = reset_initial_conditions(
                        clock_struct, init_cond, param_struct, weather, crop
                    )

    return clock_struct, init_cond, param_struct
