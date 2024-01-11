import numpy as np
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.soilProfile import SoilProfileNT
    from aquacrop.entities.initParamVariables import InitialCondition
    from numpy import ndarray




def capillary_rise(
    prof: "SoilProfileNT",
    Soil_nLayer: int,
    Soil_fshape_cr: float,
    NewCond: "InitialCondition",
    FluxOut: "ndarray",
    water_table_presence: int,
    ) -> Tuple["InitialCondition", float]:
    """
    Function to calculate capillary rise from a shallow groundwater table


    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=61" target="_blank">Reference Manual: capillary rise calculations</a> (pg. 52-61)


    Arguments:


        prof (SoilProfileNT): Soil profile named tuple

        Soil_nLayer (int): number of soil layers

        Soil_fshape_cr (float): Capillary rise shape factor

        NewCond (InitialCondition): InitialCondition object containing model paramaters

        FluxOut (numpy.array): Flux of water out of each soil compartment

        water_table_presence (int): water_table present (1:yes, 0:no)


    Returns:

        NewCond (InitialCondition): InitCond object containing updated model paramaters

        CrTot (float): Total Capillary rise





    """

    ## Get groundwater table elevation on current day ##
    z_gw = NewCond.z_gw

    ## Calculate capillary rise ##
    if water_table_presence == 0:  # No water table present
        # Capillary rise is zero
        CrTot = 0
    elif water_table_presence == 1:  # Water table present
        # Get maximum capillary rise for bottom compartment
        zBot = prof.dzsum[-1]
        zBotMid = prof.zMid[-1]
        prof = prof
        if (prof.Ksat[-1] > 0) and (z_gw > 0) and ((z_gw - zBotMid) < 4):
            if zBotMid >= z_gw:
                MaxCR = 99
            else:
                MaxCR = np.exp((np.log(z_gw - zBotMid) - prof.bCR[-1]) / prof.aCR[-1])
                if MaxCR > 99:
                    MaxCR = 99

        else:
            MaxCR = 0

        ######################### this needs fixing, will currently break####################

        # # Find top of next soil layer that is not within modelled soil profile
        zTopLayer = 0
        for layeri in np.sort(np.unique(prof.Layer)):
            # Calculate layer thickness
            l_idx = np.argwhere(prof.Layer==layeri).flatten()

            LayThk = prof.dz[l_idx].sum()
            zTopLayer = zTopLayer+LayThk

        # Check for restrictions on upward flow caused by properties of
        # compartments that are not modelled in the soil water balance
        layeri = prof.Layer[-1]

        assert layeri == Soil_nLayer

        while (zTopLayer < z_gw) and (layeri < Soil_nLayer):
            # this needs fixing, will currently break

            
            compdf = prof.Layer[layeri]
            if (compdf.Ksat > 0) and (z_gw > 0) and ((z_gw-zTopLayer) < 4):
                if zTopLayer >= z_gw:
                    LimCR = 99
                else:
                    LimCR = np.exp((np.log(z_gw-zTopLayer)-compdf.bCR)/compdf.aCR)
                    if LimCR > 99:
                        LimCR = 99

            else:
                LimCR = 0

            if MaxCR > LimCR:
                MaxCR = LimCR

            zTopLayer = zTopLayer+compdf.dz

            layeri = layeri+1 # could be that the increment should be at the end of the loop rather than at the start (bad indexing otherwise)

        #####################################################################################

        # Calculate capillary rise
        compi = len(prof.Comp) - 1  # Start at bottom of root zone
        WCr = 0  # Capillary rise counter
        while (round(MaxCR * 1000) > 0) and (compi > -1) and (round(FluxOut[compi] * 1000) == 0):
            # Proceed upwards until maximum capillary rise occurs, soil surface
            # is reached, or encounter a compartment where downward
            # drainage/infiltration has already occurred on current day
            # Find layer of current compartment
            # Calculate driving force
            if (NewCond.th[compi] >= prof.th_wp[compi]) and (Soil_fshape_cr > 0):
                Df = 1 - (
                    (
                        (NewCond.th[compi] - prof.th_wp[compi])
                        / (NewCond.th_fc_Adj[compi] - prof.th_wp[compi])
                    )
                    ** Soil_fshape_cr
                )
                if Df > 1:
                    Df = 1
                elif Df < 0:
                    Df = 0

            else:
                Df = 1

            # Calculate relative hydraulic conductivity
            thThr = (prof.th_wp[compi] + prof.th_fc[compi]) / 2
            if NewCond.th[compi] < thThr:
                if (NewCond.th[compi] <= prof.th_wp[compi]) or (thThr <= prof.th_wp[compi]):
                    Krel = 0
                else:
                    Krel = (NewCond.th[compi] - prof.th_wp[compi]) / (thThr - prof.th_wp[compi])

            else:
                Krel = 1

            # Check if room is available to store water from capillary rise
            dth = round(NewCond.th_fc_Adj[compi] - NewCond.th[compi],4)

            # Store water if room is available
            if (dth > 0) and ((zBot - prof.dz[compi] / 2) < z_gw):
                dthMax = Krel * Df * MaxCR / (1000 * prof.dz[compi])
                if dth >= dthMax:
                    NewCond.th[compi] = NewCond.th[compi] + dthMax
                    CRcomp = dthMax * 1000 * prof.dz[compi]
                    MaxCR = 0
                else:
                    NewCond.th[compi] = NewCond.th_fc_Adj[compi]
                    CRcomp = dth * 1000 * prof.dz[compi]
                    MaxCR = (Krel * MaxCR) - CRcomp

                WCr = WCr + CRcomp

            # Update bottom elevation of compartment
            zBot = zBot - prof.dz[compi]
            # Update compartment and layer counters
            compi = compi - 1
            # Update restriction on maximum capillary rise
            if compi > -1:

                zBotMid = zBot - (prof.dz[compi] / 2)
                if (prof.Ksat[compi] > 0) and (z_gw > 0) and ((z_gw - zBotMid) < 4):
                    if zBotMid >= z_gw:
                        LimCR = 99
                    else:
                        LimCR = np.exp((np.log(z_gw - zBotMid) - prof.bCR[compi]) / prof.aCR[compi])
                        if LimCR > 99:
                            LimCR = 99

                else:
                    LimCR = 0

                if MaxCR > LimCR:
                    MaxCR = LimCR

        # Store total depth of capillary rise
        CrTot = WCr

    return NewCond, CrTot
