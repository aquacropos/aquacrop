"""
This file contains the AquacropModel class that runs the simulation.
"""
import os

import numpy as np
import pandas as pd


from .scripts.checkIfPackageIsCompiled import compile_all_AOT_files

# Important: This code is necessary to check if the AOT files are compiled.
if os.getenv("DEVELOPMENT"):
    print("Running the simulation in development mode.")
else:
    compile_all_AOT_files()

# pylint: disable=wrong-import-position

from . import data
from .entities.fieldManagement import FieldMngt
from .entities.groundWater import GroundWater
from .entities.irrigationManagement import IrrigationManagement
from .entities.output import Output
from .initialize.compute_variables import compute_variables
from .initialize.create_soil_profile import create_soil_profile
from .initialize.read_clocks_parameters import read_clock_paramaters
from .initialize.read_field_managment import read_field_management
from .initialize.read_groundwater_table import read_groundwater_table
from .initialize.read_irrigation_management import read_irrigation_management
from .initialize.read_model_initial_conditions import read_model_initial_conditions
from .initialize.read_model_parameters import read_model_parameters
from .initialize.read_weather_inputs import read_weather_inputs
from .timestep.check_if_model_is_finished import check_model_is_finished
from .timestep.run_single_timestep import solution_single_time_step
from .timestep.update_time import update_time
from .timestep.outputs_when_model_is_finished import outputs_when_model_is_finished


def list_data():
    """
    lists all built-in data files
    """
    path = data.__path__[0]

    return os.listdir(path)


def get_filepath(filename):
    """
    get selected data file
    """
    filepath = os.path.join(data.__path__[0], filename)

    return filepath


def get_data(filename, **kwargs):
    """
    get selected data file
    """
    filepath = os.path.join(data.__path__[0], filename)

    return np.genfromtxt(filepath, **kwargs)


def prepare_weather(weather_file_path):
    """
    function to read in weather data and return a dataframe containing
    the weather data

    *Arguments:*\n
    `weather_file_path` : `str` :  file location of weather data

    *Returns:*

    `weather_df`: `pandas.DataFrame` :  weather data for simulation period

    """

    weather_df = pd.read_csv(weather_file_path, header=0, delim_whitespace=True)

    assert len(weather_df.columns) == 7

    # rename the columns
    weather_df.columns = str(
        "Day Month Year MinTemp MaxTemp Precipitation ReferenceET"
    ).split()

    # put the weather dates into datetime format
    weather_df["Date"] = pd.to_datetime(weather_df[["Year", "Month", "Day"]])

    # drop the day month year columns
    weather_df = weather_df.drop(["Day", "Month", "Year"], axis=1)

    # set limit on ET0 to avoid divide by zero errors
    weather_df.ReferenceET.clip(lower=0.1, inplace=True)

    return weather_df


