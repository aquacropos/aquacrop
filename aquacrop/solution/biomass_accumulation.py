import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC
# temporary name for compiled module
cc = CC("solution_biomass_accumulation")
cc.verbose = False


try:
    from ..entities.crop import CropStructNT_type_sig
except:
    from entities.crop import CropStructNT_type_sig

from typing import NamedTuple, Tuple


@cc.export("biomass_accumulation", (CropStructNT_type_sig,i8,i8,f8,f8,f8,f8,f8,f8,f8,b1))
def biomass_accumulation(
    Crop: NamedTuple,
    NewCond_DAP: int,
    NewCond_DelayedCDs: int,
    NewCond_HIref: float,
    NewCond_PctLagPhase: float,
    NewCond_B: float,
    NewCond_B_NS: float,
    Tr: float,
    TrPot: float,
    et0: float,
    growing_season: bool,
    ) -> Tuple[float, float]:
    """
    Function to calculate biomass accumulation

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=107" target="_blank">Reference Manual: biomass accumulaiton</a> (pg. 98-108)


    Arguments:

        Crop (NamedTuple): Crop object

        NewCond_DAP (int): days since planting

        NewCond_DelayedCDs (int): Delayed calendar days

        NewCond_HIref (float): reference harvest index

        NewCond_PctLagPhase (float): percentage of way through early HI development stage

        NewCond_B (float): Current biomass growth

        NewCond_B_NS (float): current no stress biomass growth

        TrPot (float): Daily crop transpiration

        TrPot (float): Daily potential transpiration

        et0 (float): Daily reference evapotranspiration

        growing_season (bool): is Growing season? (True, False)

    Returns:

        NewCond_B (float): new biomass growth

        NewCond_B_NS (float): new (No stress) biomass growth


    """

    ## Store initial conditions in a new structure for updating ##
    # NewCond = InitCond

    ## Calculate biomass accumulation (if in growing season) ##
    if growing_season == True:
        # Get time for harvest index build-up
        HIt = NewCond_DAP - NewCond_DelayedCDs - Crop.HIstartCD - 1

        if ((Crop.CropType == 2) or (Crop.CropType == 3)) and (NewCond_HIref > 0):
            # Adjust WP for reproductive stage
            if Crop.Determinant == 1:
                fswitch = NewCond_PctLagPhase / 100
            else:
                if HIt < (Crop.YldFormCD / 3):
                    fswitch = HIt / (Crop.YldFormCD / 3)
                else:
                    fswitch = 1

            WPadj = Crop.WP * (1 - (1 - Crop.WPy / 100) * fswitch)
        else:
            WPadj = Crop.WP

        # Adjust WP for CO2 effects
        WPadj = WPadj * Crop.fCO2

        # Calculate biomass accumulation on current day
        # No water stress
        dB_NS = WPadj * (TrPot / et0)
        # With water stress
        dB = WPadj * (Tr / et0)
        if np.isnan(dB) == True:
            dB = 0

        # Update biomass accumulation
        NewCond_B = NewCond_B + dB
        NewCond_B_NS = NewCond_B_NS + dB_NS
    else:
        # No biomass accumulation outside of growing season
        NewCond_B = 0
        NewCond_B_NS = 0

    return (NewCond_B,
            NewCond_B_NS)

if __name__ == "__main__":
    cc.compile()
