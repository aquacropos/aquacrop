"""
Update time function
"""
from .reset_initial_conditions import reset_initial_conditions


def update_time(clock_struct, init_cond, param_struct, weather):
    """
    Function to update current time in model.

    *Arguments:*\n

    `clock_struct` : `clock_structClass` :  model time paramaters

    `init_cond` : `init_cond obj` :  containing current model paramaters

    `param_struct` : `init_cond obj` :  containing model paramaters

    `weather`: `np.array` :  weather data for simulation period

    *Returns:*

    `clock_struct` : `clock_structClass` :  model time paramaters

    `init_cond` : `init_condClass` :  containing reset model paramaters

    `param_struct` : `init_cond obj` :  containing model paramaters
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
                    clock_struct, init_cond, param_struct, weather
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
                        clock_struct, init_cond, param_struct, weather
                    )

    return clock_struct, init_cond, param_struct
