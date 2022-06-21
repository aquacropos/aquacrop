import numpy as np
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.soilProfile import SoilProfileNT
    from numpy import ndarray



from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.soilProfile import SoilProfileNT_typ_sig
except:
    from entities.soilProfile import SoilProfileNT_typ_sig
    
# temporary name for compiled module
cc = CC("solution_evap_layer_water_content")

@njit
@cc.export("evap_layer_water_content", (f8[:],f8,SoilProfileNT_typ_sig))
def evap_layer_water_content(
    InitCond_th: "ndarray",
    InitCond_EvapZ: float,
    prof: "SoilProfileNT",
) -> Tuple[float, float, float, float, float]:
    """
    Function to get water contents in the evaporation layer

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=82" target="_blank">Reference Manual: evaporation equations</a> (pg. 73-81)


    Arguments:

        InitCond_th (numpy.array): Initial water content

        InitCond_EvapZ (float): evaporation depth

        prof (SoilProfileNT): Soil object containing soil paramaters


    Returns:


        Wevap_Sat (float): Water storage in evaporation layer at saturation (mm)

        Wevap_Fc (float): Water storage in evaporation layer at field capacity (mm)

        Wevap_Wp (float): Water storage in evaporation layer at permanent wilting point (mm)

        Wevap_Dry (float): Water storage in evaporation layer at air dry (mm)

        Wevap_Act (float): Actual water storage in evaporation layer (mm)



    """

    # Find soil compartments covered by evaporation layer
    comp_sto = np.sum(prof.dzsum < InitCond_EvapZ) + 1

    Wevap_Sat = 0
    Wevap_Fc = 0
    Wevap_Wp = 0
    Wevap_Dry = 0
    Wevap_Act = 0

    for ii in range(int(comp_sto)):

        # Determine fraction of soil compartment covered by evaporation layer
        if prof.dzsum[ii] > InitCond_EvapZ:
            factor = 1 - ((prof.dzsum[ii] - InitCond_EvapZ) / prof.dz[ii])
        else:
            factor = 1

        # Actual water storage in evaporation layer (mm)
        Wevap_Act += factor * 1000 * InitCond_th[ii] * prof.dz[ii]
        # Water storage in evaporation layer at saturation (mm)
        Wevap_Sat += factor * 1000 * prof.th_s[ii] * prof.dz[ii]
        # Water storage in evaporation layer at field capacity (mm)
        Wevap_Fc += factor * 1000 * prof.th_fc[ii] * prof.dz[ii]
        # Water storage in evaporation layer at permanent wilting point (mm)
        Wevap_Wp += factor * 1000 * prof.th_wp[ii] * prof.dz[ii]
        # Water storage in evaporation layer at air dry (mm)
        Wevap_Dry += factor * 1000 * prof.th_dry[ii] * prof.dz[ii]

    if Wevap_Act < 0:
        Wevap_Act = 0

    return Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act

if __name__ == "__main__":
    cc.compile()
