from numba import njit, f8, i8, b1
from numba.pycc import CC

# temporary name for compiled module
cc = CC("solution_growing_degree_day")



@cc.export("growing_degree_day", "f8(i4,f8,f8,f8,f8)")
def growing_degree_day(
    GDDmethod: int,
    Tupp: float,
    Tbase: float,
    temp_max: float,
    temp_min: float,
    ):
    """
    Function to calculate number of growing degree days on current day

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=28" target="_blank">Reference manual: growing degree day calculations</a> (pg. 19-20)


    Arguments:

        GDDmethod (int): gdd calculation method

        Tupp (float): Upper temperature (degC) above which crop development no longer increases

        Tbase (float): Base temperature (degC) below which growth does not progress

        temp_max (float): Maximum tempature on current day (celcius)

        temp_min (float): Minimum tempature on current day (celcius)


    Returns:

        gdd (float): Growing degree days for current day



    """

    ## Calculate GDDs ##
    if GDDmethod == 1:
        # method 1
        Tmean = (temp_max + temp_min) / 2
        Tmean = min(Tmean, Tupp)
        Tmean = max(Tmean, Tbase)
        gdd = Tmean - Tbase
    elif GDDmethod == 2:
        # method 2
        temp_max = min(temp_max, Tupp)
        temp_max = max(temp_max, Tbase)

        temp_min = min(temp_min, Tupp)
        temp_min = max(temp_min, Tbase)

        Tmean = (temp_max + temp_min) / 2
        gdd = Tmean - Tbase
    elif GDDmethod == 3:
        # method 3
        temp_max = min(temp_max, Tupp)
        temp_max = max(temp_max, Tbase)

        temp_min = min(temp_min, Tupp)
        Tmean = (temp_max + temp_min) / 2
        Tmean = max(Tmean, Tbase)
        gdd = Tmean - Tbase

    return gdd

if __name__ == "__main__":
    cc.compile()
