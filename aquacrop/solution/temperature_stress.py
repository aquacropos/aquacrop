import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.crop import CropStructNT_type_sig
except:
    from entities.crop import CropStructNT_type_sig
    
# temporary name for compiled module
cc = CC("solution_temperature_stress")


@cc.export("temperature_stress", (CropStructNT_type_sig,f8,f8))
def temperature_stress(Crop, temp_max, temp_min):
    # Function to calculate temperature stress coefficients
    """
    Function to get irrigation depth for current day

    <a href="../pdfs/ac_ref_man_3.pdf#page=23" target="_blank">Reference Manual: temperature stress</a> (pg. 14)



    *Arguments:*



    `Crop`: `Crop` : Crop object containing Crop paramaters

    `temp_max`: `float` : max tempatature on current day (celcius)

    `temp_min`: `float` : min tempature on current day (celcius)


    *Returns:*


    `Kst`: `Kst` : Kst object containing tempature stress paramators







    """

    ## Calculate temperature stress coefficients affecting crop pollination ##
    # Get parameters for logistic curve
    KsPol_up = 1
    KsPol_lo = 0.001

    # Kst = Kst()

    # Calculate effects of heat stress on pollination
    if Crop.PolHeatStress == 0:
        # No heat stress effects on pollination
        Kst_PolH = 1
    elif Crop.PolHeatStress == 1:
        # Pollination affected by heat stress
        if temp_max <= Crop.Tmax_lo:
            Kst_PolH = 1
        elif temp_max >= Crop.Tmax_up:
            Kst_PolH = 0
        else:
            Trel = (temp_max - Crop.Tmax_lo) / (Crop.Tmax_up - Crop.Tmax_lo)
            Kst_PolH = (KsPol_up * KsPol_lo) / (
                KsPol_lo + (KsPol_up - KsPol_lo) * np.exp(-Crop.fshape_b * (1 - Trel))
            )

    # Calculate effects of cold stress on pollination
    if Crop.PolColdStress == 0:
        # No cold stress effects on pollination
        Kst_PolC = 1
    elif Crop.PolColdStress == 1:
        # Pollination affected by cold stress
        if temp_min >= Crop.Tmin_up:
            Kst_PolC = 1
        elif temp_min <= Crop.Tmin_lo:
            Kst_PolC = 0
        else:
            Trel = (Crop.Tmin_up - temp_min) / (Crop.Tmin_up - Crop.Tmin_lo)
            Kst_PolC = (KsPol_up * KsPol_lo) / (
                KsPol_lo + (KsPol_up - KsPol_lo) * np.exp(-Crop.fshape_b * (1 - Trel))
            )

    return (Kst_PolH,Kst_PolC)

if __name__ == "__main__":
    cc.compile()
