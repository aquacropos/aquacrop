"""
This file contains the AquacropModel class that runs the simulation.
"""
import os
import time

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
    function to read in _weather data and return a dataframe containing
    the _weather data

    *Arguments:*\n
    `weather_file_path` : `str` :  file location of _weather data

    *Returns:*

    `weather_df`: `pandas.DataFrame` :  _weather data for simulation period

    """

    weather_df = pd.read_csv(weather_file_path, header=0, delim_whitespace=True)

    assert len(weather_df.columns) == 7

    # rename the columns
    weather_df.columns = str(
        "Day Month Year MinTemp MaxTemp Precipitation ReferenceET"
    ).split()

    # put the _weather dates into datetime format
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

        if irrigation_management is None:
            self.irrigation_management = IrrigationManagement(IrrMethod=0)
        if field_management is None:
            self.field_management = FieldMngt()
        if fallow_field_management is None:
            self.fallow_field_management = FieldMngt()
        if groundwater is None:
            self.groundwater = GroundWater()

        # Model parameters
        self.__steps_are_finished = False
        self.__has_model_executed = False  # Determines if the model has been run
        self.__has_model_finished = False  # Determines if the model is finished
        self.__start_model_execution = None  # Time when the execution start
        self.__end_model_execution = None  # Time when the execution end
        # Attributes initialised later
        self._clock_struct = None
        self._param_struct = None
        self._init_cond = None
        self._outputs = None
        self._weather = None

    def _initialize(self):
        """
        Initialise all model variables
        """

        # define model runtime
        self._clock_struct = read_clock_paramaters(
            self.sim_start_time, self.sim_end_time
        )

        # get _weather data
        self.weather_df = read_weather_inputs(self._clock_struct, self.weather_df)

        # read model params
        self._clock_struct, self._param_struct = read_model_parameters(
            self._clock_struct, self.soil, self.crop, self.weather_df
        )

        # read irrigation management
        self._param_struct = read_irrigation_management(
            self._param_struct, self.irrigation_management, self._clock_struct
        )

        # read field management
        self._param_struct = read_field_management(
            self._param_struct, self.field_management, self.fallow_field_management
        )

        # read groundwater table
        self._param_struct = read_groundwater_table(
            self._param_struct, self.groundwater, self._clock_struct
        )

        # Compute additional variables
        self._param_struct.CO2concAdj = self.co2_concentration
        self._param_struct = compute_variables(
            self._param_struct, self.weather_df, self._clock_struct
        )

        # read, calculate inital conditions
        self._param_struct, self._init_cond = read_model_initial_conditions(
            self._param_struct, self._clock_struct, self.initial_water_content
        )

        self._param_struct = create_soil_profile(self._param_struct)

        # Outputs results (water_flux, crop_growth, final_stats)
        self._outputs = Output(self._clock_struct.time_span, self._init_cond.th)

        # save model _weather to _init_cond
        self._weather = self.weather_df.values

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
            self.__start_model_execution = time.time()
            while self._clock_struct.model_is_finished is False:

                (
                    self._clock_struct,
                    self._init_cond,
                    self._param_struct,
                    self._outputs,
                ) = self._perform_timestep()
            self.__end_model_execution = time.time()
            self.__has_model_executed = True
            self.__has_model_finished = True
            return True
        else:
            self.__start_model_execution = time.time()
            for i in range(num_steps):

                if i == range(num_steps)[-1]:
                    self.__steps_are_finished = True
                (
                    self._clock_struct,
                    self._init_cond,
                    self._param_struct,
                    self._outputs,
                ) = self._perform_timestep()

                if self._clock_struct.model_is_finished:
                    self.__end_model_execution = time.time()
                    self.__has_model_executed = True
                    self.__has_model_finished = True
                    return True

            self.__end_model_execution = time.time()
            self.__has_model_executed = True
            self.__has_model_finished = False
            return True

    def _perform_timestep(self):

        """
        Function to run a single time-step (day) calculation of AquaCrop-OS

        """

        # extract _weather data for current timestep
        weather_step = _weather_data_current_timestep(
            self._weather, self._clock_struct.time_step_counter
        )

        # Get model solution_single_time_step
        new_cond, param_struct, outputs = solution_single_time_step(
            self._init_cond,
            self._param_struct,
            self._clock_struct,
            weather_step,
            self._outputs,
        )

        # Check model termination
        clock_struct = self._clock_struct
        clock_struct.model_is_finished = check_model_is_finished(
            self._clock_struct.step_end_time,
            self._clock_struct.simulation_end_date,
            self._clock_struct.model_is_finished,
            self._clock_struct.season_counter,
            self._clock_struct.n_seasons,
            new_cond.HarvestFlag,
        )

        # Update time step
        clock_struct, _init_cond, param_struct = update_time(
            clock_struct, new_cond, param_struct, self._weather
        )

        # Create  _outputsdataframes when model is finished
        final_water_flux_growth_outputs = outputs_when_model_is_finished(
            clock_struct.model_is_finished,
            outputs.water_flux,
            outputs.water_storage,
            outputs.crop_growth,
            self.__steps_are_finished,
        )

        if final_water_flux_growth_outputs is not False:
            (
                outputs.water_flux,
                outputs.water_storage,
                outputs.crop_growth,
            ) = final_water_flux_growth_outputs

        return clock_struct, _init_cond, param_struct, outputs

    def get_final_statistics(self):
        """
        Return all the simulation results
        """
        if self.__has_model_executed:
            if self.__has_model_finished:
                return self._outputs.final_stats
            else:
                return False  # If the model is not finished, the results are not generated.
        else:
            raise ValueError(
                "You cannot get results without running the model. Please execute the run_model() method."
            )

    def get_water_storage(self):
        """
        Return water storage in soil results
        """
        if self.__has_model_executed:
            return self._outputs.water_storage
        else:
            raise ValueError(
                "You cannot get results without running the model. Please execute the run_model() method."
            )

    def get_water_flux(self):
        """
        Return water flux results
        """
        if self.__has_model_executed:
            return self._outputs.water_flux
        else:
            raise ValueError(
                "You cannot get results without running the model. Please execute the run_model() method."
            )

    def get_crop_growth(self):
        """
        Return crop growth results
        """
        if self.__has_model_executed:
            return self._outputs.crop_growth
        else:
            raise ValueError(
                "You cannot get results without running the model. Please execute the run_model() method."
            )

    def get_additional_information(self):
        """
        Additional model information.

           Returns:
               dict:
                   has_model_finished (boolean): Determines if the model is finished
                   execution_time : Time taken for the model to run

        """
        if self.__has_model_executed:
            return {
                "has_model_finished": self.__has_model_finished,
                "execution_time": self.__end_model_execution
                - self.__start_model_execution,
            }
        else:
            raise ValueError(
                "You cannot get results without running the model. Please execute the run_model() method."
            )


def _weather_data_current_timestep(_weather, time_step_counter):
    """
    Extract _weather data for current timestep
    """
    return _weather[time_step_counter]
