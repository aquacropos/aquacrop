from .reset_initial_conditions import reset_initial_conditions


def update_time(ClockStruct, InitCond, ParamStruct, weather):
    """
    Function to update current time in model

    *Arguments:*\n

    `ClockStruct` : `ClockStructClass` :  model time paramaters

    `InitCond` : `InitCondClass` :  containing current model paramaters

    `weather`: `np.array` :  weather data for simulation period


    *Returns:*

    `ClockStruct` : `ClockStructClass` :  model time paramaters


    `InitCond` : `InitCondClass` :  containing reset model paramaters


    """
    # Update time
    if ClockStruct.model_is_finished is False:
        if (InitCond.HarvestFlag is True) and ((ClockStruct.sim_off_season is False)):
            # End of growing season has been reached and not simulating
            # off-season soil water balance. Advance time to the start of the
            # next growing season.
            # Check if in last growing season
            if ClockStruct.season_counter < ClockStruct.n_seasons - 1:
                # Update growing season counter
                ClockStruct.season_counter = ClockStruct.season_counter + 1
                # Update time-step counter
                # ClockStruct.time_span = pd.Series(ClockStruct.time_span)
                ClockStruct.time_step_counter = ClockStruct.time_span.get_loc(
                    ClockStruct.planting_dates[ClockStruct.season_counter]
                )
                # Update start time of time-step
                ClockStruct.step_start_time = ClockStruct.time_span[
                    ClockStruct.time_step_counter
                ]
                # Update end time of time-step
                ClockStruct.step_end_time = ClockStruct.time_span[
                    ClockStruct.time_step_counter + 1
                ]
                # Reset initial conditions for start of growing season
                InitCond, ParamStruct = reset_initial_conditions(
                    ClockStruct, InitCond, ParamStruct, weather
                )

        else:
            # Simulation considers off-season, so progress by one time-step
            # (one day)
            # Time-step counter
            ClockStruct.time_step_counter = ClockStruct.time_step_counter + 1
            # Start of time step (beginning of current day)
            # ClockStruct.time_span = pd.Series(ClockStruct.time_span)
            ClockStruct.step_start_time = ClockStruct.time_span[
                ClockStruct.time_step_counter
            ]
            # End of time step (beginning of next day)
            ClockStruct.step_end_time = ClockStruct.time_span[
                ClockStruct.time_step_counter + 1
            ]
            # Check if in last growing season
            if ClockStruct.season_counter < ClockStruct.n_seasons - 1:
                # Check if upcoming day is the start of a new growing season
                if (
                    ClockStruct.step_start_time
                    == ClockStruct.planting_dates[ClockStruct.season_counter + 1]
                ):
                    # Update growing season counter
                    ClockStruct.season_counter = ClockStruct.season_counter + 1
                    # Reset initial conditions for start of growing season
                    InitCond, ParamStruct = reset_initial_conditions(
                        ClockStruct, InitCond, ParamStruct, weather
                    )

    return ClockStruct, InitCond, ParamStruct
