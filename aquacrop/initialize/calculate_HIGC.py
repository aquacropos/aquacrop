import numpy as np


def calculate_HIGC(crop):
    """
    Function to calculate harvest index growth coefficient

    *Arguments:*\n

    `crop` : `CropClass` :  Crop object containing crop paramaters


    *Returns:*

    `crop` : `CropClass` : updated Crop object


    """
    # Determine HIGC
    # Total yield formation days
    tHI = crop.YldFormCD
    # Iteratively estimate HIGC
    HIGC = 0.001
    HIest = 0
    while HIest <= (0.98 * crop.HI0):
        HIGC = HIGC + 0.001
        HIest = (crop.HIini * crop.HI0) / (
            crop.HIini + (crop.HI0 - crop.HIini) * np.exp(-HIGC * tHI)
        )

    if HIest >= crop.HI0:
        HIGC = HIGC - 0.001

    crop.HIGC = HIGC

    return crop
