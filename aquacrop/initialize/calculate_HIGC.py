import numpy as np



def calculate_HIGC(
    crop_YldFormCD: int,
    crop_HI0: float,
    crop_HIini: float,
) -> float:
    """
    Function to calculate harvest index growth coefficient

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=119" target="_blank">Reference Manual</a> (pg. 110)


    Arguments:

        crop_YldFormCD (int):  length of yield formation period (calendar days)

        crop_HI0 (float):  reference harvest index

        crop_HIini (float):  initial harvest index


    Returns:

        crop_HIGC (float): harvest index growth coefficient


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
