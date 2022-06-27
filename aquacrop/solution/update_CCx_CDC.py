import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC

# temporary name for compiled module
cc = CC("solution_update_CCx_CDC")

from typing import Tuple


@cc.export("update_CCx_CDC", "(f8,f8,f8,f8)")
def update_CCx_CDC(
    cc_prev: float,
    CDC: float,
    CCx: float,
    dt: float,
    ) -> Tuple[float,float]:
    """
    Function to update CCx and CDC parameter valyes for rewatering in late season of an early declining canopy

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=36" target="_blank">Reference Manual: canopy_cover stress response</a> (pg. 27-33)


    Arguments:


        cc_prev (float): Canopy Cover at previous timestep.

        CDC (float): Canopy decline coefficient (fraction per gdd/calendar day)

        CCx (float): Maximum canopy cover (fraction of soil cover)

        dt (float): Time delta of canopy growth (1 calander day or ... gdd)


    Returns:

        CCxAdj (float): updated CCxAdj

        CDCadj (float): updated CDCadj





    """

    ## Get adjusted CCx ##
    CCXadj = cc_prev / (1 - 0.05 * (np.exp(dt * ((CDC * 3.33) / (CCx + 2.29))) - 1))

    ## Get adjusted CDC ##
    CDCadj = CDC * ((CCXadj + 2.29) / (CCx + 2.29))

    return CCXadj, CDCadj

if __name__ == "__main__":
    cc.compile()
