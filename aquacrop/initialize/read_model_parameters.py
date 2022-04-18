import numpy as np
import pandas as pd
from ..entities.paramStruct import ParamStructClass
from .compute_crop_calendar import compute_crop_calendar




def read_model_parameters(ClockStruct, Soil, Crop, weather_df):
    """
    Finalise soil and crop paramaters including planting and harvest dates
    save to new object ParamStruct


    *Arguments:*\n

    `ClockStruct` : `ClockStructClass`:  time params

    `Soil` : `SoilClass` :  soil object

    `Crop` : `CropClass` :  crop object

    `planting_dates` : `list` :  list of datetimes

    `harvest_dates` : `list` : list of datetimes

    *Returns:*

    `ClockStruct` : `ClockStructClass` : updated time paramaters

    `ParamStruct` : `ParamStructClass` :  Contains model crop and soil paramaters

    """
    # create ParamStruct object
    ParamStruct = ParamStructClass()

    Soil.fill_nan()

    # Assign Soil object to ParamStruct
    ParamStruct.Soil = Soil

    while Soil.zSoil < Crop.Zmax + 0.1:
        for i in Soil.profile.index[::-1]:
            if Soil.profile.loc[i, "dz"] < 0.25:
                Soil.profile.loc[i, "dz"] += 0.1
                Soil.fill_nan()
                break

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
    #         paramStruct.SpecifiedPlantcalendar = 'Y'
    #     else:
    #         paramStruct.SpecifiedPlantcalendar = 'N'

    #     # add crop list to paramStruct
    #     paramStruct.cropList = cropList

    ############################
    # plant and harvest times
    ############################

    #     # find planting and harvest dates
    #     # check if there is more than 1 crop or multiple plant dates in sim year
    #     if paramStruct.SpecifiedPlantcalendar == "Y":
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
    CropList = [Crop]
    ParamStruct.CropList = CropList
    ParamStruct.NCrops = 1

    # Get start and end years for full simulation
    SimStartDate = ClockStruct.simulation_start_date
    SimEndDate = ClockStruct.simulation_end_date

    # extract the years and months of these dates
    start_end_years = pd.DatetimeIndex([SimStartDate, SimEndDate]).year
    start_end_months = pd.DatetimeIndex([SimStartDate, SimEndDate]).month

    if Crop.harvest_date == None:
        Crop = compute_crop_calendar(Crop, ClockStruct, weather_df)
        mature = int(Crop.MaturityCD + 30)
        plant = pd.to_datetime("1990/" + Crop.planting_date)
        harv = plant + np.timedelta64(mature, "D")
        new_harvest_date = str(harv.month) + "/" + str(harv.day)
        Crop.harvest_date = new_harvest_date

    # check if crop growing season runs over calander year
    # Planting and harvest dates are in days/months format so just add arbitrary year
    singleYear = pd.to_datetime("1990/" + Crop.planting_date) < pd.to_datetime(
        "1990/" + Crop.harvest_date
    )
    if singleYear:
        # if normal year

        # specify the planting and harvest years as normal
        plant_years = list(range(start_end_years[0], start_end_years[1] + 1))
        harvest_years = plant_years
    else:
        # if it takes over a year then the plant year finishes 1 year before end of sim
        # and harvest year starts 1 year after sim start

        if pd.to_datetime(str(start_end_years[1] + 2) + "/" + Crop.harvest_date) < SimEndDate:

            # specify shifted planting and harvest years
            plant_years = list(range(start_end_years[0], start_end_years[1] + 1))
            harvest_years = list(range(start_end_years[0] + 1, start_end_years[1] + 2))
        else:

            plant_years = list(range(start_end_years[0], start_end_years[1]))
            harvest_years = list(range(start_end_years[0] + 1, start_end_years[1] + 1))

    # Correct for partial first growing season (may occur when simulating
    # off-season soil water balance)
    if (
        pd.to_datetime(str(plant_years[0]) + "/" + Crop.planting_date)
        < ClockStruct.simulation_start_date
    ):
        # shift everything by 1 year
        plant_years = plant_years[1:]
        harvest_years = harvest_years[1:]

    # ensure number of planting and harvest years are the same
    assert len(plant_years) == len(harvest_years)

    # create lists to hold variables
    planting_dates = []
    harvest_dates = []
    CropChoices = []

    # save full harvest/planting dates and crop choices to lists
    for i in range(len(plant_years)):
        planting_dates.append(str(plant_years[i]) + "/" + ParamStruct.CropList[0].planting_date)
        harvest_dates.append(str(harvest_years[i]) + "/" + ParamStruct.CropList[0].harvest_date)
        CropChoices.append(ParamStruct.CropList[0].Name)

    # save crop choices
    ParamStruct.CropChoices = list(CropChoices)

    # save clock paramaters
    ClockStruct.planting_dates = pd.to_datetime(planting_dates)
    ClockStruct.harvest_dates = pd.to_datetime(harvest_dates)
    ClockStruct.n_seasons = len(planting_dates)

    # Initialise growing season counter
    if pd.to_datetime(ClockStruct.step_start_time) == ClockStruct.planting_dates[0]:
        ClockStruct.season_counter = 0
    else:
        ClockStruct.season_counter = -1

    # return the FileLocations object as i have added some elements
    return ClockStruct, ParamStruct



