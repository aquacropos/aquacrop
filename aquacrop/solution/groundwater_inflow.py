import numpy as np




def groundwater_inflow(prof, NewCond):
    """
    Function to calculate capillary rise in the presence of a shallow groundwater table

    <a href="../pdfs/ac_ref_man_3.pdf#page=61" target="_blank">Reference Manual: capillary rise calculations</a> (pg. 52-61)


    *Arguments:*



    `Soil`: `SoilClass` : Soil object containing soil paramaters

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters

    `GwIn`: `float` : Groundwater inflow


    """

    ## Store initial conditions for updating ##
    GwIn = 0

    ## Perform calculations ##
    if NewCond.WTinSoil == True:
        # Water table in soil profile. Calculate horizontal inflow.
        # Get groundwater table elevation on current day
        zGW = NewCond.zGW

        # Find compartment mid-points
        zMid = prof.zMid
        # For compartments below water table, set to saturation #
        idx = np.argwhere(zMid >= zGW).flatten()[0]
        for ii in range(idx, len(prof.Comp)):
            # Get soil layer
            if NewCond.th[ii] < prof.th_s[ii]:
                # Update water content
                dth = prof.th_s[ii] - NewCond.th[ii]
                NewCond.th[ii] = prof.th_s[ii]
                # Update groundwater inflow
                GwIn = GwIn + (dth * 1000 * prof.dz[ii])

    return NewCond, GwIn


