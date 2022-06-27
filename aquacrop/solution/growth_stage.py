from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.crop import Crop
    from aquacrop.entities.initParamVariables import InitialCondition


def growth_stage(
    Crop: "Crop",
    InitCond: "InitialCondition",
    growing_season: bool,
    ) -> "InitialCondition":
    """
    Function to determine current growth stage of crop

    (used only for irrigation soil moisture thresholds)

    Arguments:

        Crop (Crop): Crop object containing Crop paramaters

        InitCond (InitialCondition): InitCond object containing model paramaters

        growing_season (bool): is growing season (True or Flase)


    Returns:

        NewCond (InitialCondition): InitCond object containing updated model paramaters



    """

    ## Store initial conditions in new structure for updating ##
    NewCond = InitCond

    ## Get growth stage (if in growing season) ##
    if growing_season == True:
        # Adjust time for any delayed growth
        if Crop.CalendarType == 1:
            tAdj = NewCond.dap - NewCond.delayed_cds
        elif Crop.CalendarType == 2:
            tAdj = NewCond.gdd_cum - NewCond.delayed_gdds

        # Update growth stage
        if tAdj <= Crop.Canopy10Pct:
            NewCond.growth_stage = 1
        elif tAdj <= Crop.MaxCanopy:
            NewCond.growth_stage = 2
        elif tAdj <= Crop.Senescence:
            NewCond.growth_stage = 3
        elif tAdj > Crop.Senescence:
            NewCond.growth_stage = 4

    else:
        # Not in growing season so growth stage is set to dummy value
        NewCond.growth_stage = 0

    return NewCond

