from numba import njit, f8, i8, b1
from numba.pycc import CC

# temporary name for compiled module
cc = CC("solution_growing_degree_day")



@cc.export("growing_degree_day", "f8(i4,f8,f8,f8,f8)")
def growing_degree_day(GDDmethod, Tupp, Tbase, Tmax, Tmin):
    """
    Function to calculate number of growing degree days on current day

    <a href="../pdfs/ac_ref_man_3.pdf#page=28" target="_blank">Reference manual: growing degree day calculations</a> (pg. 19-20)



    *Arguments:*

    `GDDmethod`: `int` : GDD calculation method

    `Tupp`: `float` : Upper temperature (degC) above which crop development no longer increases

    `Tbase`: `float` : Base temperature (degC) below which growth does not progress

    `Tmax`: `float` : Maximum tempature on current day (celcius)

    `Tmin`: `float` : Minimum tempature on current day (celcius)


    *Returns:*


    `GDD`: `float` : Growing degree days for current day



    """

    ## Calculate GDDs ##
    if GDDmethod == 1:
        # Method 1
        Tmean = (Tmax + Tmin) / 2
        Tmean = min(Tmean, Tupp)
        Tmean = max(Tmean, Tbase)
        GDD = Tmean - Tbase
    elif GDDmethod == 2:
        # Method 2
        Tmax = min(Tmax, Tupp)
        Tmax = max(Tmax, Tbase)

        Tmin = min(Tmin, Tupp)
        Tmin = max(Tmin, Tbase)

        Tmean = (Tmax + Tmin) / 2
        GDD = Tmean - Tbase
    elif GDDmethod == 3:
        # Method 3
        Tmax = min(Tmax, Tupp)
        Tmax = max(Tmax, Tbase)

        Tmin = min(Tmin, Tupp)
        Tmean = (Tmax + Tmin) / 2
        Tmean = max(Tmean, Tbase)
        GDD = Tmean - Tbase

    return GDD

if __name__ == "__main__":
    cc.compile()
