import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC

# temporary name for compiled module
cc = CC("solution_cc_required_time")



@cc.export("cc_required_time", "f8(f8,f8,f8,f8,f8,unicode_type)")
def cc_required_time(CCprev, CCo, CCx, CGC, CDC, Mode):
    """
    Function to find time required to reach CC at end of previous day, given current CGC or CDC

    <a href="../pdfs/ac_ref_man_3.pdf#page=30" target="_blank">Reference Manual: CC devlopment</a> (pg. 21-24)



    *Arguments:*


    `CCprev`: `float` : Canopy Cover at previous timestep.

    `CCo`: `float` : Fractional canopy cover size at emergence

    `CCx`: `float` : Maximum canopy cover (fraction of soil cover)

    `CGC`: `float` : Canopy growth coefficient (fraction per GDD)

    `CDC`: `float` : Canopy decline coefficient (fraction per GDD/calendar day)

    `Mode`: `str` : Canopy growth/decline coefficient (fraction per GDD/calendar day)


    *Returns:*

    `tReq`: `float` : time required to reach CC at end of previous day





    """

    ## Get CGC and/or time (GDD or CD) required to reach CC on previous day ##
    if Mode == "CGC":
        if CCprev <= (CCx / 2):

            # print(CCprev,CCo,(tSum-dt),tSum,dt)
            CGCx = np.log(CCprev / CCo)
            # print(np.log(CCprev/CCo),(tSum-dt),CGCx)
        else:
            # print(CCx,CCo,CCprev)
            CGCx = np.log((0.25 * CCx * CCx / CCo) / (CCx - CCprev))

        tReq = CGCx / CGC

    elif Mode == "CDC":
        tReq = (np.log(1 + (1 - CCprev / CCx) / 0.05)) / (CDC / CCx)

    return tReq

if __name__ == "__main__":
    cc.compile()
