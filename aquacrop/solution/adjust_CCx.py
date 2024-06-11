import os

if __name__ != "__main__":
    if os.getenv("DEVELOPMENT"):
        from .cc_development import cc_development
        from .cc_required_time import cc_required_time
    else:
        from .cc_development import cc_development
        from .cc_required_time import cc_required_time
else:
    from .cc_development import cc_development
    from .cc_required_time import cc_required_time
   


def adjust_CCx(
    cc_prev: float,
    CCo: float,
    CCx: float,
    CGC: float,
    CDC: float,
    dt: float,
    tSum: float,
    Crop_CanopyDevEnd: float,
    Crop_CCx: float
    ) -> float:
    """
    Function to adjust CCx value for changes in CGC due to water stress during the growing season

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=36" target="_blank">Reference Manual: canopy_cover stress response</a> (pg. 27-33)


    Arguments:

        cc_prev (float): Canopy Cover at previous timestep.

        CCo (float): Fractional canopy cover size at emergence

        CCx (float): Maximum canopy cover (fraction of soil cover)

        CGC (float): Canopy growth coefficient (fraction per gdd)

        CDC (float): Canopy decline coefficient (fraction per gdd/calendar day)

        dt (float): Time delta of canopy growth (1 calander day or ... gdd)

        tSum (float): time since germination (CD or gdd)

        Crop_CanopyDevEnd (float): time that Canopy developement ends

        Crop_CCx (float): Maximum canopy cover (fraction of soil cover)

    Returns:

        CCxAdj (float): Adjusted CCx



    """

    ## Get time required to reach canopy_cover on previous day ##
    tCCtmp = cc_required_time(cc_prev, CCo, CCx, CGC, CDC, "CGC")

    ## Determine CCx adjusted ##
    if tCCtmp > 0:
        tCCtmp = tCCtmp + (Crop_CanopyDevEnd - tSum) + dt
        CCxAdj = cc_development(CCo, CCx, CGC, CDC, tCCtmp, "Growth", Crop_CCx)
    else:
        CCxAdj = 0

    return CCxAdj

