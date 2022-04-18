import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC

# temporary name for compiled module
cc = CC("solution_update_CCx_CDC")


@cc.export("update_CCx_CDC", "(f8,f8,f8,f8)")
def update_CCx_CDC(CCprev, CDC, CCx, dt):
    """
    Function to update CCx and CDC parameter valyes for rewatering in late season of an early declining canopy

    <a href="../pdfs/ac_ref_man_3.pdf#page=36" target="_blank">Reference Manual: CC stress response</a> (pg. 27-33)


    *Arguments:*


    `CCprev`: `float` : Canopy Cover at previous timestep.

    `CDC`: `float` : Canopy decline coefficient (fraction per GDD/calendar day)

    `CCx`: `float` : Maximum canopy cover (fraction of soil cover)

    `dt`: `float` : Time delta of canopy growth (1 calander day or ... GDD)


    *Returns:*

    `CCxAdj`: `float` : updated CCxAdj

    `CDCadj`: `float` : updated CDCadj





    """

    ## Get adjusted CCx ##
    CCXadj = CCprev / (1 - 0.05 * (np.exp(dt * ((CDC * 3.33) / (CCx + 2.29))) - 1))

    ## Get adjusted CDC ##
    CDCadj = CDC * ((CCXadj + 2.29) / (CCx + 2.29))

    return CCXadj, CDCadj

if __name__ == "__main__":
    cc.compile()
