import numpy as np
from numba import njit, f8, i8, b1
from numba.pycc import CC
import sys
# temporary name for compiled module
cc = CC("solution_cc_development")


@cc.export("cc_development", "f8(f8,f8,f8,f8,f8,unicode_type,f8)")
def cc_development(CCo, CCx, CGC, CDC, dt, Mode, CCx0):
    """
    Function to calculate canopy cover development by end of the current simulation day

    <a href="../pdfs/ac_ref_man_3.pdf#page=30" target="_blank">Reference Manual: CC devlopment</a> (pg. 21-24)


    *Arguments:*



    `CCo`: `float` : Fractional canopy cover size at emergence

    `CCx`: `float` : Maximum canopy cover (fraction of soil cover)

    `CGC`: `float` : Canopy growth coefficient (fraction per GDD)

    `CDC`: `float` : Canopy decline coefficient (fraction per GDD/calendar day)

    `dt`: `float` : Time delta of canopy growth (1 calander day or ... GDD)

    `Mode`: `str` : Stage of Canopy developement (Growth or Decline)

    `CCx0`: `float` : Maximum canopy cover (fraction of soil cover)

    *Returns:*

    `CC`: `float` : Canopy Cover




    """

    ## Initialise output ##

    ## Calculate new canopy cover ##
    if Mode == "Growth":
        # Calculate canopy growth
        # Exponential growth stage
        CC = CCo * np.exp(CGC * dt)
        if CC > (CCx / 2):
            # Exponential decay stage
            CC = CCx - 0.25 * (CCx / CCo) * CCx * np.exp(-CGC * dt)

        # Limit CC to CCx
        if CC > CCx:
            CC = CCx

    elif Mode == "Decline":
        # Calculate canopy decline
        if CCx < 0.001:
            CC = 0
        else:
            CC = CCx * (
                1
                - 0.05
                * (np.exp(dt * CDC * 3.33 * ((CCx + 2.29) / (CCx0 + 2.29)) / (CCx + 2.29)) - 1)
            )

    ## Limit canopy cover to between 0 and 1 ##
    if CC > 1:
        CC = 1
    elif CC < 0:
        CC = 0

    return CC

if __name__ == "__main__":
    cc.compile()