# def changeThicknessSoilCompartmentToReachMaxRootDepth(soil, crop):
#     # -+-+- Change soil thikness -+-+-+-
#     # This loop go to the last soil index and added 0.1 meter if
#     # the soil is less than 0.25m until the max crop soil is reached
#     while soil.zSoil < crop.zMax + 0.1:
#         for i in soil.profile.index[::-1]:
#             # print(soil.profile.loc[i, "dz"])
#             # print(soil.profile.loc[i])

#             if soil.profile.loc[i, "dz"] < 0.25:
#                 soil.profile.loc[i, "dz"] += 0.1
#                 soil.fill_nan()
#                 break
#     return soil


# def cropgrowingSeasonOccursInTheSameYear(crop):
#     # check if crop growing season runs over calendar year
#     # Planting and harvest dates are in days/months format so just add arbitrary year
#     if(pd.to_datetime("1990/" + crop.plantingDate) < pd.to_datetime(
#         "1990/" + crop.harvestDate
#     )):
#         return True
#     return False


# def plantAndHarvestYearsForSingleYearCrop(start_end_years):
#     plant_harvest_years = list(
#         range(start_end_years[0], start_end_years[1] + 1))
#     return plant_harvest_years


# def plantAndHarvestYearsForMultiplesYearCrop(harvestDate, SimEndDate, start_end_years):
#     # if it takes over a year then the plant year finishes 1 year before end of sim
#     # and harvest year starts 1 year after sim start
#     if pd.to_datetime(str(start_end_years[1] + 2) + "/" + harvestDate) < SimEndDate:

#         # specify shifted planting and harvest years
#         plant_years = list(
#             range(start_end_years[0], start_end_years[1] + 1))
#         harvest_years = list(
#             range(start_end_years[0] + 1, start_end_years[1] + 2))
#     else:
#         plant_years = list(range(start_end_years[0], start_end_years[1]))
#         harvest_years = list(
#             range(start_end_years[0] + 1, start_end_years[1] + 1))

#     return plant_years, harvest_years


# def CorrectForPartialFirstgrowingSeason(plantingDate, simulationStartDate, plant_years, harvest_years):
#     if (
#         pd.to_datetime(str(plant_years[0]) + "/" + plantingDate)
#         < simulationStartDate
#     ):
#         # shift everything by 1 year
#         plant_years = plant_years[1:]
#         harvest_years = harvest_years[1:]
#     return plant_years, harvest_years

# def createListsToHoldVariables(plant_years, harvest_years, plantingDate, harvestDate, CropName):
#  # create lists to hold variables
#     plantingDates = []
#     harvestDates = []
#     cropChoices = []

#     # save full harvest/planting dates and crop choices to lists
#     for i in range(len(plant_years)):
#         plantingDates.append(
#             str(plant_years[i]) + "/" + plantingDate)
#         harvestDates.append(
#             str(harvest_years[i]) + "/" + harvestDate)
#         cropChoices.append(CropName)
#     return plantingDates, harvestDates, cropChoices