def check_model_is_finished(
    step_end_time: str,
    simulation_end_date: str,
    model_is_finished: bool,
    season_counter: int,
    n_seasons: int,
    harvest_flag: bool,
) -> bool:
    """
    Function to check and declare model termination


    Arguments:

        step_end_time (str):  date of next step

        simulation_end_date (str):  date of end of simulation

        model_is_finished (bool):  is model finished

        season_counter (int):  tracking the number of seasons simulated

        n_seasons (int):  total number of seasons being simulated

        harvest_flag (bool):  Has crop been harvested

    Returns:

        model_is_finished (bool): is simulation finished


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
