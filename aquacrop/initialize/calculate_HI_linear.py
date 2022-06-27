import numpy as np
from typing import Tuple


def calculate_HI_linear(
    crop_YldFormCD: int,
    crop_HIini: float,
    crop_HI0: float,
    crop_HIGC: float,
) -> Tuple[float, float]:
    """
    Function to calculate time to switch to linear harvest index build-up,
    and associated linear rate of build-up. Only for fruit/grain crops.

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=121" target="_blank">Reference Manual</a> (pg. 112)


    Arguments:

        crop_YldFormCD (int):  length of yield formaiton period (calendar days)

        crop_HIini (float):  initial harvest index

        crop_HI0 (float):  reference harvest index

        crop_HIGC (float):  harvest index growth coefficent


    Returns:

        crop_tLinSwitch (float): time to switch to linear harvest index build-up

        crop_dHILinear (float): linear rate of HI build-up


    """
    # Determine linear switch point
    # Initialise variables
    ti = 0
    tmax = crop_YldFormCD
    HIest = 0
    HIprev = crop_HIini
    # Iterate to find linear switch point
    while (HIest <= crop_HI0) and (ti < tmax):
        ti = ti + 1
        HInew = (crop_HIini * crop_HI0) / (
            crop_HIini + (crop_HI0 - crop_HIini) * np.exp(-crop_HIGC * ti)
        )
        HIest = HInew + (tmax - ti) * (HInew - HIprev)
        HIprev = HInew

    tSwitch = ti - 1

    # Determine linear build-up rate
    if tSwitch > 0:
        HIest = (crop_HIini * crop_HI0) / (
            crop_HIini + (crop_HI0 - crop_HIini) * np.exp(-crop_HIGC * tSwitch)
        )
    else:
        HIest = 0

    dHILin = (crop_HI0 - HIest) / (tmax - tSwitch)

    crop_tLinSwitch = tSwitch
    crop_dHILinear = dHILin

    return crop_tLinSwitch, crop_dHILinear
