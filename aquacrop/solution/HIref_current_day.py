import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.crop import CropStructNT_type_sig
except:
    from entities.crop import CropStructNT_type_sig
    
# temporary name for compiled module
cc = CC("solution_HIref_current_day")



@cc.export("HIref_current_day", (f8,i8,i8,b1,f8,f8,CropStructNT_type_sig,b1))
def HIref_current_day(
    NewCond_HIref,
    NewCond_DAP,
    NewCond_DelayedCDs,
    NewCond_YieldForm,
    NewCond_PctLagPhase,
    NewCond_CCprev,
    Crop,
    growing_season):
    """
    Function to calculate reference (no adjustment for stress effects)
    harvest index on current day

    <a href="../pdfs/ac_ref_man_3.pdf#page=119" target="_blank">Reference Manual: harvest index calculations</a> (pg. 110-126)



    *Arguments:*



    `InitCond`: `InitialCondition` : InitCond object containing model paramaters

    `Crop`: `Crop` : Crop object containing Crop paramaters

    `growing_season`: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitialCondition` : InitCond object containing updated model paramaters




    """

    ## Store initial conditions for updating ##
    # NewCond = InitCond

    InitCond_HIref = NewCond_HIref*1

    # NewCond.hi_ref = 0.

    ## Calculate reference harvest index (if in growing season) ##
    if growing_season == True:
        # Check if in yield_ formation period
        tAdj = NewCond_DAP - NewCond_DelayedCDs
        if tAdj > Crop.HIstartCD:

            NewCond_YieldForm = True
        else:
            NewCond_YieldForm = False

        # Get time for harvest index calculation
        HIt = NewCond_DAP - NewCond_DelayedCDs - Crop.HIstartCD - 1

        if HIt <= 0:
            # Yet to reach time for harvest_index build-up
            NewCond_HIref = 0
            NewCond_PctLagPhase = 0
        else:
            if NewCond_CCprev <= (Crop.CCmin * Crop.CCx):
                # harvest_index cannot develop further as canopy cover is too small
                NewCond_HIref = InitCond_HIref
            else:
                # Check crop type
                if (Crop.CropType == 1) or (Crop.CropType == 2):
                    # If crop type is leafy vegetable or root/tuber, then proceed with
                    # logistic growth (i.e. no linear switch)
                    NewCond_PctLagPhase = 100  # No lag phase
                    # Calculate reference harvest index for current day
                    NewCond_HIref = (Crop.HIini * Crop.HI0) / (
                        Crop.HIini + (Crop.HI0 - Crop.HIini) * np.exp(-Crop.HIGC * HIt)
                    )
                    # Harvest index apprAOSP_hing maximum limit
                    if NewCond_HIref >= (0.9799 * Crop.HI0):
                        NewCond_HIref = Crop.HI0

                elif Crop.CropType == 3:
                    # If crop type is fruit/grain producing, check for linear switch
                    if HIt < Crop.tLinSwitch:
                        # Not yet reached linear switch point, therefore proceed with
                        # logistic build-up
                        NewCond_PctLagPhase = 100 * (HIt / Crop.tLinSwitch)
                        # Calculate reference harvest index for current day
                        # (logistic build-up)
                        NewCond_HIref = (Crop.HIini * Crop.HI0) / (
                            Crop.HIini + (Crop.HI0 - Crop.HIini) * np.exp(-Crop.HIGC * HIt)
                        )
                    else:
                        # Linear switch point has been reached
                        NewCond_PctLagPhase = 100
                        # Calculate reference harvest index for current day
                        # (logistic portion)
                        NewCond_HIref = (Crop.HIini * Crop.HI0) / (
                            Crop.HIini
                            + (Crop.HI0 - Crop.HIini) * np.exp(-Crop.HIGC * Crop.tLinSwitch)
                        )
                        # Calculate reference harvest index for current day
                        # (total - logistic portion + linear portion)
                        NewCond_HIref = NewCond_HIref + (Crop.dHILinear * (HIt - Crop.tLinSwitch))

                # Limit hi_ref and round off computed value
                if NewCond_HIref > Crop.HI0:
                    NewCond_HIref = Crop.HI0
                elif NewCond_HIref <= (Crop.HIini + 0.004):
                    NewCond_HIref = 0
                elif (Crop.HI0 - NewCond_HIref) < 0.004:
                    NewCond_HIref = Crop.HI0

    else:
        # Reference harvest index is zero outside of growing season
        NewCond_HIref = 0

    return (NewCond_HIref,
            NewCond_YieldForm,
            NewCond_PctLagPhase,
            )

if __name__ == "__main__":
    cc.compile()
