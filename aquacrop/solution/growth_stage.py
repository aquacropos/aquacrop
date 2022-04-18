


def growth_stage(Crop, InitCond, GrowingSeason):
    """
    Function to determine current growth stage of crop

    (used only for irrigation soil moisture thresholds)

    *Arguments:*



    `Crop`: `CropClass` : Crop object containing Crop paramaters

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `GrowingSeason`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters





    """

    ## Store initial conditions in new structure for updating ##
    NewCond = InitCond

    ## Get growth stage (if in growing season) ##
    if GrowingSeason == True:
        # Adjust time for any delayed growth
        if Crop.CalendarType == 1:
            tAdj = NewCond.DAP - NewCond.DelayedCDs
        elif Crop.CalendarType == 2:
            tAdj = NewCond.GDDcum - NewCond.DelayedGDDs

        # Update growth stage
        if tAdj <= Crop.Canopy10Pct:
            NewCond.GrowthStage = 1
        elif tAdj <= Crop.MaxCanopy:
            NewCond.GrowthStage = 2
        elif tAdj <= Crop.Senescence:
            NewCond.GrowthStage = 3
        elif tAdj > Crop.Senescence:
            NewCond.GrowthStage = 4

    else:
        # Not in growing season so growth stage is set to dummy value
        NewCond.GrowthStage = 0

    return NewCond

