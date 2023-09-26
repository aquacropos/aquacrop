import numpy as np

from typing import Tuple,TYPE_CHECKING



if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.soilProfile import SoilProfileNT
    from aquacrop.entities.initParamVariables import InitialCondition




def groundwater_inflow(
    prof: "SoilProfileNT",
    NewCond: "InitialCondition"
    ) -> Tuple["InitialCondition",float]:
    """
    Function to calculate capillary rise in the presence of a shallow groundwater table

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=61" target="_blank">Reference Manual: capillary rise calculations</a> (pg. 52-61)


    Arguments:

        prof (SoilProfileNT): Soil profile parameters

        NewCond (InitialCondition): model parameters


    Returns:


        NewCond (InitialCondition): InitCond object containing updated model parameters

        GwIn (float): Groundwater inflow


    """

    ## Store initial conditions for updating ##
    GwIn = 0

    ## Perform calculations ##
    if NewCond.wt_in_soil == True:
        # Water table in soil profile. Calculate horizontal inflow.
        # Get groundwater table elevation on current day
        # print(f'Setting z_gw in groundwater_inflow.py as: {NewCond.z_gw}')
        z_gw = NewCond.z_gw

        # Find compartment mid-points
        zMid = prof.zMid

        idx = np.argwhere(zMid >= z_gw).flatten()[0]

        for ii in range(idx, len(prof.Comp)):
            # Get soil layer
            if NewCond.th[ii] < prof.th_s[ii]:
                # Update water content
                dth = prof.th_s[ii] - NewCond.th[ii]
                NewCond.th[ii] = prof.th_s[ii]
                # Update groundwater inflow
                GwIn = GwIn + (dth * 1000 * prof.dz[ii])

    return NewCond, GwIn