class AquaCropModel:
    """
    AquaCrop model class.

    This is the main class of the AquaCrop model.
    It is in charge of executing all the operations.

    *Arguments:*\n
    `sim_start_time` : `date YYYY/MM/DD` : Simulation start date
    `sim_end_time` : `date YYYY/MM/DD` : Simulation end date
    `weather_df`: `pandas.DataFrame` : Weather data (TODO: SPECIFY DATA TYPE)
    `soil`: `Soil Object `: Soil object contains paramaters and variables of the soil
        used in the simulation
    `crop`: `Crop Object`: Crop object contains Paramaters and variables of the crop used
        in the simulation
    `initial_water_content`: `InitialWaterContent Object` : Defines water content at start
        of simulation
    `irrigation_management`: `IrrigationManagement Object`: Defines irrigation strategy
    `field_management`: `FieldMngt Obj : Defines field management options`
    `fallow_field_management`: TODO: Define it.
    `groundwater`: `GroundWater object`: Stores information on water table params
    `planting_dates`: TODO: This is not used.
    `harvest_dates`:  TODO: This is not used.
    `co2_concentration`: `CO2 object`: Defines CO2 concentrations
    """

    def __init__(
        self,
        sim_start_time,
        sim_end_time,
        weather_df,
        soil,
        crop,
        initial_water_content,
        irrigation_management=None,
        field_management=None,
        fallow_field_management=None,
        groundwater=None,
        planting_dates=None,
        harvest_dates=None,
        co2_concentration=None,
    ):

        self.sim_start_time = sim_start_time
        self.sim_end_time = sim_end_time
        self.weather_df = weather_df
        self.soil = soil
        self.crop = crop
        self.initial_water_content = initial_water_content
        self.planting_dates = planting_dates
        self.harvest_dates = harvest_dates
        self.co2_concentration = co2_concentration

        self.irrigation_management = irrigation_management
        self.field_management = field_management
        self.fallow_field_management = fallow_field_management
        self.groundwater = groundwater
        self.steps_are_finished = False

        if irrigation_management is None:
            self.irrigation_management = IrrigationManagement(IrrMethod=0)
        if field_management is None:
            self.field_management = FieldMngt()
        if fallow_field_management is None:
            self.fallow_field_management = FieldMngt()
        if groundwater is None:
            self.groundwater = GroundWater()

        # Attributes initialised later
        self.clock_struct = None
        self.param_struct = None
        self.init_cond = None
        self.outputs = None
        self.weather = None

    def _initialize(
        self,
    ):
        """
        Initialise all model variables
        """

        # define model runtime
        self.clock_struct = read_clock_paramaters(
            self.sim_start_time, self.sim_end_time
        )

        # get weather data
        self.weather_df = read_weather_inputs(self.clock_struct, self.weather_df)

        # read model params
        self.clock_struct, self.param_struct = read_model_parameters(
            self.clock_struct, self.soil, self.crop, self.weather_df
        )

        # read irrigation management
        self.param_struct = read_irrigation_management(
            self.param_struct, self.irrigation_management, self.clock_struct
        )

        # read field management
        self.param_struct = read_field_management(
            self.param_struct, self.field_management, self.fallow_field_management
        )

        # read groundwater table
        self.param_struct = read_groundwater_table(
            self.param_struct, self.groundwater, self.clock_struct
        )

        # Compute additional variables
        self.param_struct.CO2concAdj = self.co2_concentration
        self.param_struct = compute_variables(
            self.param_struct, self.weather_df, self.clock_struct
        )

        # read, calculate inital conditions
        self.param_struct, self.init_cond = read_model_initial_conditions(
            self.param_struct, self.clock_struct, self.initial_water_content
        )

        self.param_struct = create_soil_profile(self.param_struct)

        # Outputs results (water_flux, crop_growth, final_stats)
        self.outputs = Output(self.clock_struct.time_span, self.init_cond.th)

        # save model weather to init_cond
        self.weather = self.weather_df.values

    def run_model(self, num_steps=1, till_termination=False):
        """
        This function is responsible for executing the model.

        *Arguments:*\n
        `num_steps`: `int` : Number of stepts (Days) to be executed.
        `till_termination`: `boolean` : Run the simulation to completion

        *Returns:*
        Dictionary:
        `finished`: `boolean`: Informs if the simulation is finished
        `results`: `Output object`: All results of the simulation
        """

        self._initialize()

        if till_termination:

            while self.clock_struct.model_is_finished is False:

                (
                    self.clock_struct,
                    self.init_cond,
                    self.param_struct,
                    self.outputs,
                ) = self.perform_timestep()

            return {"finished": True, "results": self.outputs}
        else:

            for i in range(num_steps):

                if i == range(num_steps)[-1]:
                    self.steps_are_finished = True
                (
                    self.clock_struct,
                    self.init_cond,
                    self.param_struct,
                    self.outputs,
                ) = self.perform_timestep()

                if self.clock_struct.model_is_finished:
                    return {"finished": True, "results": self.outputs}

            return {"finished": False, "results": self.outputs}

    def perform_timestep(self):

        """
        Function to run a single time-step (day) calculation of AquaCrop-OS

        """

        # extract weather data for current timestep
        weather_step = weather_data_current_timestep(
            self.weather, self.clock_struct.time_step_counter
        )

        # Get model solution_single_time_step
        new_cond, param_struct, outputs = solution_single_time_step(
            self.init_cond,
            self.param_struct,
            self.clock_struct,
            weather_step,
            self.outputs,
        )

        # Check model termination
        clock_struct = self.clock_struct
        clock_struct.model_is_finished = check_model_is_finished(
            self.clock_struct.step_end_time,
            self.clock_struct.simulation_end_date,
            self.clock_struct.model_is_finished,
            self.clock_struct.season_counter,
            self.clock_struct.n_seasons,
            new_cond.HarvestFlag,
        )

        # Update time step
        clock_struct, init_cond, param_struct = update_time(
            clock_struct, new_cond, param_struct, self.weather
        )

        # Create  outputs dataframes when model is finished
        (
            outputs.water_flux,
            outputs.water_storage,
            outputs.crop_growth,
        ) = outputs_when_model_is_finished(
            clock_struct.model_is_finished,
            outputs.water_flux,
            outputs.water_storage,
            outputs.crop_growth,
            self.steps_are_finished,
        )

        return clock_struct, init_cond, param_struct, outputs


def weather_data_current_timestep(weather, time_step_counter):
    """
    Extract weather data for current timestep
    """
    return weather[time_step_counter]
