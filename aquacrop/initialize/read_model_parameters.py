import numpy as np
import pandas as pd
from ..entities.paramStruct import ParamStruct
from .compute_crop_calendar import compute_crop_calendar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from pandas import DataFrame
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.crop import Crop
    from aquacrop.entities.inititalWaterContent import InitialWaterContent
    from aquacrop.entities.soil import Soil

def read_model_parameters(
    clock_struct: "ClockStruct",
    soil: "Soil",
    crop: "Crop",
    weather_df: "DataFrame"):

    """
    Finalise soil and crop paramaters including planting and harvest dates
    save to new object param_struct


    Arguments:

        clock_struct (ClockStruct):  time params

        soil (Soil):  soil object

        crop (Crop):  crop object

        weather_df (DataFrame): list of datetimes

    Returns:

        clock_struct (ClockStruct): updated time paramaters

        param_struct (ParamStruct):  Contains model crop and soil paramaters

    """
    # create param_struct object
    param_struct = ParamStruct()

    soil.fill_nan()

    # Assign soil object to param_struct
    param_struct.Soil = soil

    while soil.zSoil < crop.Zmax + 0.1:
        for i in soil.profile.index[::-1]:
            if soil.profile.loc[i, "dz"] < 0.25:
                soil.profile.loc[i, "dz"] += 0.1
                soil.fill_nan()
                break

    # TODO: Why all these commented lines? The model does not allow rotations now?
    ###########
    # crop
    ###########

    #     if isinstance(crop, Iterable):
    #         cropList=list(crop)
    #     else:
    #         cropList = [crop]

    #     # assign variables to paramstruct
    #     paramStruct.nCrops = len(cropList)
    #     if paramStruct.nCrops > 1:
    #         paramStruct.SpecifiedPlantcalendar = 'yield_'
    #     else:
    #         paramStruct.SpecifiedPlantcalendar = 'N'

    #     # add crop list to paramStruct
    #     paramStruct.cropList = cropList

    ############################
    # plant and harvest times
    ############################

    #     # find planting and harvest dates
    #     # check if there is more than 1 crop or multiple plant dates in sim year
    #     if paramStruct.SpecifiedPlantcalendar == "yield_":
    #         # if here than crop rotation occours during same period

    #         # create variables from dataframe
    #         plantingDates = pd.to_datetime(planting_dates)
    #         harvestDates = pd.to_datetime(harvest_dates)

    #         if (paramStruct.nCrops > 1):

    #             cropChoices = [crop.name for crop in paramStruct.cropList]

    #         assert len(cropChoices) == len(plantingDates) == len(harvestDates)

    # elif paramStruct.nCrops == 1:
    # Only one crop type considered during simulation - i.e. no rotations
    # either within or between years
    crop_list = [crop]
    param_struct.CropList = crop_list
    param_struct.NCrops = 1

    # Get start and end years for full simulation
    sim_start_date = clock_struct.simulation_start_date
    sim_end_date = clock_struct.simulation_end_date

    if crop.harvest_date is None:
        crop = compute_crop_calendar(
            crop,
            clock_struct.planting_dates,
            clock_struct.simulation_start_date,
            clock_struct.simulation_end_date,
            clock_struct.time_span,
            weather_df,
        )
        mature = int(crop.MaturityCD + 30)
        plant = pd.to_datetime("1990/" + crop.planting_date)
        harv = plant + np.timedelta64(mature, "D")
        new_harvest_date = str(harv.month) + "/" + str(harv.day)
        crop.harvest_date = new_harvest_date

    # extract years from simulation start and end date
    start_end_years = [sim_start_date.year, sim_end_date.year]

    # check if crop growing season runs over calander year
    # Planting and harvest dates are in days/months format so just add arbitrary year
    single_year = pd.to_datetime("1990/" + crop.planting_date) < pd.to_datetime(
        "1990/" + crop.harvest_date
    )

    if single_year:
        # if normal year

        # Check if the simulation in the following year does not exceed planting date.
        mock_simulation_end_date = pd.to_datetime("1990/" + f'{sim_end_date.month}' + "/" + f'{sim_end_date.day}')
        mock_simulation_start_date = pd.to_datetime("1990/" + crop.planting_date)
        last_simulation_year_does_not_start = mock_simulation_end_date <= mock_simulation_start_date

        if last_simulation_year_does_not_start:
            start_end_years[1] = start_end_years[1] - 1

        # specify the planting and harvest years as normal
        plant_years = list(range(start_end_years[0], start_end_years[1] + 1))
        harvest_years = plant_years
    else:
        # if it takes over a year then the plant year finishes 1 year before end of sim
        # and harvest year starts 1 year after sim start

        if (
            pd.to_datetime(str(start_end_years[1] + 2) + "/" + crop.harvest_date)
            < sim_end_date
        ):

            # specify shifted planting and harvest years
            plant_years = list(range(start_end_years[0], start_end_years[1] + 1))
            harvest_years = list(range(start_end_years[0] + 1, start_end_years[1] + 2))
        else:

            plant_years = list(range(start_end_years[0], start_end_years[1]))
            harvest_years = list(range(start_end_years[0] + 1, start_end_years[1] + 1))

    # Correct for partial first growing season (may occur when simulating
    # off-season soil water balance)
    if (
        pd.to_datetime(str(plant_years[0]) + "/" + crop.planting_date)
        < clock_struct.simulation_start_date
    ):
        # shift everything by 1 year
        plant_years = plant_years[1:]
        harvest_years = harvest_years[1:]

    # ensure number of planting and harvest years are the same
    assert len(plant_years) == len(harvest_years)

    # create lists to hold variables
    planting_dates = []
    harvest_dates = []
    crop_choices = []

    # save full harvest/planting dates and crop choices to lists
    for i, _ in enumerate(plant_years):
        planting_dates.append(
            str(plant_years[i]) + "/" + param_struct.CropList[0].planting_date
        )
        harvest_dates.append(
            str(harvest_years[i]) + "/" + param_struct.CropList[0].harvest_date
        )
        crop_choices.append(param_struct.CropList[0].Name)

    # save crop choices
    param_struct.CropChoices = list(crop_choices)

    # save clock paramaters
    clock_struct.planting_dates = pd.to_datetime(planting_dates)
    clock_struct.harvest_dates = pd.to_datetime(harvest_dates)
    clock_struct.n_seasons = len(planting_dates)

    # Initialise growing season counter
    if pd.to_datetime(clock_struct.step_start_time) == clock_struct.planting_dates[0]:
        clock_struct.season_counter = 0
    else:
        clock_struct.season_counter = -1

    # return the FileLocations object as i have added some elements
    return clock_struct, param_struct
