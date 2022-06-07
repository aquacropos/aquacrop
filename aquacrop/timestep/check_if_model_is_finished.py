def check_model_is_finished(
    step_end_time,
    simulation_end_date,
    model_is_finished,
    season_counter,
    n_seasons,
    harvest_flag,
):
    """
    Function to check and declare model termination


    *Arguments:*\n

    `ClockStruct` : `ClockStruct` :  model time paramaters

    `InitCond` : `InitialCondition` :  containing current model paramaters

    *Returns:*

    `ClockStruct` : `ClockStruct` : updated clock paramaters


    """

    # Check if current time-step is the last
    current_time = step_end_time
    if current_time < simulation_end_date:
        model_is_finished = False
    elif current_time >= simulation_end_date:
        model_is_finished = True

    # Check if at the end of last growing season ##
    # Allow model to exit early if crop has reached maturity or died, and in
    # the last simulated growing season
    if (harvest_flag is True) and (season_counter == n_seasons - 1):
        model_is_finished = True

    return model_is_finished
