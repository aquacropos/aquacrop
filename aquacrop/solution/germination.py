import numpy as np




def germination(InitCond, Soil_zGerm, prof, Crop_GermThr, Crop_PlantMethod, gdd, growing_season):
    """
    Function to check if crop has germinated


    <a href="../pdfs/ac_ref_man_3.pdf#page=32" target="_blank">Reference Manual: germination condition</a> (pg. 23)


    *Arguments:*


    `InitCond`: `InitialCondition` : InitCond object containing model paramaters

    `Soil_zGerm`: `float` : Soil depth affecting germination

    `prof`: `SoilProfile` : Soil object containing soil paramaters

    `Crop_GermThr`: `float` : Crop germination threshold

    `Crop_PlantMethod`: `bool` : sown as seedling True or False

    `gdd`: `float` : Number of Growing Degree Days on current day

    `growing_season`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitialCondition` : InitCond object containing updated model paramaters







    """

    ## Store initial conditions in new structure for updating ##
    NewCond = InitCond

    ## Check for germination (if in growing season) ##
    if growing_season == True:

        if (NewCond.germination == False):
            # Find compartments covered by top soil layer affecting germination
            comp_sto = np.argwhere(prof.dzsum >= Soil_zGerm).flatten()[0]
            # Calculate water content in top soil layer
            Wr = 0
            WrFC = 0
            WrWP = 0
            for ii in range(comp_sto + 1):
                # Get soil layer
                # Determine fraction of compartment covered by top soil layer
                if prof.dzsum[ii] > Soil_zGerm:
                    factor = 1 - ((prof.dzsum[ii] - Soil_zGerm) / prof.dz[ii])
                else:
                    factor = 1

                # Increment actual water storage (mm)
                Wr = Wr + round(factor * 1000 * InitCond.th[ii] * prof.dz[ii], 3)
                # Increment water storage at field capacity (mm)
                WrFC = WrFC + round(factor * 1000 * prof.th_fc[ii] * prof.dz[ii], 3)
                # Increment water storage at permanent wilting point (mm)
                WrWP = WrWP + round(factor * 1000 * prof.th_wp[ii] * prof.dz[ii], 3)

            # Limit actual water storage to not be less than zero
            if Wr < 0:
                Wr = 0

            # Calculate proportional water content
            WcProp = 1 - ((WrFC - Wr) / (WrFC - WrWP))

            # Check if water content is above germination threshold
            if (WcProp >= Crop_GermThr):
                # Crop has germinated
                NewCond.germination = True
                # If crop sown as seedling, turn on seedling protection
                if Crop_PlantMethod == True:
                    NewCond.protected_seed = True
                else:
                    # Crop is transplanted so no protection
                    NewCond.protected_seed = False

            # Increment delayed growth time counters if germination is yet to
            # occur, and also set seed protection to False if yet to germinate
            else:
                NewCond.delayed_cds = InitCond.delayed_cds + 1
                NewCond.delayed_gdds = InitCond.delayed_gdds + gdd
                NewCond.protected_seed = False

    else:
        # Not in growing season so no germination calculation is performed.
        NewCond.germination = False
        NewCond.protected_seed = False
        NewCond.delayed_cds = 0
        NewCond.delayed_gdds = 0

    return NewCond

