"""
Contains model information regarding dates and step times etc.

"""


class ClockStruct:
    """
    Contains model information regarding dates and step times etc.

    Atributes:\n

    `time_step_counter` : `int`: Keeps track of current timestep

    `model_is_finished` : `Bool`: False unless model has finished

    `simulation_start_date` : `np.Datetime64`: Date of simulation start

    `simulation_end_date` : `np.Datetime64`: Date of simulation end

    `time_step` : `int`: time step (evaluation needed)

    `n_steps` : `int`: total number of days of simulation

    `time_span` : `np.array`: all dates (np.Datetime64) that
        lie within the start and end dates of simulation

    `step_start_time` : `np.Datetime64`: Date at start of timestep

    `step_end_time` : `np.Datetime64`: Date at end of timestep

    `evap_time_steps` : `int`: Number of time-steps (per day) for soil
        evaporation calculation

    `sim_off_season` : `str`: 'Y' if you want to simulate the off season,
    'N' otherwise

    `planting_dates` : `list-like`: list of planting dates in datetime format

    `harvest_dates` : `list-like`: list of harvest dates in datetime format

    `n_seasons` : `int`: Total number of seasons to be simulated

    `season_counter` : `int`: counter to keep track of which season we are
        currenlty simulating


    """

    def __init__(self):

        self.time_step_counter = 0  # Keeps track of current timestep
        self.model_is_finished = False  # False unless model has finished
        self.simulation_start_date = 0  # Date of simulation start
        self.simulation_end_date = 0  # Date of simulation end
        self.time_step = 0  # time step (evaluaiton needed)
        self.n_steps = 0  # total number of days of simulation
        self.time_span = (
            0  # all dates that lie within the start and end dates of simulation
        )
        self.step_start_time = 0  # Date at start of timestep
        self.step_end_time = 0  # Date at start of timestep
        # Number of time-steps (per day) for soil evaporation calculation
        self.evap_time_steps = 20
        self.sim_off_season = (
            "N"  # 'Yes' if you want to simulate the off season, 'N' otherwise
        )
        self.planting_dates = (
            []
        )  # list of crop planting dates during simulation
        self.harvest_dates = []  # list of crop planting dates during simulation
        self.n_seasons = 0  # total number of seasons (plant and harvest)
        self.season_counter = -1  # running counter of seasons
