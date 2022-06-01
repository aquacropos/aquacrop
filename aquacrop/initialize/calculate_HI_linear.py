import numpy as np


def calculate_HI_linear(
    crop_YldFormCD,
    crop_HIini,
    crop_HI0,
    crop_HIGC,
):

    """
    Function to calculate time to switch to linear harvest index build-up,
    and associated linear rate of build-up. Only for fruit/grain crops.

    *Arguments:*\n

    `crop` : `Crop` :  Crop object containing crop paramaters


    *Returns:*

    `crop` : `Crop` : updated Crop object


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
