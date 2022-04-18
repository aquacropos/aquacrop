import os

if __name__ != "__main__":
    if os.getenv("DEVELOPMENT"):
        from .cc_development import cc_development
        from .cc_required_time import cc_required_time
    else:
        from .solution_cc_development import cc_development
        from .solution_cc_required_time import cc_required_time
else:
    from .cc_development import cc_development
    from .cc_required_time import cc_required_time
   


def adjust_CCx(CCprev, CCo, CCx, CGC, CDC, dt, tSum, Crop_CanopyDevEnd, Crop_CCx):
    """
    Function to adjust CCx value for changes in CGC due to water stress during the growing season

    <a href="../pdfs/ac_ref_man_3.pdf#page=36" target="_blank">Reference Manual: CC stress response</a> (pg. 27-33)


    *Arguments:*


    `CCprev`: `float` : Canopy Cover at previous timestep.

    `CCo`: `float` : Fractional canopy cover size at emergence

    `CCx`: `float` : Maximum canopy cover (fraction of soil cover)

    `CGC`: `float` : Canopy growth coefficient (fraction per GDD)

    `CDC`: `float` : Canopy decline coefficient (fraction per GDD/calendar day)

    `dt`: `float` : Time delta of canopy growth (1 calander day or ... GDD)

    `tSum`: `float` : time since germination (CD or GDD)

    `Crop_CanopyDevEnd`: `float` : time that Canopy developement ends

    `Crop_CCx`: `float` : Maximum canopy cover (fraction of soil cover)

    *Returns:*

    `CCxAdj`: `float` : Adjusted CCx





    """

    ## Get time required to reach CC on previous day ##
    tCCtmp = cc_required_time(CCprev, CCo, CCx, CGC, CDC, "CGC")

    ## Determine CCx adjusted ##
    if tCCtmp > 0:
        tCCtmp = tCCtmp + (Crop_CanopyDevEnd - tSum) + dt
        CCxAdj = cc_development(CCo, CCx, CGC, CDC, tCCtmp, "Growth", Crop_CCx)
    else:
        CCxAdj = 0

    return CCxAdj

