
from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.rootZoneWaterContent import thRZNT_type_sig
except:
    from entities.rootZoneWaterContent import thRZNT_type_sig

from typing import NamedTuple, Tuple


# temporary name for compiled module
cc = CC("solution_aeration_stress")
cc.verbose = False



@cc.export("aeration_stress", (f8,f8,thRZNT_type_sig))
def aeration_stress(
    NewCond_AerDays: float,
    Crop_LagAer: float,
    thRZ: NamedTuple,
    ) -> Tuple[float, float]:
    """
    Function to calculate aeration stress coefficient

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=90" target="_blank">Reference Manual: aeration stress</a> (pg. 89-90)


    Arguments:

        NewCond_AerDays (int): number aeration stress days

        Crop_LagAer (int): lag days before aeration stress

        thRZ (NamedTuple): object that contains information on the total water in the root zone


    Returns:

        Ksa_Aer (float): aeration stress coefficient

        NewCond_AerDays (float): updated aer days



    """

    ## Determine aeration stress (root zone) ##
    if thRZ.Act > thRZ.Aer:
        # Calculate aeration stress coefficient
        if NewCond_AerDays < Crop_LagAer:
            stress = 1 - ((thRZ.S - thRZ.Act) / (thRZ.S - thRZ.Aer))
            Ksa_Aer = 1 - ((NewCond_AerDays / 3) * stress)
        elif NewCond_AerDays >= Crop_LagAer:
            Ksa_Aer = (thRZ.S - thRZ.Act) / (thRZ.S - thRZ.Aer)

        # Increment aeration days counter
        NewCond_AerDays = NewCond_AerDays + 1
        if NewCond_AerDays > Crop_LagAer:
            NewCond_AerDays = Crop_LagAer

    else:
        # Set aeration stress coefficient to one (no stress value)
        Ksa_Aer = 1
        # Reset aeration days counter
        NewCond_AerDays = 0

    return Ksa_Aer, NewCond_AerDays

if __name__ == "__main__":
    cc.compile()
