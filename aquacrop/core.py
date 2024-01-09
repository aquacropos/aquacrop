"""
This file contains the AquacropModel class that runs the simulation.
"""
import time
import datetime
import os
import logging
import warnings
from typing import Dict, Union, Optional, Tuple, TYPE_CHECKING
from .scripts.checkIfPackageIsCompiled import compile_all_AOT_files

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from pandas import DataFrame
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.co2 import CO2
    from aquacrop.entities.crop import Crop
    from aquacrop.entities.initParamVariables import InitialCondition
    from aquacrop.entities.inititalWaterContent import InitialWaterContent
    from aquacrop.entities.paramStruct import ParamStruct
    from aquacrop.entities.soil import Soil


# Important: This code is necessary to check if the AOT files are compiled.
if os.getenv("DEVELOPMENT"):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logging.info("Running the simulation in development mode.")
else:
    compile_all_AOT_files()


# pylint: disable=wrong-import-position
from .entities.co2 import CO2
from .entities.fieldManagement import FieldMngt
from .entities.groundWater import GroundWater
from .entities.irrigationManagement import IrrigationManagement
from .entities.output import Output
from .initialize.compute_variables import compute_variables
from .initialize.create_soil_profile import create_soil_profile
from .initialize.read_clocks_parameters import read_clock_parameters
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

