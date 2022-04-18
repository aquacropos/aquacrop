import numpy as np




def calculate_HI_linear(crop):

    """
    Function to calculate time to switch to linear harvest index build-up,
    and associated linear rate of build-up. Only for fruit/grain crops.

    *Arguments:*\n

    `crop` : `CropClass` :  Crop object containing crop paramaters


    *Returns:*

    `crop` : `CropClass` : updated Crop object


    """
    # Determine linear switch point
    # Initialise variables
    ti = 0
    tmax = crop.YldFormCD
    HIest = 0
    HIprev = crop.HIini
    # Iterate to find linear switch point
    while (HIest <= crop.HI0) and (ti < tmax):
        ti = ti + 1
        HInew = (crop.HIini * crop.HI0) / (
            crop.HIini + (crop.HI0 - crop.HIini) * np.exp(-crop.HIGC * ti)
        )
        HIest = HInew + (tmax - ti) * (HInew - HIprev)
        HIprev = HInew

    tSwitch = ti - 1

    # Determine linear build-up rate
    if tSwitch > 0:
        HIest = (crop.HIini * crop.HI0) / (
            crop.HIini + (crop.HI0 - crop.HIini) * np.exp(-crop.HIGC * tSwitch)
        )
    else:
        HIest = 0

    dHILin = (crop.HI0 - HIest) / (tmax - tSwitch)

    crop.tLinSwitch = tSwitch
    crop.dHILinear = dHILin

    return crop

