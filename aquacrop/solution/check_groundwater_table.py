import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC


try:
    from ..entities.soilProfile import SoilProfileNT_typ_sig
except:
    from entities.soilProfile import SoilProfileNT_typ_sig
# temporary name for compiled module
cc = CC("solution_check_groundwater_table")

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.soilProfile import SoilProfileNT
    from aquacrop.entities.initParamVariables import InitialCondition
    from numpy import ndarray





@cc.export("check_groundwater_table", (SoilProfileNT_typ_sig,f8,f8[:],f8[:],i8,f8))
def check_groundwater_table(
    prof: "SoilProfileNT",
    NewCond_zGW: float,
    NewCond_th: "ndarray",
    NewCond_th_fc_Adj: "ndarray",
    water_table_presence: int,
    z_gw: float,
) -> "ndarray":
    """
    Function to check for presence of a groundwater table, and, if present,
    to adjust compartment water contents and field capacities where necessary

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=61" target="_blank">Reference manual: water table adjustment equations</a> (pg. 52-57)


    Arguments:

        prof (SoilProfileNT): soil profile paramaters

        NewCond_zGW (float): groundwater depth

        NewCond_th (ndarray): water content in each soil commpartment

        NewCond_th_fc_Adj (ndarray): adjusted water content at field capacity

        water_table_presence (int): indicates if water table is present or not

        z_gw (float): groundwater depth

    Returns:

        NewCond_th_fc_Adj (ndarray): adjusted water content at field capacity

        thfcAdj (ndarray): adjusted water content at field capacity



    """
    
    ## Perform calculations (if variable water table is present) ##
    if water_table_presence == 1:

        # Update groundwater conditions for current day
        NewCond_zGW = z_gw

        # Find compartment mid-points
        zMid = prof.zMid

        # Check if water table is within modelled soil profile
        if NewCond_zGW >= 0:
            if len(zMid[zMid >= NewCond_zGW]) == 0:
                NewCond_WTinSoil = False
            else:
                NewCond_WTinSoil = True

        # If water table is in soil profile, adjust water contents
        # if NewCond_WTinSoil == True:
        #     idx = np.argwhere(zMid >= NewCond_zGW).flatten()[0]
        #     for ii in range(idx, len(prof.Comp)):
        #         NewCond_th[ii] = prof.th_s[ii]

        # Adjust compartment field capacity
        compi = len(prof.Comp) - 1
        thfcAdj = np.zeros(compi + 1)
        # Find thFCadj for all compartments
        while compi >= 0:
            if prof.th_fc[compi] <= 0.1:
                Xmax = 1
            else:
                if prof.th_fc[compi] >= 0.3:
                    Xmax = 2
                else:
                    pF = 2 + 0.3 * (prof.th_fc[compi] - 0.1) / 0.2
                    Xmax = (np.exp(pF * np.log(10))) / 100

            if (NewCond_zGW < 0) or ((NewCond_zGW - zMid[compi]) >= Xmax):
                for ii in range(compi + 1):

                    thfcAdj[ii] = prof.th_fc[ii]

                compi = -1
            else:
                if prof.th_fc[compi] >= prof.th_s[compi]:
                    thfcAdj[compi] = prof.th_fc[compi]
                else:
                    if zMid[compi] >= NewCond_zGW:
                        thfcAdj[compi] = prof.th_s[compi]
                    else:
                        dV = prof.th_s[compi] - prof.th_fc[compi]
                        dFC = (dV / (Xmax * Xmax)) * ((zMid[compi] - (NewCond_zGW - Xmax)) ** 2)
                        thfcAdj[compi] = prof.th_fc[compi] + dFC

                compi = compi - 1

        # Store adjusted field capacity values
        NewCond_th_fc_Adj = thfcAdj
        # prof.th_fc_Adj = thfcAdj
        return (NewCond_th_fc_Adj, NewCond_WTinSoil)

    return (NewCond_th_fc_Adj, None)

if __name__ == "__main__":
    cc.compile()
