import numpy as np


def calculate_HIGC(
    crop_YldFormCD,
    crop_HI0,
    crop_HIini,
):
    """
    Function to calculate harvest index growth coefficient

    *Arguments:*\n

    `crop` : `Crop` :  Crop object containing crop paramaters


    *Returns:*

    `crop` : `Crop` : updated Crop object


    """
    # Determine HIGC
    # Total yield_ formation days
    tHI = crop_YldFormCD
    # Iteratively estimate HIGC
    HIGC = 0.001
    HIest = 0
    while HIest <= (0.98 * crop_HI0):
        HIGC = HIGC + 0.001
        HIest = (crop_HIini * crop_HI0) / (
            crop_HIini + (crop_HI0 - crop_HIini) * np.exp(-HIGC * tHI)
        )

    if HIest >= crop_HI0:
        HIGC = HIGC - 0.001

    crop_HIGC = HIGC

    return crop_HIGC
