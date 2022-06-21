import numpy as np
from numba import njit, f8, i8, b1
from numba.pycc import CC
import sys
# temporary name for compiled module
cc = CC("solution_cc_development")


@cc.export("cc_development", "f8(f8,f8,f8,f8,f8,unicode_type,f8)")
def cc_development(
    CCo: float,
    CCx: float,
    CGC: float,
    CDC: float,
    dt: float,
    Mode: str,
    CCx0: float,
    ) -> float:

    """
    Function to calculate canopy cover development by end of the current simulation day

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=30" target="_blank">Reference Manual: canopy_cover devlopment</a> (pg. 21-24)


    Arguments:


        CCo (float): Fractional canopy cover size at emergence

        CCx (float): Maximum canopy cover (fraction of soil cover)

        CGC (float): Canopy growth coefficient (fraction per gdd)

        CDC (float): Canopy decline coefficient (fraction per gdd/calendar day)

        dt (float): Time delta of canopy growth (1 calander day or ... gdd)

        Mode (str): stage of Canopy developement (Growth or Decline)

        CCx0 (float): Maximum canopy cover (fraction of soil cover)

    Returns:

        canopy_cover (float): Canopy Cover



    """

    ## Initialise output ##

    ## Calculate new canopy cover ##
    if Mode == "Growth":
        # Calculate canopy growth
        # Exponential growth stage
        canopy_cover = CCo * np.exp(CGC * dt)
        if canopy_cover > (CCx / 2):
            # Exponential decay stage
            canopy_cover = CCx - 0.25 * (CCx / CCo) * CCx * np.exp(-CGC * dt)

        # Limit canopy_cover to CCx
        if canopy_cover > CCx:
            canopy_cover = CCx

    elif Mode == "Decline":
        # Calculate canopy decline
        if CCx < 0.001:
            canopy_cover = 0
        else:
            canopy_cover = CCx * (
                1
                - 0.05
                * (np.exp(dt * CDC * 3.33 * ((CCx + 2.29) / (CCx0 + 2.29)) / (CCx + 2.29)) - 1)
            )

    ## Limit canopy cover to between 0 and 1 ##
    if canopy_cover > 1:
        canopy_cover = 1
    elif canopy_cover < 0:
        canopy_cover = 0

    return canopy_cover

if __name__ == "__main__":
    cc.compile()
