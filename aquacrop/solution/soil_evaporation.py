import os
import numpy as np

        
from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.soilProfile import SoilProfileNT_typ_sig
except:
    from entities.soilProfile import SoilProfileNT_typ_sig


if __name__ != "__main__":
    if os.getenv("DEVELOPMENT"):
        from .evap_layer_water_content import evap_layer_water_content
    else:
        from .solution_evap_layer_water_content import evap_layer_water_content
else:
    from .evap_layer_water_content import evap_layer_water_content


# temporary name for compiled module
cc = CC("solution_soil_evaporation")


@cc.export(
    "soil_evaporation", (i8,i8,i8,SoilProfileNT_typ_sig,
    f8,f8,f8,f8,f8,f8,f8,i8,f8,i8,f8,b1,f8,f8,i8,f8,f8,f8,f8[:],f8,f8,f8,f8,f8,f8,
        f8,b1,f8,f8,f8,f8,f8,f8,f8,b1),
)
def soil_evaporation(
    ClockStruct_EvapTimeSteps,
    ClockStruct_SimOffSeason,
    ClockStruct_TimeStepCounter,
    prof,
    Soil_EvapZmin,
    Soil_EvapZmax,
    Soil_REW,
    Soil_Kex,
    Soil_fwcc,
    Soil_fWrelExp,
    Soil_fevap,
    Crop_CalendarType,
    Crop_Senescence,
    IrrMngt_IrrMethod,
    IrrMngt_WetSurf,
    FieldMngt_Mulches,
    FieldMngt_fMulch,
    FieldMngt_MulchPct,
    NewCond_DAP,
    NewCond_Wsurf,
    NewCond_EvapZ,
    NewCond_Stage2,
    NewCond_th,
    NewCond_DelayedCDs,
    NewCond_GDDcum,
    NewCond_DelayedGDDs,
    NewCond_CCxW,
    NewCond_CCadj,
    NewCond_CCxAct,
    NewCond_CC,
    NewCond_PrematSenes,
    NewCond_SurfaceStorage,
    NewCond_Wstage2,
    NewCond_Epot,
    et0,
    Infl,
    Rain,
    Irr,
    growing_season,
):

    """
    Function to calculate daily soil evaporation

    <a href="../pdfs/ac_ref_man_3.pdf#page=82" target="_blank">Reference Manual: evaporation equations</a> (pg. 73-81)


    *Arguments:*



    `Clock params`: `bool, int` : clock params

    `Soil parameters`: `float` : soil parameters

    `Crop params`: `float` : Crop paramaters

    `IrrMngt params`: `int, float`: irrigation management paramaters

    `FieldMngt`: `FieldMngtStruct` : Field management paramaters

    `InitCond`: `InitialCondition` : InitCond object containing model paramaters

    `et0`: `float` : daily reference evapotranspiration

    `Infl`: `float` : Infiltration on current day

    `Rain`: `float` : daily precipitation mm

    `Irr`: `float` : Irrigation applied on current day

    `growing_season`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitialCondition` : InitCond object containing updated model paramaters

    `EsAct`: `float` : Actual surface evaporation current day

    `EsPot`: `float` : Potential surface evaporation current day





    """

    # Wevap = WaterEvaporation()

    ## Store initial conditions in new structure that will be updated ##
    # NewCond = InitCond

    ## Prepare stage 2 evaporation (rew gone) ##
    # Only do this if it is first day of simulation, or if it is first day of
    # growing season and not simulating off-season
    if (ClockStruct_TimeStepCounter == 0) or (
        (NewCond_DAP == 1) and (ClockStruct_SimOffSeason == False)
    ):
        # Reset storage in surface soil layer to zero
        NewCond_Wsurf = 0
        # Set evaporation depth to minimum
        NewCond_EvapZ = Soil_EvapZmin
        # Trigger stage 2 evaporation
        NewCond_Stage2 = True
        # Get relative water content for start of stage 2 evaporation
        Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act = evap_layer_water_content(
            NewCond_th,
            NewCond_EvapZ,
            prof,
        )
        NewCond_Wstage2 = round(
            (Wevap_Act - (Wevap_Fc - Soil_REW)) / (Wevap_Sat - (Wevap_Fc - Soil_REW)), 2
        )
        if NewCond_Wstage2 < 0:
            NewCond_Wstage2 = 0

    ## Prepare soil evaporation stage 1 ##
    # Adjust water in surface evaporation layer for any infiltration
    if (Rain > 0) or ((Irr > 0) and (IrrMngt_IrrMethod != 4)):
        # Only prepare stage one when rainfall occurs, or when irrigation is
        # trigerred (not in net irrigation mode)
        if Infl > 0:
            # Update storage in surface evaporation layer for incoming
            # infiltration
            NewCond_Wsurf = Infl
            # Water stored in surface evaporation layer cannot exceed rew
            if NewCond_Wsurf > Soil_REW:
                NewCond_Wsurf = Soil_REW

            # Reset variables
            NewCond_Wstage2 = 0
            NewCond_EvapZ = Soil_EvapZmin
            NewCond_Stage2 = False

    ## Calculate potential soil evaporation rate (mm/day) ##
    if growing_season == True:
        # Adjust time for any delayed development
        if Crop_CalendarType == 1:
            tAdj = NewCond_DAP - NewCond_DelayedCDs
        elif Crop_CalendarType == 2:
            tAdj = NewCond_GDDcum - NewCond_DelayedGDDs

        # Calculate maximum potential soil evaporation
        EsPotMax = Soil_Kex * et0 * (1 - NewCond_CCxW * (Soil_fwcc / 100))
        # Calculate potential soil evaporation (given current canopy cover
        # size)
        EsPot = Soil_Kex * (1 - NewCond_CCadj) * et0

        # Adjust potential soil evaporation for effects of withered canopy
        if (tAdj > Crop_Senescence) and (NewCond_CCxAct > 0):
            if NewCond_CC > (NewCond_CCxAct / 2):
                if NewCond_CC > NewCond_CCxAct:
                    mult = 0
                else:
                    mult = (NewCond_CCxAct - NewCond_CC) / (NewCond_CCxAct / 2)

            else:
                mult = 1

            EsPot = EsPot * (1 - NewCond_CCxAct * (Soil_fwcc / 100) * mult)
            CCxActAdj = (
                (1.72 * NewCond_CCxAct) - (NewCond_CCxAct ** 2) + 0.3 * (NewCond_CCxAct ** 3)
            )
            EsPotMin = Soil_Kex * (1 - CCxActAdj) * et0
            if EsPotMin < 0:
                EsPotMin = 0

            if EsPot < EsPotMin:
                EsPot = EsPotMin
            elif EsPot > EsPotMax:
                EsPot = EsPotMax

        if NewCond_PrematSenes == True:
            if EsPot > EsPotMax:
                EsPot = EsPotMax

    else:
        # No canopy cover outside of growing season so potential soil
        # evaporation only depends on reference evapotranspiration
        EsPot = Soil_Kex * et0

    ## Adjust potential soil evaporation for mulches and/or partial wetting ##
    # mulches
    if NewCond_SurfaceStorage < 0.000001:
        if not FieldMngt_Mulches:
            # No mulches present
            EsPotMul = EsPot
        elif FieldMngt_Mulches:
            # mulches present
            EsPotMul = EsPot * (1 - FieldMngt_fMulch * (FieldMngt_MulchPct / 100))

    else:
        # Surface is flooded - no adjustment of potential soil evaporation for
        # mulches
        EsPotMul = EsPot

    # Partial surface wetting by irrigation
    if (Irr > 0) and (IrrMngt_IrrMethod != 4):
        # Only apply adjustment if irrigation occurs and not in net irrigation
        # mode
        if (Rain > 1) or (NewCond_SurfaceStorage > 0):
            # No adjustment for partial wetting - assume surface is fully wet
            EsPotIrr = EsPot
        else:
            # Adjust for proprtion of surface area wetted by irrigation
            EsPotIrr = EsPot * (IrrMngt_WetSurf / 100)

    else:
        # No adjustment for partial surface wetting
        EsPotIrr = EsPot

    # Assign minimum value (mulches and partial wetting don't combine)
    EsPot = min(EsPotIrr, EsPotMul)

    ## Surface evaporation ##
    # Initialise actual evaporation counter
    EsAct = 0
    # Evaporate surface storage
    if NewCond_SurfaceStorage > 0:
        if NewCond_SurfaceStorage > EsPot:
            # All potential soil evaporation can be supplied by surface storage
            EsAct = EsPot
            # Update surface storage
            NewCond_SurfaceStorage = NewCond_SurfaceStorage - EsAct
        else:
            # Surface storage is not sufficient to meet all potential soil
            # evaporation
            EsAct = NewCond_SurfaceStorage
            # Update surface storage, evaporation layer depth, stage
            NewCond_SurfaceStorage = 0
            NewCond_Wsurf = Soil_REW
            NewCond_Wstage2 = 0
            NewCond_EvapZ = Soil_EvapZmin
            NewCond_Stage2 = False

    ## stage 1 evaporation ##
    # Determine total water to be extracted
    ToExtract = EsPot - EsAct
    # Determine total water to be extracted in stage one (limited by surface
    # layer water storage)
    ExtractPotStg1 = min(ToExtract, NewCond_Wsurf)
    # Extract water
    if ExtractPotStg1 > 0:
        # Find soil compartments covered by evaporation layer
        comp_sto = np.sum(prof.dzsum < Soil_EvapZmin) + 1
        comp = -1
        # prof = Soil_Profile
        while (ExtractPotStg1 > 0) and (comp < comp_sto):
            # Increment compartment counter
            comp = comp + 1
            # Specify layer number
            # Determine proportion of compartment in evaporation layer
            if prof.dzsum[comp] > Soil_EvapZmin:
                factor = 1 - ((prof.dzsum[comp] - Soil_EvapZmin) / prof.dz[comp])
            else:
                factor = 1

            # Water storage (mm) at air dry
            Wdry = 1000 * prof.th_dry[comp] * prof.dz[comp]
            # Available water (mm)
            W = 1000 * NewCond_th[comp] * prof.dz[comp]
            # Water available in compartment for extraction (mm)
            AvW = (W - Wdry) * factor
            if AvW < 0:
                AvW = 0

            if AvW >= ExtractPotStg1:
                # Update actual evaporation
                EsAct = EsAct + ExtractPotStg1
                # Update depth of water in current compartment
                W = W - ExtractPotStg1
                # Update total water to be extracted
                ToExtract = ToExtract - ExtractPotStg1
                # Update water to be extracted from surface layer (stage 1)
                ExtractPotStg1 = 0
            else:
                # Update actual evaporation
                EsAct = EsAct + AvW
                # Update water to be extracted from surface layer (stage 1)
                ExtractPotStg1 = ExtractPotStg1 - AvW
                # Update total water to be extracted
                ToExtract = ToExtract - AvW
                # Update depth of water in current compartment
                W = W - AvW

            # Update water content
            NewCond_th[comp] = W / (1000 * prof.dz[comp])

        # Update surface evaporation layer water balance
        NewCond_Wsurf = NewCond_Wsurf - EsAct
        if (NewCond_Wsurf < 0) or (ExtractPotStg1 > 0.0001):
            NewCond_Wsurf = 0

        # If surface storage completely depleted, prepare stage 2
        if NewCond_Wsurf < 0.0001:
            # Get water contents (mm)
            Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act = evap_layer_water_content(
                NewCond_th,
                NewCond_EvapZ,
                prof,
            )
            # Proportional water storage for start of stage two evaporation
            NewCond_Wstage2 = round(
                (Wevap_Act - (Wevap_Fc - Soil_REW)) / (Wevap_Sat - (Wevap_Fc - Soil_REW)), 2
            )
            if NewCond_Wstage2 < 0:
                NewCond_Wstage2 = 0

    ## stage 2 evaporation ##
    # Extract water
    if ToExtract > 0:
        # Start stage 2
        NewCond_Stage2 = True
        # Get sub-daily evaporative demand
        Edt = ToExtract / ClockStruct_EvapTimeSteps
        # Loop sub-daily steps
        for jj in range(int(ClockStruct_EvapTimeSteps)):
            # Get current water storage (mm)
            Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act = evap_layer_water_content(
                NewCond_th,
                NewCond_EvapZ,
                prof,
            )
            # Get water storage (mm) at start of stage 2 evaporation
            Wupper = NewCond_Wstage2 * (Wevap_Sat - (Wevap_Fc - Soil_REW)) + (Wevap_Fc - Soil_REW)
            # Get water storage (mm) when there is no evaporation
            Wlower = Wevap_Dry
            # Get relative depletion of evaporation storage in stage 2
            Wrel = (Wevap_Act - Wlower) / (Wupper - Wlower)
            # Check if need to expand evaporation layer
            if Soil_EvapZmax > Soil_EvapZmin:
                Wcheck = Soil_fWrelExp * (
                    (Soil_EvapZmax - NewCond_EvapZ) / (Soil_EvapZmax - Soil_EvapZmin)
                )
                while (Wrel < Wcheck) and (NewCond_EvapZ < Soil_EvapZmax):
                    # Expand evaporation layer by 1 mm
                    NewCond_EvapZ = NewCond_EvapZ + 0.001
                    # Update water storage (mm) in evaporation layer
                    Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act = evap_layer_water_content(
                        NewCond_th,
                        NewCond_EvapZ,
                        prof,
                    )
                    Wupper = NewCond_Wstage2 * (Wevap_Sat - (Wevap_Fc - Soil_REW)) + (
                        Wevap_Fc - Soil_REW
                    )
                    Wlower = Wevap_Dry
                    # Update relative depletion of evaporation storage
                    Wrel = (Wevap_Act - Wlower) / (Wupper - Wlower)
                    Wcheck = Soil_fWrelExp * (
                        (Soil_EvapZmax - NewCond_EvapZ) / (Soil_EvapZmax - Soil_EvapZmin)
                    )

            # Get stage 2 evaporation reduction coefficient
            Kr = (np.exp(Soil_fevap * Wrel) - 1) / (np.exp(Soil_fevap) - 1)
            if Kr > 1:
                Kr = 1

            # Get water to extract (mm)
            ToExtractStg2 = Kr * Edt

            # Extract water from compartments
            comp_sto = np.sum(prof.dzsum < NewCond_EvapZ) + 1
            comp = -1
            # prof = Soil_Profile
            while (ToExtractStg2 > 0) and (comp < comp_sto):
                # Increment compartment counter
                comp = comp + 1
                # Specify layer number
                # Determine proportion of compartment in evaporation layer
                if prof.dzsum[comp] > NewCond_EvapZ:
                    factor = 1 - ((prof.dzsum[comp] - NewCond_EvapZ) / prof.dz[comp])
                else:
                    factor = 1

                # Water storage (mm) at air dry
                Wdry = 1000 * prof.th_dry[comp] * prof.dz[comp]
                # Available water (mm)
                W = 1000 * NewCond_th[comp] * prof.dz[comp]
                # Water available in compartment for extraction (mm)
                AvW = (W - Wdry) * factor
                if AvW >= ToExtractStg2:
                    # Update actual evaporation
                    EsAct = EsAct + ToExtractStg2
                    # Update depth of water in current compartment
                    W = W - ToExtractStg2
                    # Update total water to be extracted
                    ToExtract = ToExtract - ToExtractStg2
                    # Update water to be extracted from surface layer (stage 1)
                    ToExtractStg2 = 0
                else:
                    # Update actual evaporation
                    EsAct = EsAct + AvW
                    # Update depth of water in current compartment
                    W = W - AvW
                    # Update water to be extracted from surface layer (stage 1)
                    ToExtractStg2 = ToExtractStg2 - AvW
                    # Update total water to be extracted
                    ToExtract = ToExtract - AvW

                # Update water content
                NewCond_th[comp] = W / (1000 * prof.dz[comp])

    ## Store potential evaporation for irrigation calculations on next day ##
    NewCond_Epot = EsPot

    return (
        NewCond_Epot,
        NewCond_th,
        NewCond_Stage2,
        NewCond_Wstage2,
        NewCond_Wsurf,
        NewCond_SurfaceStorage,
        NewCond_EvapZ,
        EsAct,
        EsPot,
    )

if __name__ == "__main__":
    cc.compile()
