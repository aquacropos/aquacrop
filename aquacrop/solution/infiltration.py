import numpy as np


from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.soilProfile import SoilProfileNT_typ_sig
except:
    from entities.soilProfile import SoilProfileNT_typ_sig
    
# temporary name for compiled module
cc = CC("solution_infiltration")


@cc.export("infiltration", (SoilProfileNT_typ_sig,f8,f8[:],f8[:],f8,f8,f8,b1,f8,f8[:],f8,f8,b1))
def infiltration(
     prof,
     NewCond_SurfaceStorage, 
     NewCond_th_fc_Adj, 
     NewCond_th, 
     Infl, 
     Irr, 
     IrrMngt_AppEff, 
     FieldMngt_Bunds,
     FieldMngt_zBund,
     FluxOut, 
     DeepPerc0, 
     Runoff0, 
     growing_season
):
    """
    Function to infiltrate incoming water (rainfall and irrigation)

    <a href="../pdfs/ac_ref_man_3.pdf#page=51" target="_blank">Reference Manual: drainage calculations</a> (pg. 42-65)



    *Arguments:*



    `prof`: `SoilProfile` : Soil object containing soil paramaters

    `InitCond`: `InitialCondition` : InitCond object containing model paramaters

    `Infl`: `float` : Infiltration so far

    `Irr`: `float` : Irrigation on current day

    `IrrMngt_AppEff`: `float`: irrigation application efficiency

    `FieldMngt`: `FieldMngtStruct` : field management params

    `FluxOut`: `np.array` : flux of water out of each compartment

    `DeepPerc0`: `float` : initial Deep Percolation

    `Runoff0`: `float` : initial Surface Runoff

    `growing_season`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitialCondition` : InitCond object containing updated model paramaters

    `DeepPerc`:: `float` : Total Deep Percolation

    `RunoffTot`: `float` : Total surface Runoff

    `Infl`: `float` : Infiltration on current day

    `FluxOut`: `np.array` : flux of water out of each compartment




    """
    ## Store initial conditions in new structure for updating ##
    # NewCond = InitCond

    InitCond_SurfaceStorage = NewCond_SurfaceStorage*1
    InitCond_th_fc_Adj = NewCond_th_fc_Adj*1
    InitCond_th = NewCond_th*1

    thnew = NewCond_th*1.

    Soil_nComp = thnew.shape[0]

    Infl = max(Infl,0.)

    ## Update infiltration rate for irrigation ##
    # Note: irrigation amount adjusted for specified application efficiency
    if growing_season == True:
        Infl = Infl + (Irr * (IrrMngt_AppEff / 100))

    assert Infl >= 0

    ## Determine surface storage (if bunds are present) ##
    if FieldMngt_Bunds:
        # bunds on field
        if FieldMngt_zBund > 0.001:
            # Bund height too small to be considered
            InflTot = Infl + NewCond_SurfaceStorage
            if InflTot > 0:
                # Update surface storage and infiltration storage
                if InflTot > prof.Ksat[0]:
                    # Infiltration limited by saturated hydraulic conductivity
                    # of surface soil layer
                    ToStore = prof.Ksat[0]
                    # Additional water ponds on surface
                    NewCond_SurfaceStorage = InflTot - prof.Ksat[0]
                else:
                    # All water infiltrates
                    ToStore = InflTot
                    # Reset surface storage depth to zero
                    NewCond_SurfaceStorage = 0

                # Calculate additional runoff
                if NewCond_SurfaceStorage > (FieldMngt_zBund * 1000):
                    # Water overtops bunds and runs off
                    RunoffIni = NewCond_SurfaceStorage - (FieldMngt_zBund * 1000)
                    # Surface storage equal to bund height
                    NewCond_SurfaceStorage = FieldMngt_zBund * 1000
                else:
                    # No overtopping of bunds
                    RunoffIni = 0

            else:
                # No storage or runoff
                ToStore = 0
                RunoffIni = 0

    elif FieldMngt_Bunds == False:
        # No bunds on field
        if Infl > prof.Ksat[0]:
            # Infiltration limited by saturated hydraulic conductivity of top
            # soil layer
            ToStore = prof.Ksat[0]
            # Additional water runs off
            RunoffIni = Infl - prof.Ksat[0]
        else:
            # All water infiltrates
            ToStore = Infl
            RunoffIni = 0

        # Update surface storage
        NewCond_SurfaceStorage = 0
        # Add any water remaining behind bunds to surface runoff (needed for
        # days when bunds are removed to maintain water balance)
        RunoffIni = RunoffIni + InitCond_SurfaceStorage

    ## Initialise counters
    ii = -1
    Runoff = 0
    ## Infiltrate incoming water ##
    if ToStore > 0:
        while (ToStore > 0) and (ii < Soil_nComp - 1):
            # Update compartment counter
            ii = ii + 1
            # Get soil layer

            # Calculate saturated drainage ability
            dthdtS = prof.tau[ii] * (prof.th_s[ii] - prof.th_fc[ii])
            # Calculate drainage factor
            factor = prof.Ksat[ii] / (dthdtS * 1000 * prof.dz[ii])

            # Calculate drainage ability required
            dthdt0 = ToStore / (1000 * prof.dz[ii])

            # Check drainage ability
            if dthdt0 < dthdtS:
                # Calculate water content, thX, needed to meet drainage dthdt0
                if dthdt0 <= 0:
                    theta0 = InitCond_th_fc_Adj[ii]
                else:
                    A = 1 + (
                        (dthdt0 * (np.exp(prof.th_s[ii] - prof.th_fc[ii]) - 1))
                        / (prof.tau[ii] * (prof.th_s[ii] - prof.th_fc[ii]))
                    )

                    theta0 = prof.th_fc[ii] + np.log(A)

                # Limit thX to between saturation and field capacity
                if theta0 > prof.th_s[ii]:
                    theta0 = prof.th_s[ii]
                elif theta0 <= InitCond_th_fc_Adj[ii]:
                    theta0 = InitCond_th_fc_Adj[ii]
                    dthdt0 = 0

            else:
                # Limit water content and drainage to saturation
                theta0 = prof.th_s[ii]
                dthdt0 = dthdtS

            # Calculate maximum water flow through compartment ii
            drainmax = factor * dthdt0 * 1000 * prof.dz[ii]
            # Calculate total drainage from compartment ii
            drainage = drainmax + FluxOut[ii]
            # Limit drainage to saturated hydraulic conductivity
            if drainage > prof.Ksat[ii]:
                drainmax = prof.Ksat[ii] - FluxOut[ii]

            # Calculate difference between threshold and current water contents
            diff = theta0 - InitCond_th[ii]

            if diff > 0:
                # Increase water content of compartment ii
                thnew[ii] = thnew[ii] + (ToStore / (1000 * prof.dz[ii]))
                if thnew[ii] > theta0:
                    # Water remaining that can infiltrate to compartments below
                    ToStore = (thnew[ii] - theta0) * 1000 * prof.dz[ii]
                    thnew[ii] = theta0
                else:
                    # All infiltrating water has been stored
                    ToStore = 0

            # Update outflow from current compartment (drainage + infiltration
            # flows)
            FluxOut[ii] = FluxOut[ii] + ToStore

            # Calculate back-up of water into compartments above
            excess = ToStore - drainmax
            if excess < 0:
                excess = 0

            # Update water to store
            ToStore = ToStore - excess

            # Redistribute excess to compartments above
            if excess > 0:
                precomp = ii + 1
                while (excess > 0) and (precomp != 0):
                    # Keep storing in compartments above until soil surface is
                    # reached
                    # Update compartment counter
                    precomp = precomp - 1
                    # Update layer number

                    # Update outflow from compartment
                    FluxOut[precomp] = FluxOut[precomp] - excess
                    # Update water content
                    thnew[precomp] = thnew[precomp] + (excess / (prof.dz[precomp] * 1000))
                    # Limit water content to saturation
                    if thnew[precomp] > prof.th_s[precomp]:
                        # Update excess to store
                        excess = (thnew[precomp] - prof.th_s[precomp]) * 1000 * prof.dz[precomp]
                        # Set water content to saturation
                        thnew[precomp] = prof.th_s[precomp]
                    else:
                        # All excess stored
                        excess = 0

                if excess > 0:
                    # Any leftover water not stored becomes runoff
                    Runoff = Runoff + excess

        # Infiltration left to store after bottom compartment becomes deep
        # percolation (mm)
        DeepPerc = ToStore
    else:
        # No infiltration
        DeepPerc = 0
        Runoff = 0

    ## Update total runoff ##
    Runoff = Runoff + RunoffIni

    ## Update surface storage (if bunds are present) ##
    if Runoff > RunoffIni:
        if FieldMngt_Bunds:
            if FieldMngt_zBund > 0.001:
                # Increase surface storage
                NewCond_SurfaceStorage = NewCond_SurfaceStorage + (Runoff - RunoffIni)
                # Limit surface storage to bund height
                if NewCond_SurfaceStorage > (FieldMngt_zBund * 1000):
                    # Additonal water above top of bunds becomes runoff
                    Runoff = RunoffIni + (NewCond_SurfaceStorage - (FieldMngt_zBund * 1000))
                    # Set surface storage to bund height
                    NewCond_SurfaceStorage = FieldMngt_zBund * 1000
                else:
                    # No additional overtopping of bunds
                    Runoff = RunoffIni

    ## Store updated water contents ##
    NewCond_th = thnew

    ## Update deep percolation, surface runoff, and infiltration values ##
    DeepPerc = DeepPerc + DeepPerc0
    Infl = Infl - Runoff
    RunoffTot = Runoff + Runoff0

    return NewCond_th,NewCond_SurfaceStorage, DeepPerc, RunoffTot, Infl, FluxOut

if __name__ == "__main__":
    cc.compile()