class AquaCropModel:
    """
    This is the main class of the AquaCrop-OSPy model.
    It is in charge of executing all the operations.

    Parameters:

        sim_start_time (str): YYYY/MM/DD, Simulation start date

        sim_end_time (str): date YYYY/MM/DD, Simulation end date

        weather_df: daily weather data , created using prepare_weather

        soil: Soil object contains paramaters and variables of the soil
                used in the simulation

        crop: Crop object contains Paramaters and variables of the crop used
                in the simulation

        initial_water_content: Defines water content at start of simulation

        irrigation_management: Defines irrigation strategy

        field_management: Defines field management options

        fallow_field_management: Defines field management options during fallow period

        groundwater: Stores information on water table parameters

        co2_concentration: Defines CO2 concentrations

        off_season: (True) simulate off-season or (False) skip ahead to start of 
                    next growing season


    """

    # Model parameters
    __steps_are_finished: bool = False  # True if all steps of the simulation are done.
    __has_model_executed: bool = False  # Determines if the model has been run
    __has_model_finished: bool = False  # Determines if the model is finished
    __start_model_execution: float = 0.0  # Time when the execution start
    __end_model_execution: float = 0.0  # Time when the execution end
    # Attributes initialised later
    _clock_struct: "ClockStruct"
    _param_struct: "ParamStruct"
    _init_cond: "InitialCondition"
    _outputs: "Output"
    _weather: "DataFrame"

    def __init__(
        self,
        sim_start_time: str,
        sim_end_time: str,
        weather_df: "DataFrame",
        soil: "Soil",
        crop: "Crop",
        initial_water_content: "InitialWaterContent",
        irrigation_management: Optional["IrrigationManagement"] = None,
        field_management: Optional["FieldMngt"] = None,
        fallow_field_management: Optional["FieldMngt"] = None,
        groundwater: Optional["GroundWater"] = None,
        co2_concentration: Optional["CO2"] = None,
        off_season: bool=False,
    ) -> None:

        self.sim_start_time = sim_start_time
        self.sim_end_time = sim_end_time
        self.weather_df = weather_df
        self.soil = soil
        self.crop = crop
        self.initial_water_content = initial_water_content   
        self.co2_concentration = co2_concentration
        self.off_season = off_season
      
        self.irrigation_management = irrigation_management
        self.field_management = field_management
        self.fallow_field_management = fallow_field_management
        self.groundwater = groundwater

        if irrigation_management is None:
            self.irrigation_management = IrrigationManagement(irrigation_method=0)
        if field_management is None:
            self.field_management = FieldMngt()
        if fallow_field_management is None:
            self.fallow_field_management = FieldMngt()
        if groundwater is None:
            self.groundwater = GroundWater()
        if co2_concentration is None:
            self.co2_concentration = CO2()

    @property
    def sim_start_time(self) -> str:
        """
        Return sim start date
        """
        return self._sim_start_time

    @sim_start_time.setter
    def sim_start_time(self, value: str) -> None:
        """
        Check if sim start date is in a correct format.
        """

        if _sim_date_format_is_correct(value) is not False:
            self._sim_start_time = value
        else:
            raise ValueError("sim_start_time format must be 'YYYY/MM/DD'")

    @property
    def sim_end_time(self) -> str:
        """
        Return sim end date
        """
        return self._sim_end_time

    @sim_end_time.setter
    def sim_end_time(self, value: str) -> None:
        """
        Check if sim end date is in a correct format.
        """
        if _sim_date_format_is_correct(value) is not False:
            self._sim_end_time = value
        else:
            raise ValueError("sim_end_time format must be 'YYYY/MM/DD'")

    @property
    def weather_df(self) -> "DataFrame":
        """
        Return weather dataframe
        """
        return self._weather_df

    @weather_df.setter
    def weather_df(self, value: "DataFrame"):
        """
        Check if weather dataframe is in a correct format.
        """
        weather_df_columns = "Date MinTemp MaxTemp Precipitation ReferenceET".split(" ")
        if not all([column in value for column in weather_df_columns]):
            raise ValueError(
                "Error in weather_df format. Check if all the following columns exist "
                + "(Date MinTemp MaxTemp Precipitation ReferenceET)."
            )

        self._weather_df = value

    def _initialize(self) -> None:
        """
        Initialise all model variables
        """

        # Initialize ClockStruct object
        self._clock_struct = read_clock_parameters(
            self.sim_start_time, self.sim_end_time, self.off_season
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
        self._param_struct.CO2 = self.co2_concentration
        self._param_struct = compute_variables(
            self._param_struct, self.weather_df, self._clock_struct
        )

        # read, calculate inital conditions
        self._param_struct, self._init_cond = read_model_initial_conditions(
            self._param_struct, self._clock_struct, self.initial_water_content, self.crop
        )

        self._param_struct = create_soil_profile(self._param_struct)

        # Outputs results (water_flux, crop_growth, final_stats)
        self._outputs = Output(self._clock_struct.time_span, self._init_cond.th)

        # save model _weather to _init_cond
        self._weather = self.weather_df.values

    def run_model(
        self,
        num_steps: int = 1,
        till_termination: bool = False,
        initialize_model: bool = True,
        process_outputs: bool = False,
    ) -> bool:
        """
        This function is responsible for executing the model.

        Arguments:

            num_steps: Number of steps (Days) to be executed.

            till_termination: Run the simulation to completion

            initialize_model: Whether to initialize the model \
            (i.e., go back to beginning of season)

            process_outputs: process outputs into dataframe before \
                simulation is finished

        Returns:
            True if finished
        """

        if initialize_model:
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
            if num_steps < 1:
                raise ValueError("num_steps must be equal to or greater than 1.")
            self.__start_model_execution = time.time()
            for i in range(num_steps):

                if (i == range(num_steps)[-1]) and (process_outputs is True):
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

    def _perform_timestep(
        self,
    ) -> Tuple["ClockStruct", "InitialCondition", "ParamStruct", "Output"]:

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
            new_cond.harvest_flag,
        )

        # Update time step
        clock_struct, _init_cond, param_struct = update_time(
            clock_struct, new_cond, param_struct, self._weather, self.crop
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

    def get_simulation_results(self):
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
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )

    def get_water_storage(self):
        """
        Return water storage in soil results
        """
        if self.__has_model_executed:
            return self._outputs.water_storage
        else:
            raise ValueError(
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )

    def get_water_flux(self):
        """
        Return water flux results
        """
        if self.__has_model_executed:
            return self._outputs.water_flux
        else:
            raise ValueError(
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )

    def get_crop_growth(self):
        """
        Return crop growth results
        """
        if self.__has_model_executed:
            return self._outputs.crop_growth
        else:
            raise ValueError(
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )

    def get_additional_information(self) -> Dict[str, Union[bool, float]]:
        """
        Additional model information.

        Returns:
            dict: {has_model_finished,execution_time}

        """
        if self.__has_model_executed:
            return {
                "has_model_finished": self.__has_model_finished,
                "execution_time": self.__end_model_execution
                - self.__start_model_execution,
            }
        else:
            raise ValueError(
                "You cannot get results without running the model. "
                + "Please execute the run_model() method."
            )


def check_iwc_soil_match(iwc_layers: int, soil_layers: int) -> bool:
    """
    This function checks if the number of soil layers is equivalent between the user-specified soil profile and initial water content.
    
    Arguments:
        iwc_layers
        soil_layers
        
    Return:
        boolean: True if number of layers match
    
    """
    if(iwc_layers == soil_layers):
        return True
    else:
        return False
        



def _sim_date_format_is_correct(date: str) -> bool:
    """
    This function checks if the start or end date of the simulation is in the correct format.

    Arguments:
        date

    Return:
        boolean: True if the date is correct.
    """
    format_dates_string = "%Y/%m/%d"
    try:
        datetime.datetime.strptime(date, format_dates_string)
        return True
    except ValueError:
        return False


def _weather_data_current_timestep(_weather, time_step_counter):
    """
    Extract _weather data for current timestep
    """
    return _weather[time_step_counter]
