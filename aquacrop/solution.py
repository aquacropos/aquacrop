# __all__ = ['growing_degree_day', 'root_zone_water', 'check_groundwater_table', 'root_development', 'pre_irrigation',
#            'drainage', 'rainfall_partition', 'irrigation', 'infiltration', 'capillary_rise', 'germination',
#            'growth_stage', 'water_stress', 'cc_development', 'cc_required_time', 'adjust_CCx', 'update_CCx_CDC',
#            'canopy_cover', 'evap_layer_water_content', 'soil_evaporation', 'aeration_stress', 'transpiration',
#            'groundwater_inflow', 'HIref_current_day', 'biomass_accumulation', 'temperature_stress',
#            'HIadj_pre_anthesis', 'HIadj_pollination', 'HIadj_post_anthesis', 'harvest_index']


# remove functions from __all__ as they become replace by compiled equivalent
__all__ = [
    "pre_irrigation",
    "capillary_rise",
    "irrigation",
    "germination",
    "growth_stage",
    "adjust_CCx",
    "canopy_cover",
    "transpiration",
    "groundwater_inflow",
    "harvest_index",
]

# Cell
try:
    from classes import *
except:
    from .classes import *

import numpy as np
from numba import njit, f8, i8, b1

# from aquacrop.classes import InitCondStructType
# InitCond_type_sig = InitCondStructType(fields=InitCond_spec)



from numba.pycc import CC

# temporary name for compiled module
cc = CC("solution_aot")

# This compiled function is called a few times inside other functions
if __name__ != "__main__":
    from .solution_aot import (
        _water_stress,
        _evap_layer_water_content,
        _root_zone_water,
        _cc_development,
        _update_CCx_CDC,
        _cc_required_time,
        _aeration_stress, 
        _temperature_stress, 
        _HIadj_pre_anthesis,                      
        _HIadj_post_anthesis, 
        _HIadj_pollination
        
        )

# Cell
# @njit()
@cc.export("_growing_degree_day", "f8(i4,f8,f8,f8,f8)")
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

# Cell
@njit
@cc.export("_root_zone_water", (SoilProfileNT_typ_sig,f8,f8[:],f8,f8,f8))
def root_zone_water(
    prof,
    InitCond_Zroot,
    InitCond_th,
    Soil_zTop,
    Crop_Zmin,
    Crop_Aer,
):
    """
    Function to calculate actual and total available water in the rootzone at current time step


    <a href="../pdfs/ac_ref_man_3.pdf#page=14" target="_blank">Reference Manual: root-zone water calculations</a> (pg. 5-8)


    *Arguments:*

    `prof`: `SoilProfileClass` : jit class Object containing soil paramaters

    `InitCond_Zroot`: `float` : Initial rooting depth

    `InitCond_th`: `np.array` : Initial water content

    `Soil_zTop`: `float` : Top soil depth

    `Crop_Zmin`: `float` : crop minimum rooting depth

    `Crop_Aer`: `int` : number of aeration stress days

    *Returns:*

     `WrAct`: `float` :  Actual rootzone water content

     `Dr`: `DrClass` :  Depletion objection containing rootzone and topsoil depletion

     `TAW`: `TAWClass` :  `TAWClass` containing rootzone and topsoil total avalable water

     `thRZ`: `thRZClass` :  thRZ object conaining rootzone water content paramaters



    """

    ## Calculate root zone water content and available water ##
    # Compartments covered by the root zone
    rootdepth = round(np.maximum(InitCond_Zroot, Crop_Zmin), 2)
    comp_sto = np.argwhere(prof.dzsum >= rootdepth).flatten()[0]

    # Initialise counters
    WrAct = 0
    WrS = 0
    WrFC = 0
    WrWP = 0
    WrDry = 0
    WrAer = 0
    for ii in range(comp_sto + 1):
        # Fraction of compartment covered by root zone
        if prof.dzsum[ii] > rootdepth:
            factor = 1 - ((prof.dzsum[ii] - rootdepth) / prof.dz[ii])
        else:
            factor = 1

        # Actual water storage in root zone (mm)
        WrAct = WrAct + round(factor * 1000 * InitCond_th[ii] * prof.dz[ii], 2)
        # Water storage in root zone at saturation (mm)
        WrS = WrS + round(factor * 1000 * prof.th_s[ii] * prof.dz[ii], 2)
        # Water storage in root zone at field capacity (mm)
        WrFC = WrFC + round(factor * 1000 * prof.th_fc[ii] * prof.dz[ii], 2)
        # Water storage in root zone at permanent wilting point (mm)
        WrWP = WrWP + round(factor * 1000 * prof.th_wp[ii] * prof.dz[ii], 2)
        # Water storage in root zone at air dry (mm)
        WrDry = WrDry + round(factor * 1000 * prof.th_dry[ii] * prof.dz[ii], 2)
        # Water storage in root zone at aeration stress threshold (mm)
        WrAer = WrAer + round(factor * 1000 * (prof.th_s[ii] - (Crop_Aer / 100)) * prof.dz[ii], 2)

    if WrAct < 0:
        WrAct = 0

    # define total available water, depletion, root zone water content
    # TAW = TAWClass()
    # Dr = DrClass()
    # thRZ = thRZClass()

    # Calculate total available water (m3/m3)
    TAW_Rz = max(WrFC - WrWP, 0.0)
    # Calculate soil water depletion (mm)
    Dr_Rz = min(WrFC - WrAct, TAW_Rz)

    # Actual root zone water content (m3/m3)
    thRZ_Act = WrAct / (rootdepth * 1000)
    # Root zone water content at saturation (m3/m3)
    thRZ_S = WrS / (rootdepth * 1000)
    # Root zone water content at field capacity (m3/m3)
    thRZ_FC = WrFC / (rootdepth * 1000)
    # Root zone water content at permanent wilting point (m3/m3)
    thRZ_WP = WrWP / (rootdepth * 1000)
    # Root zone water content at air dry (m3/m3)
    thRZ_Dry = WrDry / (rootdepth * 1000)
    # Root zone water content at aeration stress threshold (m3/m3)
    thRZ_Aer = WrAer / (rootdepth * 1000)

    # print('inside')

    # thRZ = thRZNT(
    # Act=thRZ_Act,
    # S=thRZ_S,
    # FC=thRZ_FC,
    # WP=thRZ_WP,
    # Dry=thRZ_Dry,
    # Aer=thRZ_Aer,
    # )
    # print(thRZ)


    ## Calculate top soil water content and available water ##
    if rootdepth > Soil_zTop:
        # Determine compartments covered by the top soil
        ztopdepth = round(Soil_zTop, 2)
        comp_sto = np.sum(prof.dzsum <= ztopdepth)
        # Initialise counters
        WrAct_Zt = 0
        WrFC_Zt = 0
        WrWP_Zt = 0
        # Calculate water storage in top soil
        assert comp_sto > 0

        for ii in range(comp_sto):

            # Fraction of compartment covered by root zone
            if prof.dzsum[ii] > ztopdepth:
                factor = 1 - ((prof.dzsum[ii] - ztopdepth) / prof.dz[ii])
            else:
                factor = 1

            # Actual water storage in top soil (mm)
            WrAct_Zt = WrAct_Zt + (factor * 1000 * InitCond_th[ii] * prof.dz[ii])
            # Water storage in top soil at field capacity (mm)
            WrFC_Zt = WrFC_Zt + (factor * 1000 * prof.th_fc[ii] * prof.dz[ii])
            # Water storage in top soil at permanent wilting point (mm)
            WrWP_Zt = WrWP_Zt + (factor * 1000 * prof.th_wp[ii] * prof.dz[ii])

        # Ensure available water in top soil is not less than zero
        if WrAct_Zt < 0:
            WrAct_Zt = 0

        # Calculate total available water in top soil (m3/m3)
        TAW_Zt = max(WrFC_Zt - WrWP_Zt, 0)
        # Calculate depletion in top soil (mm)
        Dr_Zt = min(WrFC_Zt - WrAct_Zt, TAW_Zt)
    else:
        # Set top soil depletions and TAW to root zone values
        Dr_Zt = Dr_Rz
        TAW_Zt = TAW_Rz


    return (
        WrAct,
        Dr_Zt,
        Dr_Rz,
        TAW_Zt,
        TAW_Rz,
        thRZ_Act,
        thRZ_S,
        thRZ_FC,
        thRZ_WP,
        thRZ_Dry,
        thRZ_Aer,
    )


# Cell
@cc.export("_check_groundwater_table", (SoilProfileNT_typ_sig,f8,f8[:],f8[:],i8,f8))
def check_groundwater_table(
    prof,
    NewCond_zGW,
    NewCond_th,
    NewCond_th_fc_Adj,
    water_table_presence,
    zGW,
):
    """
    Function to check for presence of a groundwater table, and, if present,
    to adjust compartment water contents and field capacities where necessary

    <a href="../pdfs/ac_ref_man_3.pdf#page=61" target="_blank">Reference manual: water table adjustment equations</a> (pg. 52-57)


    *Arguments:*

    `Soil`: `SoilClass` : Soil object containing soil paramaters

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `water_table_presence`: int :  indicates if water table is present or not


    *Returns:*

    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters

    `Soil`: `SoilClass` : Soil object containing updated soil paramaters




    """

    ## Perform calculations (if variable water table is present) ##
    if water_table_presence == 1:

        # Update groundwater conditions for current day
        NewCond_zGW = zGW

        # Find compartment mid-points
        zMid = prof.zMid

        # Check if water table is within modelled soil profile
        if NewCond_zGW >= 0:
            if len(zMid[zMid >= NewCond_zGW]) == 0:
                NewCond_WTinSoil = False
            else:
                NewCond_WTinSoil = True

        # If water table is in soil profile, adjust water contents
        if NewCond_WTinSoil == True:
            idx = np.argwhere(zMid >= NewCond_zGW).flatten()[0]
            for ii in range(idx, len(prof.Comp)):
                NewCond_th[ii] = prof.th_s[ii]

        # Adjust compartment field capacity
        compi = len(prof.Comp) - 1
        thfcAdj = np.zeros(compi + 1)
        # Find thFCadj for all compartments
        while compi >= 0:
            if prof.th_fc[compi] <= 0.1:
                Xmax = 1
            else:
                if prof.th_fc[compi] >= 0.3:
                    Xmax = 2
                else:
                    pF = 2 + 0.3 * (prof.th_fc[compi] - 0.1) / 0.2
                    Xmax = (np.exp(pF * np.log(10))) / 100

            if (NewCond_zGW < 0) or ((NewCond_zGW - zMid[compi]) >= Xmax):
                for ii in range(compi):

                    thfcAdj[ii] = prof.th_fc[ii]

                compi = -1
            else:
                if prof.th_fc[compi] >= prof.th_s[compi]:
                    thfcAdj[compi] = prof.th_fc[compi]
                else:
                    if zMid[compi] >= NewCond_zGW:
                        thfcAdj[compi] = prof.th_s[compi]
                    else:
                        dV = prof.th_s[compi] - prof.th_fc[compi]
                        dFC = (dV / (Xmax * Xmax)) * ((zMid[compi] - (NewCond_zGW - Xmax)) ** 2)
                        thfcAdj[compi] = prof.th_fc[compi] + dFC

                compi = compi - 1

        # Store adjusted field capacity values
        NewCond_th_fc_Adj = thfcAdj
        # prof.th_fc_Adj = thfcAdj

    return (NewCond_th_fc_Adj, thfcAdj)


# Cell
# @njit()
@cc.export("_root_development", (CropStructNT_type_sig,SoilProfileNT_typ_sig,f8,f8,f8,f8,f8,f8,f8[:],f8,f8,b1,f8,f8,f8,f8,b1,i8))
def root_development(Crop,
                    prof,
                    NewCond_DAP,
                    NewCond_Zroot,
                    NewCond_DelayedCDs,
                    NewCond_GDDcum,
                    NewCond_DelayedGDDs,
                    NewCond_TrRatio,
                    NewCond_th,
                    NewCond_CC,
                    NewCond_CC_NS,
                    NewCond_Germination,
                    NewCond_rCor,
                    NewCond_Tpot,
                    NewCond_zGW,
                    GDD,
                    GrowingSeason,
                    water_table_presence):
    """
    Function to calculate root zone expansion

    <a href="../pdfs/ac_ref_man_3.pdf#page=46" target="_blank">Reference Manual: root developement equations</a> (pg. 37-41)


    *Arguments:*

    `Crop`: `CropStruct` : jit class object containing Crop paramaters

    `prof`: `SoilProfileClass` : jit class object containing soil paramaters

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `GDD`: `float` : Growing degree days on current day

    `GrowingSeason`: `bool` : is growing season (True or Flase)

    `water_table_presence`: `int` : water table present (True=1 or Flase=0)


    *Returns:*

    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters


    """
    # Store initial conditions for updating
    # NewCond = InitCond

    # save initial zroot
    Zroot_init = float(NewCond_Zroot) * 1.0
    Soil_nLayer = np.unique(prof.Layer).shape[0]

    # Calculate root expansion (if in growing season)
    if GrowingSeason == True:
        # If today is first day of season, root depth is equal to minimum depth
        if NewCond_DAP == 1:
            NewCond_Zroot = float(Crop.Zmin) * 1.0
            Zroot_init = float(Crop.Zmin) * 1.0

        # Adjust time for any delayed development
        if Crop.CalendarType == 1:
            tAdj = NewCond_DAP - NewCond_DelayedCDs
        elif Crop.CalendarType == 2:
            tAdj = NewCond_GDDcum - NewCond_DelayedGDDs

        # Calculate root expansion #
        Zini = Crop.Zmin * (Crop.PctZmin / 100)
        t0 = round((Crop.Emergence / 2))
        tmax = Crop.MaxRooting
        if Crop.CalendarType == 1:
            tOld = tAdj - 1
        elif Crop.CalendarType == 2:
            tOld = tAdj - GDD

        # Potential root depth on previous day
        if tOld >= tmax:
            ZrOld = Crop.Zmax
        elif tOld <= t0:
            ZrOld = Zini
        else:
            X = (tOld - t0) / (tmax - t0)
            ZrOld = Zini + (Crop.Zmax - Zini) * np.power(X, 1 / Crop.fshape_r)

        if ZrOld < Crop.Zmin:
            ZrOld = Crop.Zmin

        # Potential root depth on current day
        if tAdj >= tmax:
            Zr = Crop.Zmax
        elif tAdj <= t0:
            Zr = Zini
        else:
            X = (tAdj - t0) / (tmax - t0)
            Zr = Zini + (Crop.Zmax - Zini) * np.power(X, 1 / Crop.fshape_r)

        if Zr < Crop.Zmin:
            Zr = Crop.Zmin

        # Store Zr as potential value
        ZrPot = Zr

        # Determine rate of change
        dZr = Zr - ZrOld

        # Adjust expansion rate for presence of restrictive soil horizons
        if Zr > Crop.Zmin:
            layeri = 1
            l_idx = np.argwhere(prof.Layer == layeri).flatten()
            Zsoil = prof.dz[l_idx].sum()
            while (round(Zsoil, 2) <= Crop.Zmin) and (layeri < Soil_nLayer):
                layeri = layeri + 1
                l_idx = np.argwhere(prof.Layer == layeri).flatten()
                Zsoil = Zsoil + prof.dz[l_idx].sum()

            soil_layer_dz = prof.dz[l_idx].sum()
            layer_comp = l_idx[0]
            # soil_layer = prof.Layer[layeri]
            ZrAdj = Crop.Zmin
            ZrRemain = Zr - Crop.Zmin
            deltaZ = Zsoil - Crop.Zmin
            EndProf = False
            while EndProf == False:
                ZrTest = ZrAdj + (ZrRemain * (prof.Penetrability[layer_comp] / 100))
                if (
                    (layeri == Soil_nLayer)
                    or (prof.Penetrability[layer_comp] == 0)
                    or (ZrTest <= Zsoil)
                ):
                    ZrOUT = ZrTest
                    EndProf = True
                else:
                    ZrAdj = Zsoil
                    ZrRemain = ZrRemain - (deltaZ / (prof.Penetrability[layer_comp] / 100))
                    layeri = layeri + 1
                    l_idx = np.argwhere(prof.Layer == layeri).flatten()
                    layer_comp = l_idx[0]
                    soil_layer_dz = prof.dz[l_idx].sum()
                    Zsoil = Zsoil + soil_layer_dz
                    deltaZ = soil_layer_dz

            # Correct Zr and dZr for effects of restrictive horizons
            Zr = ZrOUT
            dZr = Zr - ZrOld

        # Adjust rate of expansion for any stomatal water stress
        if NewCond_TrRatio < 0.9999:
            if Crop.fshape_ex >= 0:
                dZr = dZr * NewCond_TrRatio
            else:
                fAdj = (np.exp(NewCond_TrRatio * Crop.fshape_ex) - 1) / (np.exp(Crop.fshape_ex) - 1)
                dZr = dZr * fAdj

        # print(NewCond.DAP,NewCond.th)

        # Adjust rate of root expansion for dry soil at expansion front
        if dZr > 0.001:
            # Define water stress threshold for inhibition of root expansion
            pZexp = Crop.p_up[1] + ((1 - Crop.p_up[1]) / 2)
            # Define potential new root depth
            ZiTmp = float(Zroot_init + dZr)
            # Find compartment that root zone will expand in to
            # compi_index = prof.dzsum[prof.dzsum>=ZiTmp].index[0] # have changed to index
            idx = np.argwhere(prof.dzsum >= ZiTmp).flatten()[0]
            prof = prof
            # Get TAW in compartment
            layeri = prof.Layer[idx]
            TAWprof = prof.th_fc[idx] - prof.th_wp[idx]
            # Define stress threshold
            thThr = prof.th_fc[idx] - (pZexp * TAWprof)
            # Check for stress conditions
            if NewCond_th[idx] < thThr:
                # Root expansion limited by water content at expansion front
                if NewCond_th[idx] <= prof.th_wp[idx]:

                    # Expansion fully inhibited
                    dZr = 0
                else:
                    # Expansion partially inhibited
                    Wrel = (prof.th_fc[idx] - NewCond_th[idx]) / TAWprof
                    Drel = 1 - ((1 - Wrel) / (1 - pZexp))
                    Ks = 1 - (
                        (np.exp(Drel * Crop.fshape_w[1]) - 1) / (np.exp(Crop.fshape_w[1]) - 1)
                    )
                    dZr = dZr * Ks

        # Adjust for early senescence
        if (NewCond_CC <= 0) and (NewCond_CC_NS > 0.5):
            dZr = 0

        # Adjust root expansion for failure to germinate (roots cannot expand
        # if crop has not germinated)
        if NewCond_Germination == False:
            dZr = 0

        # Get new rooting depth
        NewCond_Zroot = float(Zroot_init + dZr)

        # Adjust root density if deepening is restricted due to dry subsoil
        # and/or restrictive layers
        if NewCond_Zroot < ZrPot:
            NewCond_rCor = (
                2 * (ZrPot / NewCond_Zroot) * ((Crop.SxTop + Crop.SxBot) / 2) - Crop.SxTop
            ) / Crop.SxBot

            if NewCond_Tpot > 0:
                NewCond_rCor = NewCond_rCor * NewCond_TrRatio
                if NewCond_rCor < 1:
                    NewCond_rCor = 1

        else:
            NewCond_rCor = 1

        # Limit rooting depth if groundwater table is present (roots cannot
        # develop below the water table)
        if (water_table_presence == 1) and (NewCond_zGW > 0):
            if NewCond_Zroot > NewCond_zGW:
                NewCond_Zroot = float(NewCond_zGW)
                if NewCond_Zroot < Crop.Zmin:
                    NewCond_Zroot = float(Crop.Zmin)

    else:
        # No root system outside of the growing season
        NewCond_Zroot = 0

    return NewCond_Zroot


# Cell
# @njit()
def pre_irrigation(prof, Crop, InitCond, GrowingSeason, IrrMngt):
    """
    Function to calculate pre-irrigation when in net irrigation mode

    <a href="../pdfs/ac_ref_man_1.pdf#page=40" target="_blank">Reference Manual: Net irrigation description</a> (pg. 31)


    *Arguments:*

    `prof`: `SoilProfileClass` : Soil object containing soil paramaters

    `Crop`: `CropStruct` : Crop object containing Crop paramaters

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `GrowingSeason`: `bool` : is growing season (True or Flase)

    `IrrMngt`: ``IrrMngtStruct`  object containing irrigation management paramaters



    *Returns:*

    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters

    `PreIrr`: `float` : Pre-Irrigaiton applied on current day mm




    """
    # Store initial conditions for updating ##
    NewCond = InitCond

    ## Calculate pre-irrigation needs ##
    if GrowingSeason == True:
        if (IrrMngt.IrrMethod != 4) or (NewCond.DAP != 1):
            # No pre-irrigation as not in net irrigation mode or not on first day
            # of the growing season
            PreIrr = 0
        else:
            # Determine compartments covered by the root zone
            rootdepth = round(max(NewCond.Zroot, Crop.Zmin), 2)

            compRz = np.argwhere(prof.dzsum >= rootdepth).flatten()[0]

            PreIrr = 0
            for ii in range(int(compRz)):

                # Determine critical water content threshold
                thCrit = prof.th_wp[ii] + (
                    (IrrMngt.NetIrrSMT / 100) * (prof.th_fc[ii] - prof.th_wp[ii])
                )

                # Check if pre-irrigation is required
                if NewCond.th[ii] < thCrit:
                    PreIrr = PreIrr + ((thCrit - NewCond.th[ii]) * 1000 * prof.dz[ii])
                    NewCond.th[ii] = thCrit

    else:
        PreIrr = 0

    return NewCond, PreIrr


# Cell
# @njit()
@cc.export("_drainage", (SoilProfileNT_typ_sig,f8[:],f8[:]))
def drainage(
    prof, th_init, th_fc_Adj_init
):
    """
    Function to redistribute stored soil water



    <a href="../pdfs/ac_ref_man_3.pdf#page=51" target="_blank">Reference Manual: drainage calculations</a> (pg. 42-65)


    *Arguments:*



    `prof`: `SoilProfileClass` : jit class object object containing soil paramaters

    `th_init`: `np.array` : initial water content

    `th_fc_Adj_init`: `np.array` : adjusted water content at field capacity


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters

    `DeepPerc`:: `float` : Total Deep Percolation

    `FluxOut`:: `array-like` : Flux of water out of each compartment





    """

    # Store initial conditions in new structure for updating %%
    #     NewCond = InitCond

    #     th_init = InitCond.th
    #     th_fc_Adj_init = InitCond.th_fc_Adj

    #  Preallocate arrays %%
    thnew = np.zeros(th_init.shape[0])
    FluxOut = np.zeros(th_init.shape[0])

    # Initialise counters and states %%
    drainsum = 0

    # Calculate drainage and updated water contents %%
    for ii in range(th_init.shape[0]):
        # Specify layer for compartment
        cth_fc = prof.th_fc[ii]
        cth_s = prof.th_s[ii]
        ctau = prof.tau[ii]
        cdz = prof.dz[ii]
        cdzsum = prof.dzsum[ii]
        cKsat = prof.Ksat[ii]

        # Calculate drainage ability of compartment ii
        if th_init[ii] <= th_fc_Adj_init[ii]:
            dthdt = 0

        elif th_init[ii] >= cth_s:
            dthdt = ctau * (cth_s - cth_fc)

            if (th_init[ii] - dthdt) < th_fc_Adj_init[ii]:
                dthdt = th_init[ii] - th_fc_Adj_init[ii]

        else:
            dthdt = (
                ctau
                * (cth_s - cth_fc)
                * ((np.exp(th_init[ii] - cth_fc) - 1) / (np.exp(cth_s - cth_fc) - 1))
            )

            if (th_init[ii] - dthdt) < th_fc_Adj_init[ii]:
                dthdt = th_init[ii] - th_fc_Adj_init[ii]

        # Drainage from compartment ii (mm)
        draincomp = dthdt * cdz * 1000

        # Check drainage ability of compartment ii against cumulative drainage
        # from compartments above
        excess = 0
        prethick = cdzsum - cdz
        drainmax = dthdt * 1000 * prethick
        if drainsum <= drainmax:
            drainability = True
        else:
            drainability = False

        # Drain compartment ii
        if drainability == True:
            # No storage needed. Update water content in compartment ii
            thnew[ii] = th_init[ii] - dthdt

            # Update cumulative drainage (mm)
            drainsum = drainsum + draincomp

            # Restrict cumulative drainage to saturated hydraulic
            # conductivity and adjust excess drainage flow
            if drainsum > cKsat:
                excess = excess + drainsum - cKsat
                drainsum = cKsat

        elif drainability == False:
            # Storage is needed
            dthdt = drainsum / (1000 * prethick)

            # Calculate value of theta (thX) needed to provide a
            # drainage ability equal to cumulative drainage
            if dthdt <= 0:
                thX = th_fc_Adj_init[ii]
            elif ctau > 0:
                A = 1 + ((dthdt * (np.exp(cth_s - cth_fc) - 1)) / (ctau * (cth_s - cth_fc)))
                thX = cth_fc + np.log(A)
                if thX < th_fc_Adj_init[ii]:
                    thX = th_fc_Adj_init[ii]

            else:
                thX = cth_s + 0.01

            # Check thX against hydraulic properties of current soil layer
            if thX <= cth_s:
                # Increase compartment ii water content with cumulative
                # drainage
                thnew[ii] = th_init[ii] + (drainsum / (1000 * cdz))
                # Check updated water content against thX
                if thnew[ii] > thX:
                    # Cumulative drainage is the drainage difference
                    # between theta_x and new theta plus drainage ability
                    # at theta_x.
                    drainsum = (thnew[ii] - thX) * 1000 * cdz
                    # Calculate drainage ability for thX
                    if thX <= th_fc_Adj_init[ii]:
                        dthdt = 0
                    elif thX >= cth_s:
                        dthdt = ctau * (cth_s - cth_fc)
                        if (thX - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thX - th_fc_Adj_init[ii]

                    else:
                        dthdt = (
                            ctau
                            * (cth_s - cth_fc)
                            * ((np.exp(thX - cth_fc) - 1) / (np.exp(cth_s - cth_fc) - 1))
                        )

                        if (thX - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thX - th_fc_Adj_init[ii]

                    # Update drainage total
                    drainsum = drainsum + (dthdt * 1000 * cdz)
                    # Restrict cumulative drainage to saturated hydraulic
                    # conductivity and adjust excess drainage flow
                    if drainsum > cKsat:
                        excess = excess + drainsum - cKsat
                        drainsum = cKsat

                    # Update water content
                    thnew[ii] = thX - dthdt

                elif thnew[ii] > th_fc_Adj_init[ii]:
                    # Calculate drainage ability for updated water content
                    if thnew[ii] <= th_fc_Adj_init[ii]:
                        dthdt = 0
                    elif thnew[ii] >= cth_s:
                        dthdt = ctau * (cth_s - cth_fc)
                        if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thnew[ii] - th_fc_Adj_init[ii]

                    else:
                        dthdt = (
                            ctau
                            * (cth_s - cth_fc)
                            * ((np.exp(thnew[ii] - cth_fc) - 1) / (np.exp(cth_s - cth_fc) - 1))
                        )
                        if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thnew[ii] - th_fc_Adj_init[ii]

                    # Update water content in compartment ii
                    thnew[ii] = thnew[ii] - dthdt
                    # Update cumulative drainage
                    drainsum = dthdt * 1000 * cdz
                    # Restrict cumulative drainage to saturated hydraulic
                    # conductivity and adjust excess drainage flow
                    if drainsum > cKsat:
                        excess = excess + drainsum - cKsat
                        drainsum = cKsat

                else:
                    # Drainage and cumulative drainage are zero as water
                    # content has not risen above field capacity in
                    # compartment ii.
                    drainsum = 0

            elif thX > cth_s:
                # Increase water content in compartment ii with cumulative
                # drainage from above
                thnew[ii] = th_init[ii] + (drainsum / (1000 * cdz))
                # Check new water content against hydraulic properties of soil
                # layer
                if thnew[ii] <= cth_s:
                    if thnew[ii] > th_fc_Adj_init[ii]:
                        # Calculate new drainage ability
                        if thnew[ii] <= th_fc_Adj_init[ii]:
                            dthdt = 0
                        elif thnew[ii] >= cth_s:
                            dthdt = ctau * (cth_s - cth_fc)
                            if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                                dthdt = thnew[ii] - th_fc_Adj_init[ii]

                        else:
                            dthdt = (
                                ctau
                                * (cth_s - cth_fc)
                                * ((np.exp(thnew[ii] - cth_fc) - 1) / (np.exp(cth_s - cth_fc) - 1))
                            )
                            if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                                dthdt = thnew[ii] - th_fc_Adj_init[ii]

                        # Update water content in compartment ii
                        thnew[ii] = thnew[ii] - dthdt
                        # Update cumulative drainage
                        drainsum = dthdt * 1000 * cdz
                        # Restrict cumulative drainage to saturated hydraulic
                        # conductivity and adjust excess drainage flow
                        if drainsum > cKsat:
                            excess = excess + drainsum - cKsat
                            drainsum = cKsat

                    else:
                        drainsum = 0

                elif thnew[ii] > cth_s:
                    # Calculate excess drainage above saturation
                    excess = (thnew[ii] - cth_s) * 1000 * cdz
                    # Calculate drainage ability for updated water content
                    if thnew[ii] <= th_fc_Adj_init[ii]:
                        dthdt = 0
                    elif thnew[ii] >= cth_s:
                        dthdt = ctau * (cth_s - cth_fc)
                        if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thnew[ii] - th_fc_Adj_init[ii]

                    else:
                        dthdt = (
                            ctau
                            * (cth_s - cth_fc)
                            * ((np.exp(thnew[ii] - cth_fc) - 1) / (np.exp(cth_s - cth_fc) - 1))
                        )
                        if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thnew[ii] - th_fc_Adj_init[ii]

                    # Update water content in compartment ii
                    thnew[ii] = cth_s - dthdt

                    # Update drainage from compartment ii
                    draincomp = dthdt * 1000 * cdz
                    # Update maximum drainage
                    drainmax = dthdt * 1000 * prethick

                    # Update excess drainage
                    if drainmax > excess:
                        drainmax = excess

                    excess = excess - drainmax
                    # Update drainsum and restrict to saturated hydraulic
                    # conductivity of soil layer
                    drainsum = draincomp + drainmax
                    if drainsum > cKsat:
                        excess = excess + drainsum - cKsat
                        drainsum = cKsat

        # Store output flux from compartment ii
        FluxOut[ii] = drainsum

        # Redistribute excess in compartment above
        if excess > 0:
            precomp = ii + 1
            while (excess > 0) and (precomp != 0):
                # Update compartment counter
                precomp = precomp - 1
                # Update layer counter
                # precompdf = Soil.Profile.Comp[precomp]

                # Update flux from compartment
                if precomp < ii:
                    FluxOut[precomp] = FluxOut[precomp] - excess

                # Increase water content to store excess
                thnew[precomp] = thnew[precomp] + (excess / (1000 * prof.dz[precomp]))

                # Limit water content to saturation and adjust excess counter
                if thnew[precomp] > prof.th_s[precomp]:
                    excess = (thnew[precomp] - prof.th_s[precomp]) * 1000 * prof.dz[precomp]
                    thnew[precomp] = prof.th_s[precomp]
                else:
                    excess = 0

    ## Update conditions and outputs ##
    # Total deep percolation (mm)
    DeepPerc = drainsum
    # Water contents
    # NewCond.th = thnew

    return thnew, DeepPerc, FluxOut


# Cell
# @njit()
@cc.export("_rainfall_partition", (f8,f8[:],i8,f8,f8,f8,f8,f8,f8,f8,f8,SoilProfileNT_typ_sig))
def rainfall_partition(
    P,
    InitCond_th,
    NewCond_DaySubmerged,
    FieldMngt_SRinhb,
    FieldMngt_Bunds,
    FieldMngt_zBund,
    FieldMngt_CNadjPct,
    Soil_CN,
    Soil_AdjCN,
    Soil_zCN,
    Soil_nComp,
    prof,
):
    """
    Function to partition rainfall into surface runoff and infiltration using the curve number approach


    <a href="../pdfs/ac_ref_man_3.pdf#page=57" target="_blank">Reference Manual: rainfall partition calculations</a> (pg. 48-51)



    *Arguments:*


    `P`: `float` : Percipitation on current day

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `FieldMngt`: `FieldMngtStruct` : field management params

    `Soil_CN`: `float` : curve number

    `Soil_AdjCN`: `float` : adjusted curve number

    `Soil_zCN`: `float` :

    `Soil_nComp`: `float` : number of compartments

    `prof`: `SoilProfileClass` : Soil object


    *Returns:*

    `Runoff`: `float` : Total Suface Runoff

    `Infl`: `float` : Total Infiltration

    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters






    """

    # can probs make this faster by doing a if P=0 loop

    ## Store initial conditions for updating ##
    # NewCond = InitCond

    ## Calculate runoff ##
    if (FieldMngt_SRinhb == False) and ((FieldMngt_Bunds == False) or (FieldMngt_zBund < 0.001)):
        # Surface runoff is not inhibited and no soil bunds are on field
        # Reset submerged days
        NewCond_DaySubmerged = 0
        # Adjust curve number for field management practices
        CN = Soil_CN * (1 + (FieldMngt_CNadjPct / 100))
        if Soil_AdjCN == 1:  # Adjust CN for antecedent moisture
            # Calculate upper and lowe curve number bounds
            CNbot = round(
                1.4 * (np.exp(-14 * np.log(10)))
                + (0.507 * CN)
                - (0.00374 * CN ** 2)
                + (0.0000867 * CN ** 3)
            )
            CNtop = round(
                5.6 * (np.exp(-14 * np.log(10)))
                + (2.33 * CN)
                - (0.0209 * CN ** 2)
                + (0.000076 * CN ** 3)
            )
            # Check which compartment cover depth of top soil used to adjust
            # curve number
            comp_sto_array = prof.dzsum[prof.dzsum >= Soil_zCN]
            if comp_sto_array.shape[0] == 0:
                comp_sto = int(Soil_nComp)
            else:
                comp_sto = int(Soil_nComp - comp_sto_array.shape[0])

            # Calculate weighting factors by compartment
            xx = 0
            wrel = np.zeros(comp_sto)
            for ii in range(comp_sto):
                if prof.dzsum[ii] > Soil_zCN:
                    prof.dzsum[ii] = Soil_zCN

                wx = 1.016 * (1 - np.exp(-4.16 * (prof.dzsum[ii] / Soil_zCN)))
                wrel[ii] = wx - xx
                if wrel[ii] < 0:
                    wrel[ii] = 0
                elif wrel[ii] > 1:
                    wrel[ii] = 1

                xx = wx

            # Calculate relative wetness of top soil
            wet_top = 0
            # prof = prof

            for ii in range(comp_sto):
                th = max(prof.th_wp[ii], InitCond_th[ii])
                wet_top = wet_top + (
                    wrel[ii] * ((th - prof.th_wp[ii]) / (prof.th_fc[ii] - prof.th_wp[ii]))
                )

            # Calculate adjusted curve number
            if wet_top > 1:
                wet_top = 1
            elif wet_top < 0:
                wet_top = 0

            CN = round(CNbot + (CNtop - CNbot) * wet_top)

        # Partition rainfall into runoff and infiltration (mm)
        S = (25400 / CN) - 254
        term = P - ((5 / 100) * S)
        if term <= 0:
            Runoff = 0
            Infl = P
        else:
            Runoff = (term ** 2) / (P + (1 - (5 / 100)) * S)
            Infl = P - Runoff

    else:
        # Bunds on field, therefore no surface runoff
        Runoff = 0
        Infl = P

    return Runoff, Infl, NewCond_DaySubmerged


# Cell
# @njit()
# @cc.export("_irrigation", (i8,f8[:],f8,f8,i8,f8[:],f8,f8,f8,f8,f8,f8[:],i8,i8,CropStructNT_type_sig,SoilProfileNT_typ_sig,f8,b1,f8,f8))
# @njit
def irrigation(
    IrrMngt_IrrMethod,
    IrrMngt_SMT,
    IrrMngt_AppEff,
    IrrMngt_MaxIrr,
    IrrMngt_IrrInterval,
    IrrMngt_Schedule,
    IrrMngt_depth,
    IrrMngt_MaxIrrSeason,
    NewCond_GrowthStage,
    NewCond_IrrCum,
    NewCond_Epot,
    NewCond_Tpot,
    NewCond_Zroot,
    NewCond_th,
    NewCond_DAP,
    NewCond_TimeStepCounter,
    Crop, prof, Soil_zTop, GrowingSeason, Rain, Runoff):
    """
    Function to get irrigation depth for current day



    <a href="../pdfs/ac_ref_man_1.pdf#page=40" target="_blank">Reference Manual: irrigation description</a> (pg. 31-32)


    *Arguments:*


    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `IrrMngt`: `IrrMngtStruct`: jit class object containing irrigation management paramaters

    `Crop`: `CropClass` : Crop object containing Crop paramaters

    `Soil`: `SoilClass` : Soil object containing soil paramaters

    `GrowingSeason`: `bool` : is growing season (True or Flase)

    `Rain`: `float` : daily precipitation mm

    `Runoff`: `float` : surface runoff on current day


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters

    `Irr`: `float` : Irrigaiton applied on current day mm

"""
    ## Store intial conditions for updating ##
    # NewCond = InitCond

    ## Determine irrigation depth (mm/day) to be applied ##
    if GrowingSeason == True:
        # Calculate root zone water content and depletion
        # TAW_ = TAWClass()
        # Dr_ = DrClass()
        # thRZ = thRZClass()
        (
            WrAct,
            Dr_Zt,
            Dr_Rz,
            TAW_Zt,
            TAW_Rz,
            thRZ_Act,
            thRZ_S,
            thRZ_FC,
            thRZ_WP,
            thRZ_Dry,
            thRZ_Aer,
        ) = _root_zone_water(
            prof,
            float(NewCond_Zroot),
            NewCond_th,
            Soil_zTop,
            float(Crop.Zmin),
            Crop.Aer,
        )
        # WrAct,Dr_,TAW_,thRZ = root_zone_water(prof,float(NewCond.Zroot),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
        # Use root zone depletions and TAW only for triggering irrigation
        Dr = Dr_Rz
        TAW = TAW_Rz

        # Determine adjustment for inflows and outflows on current day #
        if thRZ_Act > thRZ_FC:
            rootdepth = max(NewCond_Zroot, Crop.Zmin)
            AbvFc = (thRZ_Act - thRZ_FC) * 1000 * rootdepth
        else:
            AbvFc = 0

        WCadj = NewCond_Tpot + NewCond_Epot - Rain + Runoff - AbvFc

        NewCond_Depletion = Dr + WCadj
        NewCond_TAW = TAW

        # Update growth stage if it is first day of a growing season
        if NewCond_DAP == 1:
            NewCond_GrowthStage = 1

        if IrrMngt_IrrMethod == 0:
            Irr = 0

        elif IrrMngt_IrrMethod == 1:

            Dr = NewCond_Depletion / NewCond_TAW
            index = int(NewCond_GrowthStage) - 1

            if Dr > 1 - IrrMngt_SMT[index] / 100:
                # Irrigation occurs
                IrrReq = max(0, NewCond_Depletion)
                # Adjust irrigation requirements for application efficiency
                EffAdj = ((100 - IrrMngt_AppEff) + 100) / 100
                IrrReq = IrrReq * EffAdj
                # Limit irrigation to maximum depth
                Irr = min(IrrMngt_MaxIrr, IrrReq)
            else:
                Irr = 0

        elif IrrMngt_IrrMethod == 2:  # Irrigation - fixed interval

            Dr = NewCond_Depletion

            # Get number of days in growing season so far (subtract 1 so that
            # always irrigate first on day 1 of each growing season)
            nDays = NewCond_DAP - 1

            if nDays % IrrMngt_IrrInterval == 0:
                # Irrigation occurs
                IrrReq = max(0, Dr)
                # Adjust irrigation requirements for application efficiency
                EffAdj = ((100 - IrrMngt_AppEff) + 100) / 100
                IrrReq = IrrReq * EffAdj
                # Limit irrigation to maximum depth
                Irr = min(IrrMngt_MaxIrr, IrrReq)
            else:
                # No irrigation
                Irr = 0

        elif IrrMngt_IrrMethod == 3:  # Irrigation - pre-defined schedule
            # Get current date
            idx = NewCond_TimeStepCounter
            # Find irrigation value corresponding to current date
            Irr = IrrMngt_Schedule[idx]

            assert Irr >= 0

            Irr = min(IrrMngt_MaxIrr, Irr)

        elif IrrMngt_IrrMethod == 4:  # Irrigation - net irrigation
            # Net irrigation calculation performed after transpiration, so
            # irrigation is zero here

            Irr = 0

        elif IrrMngt_IrrMethod == 5:  # depth applied each day (usually specified outside of model)

            Irr = min(IrrMngt_MaxIrr, IrrMngt_depth)

        #         else:
        #             assert 1 ==2, f'somethings gone wrong in irrigation method:{IrrMngt.IrrMethod}'

        Irr = max(0, Irr)

    elif GrowingSeason == False:
        # No irrigation outside growing season
        Irr = 0.
        NewCond_IrrCum = 0.
        NewCond_Depletion = 0.
        NewCond_TAW = 0.


    if NewCond_IrrCum + Irr > IrrMngt_MaxIrrSeason:
        Irr = max(0, IrrMngt_MaxIrrSeason - NewCond_IrrCum)

    # Update cumulative irrigation counter for growing season
    NewCond_IrrCum = NewCond_IrrCum + Irr

    return NewCond_Depletion,NewCond_TAW,NewCond_IrrCum, Irr


# Cell
# @njit()
@cc.export("_infiltration", (SoilProfileNT_typ_sig,f8,f8[:],f8[:],f8,f8,f8,b1,f8,f8[:],f8,f8,b1))
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
     GrowingSeason
):
    """
    Function to infiltrate incoming water (rainfall and irrigation)

    <a href="../pdfs/ac_ref_man_3.pdf#page=51" target="_blank">Reference Manual: drainage calculations</a> (pg. 42-65)



    *Arguments:*



    `prof`: `SoilProfileClass` : Soil object containing soil paramaters

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `Infl`: `float` : Infiltration so far

    `Irr`: `float` : Irrigation on current day

    `IrrMngt_AppEff`: `float`: irrigation application efficiency

    `FieldMngt`: `FieldMngtStruct` : field management params

    `FluxOut`: `np.array` : flux of water out of each compartment

    `DeepPerc0`: `float` : initial Deep Percolation

    `Runoff0`: `float` : initial Surface Runoff

    `GrowingSeason`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters

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

    ## Update infiltration rate for irrigation ##
    # Note: irrigation amount adjusted for specified application efficiency
    if GrowingSeason == True:
        Infl = Infl + (Irr * (IrrMngt_AppEff / 100))

    assert Infl >= 0

    ## Determine surface storage (if bunds are present) ##
    if FieldMngt_Bunds:
        # Bunds on field
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


# Cell
# @njit()
def capillary_rise(prof, Soil_nLayer, Soil_fshape_cr, NewCond, FluxOut, water_table_presence):
    """
    Function to calculate capillary rise from a shallow groundwater table


    <a href="../pdfs/ac_ref_man_3.pdf#page=61" target="_blank">Reference Manual: capillary rise calculations</a> (pg. 52-61)


    *Arguments:*



    `Soil`: `SoilClass` : Soil object

    `NewCond`: `InitCondClass` : InitCond object containing model paramaters

    `FluxOut`: `np.array` : FLux of water out of each soil compartment

    `water_table_presence`: `int` : WaterTable present (1:yes, 0:no)


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters

    `CrTot`: `float` : Total Capillary rise





    """

    ## Get groundwater table elevation on current day ##
    zGW = NewCond.zGW

    ## Calculate capillary rise ##
    if water_table_presence == 0:  # No water table present
        # Capillary rise is zero
        CrTot = 0
    elif water_table_presence == 1:  # Water table present
        # Get maximum capillary rise for bottom compartment
        zBot = prof.dzsum[-1]
        zBotMid = prof.zMid[-1]
        prof = prof
        if (prof.Ksat[-1] > 0) and (zGW > 0) and ((zGW - zBotMid) < 4):
            if zBotMid >= zGW:
                MaxCR = 99
            else:
                MaxCR = np.exp((np.log(zGW - zBotMid) - prof.bCR[-1]) / prof.aCR[-1])
                if MaxCR > 99:
                    MaxCR = 99

        else:
            MaxCR = 0

        ######################### this needs fixing, will currently break####################

        #         # Find top of next soil layer that is not within modelled soil profile
        #         zTopLayer = 0
        #         for layeri in np.sort(np.unique(prof.Layer)):
        #             # Calculate layer thickness
        #             l_idx = np.argwhere(prof.Layer==layeri).flatten()

        #             LayThk = prof.dz[l_idx].sum()
        #             zTopLayer = zTopLayer+LayThk

        #         # Check for restrictions on upward flow caused by properties of
        #         # compartments that are not modelled in the soil water balance
        #         layeri = prof.Layer[-1]

        #         assert layeri == Soil_nLayer

        #         while (zTopLayer < zGW) and (layeri < Soil_nLayer):
        #             # this needs fixing, will currently break

        #             layeri = layeri+1
        #             compdf = prof.Layer[layeri]
        #             if (compdf.Ksat > 0) and (zGW > 0) and ((zGW-zTopLayer) < 4):
        #                 if zTopLayer >= zGW:
        #                     LimCR = 99
        #                 else:
        #                     LimCR = np.exp((np.log(zGW-zTopLayer)-compdf.bCR)/compdf.aCR)
        #                     if LimCR > 99:
        #                         LimCR = 99

        #             else:
        #                 LimCR = 0

        #             if MaxCR > LimCR:
        #                 MaxCR = LimCR

        #             zTopLayer = zTopLayer+compdf.dz

        #####################################################################################

        # Calculate capillary rise
        compi = len(prof.Comp) - 1  # Start at bottom of root zone
        WCr = 0  # Capillary rise counter
        while (round(MaxCR * 1000) > 0) and (compi > -1) and (round(FluxOut[compi] * 1000) == 0):
            # Proceed upwards until maximum capillary rise occurs, soil surface
            # is reached, or encounter a compartment where downward
            # drainage/infiltration has already occurred on current day
            # Find layer of current compartment
            # Calculate driving force
            if (NewCond.th[compi] >= prof.th_wp[compi]) and (Soil_fshape_cr > 0):
                Df = 1 - (
                    (
                        (NewCond.th[compi] - prof.th_wp[compi])
                        / (NewCond.th_fc_Adj[compi] - prof.th_wp[compi])
                    )
                    ** Soil_fshape_cr
                )
                if Df > 1:
                    Df = 1
                elif Df < 0:
                    Df = 0

            else:
                Df = 1

            # Calculate relative hydraulic conductivity
            thThr = (prof.th_wp[compi] + prof.th_fc[compi]) / 2
            if NewCond.th[compi] < thThr:
                if (NewCond.th[compi] <= prof.th_wp[compi]) or (thThr <= prof.th_wp[compi]):
                    Krel = 0
                else:
                    Krel = (NewCond.th[compi] - prof.th_wp[compi]) / (thThr - prof.th_wp[compi])

            else:
                Krel = 1

            # Check if room is available to store water from capillary rise
            dth = NewCond.th_fc_Adj[compi] - NewCond.th[compi]

            # Store water if room is available
            if (dth > 0) and ((zBot - prof.dz[compi] / 2) < zGW):
                dthMax = Krel * Df * MaxCR / (1000 * prof.dz[compi])
                if dth >= dthMax:
                    NewCond.th[compi] = NewCond.th[compi] + dthMax
                    CRcomp = dthMax * 1000 * prof.dz[compi]
                    MaxCR = 0
                else:
                    NewCond.th[compi] = NewCond.th_fc_Adj[compi]
                    CRcomp = dth * 1000 * prof.dz[compi]
                    MaxCR = (Krel * MaxCR) - CRcomp

                WCr = WCr + CRcomp

            # Update bottom elevation of compartment
            zBot = zBot - prof.dz[compi]
            # Update compartment and layer counters
            compi = compi - 1
            # Update restriction on maximum capillary rise
            if compi > -1:

                zBotMid = zBot - (prof.dz[compi] / 2)
                if (prof.Ksat[compi] > 0) and (zGW > 0) and ((zGW - zBotMid) < 4):
                    if zBotMid >= zGW:
                        LimCR = 99
                    else:
                        LimCR = np.exp((np.log(zGW - zBotMid) - prof.bCR[compi]) / prof.aCR[compi])
                        if LimCR > 99:
                            LimCR = 99

                else:
                    LimCR = 0

                if MaxCR > LimCR:
                    MaxCR = LimCR

        # Store total depth of capillary rise
        CrTot = WCr

    return NewCond, CrTot


# Cell
# @njit()
def germination(InitCond, Soil_zGerm, prof, Crop_GermThr, Crop_PlantMethod, GDD, GrowingSeason):
    """
    Function to check if crop has germinated


    <a href="../pdfs/ac_ref_man_3.pdf#page=32" target="_blank">Reference Manual: germination condition</a> (pg. 23)


    *Arguments:*


    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `Soil_zGerm`: `float` : Soil depth affecting germination

    `prof`: `SoilProfileClass` : Soil object containing soil paramaters

    `Crop_GermThr`: `float` : Crop germination threshold

    `Crop_PlantMethod`: `bool` : sown as seedling True or False

    `GDD`: `float` : Number of Growing Degree Days on current day

    `GrowingSeason`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters







    """

    ## Store initial conditions in new structure for updating ##
    NewCond = InitCond

    ## Check for germination (if in growing season) ##
    if GrowingSeason == True:

        if (NewCond.Germination == False):
            # Find compartments covered by top soil layer affecting germination
            comp_sto = np.argwhere(prof.dzsum >= Soil_zGerm).flatten()[0]
            # Calculate water content in top soil layer
            Wr = 0
            WrFC = 0
            WrWP = 0
            for ii in range(comp_sto + 1):
                # Get soil layer
                # Determine fraction of compartment covered by top soil layer
                if prof.dzsum[ii] > Soil_zGerm:
                    factor = 1 - ((prof.dzsum[ii] - Soil_zGerm) / prof.dz[ii])
                else:
                    factor = 1

                # Increment actual water storage (mm)
                Wr = Wr + round(factor * 1000 * InitCond.th[ii] * prof.dz[ii], 3)
                # Increment water storage at field capacity (mm)
                WrFC = WrFC + round(factor * 1000 * prof.th_fc[ii] * prof.dz[ii], 3)
                # Increment water storage at permanent wilting point (mm)
                WrWP = WrWP + round(factor * 1000 * prof.th_wp[ii] * prof.dz[ii], 3)

            # Limit actual water storage to not be less than zero
            if Wr < 0:
                Wr = 0

            # Calculate proportional water content
            WcProp = 1 - ((WrFC - Wr) / (WrFC - WrWP))

            # Check if water content is above germination threshold
            if (WcProp >= Crop_GermThr):
                # Crop has germinated
                NewCond.Germination = True
                # If crop sown as seedling, turn on seedling protection
                if Crop_PlantMethod == True:
                    NewCond.ProtectedSeed = True
                else:
                    # Crop is transplanted so no protection
                    NewCond.ProtectedSeed = False

            # Increment delayed growth time counters if germination is yet to
            # occur, and also set seed protection to False if yet to germinate
            else:
                NewCond.DelayedCDs = InitCond.DelayedCDs + 1
                NewCond.DelayedGDDs = InitCond.DelayedGDDs + GDD
                NewCond.ProtectedSeed = False

    else:
        # Not in growing season so no germination calculation is performed.
        NewCond.Germination = False
        NewCond.ProtectedSeed = False
        NewCond.DelayedCDs = 0
        NewCond.DelayedGDDs = 0

    return NewCond


# Cell
# @njit()
def growth_stage(Crop, InitCond, GrowingSeason):
    """
    Function to determine current growth stage of crop

    (used only for irrigation soil moisture thresholds)

    *Arguments:*



    `Crop`: `CropClass` : Crop object containing Crop paramaters

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `GrowingSeason`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters





    """

    ## Store initial conditions in new structure for updating ##
    NewCond = InitCond

    ## Get growth stage (if in growing season) ##
    if GrowingSeason == True:
        # Adjust time for any delayed growth
        if Crop.CalendarType == 1:
            tAdj = NewCond.DAP - NewCond.DelayedCDs
        elif Crop.CalendarType == 2:
            tAdj = NewCond.GDDcum - NewCond.DelayedGDDs

        # Update growth stage
        if tAdj <= Crop.Canopy10Pct:
            NewCond.GrowthStage = 1
        elif tAdj <= Crop.MaxCanopy:
            NewCond.GrowthStage = 2
        elif tAdj <= Crop.Senescence:
            NewCond.GrowthStage = 3
        elif tAdj > Crop.Senescence:
            NewCond.GrowthStage = 4

    else:
        # Not in growing season so growth stage is set to dummy value
        NewCond.GrowthStage = 0

    return NewCond


# Cell
@njit
@cc.export("_water_stress", "(f8[:],f8[:],f8,f8,f8[:],f8,f8,f8,f8,f8)")
def water_stress(
    Crop_p_up,
    Crop_p_lo,
    Crop_ETadj,
    Crop_beta,
    Crop_fshape_w,
    InitCond_tEarlySen,
    Dr,
    TAW,
    Et0,
    beta,
):
    """
    Function to calculate water stress coefficients

    <a href="../pdfs/ac_ref_man_3.pdf#page=18" target="_blank">Reference Manual: water stress equations</a> (pg. 9-13)


    *Arguments:*


    `Crop`: `CropClass` : Crop Object

    `InitCond`: `InitCondClass` : InitCond object

    `Dr`: `DrClass` : Depletion object (contains rootzone and top soil depletion totals)

    `TAW`: `TAWClass` : TAW object (contains rootzone and top soil total available water)

    `Et0`: `float` : Reference Evapotranspiration

    `beta`: `float` : Adjust senescence threshold if early sensescence is triggered


    *Returns:*

    `Ksw`: `KswClass` : Ksw object containint water stress coefficients

    """

    ## Calculate relative root zone water depletion for each stress type ##
    # Number of stress variables
    nstress = len(Crop_p_up)

    # Store stress thresholds
    p_up = np.ones(nstress) * Crop_p_up
    p_lo = np.ones(nstress) * Crop_p_lo
    if Crop_ETadj == 1:
        # Adjust stress thresholds for Et0 on currentbeta day (don't do this for
        # pollination water stress coefficient)

        for ii in range(3):
            p_up[ii] = p_up[ii] + (0.04 * (5 - Et0)) * (np.log10(10 - 9 * p_up[ii]))
            p_lo[ii] = p_lo[ii] + (0.04 * (5 - Et0)) * (np.log10(10 - 9 * p_lo[ii]))

    # Adjust senescence threshold if early sensescence is triggered
    if (beta == True) and (InitCond_tEarlySen > 0):
        p_up[2] = p_up[2] * (1 - Crop_beta / 100)

    # Limit values
    p_up = np.maximum(p_up, np.zeros(4))
    p_lo = np.maximum(p_lo, np.zeros(4))
    p_up = np.minimum(p_up, np.ones(4))
    p_lo = np.minimum(p_lo, np.ones(4))

    # Calculate relative depletion
    Drel = np.zeros(nstress)
    for ii in range(nstress):
        if Dr <= (p_up[ii] * TAW):
            # No water stress
            Drel[ii] = 0
        elif (Dr > (p_up[ii] * TAW)) and (Dr < (p_lo[ii] * TAW)):
            # Partial water stress
            Drel[ii] = 1 - ((p_lo[ii] - (Dr / TAW)) / (p_lo[ii] - p_up[ii]))
        elif Dr >= (p_lo[ii] * TAW):
            # Full water stress
            Drel[ii] = 1

    ## Calculate root zone water stress coefficients ##
    Ks = np.ones(3)
    for ii in range(3):
        Ks[ii] = 1 - ((np.exp(Drel[ii] * Crop_fshape_w[ii]) - 1) / (np.exp(Crop_fshape_w[ii]) - 1))

    # Ksw = KswClass()

    # Water stress coefficient for leaf expansion
    Ksw_Exp = Ks[0]
    # Water stress coefficient for stomatal closure
    Ksw_Sto = Ks[1]
    # Water stress coefficient for senescence
    Ksw_Sen = Ks[2]
    # Water stress coefficient for pollination failure
    Ksw_Pol = 1 - Drel[3]
    # Mean water stress coefficient for stomatal closure
    Ksw_StoLin = 1 - Drel[1]

    return Ksw_Exp, Ksw_Sto, Ksw_Sen, Ksw_Pol, Ksw_StoLin


# Cell
# @njit()
@cc.export("_cc_development", "f8(f8,f8,f8,f8,f8,unicode_type,f8)")
def cc_development(CCo, CCx, CGC, CDC, dt, Mode, CCx0):
    """
    Function to calculate canopy cover development by end of the current simulation day

    <a href="../pdfs/ac_ref_man_3.pdf#page=30" target="_blank">Reference Manual: CC devlopment</a> (pg. 21-24)


    *Arguments:*



    `CCo`: `float` : Fractional canopy cover size at emergence

    `CCx`: `float` : Maximum canopy cover (fraction of soil cover)

    `CGC`: `float` : Canopy growth coefficient (fraction per GDD)

    `CDC`: `float` : Canopy decline coefficient (fraction per GDD/calendar day)

    `dt`: `float` : Time delta of canopy growth (1 calander day or ... GDD)

    `Mode`: `str` : Stage of Canopy developement (Growth or Decline)

    `CCx0`: `float` : Maximum canopy cover (fraction of soil cover)

    *Returns:*

    `CC`: `float` : Canopy Cover




    """

    ## Initialise output ##

    ## Calculate new canopy cover ##
    if Mode == "Growth":
        # Calculate canopy growth
        # Exponential growth stage
        CC = CCo * np.exp(CGC * dt)
        if CC > (CCx / 2):
            # Exponential decay stage
            CC = CCx - 0.25 * (CCx / CCo) * CCx * np.exp(-CGC * dt)

        # Limit CC to CCx
        if CC > CCx:
            CC = CCx

    elif Mode == "Decline":
        # Calculate canopy decline
        if CCx < 0.001:
            CC = 0
        else:
            CC = CCx * (
                1
                - 0.05
                * (np.exp(dt * CDC * 3.33 * ((CCx + 2.29) / (CCx0 + 2.29)) / (CCx + 2.29)) - 1)
            )

    ## Limit canopy cover to between 0 and 1 ##
    if CC > 1:
        CC = 1
    elif CC < 0:
        CC = 0

    return CC


# Cell
# @njit()
@cc.export("_cc_required_time", "f8(f8,f8,f8,f8,f8,unicode_type)")
def cc_required_time(CCprev, CCo, CCx, CGC, CDC, Mode):
    """
    Function to find time required to reach CC at end of previous day, given current CGC or CDC

    <a href="../pdfs/ac_ref_man_3.pdf#page=30" target="_blank">Reference Manual: CC devlopment</a> (pg. 21-24)



    *Arguments:*


    `CCprev`: `float` : Canopy Cover at previous timestep.

    `CCo`: `float` : Fractional canopy cover size at emergence

    `CCx`: `float` : Maximum canopy cover (fraction of soil cover)

    `CGC`: `float` : Canopy growth coefficient (fraction per GDD)

    `CDC`: `float` : Canopy decline coefficient (fraction per GDD/calendar day)

    `Mode`: `str` : Canopy growth/decline coefficient (fraction per GDD/calendar day)


    *Returns:*

    `tReq`: `float` : time required to reach CC at end of previous day





    """

    ## Get CGC and/or time (GDD or CD) required to reach CC on previous day ##
    if Mode == "CGC":
        if CCprev <= (CCx / 2):

            # print(CCprev,CCo,(tSum-dt),tSum,dt)
            CGCx = np.log(CCprev / CCo)
            # print(np.log(CCprev/CCo),(tSum-dt),CGCx)
        else:
            # print(CCx,CCo,CCprev)
            CGCx = np.log((0.25 * CCx * CCx / CCo) / (CCx - CCprev))

        tReq = CGCx / CGC

    elif Mode == "CDC":
        tReq = (np.log(1 + (1 - CCprev / CCx) / 0.05)) / (CDC / CCx)

    return tReq

# Cell
# @njit()
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
    tCCtmp = _cc_required_time(CCprev, CCo, CCx, CGC, CDC, "CGC")

    ## Determine CCx adjusted ##
    if tCCtmp > 0:
        tCCtmp = tCCtmp + (Crop_CanopyDevEnd - tSum) + dt
        CCxAdj = _cc_development(CCo, CCx, CGC, CDC, tCCtmp, "Growth", Crop_CCx)
    else:
        CCxAdj = 0

    return CCxAdj


# Cell
# @njit()
@cc.export("_update_CCx_CDC", "(f8,f8,f8,f8)")
def update_CCx_CDC(CCprev, CDC, CCx, dt):
    """
    Function to update CCx and CDC parameter valyes for rewatering in late season of an early declining canopy

    <a href="../pdfs/ac_ref_man_3.pdf#page=36" target="_blank">Reference Manual: CC stress response</a> (pg. 27-33)


    *Arguments:*


    `CCprev`: `float` : Canopy Cover at previous timestep.

    `CDC`: `float` : Canopy decline coefficient (fraction per GDD/calendar day)

    `CCx`: `float` : Maximum canopy cover (fraction of soil cover)

    `dt`: `float` : Time delta of canopy growth (1 calander day or ... GDD)


    *Returns:*

    `CCxAdj`: `float` : updated CCxAdj

    `CDCadj`: `float` : updated CDCadj





    """

    ## Get adjusted CCx ##
    CCXadj = CCprev / (1 - 0.05 * (np.exp(dt * ((CDC * 3.33) / (CCx + 2.29))) - 1))

    ## Get adjusted CDC ##
    CDCadj = CDC * ((CCXadj + 2.29) / (CCx + 2.29))

    return CCXadj, CDCadj


# Cell
# @njit()
def canopy_cover(Crop, prof, Soil_zTop, InitCond, GDD, Et0, GrowingSeason):
    # def canopy_cover(Crop,Soil_Profile,Soil_zTop,InitCond,GDD,Et0,GrowingSeason):

    """
    Function to simulate canopy growth/decline

    <a href="../pdfs/ac_ref_man_3.pdf#page=30" target="_blank">Reference Manual: CC equations</a> (pg. 21-33)


    *Arguments:*


    `Crop`: `CropClass` : Crop object

    `prof`: `SoilProfileClass` : Soil object

    `Soil_zTop`: `float` : top soil depth

    `InitCond`: `InitCondClass` : InitCond object

    `GDD`: `float` : Growing Degree Days

    `Et0`: `float` : reference evapotranspiration

    `GrowingSeason`:: `bool` : is it currently within the growing season (True, Flase)

    *Returns:*


    `NewCond`: `InitCondClass` : updated InitCond object


    """

    # Function to simulate canopy growth/decline

    InitCond_CC_NS = InitCond.CC_NS
    InitCond_CC = InitCond.CC
    InitCond_ProtectedSeed = InitCond.ProtectedSeed
    InitCond_CCxAct = InitCond.CCxAct
    InitCond_CropDead = InitCond.CropDead
    InitCond_tEarlySen = InitCond.tEarlySen
    InitCond_CCxW = InitCond.CCxW

    ## Store initial conditions in a new structure for updating ##
    NewCond = InitCond
    NewCond.CCprev = InitCond.CC

    ## Calculate canopy development (if in growing season) ##
    if GrowingSeason == True:
        # Calculate root zone water content
        TAW = TAWClass()
        Dr = DrClass()
        # thRZ = thRZClass()
        _, Dr.Zt, Dr.Rz, TAW.Zt, TAW.Rz, _,_,_,_,_,_ = _root_zone_water(
            prof,
            float(NewCond.Zroot),
            NewCond.th,
            Soil_zTop,
            float(Crop.Zmin),
            Crop.Aer,
        )

        # _,Dr,TAW,_ = root_zone_water(Soil_Profile,float(NewCond.Zroot),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
        # Check whether to use root zone or top soil depletions for calculating
        # water stress
        if (Dr.Rz / TAW.Rz) <= (Dr.Zt / TAW.Zt):
            # Root zone is wetter than top soil, so use root zone value
            Dr = Dr.Rz
            TAW = TAW.Rz
        else:
            # Top soil is wetter than root zone, so use top soil values
            Dr = Dr.Zt
            TAW = TAW.Zt

        # Determine if water stress is occurring
        beta = True
        Ksw = KswClass()
        Ksw.Exp, Ksw.Sto, Ksw.Sen, Ksw.Pol, Ksw.StoLin = _water_stress(
            Crop.p_up,
            Crop.p_lo,
            Crop.ETadj,
            Crop.beta,
            Crop.fshape_w,
            NewCond.tEarlySen,
            Dr,
            TAW,
            Et0,
            beta,
        )

        # water_stress(Crop, NewCond, Dr, TAW, Et0, beta)

        # Get canopy cover growth time
        if Crop.CalendarType == 1:
            dtCC = 1
            tCCadj = NewCond.DAP - NewCond.DelayedCDs
        elif Crop.CalendarType == 2:
            dtCC = GDD
            tCCadj = NewCond.GDDcum - NewCond.DelayedGDDs

        ## Canopy development (potential) ##
        if (tCCadj < Crop.Emergence) or (round(tCCadj) > Crop.Maturity):
            # No canopy development before emergence/germination or after
            # maturity
            NewCond.CC_NS = 0
        elif tCCadj < Crop.CanopyDevEnd:
            # Canopy growth can occur
            if InitCond_CC_NS <= Crop.CC0:
                # Very small initial CC.
                NewCond.CC_NS = Crop.CC0 * np.exp(Crop.CGC * dtCC)
                # print(Crop.CC0,np.exp(Crop.CGC*dtCC))
            else:
                # Canopy growing
                tmp_tCC = tCCadj - Crop.Emergence
                NewCond.CC_NS = _cc_development(
                    Crop.CC0, 0.98 * Crop.CCx, Crop.CGC, Crop.CDC, tmp_tCC, "Growth", Crop.CCx
                )

            # Update maximum canopy cover size in growing season
            NewCond.CCxAct_NS = NewCond.CC_NS
        elif tCCadj > Crop.CanopyDevEnd:
            # No more canopy growth is possible or canopy in decline
            # Set CCx for calculation of withered canopy effects
            NewCond.CCxW_NS = NewCond.CCxAct_NS
            if tCCadj < Crop.Senescence:
                # Mid-season stage - no canopy growth
                NewCond.CC_NS = InitCond_CC_NS
                # Update maximum canopy cover size in growing season
                NewCond.CCxAct_NS = NewCond.CC_NS
            else:
                # Late-season stage - canopy decline
                tmp_tCC = tCCadj - Crop.Senescence
                NewCond.CC_NS = _cc_development(
                    Crop.CC0,
                    NewCond.CCxAct_NS,
                    Crop.CGC,
                    Crop.CDC,
                    tmp_tCC,
                    "Decline",
                    NewCond.CCxAct_NS,
                )

        ## Canopy development (actual) ##
        if (tCCadj < Crop.Emergence) or (round(tCCadj) > Crop.Maturity):
            # No canopy development before emergence/germination or after
            # maturity
            NewCond.CC = 0
            NewCond.CC0adj = Crop.CC0
        elif tCCadj < Crop.CanopyDevEnd:
            # Canopy growth can occur
            if InitCond_CC <= NewCond.CC0adj or (
                (InitCond_ProtectedSeed == True) and (InitCond_CC <= (1.25 * NewCond.CC0adj))
            ):
                # Very small initial CC or seedling in protected phase of
                # growth. In this case, assume no leaf water expansion stress
                if InitCond_ProtectedSeed == True:
                    tmp_tCC = tCCadj - Crop.Emergence
                    NewCond.CC = _cc_development(
                        Crop.CC0, Crop.CCx, Crop.CGC, Crop.CDC, tmp_tCC, "Growth", Crop.CCx
                    )
                    # Check if seed protection should be turned off
                    if NewCond.CC > (1.25 * NewCond.CC0adj):
                        # Turn off seed protection - lead expansion stress can
                        # occur on future time steps.
                        NewCond.ProtectedSeed = False

                else:
                    NewCond.CC = NewCond.CC0adj * np.exp(Crop.CGC * dtCC)

            else:
                # Canopy growing

                if InitCond_CC < (0.9799 * Crop.CCx):
                    # Adjust canopy growth coefficient for leaf expansion water
                    # stress effects
                    CGCadj = Crop.CGC * Ksw.Exp
                    if CGCadj > 0:

                        # Adjust CCx for change in CGC
                        CCXadj = adjust_CCx(
                            InitCond_CC,
                            NewCond.CC0adj,
                            Crop.CCx,
                            CGCadj,
                            Crop.CDC,
                            dtCC,
                            tCCadj,
                            Crop.CanopyDevEnd,
                            Crop.CCx,
                        )
                        if CCXadj < 0:

                            NewCond.CC = InitCond_CC
                        elif abs(InitCond_CC - (0.9799 * Crop.CCx)) < 0.001:

                            # Approaching maximum canopy cover size
                            tmp_tCC = tCCadj - Crop.Emergence
                            NewCond.CC = _cc_development(
                                Crop.CC0, Crop.CCx, Crop.CGC, Crop.CDC, tmp_tCC, "Growth", Crop.CCx
                            )
                        else:

                            # Determine time required to reach CC on previous,
                            # day, given CGCAdj value
                            tReq = _cc_required_time(
                                InitCond_CC, NewCond.CC0adj, CCXadj, CGCadj, Crop.CDC, "CGC"
                            )
                            if tReq > 0:

                                # Calclate GDD's for canopy growth
                                tmp_tCC = tReq + dtCC
                                # Determine new canopy size
                                NewCond.CC = _cc_development(
                                    NewCond.CC0adj,
                                    CCXadj,
                                    CGCadj,
                                    Crop.CDC,
                                    tmp_tCC,
                                    "Growth",
                                    Crop.CCx,
                                )
                                # print(NewCond.DAP,CCXadj,tReq)

                            else:
                                # No canopy growth
                                NewCond.CC = InitCond_CC

                    else:

                        # No canopy growth
                        NewCond.CC = InitCond_CC
                        # Update CC0
                        if NewCond.CC > NewCond.CC0adj:
                            NewCond.CC0adj = Crop.CC0
                        else:
                            NewCond.CC0adj = NewCond.CC

                else:
                    # Canopy approaching maximum size
                    tmp_tCC = tCCadj - Crop.Emergence
                    NewCond.CC = _cc_development(
                        Crop.CC0, Crop.CCx, Crop.CGC, Crop.CDC, tmp_tCC, "Growth", Crop.CCx
                    )
                    NewCond.CC0adj = Crop.CC0

            if NewCond.CC > InitCond_CCxAct:
                # Update actual maximum canopy cover size during growing season
                NewCond.CCxAct = NewCond.CC

        elif tCCadj > Crop.CanopyDevEnd:

            # No more canopy growth is possible or canopy is in decline
            if tCCadj < Crop.Senescence:
                # Mid-season stage - no canopy growth
                NewCond.CC = InitCond_CC
                if NewCond.CC > InitCond_CCxAct:
                    # Update actual maximum canopy cover size during growing
                    # season
                    NewCond.CCxAct = NewCond.CC

            else:
                # Late-season stage - canopy decline
                # Adjust canopy decline coefficient for difference between actual
                # and potential CCx
                CDCadj = Crop.CDC * ((NewCond.CCxAct + 2.29) / (Crop.CCx + 2.29))
                # Determine new canopy size
                tmp_tCC = tCCadj - Crop.Senescence
                NewCond.CC = _cc_development(
                    NewCond.CC0adj,
                    NewCond.CCxAct,
                    Crop.CGC,
                    CDCadj,
                    tmp_tCC,
                    "Decline",
                    NewCond.CCxAct,
                )

            # Check for crop growth termination
            if (NewCond.CC < 0.001) and (InitCond_CropDead == False):
                # Crop has died
                NewCond.CC = 0
                NewCond.CropDead = True

        ## Canopy senescence due to water stress (actual) ##
        if tCCadj >= Crop.Emergence:
            if (tCCadj < Crop.Senescence) or (InitCond_tEarlySen > 0):
                # Check for early canopy senescence  due to severe water
                # stress.
                if (Ksw.Sen < 1) and (InitCond_ProtectedSeed == False):

                    # Early canopy senescence
                    NewCond.PrematSenes = True
                    if InitCond_tEarlySen == 0:
                        # No prior early senescence
                        NewCond.CCxEarlySen = InitCond_CC

                    # Increment early senescence GDD counter
                    NewCond.tEarlySen = InitCond_tEarlySen + dtCC
                    # Adjust canopy decline coefficient for water stress
                    beta = False

                    Ksw = KswClass()
                    Ksw.Exp, Ksw.Sto, Ksw.Sen, Ksw.Pol, Ksw.StoLin = _water_stress(
                        Crop.p_up,
                        Crop.p_lo,
                        Crop.ETadj,
                        Crop.beta,
                        Crop.fshape_w,
                        NewCond.tEarlySen,
                        Dr,
                        TAW,
                        Et0,
                        beta,
                    )

                    # Ksw = water_stress(Crop, NewCond, Dr, TAW, Et0, beta)
                    if Ksw.Sen > 0.99999:
                        CDCadj = 0.0001
                    else:
                        CDCadj = (1 - (Ksw.Sen ** 8)) * Crop.CDC

                    # Get new canpy cover size after senescence
                    if NewCond.CCxEarlySen < 0.001:
                        CCsen = 0
                    else:
                        # Get time required to reach CC at end of previous day, given
                        # CDCadj
                        tReq = (np.log(1 + (1 - InitCond_CC / NewCond.CCxEarlySen) / 0.05)) / (
                            (CDCadj * 3.33) / (NewCond.CCxEarlySen + 2.29)
                        )
                        # Calculate GDD's for canopy decline
                        tmp_tCC = tReq + dtCC
                        # Determine new canopy size
                        CCsen = NewCond.CCxEarlySen * (
                            1
                            - 0.05
                            * (
                                np.exp(tmp_tCC * ((CDCadj * 3.33) / (NewCond.CCxEarlySen + 2.29)))
                                - 1
                            )
                        )
                        if CCsen < 0:
                            CCsen = 0

                    # Update canopy cover size
                    if tCCadj < Crop.Senescence:
                        # Limit CC to CCx
                        if CCsen > Crop.CCx:
                            CCsen = Crop.CCx

                        # CC cannot be greater than value on previous day
                        NewCond.CC = CCsen
                        if NewCond.CC > InitCond_CC:
                            NewCond.CC = InitCond_CC

                        # Update maximum canopy cover size during growing
                        # season
                        NewCond.CCxAct = NewCond.CC
                        # Update CC0 if current CC is less than initial canopy
                        # cover size at planting
                        if NewCond.CC < Crop.CC0:
                            NewCond.CC0adj = NewCond.CC
                        else:
                            NewCond.CC0adj = Crop.CC0

                    else:
                        # Update CC to account for canopy cover senescence due
                        # to water stress
                        if CCsen < NewCond.CC:
                            NewCond.CC = CCsen

                    # Check for crop growth termination
                    if (NewCond.CC < 0.001) and (InitCond_CropDead == False):
                        # Crop has died
                        NewCond.CC = 0
                        NewCond.CropDead = True

                else:
                    # No water stress
                    NewCond.PrematSenes = False
                    if (tCCadj > Crop.Senescence) and (InitCond_tEarlySen > 0):
                        # Rewatering of canopy in late season
                        # Get new values for CCx and CDC
                        tmp_tCC = tCCadj - dtCC - Crop.Senescence
                        CCXadj, CDCadj = _update_CCx_CDC(InitCond_CC, Crop.CDC, Crop.CCx, tmp_tCC)
                        NewCond.CCxAct = CCXadj
                        # Get new CC value for end of current day
                        tmp_tCC = tCCadj - Crop.Senescence
                        NewCond.CC = _cc_development(
                            NewCond.CC0adj, CCXadj, Crop.CGC, CDCadj, tmp_tCC, "Decline", CCXadj
                        )
                        # Check for crop growth termination
                        if (NewCond.CC < 0.001) and (InitCond_CropDead == False):
                            NewCond.CC = 0
                            NewCond.CropDead = True

                    # Reset early senescence counter
                    NewCond.tEarlySen = 0

                # Adjust CCx for effects of withered canopy
                if NewCond.CC > InitCond_CCxW:
                    NewCond.CCxW = NewCond.CC

        ## Calculate canopy size adjusted for micro-advective effects ##
        # Check to ensure potential CC is not slightly lower than actual
        if NewCond.CC_NS < NewCond.CC:
            NewCond.CC_NS = NewCond.CC
            if tCCadj < Crop.CanopyDevEnd:
                NewCond.CCxAct_NS = NewCond.CC_NS

        # Actual (with water stress)
        NewCond.CCadj = (1.72 * NewCond.CC) - (NewCond.CC ** 2) + (0.3 * (NewCond.CC ** 3))
        # Potential (without water stress)
        NewCond.CCadj_NS = (
            (1.72 * NewCond.CC_NS) - (NewCond.CC_NS ** 2) + (0.3 * (NewCond.CC_NS ** 3))
        )

    else:
        # No canopy outside growing season - set various values to zero
        NewCond.CC = 0
        NewCond.CCadj = 0
        NewCond.CC_NS = 0
        NewCond.CCadj_NS = 0
        NewCond.CCxW = 0
        NewCond.CCxAct = 0
        NewCond.CCxW_NS = 0
        NewCond.CCxAct_NS = 0

    return NewCond


# Cell
@njit
@cc.export("_evap_layer_water_content", (f8[:],f8,SoilProfileNT_typ_sig))
def _evap_layer_water_content(
    InitCond_th,
    InitCond_EvapZ,
    prof,
):
    """
    Function to get water contents in the evaporation layer

    <a href="../pdfs/ac_ref_man_3.pdf#page=82" target="_blank">Reference Manual: evaporation equations</a> (pg. 73-81)


    *Arguments:*



    `InitCond_th`: `np.array` : Initial water content

    `InitCond_EvapZ`: `float` : evaporation depth

    `prof`: `SoilProfileClass` : Soil object containing soil paramaters


    *Returns:*


    `Wevap_Sat`: `float` : Water storage in evaporation layer at saturation (mm)

    `Wevap_Fc`: `float` : Water storage in evaporation layer at field capacity (mm)

    `Wevap_Wp`: `float` : Water storage in evaporation layer at permanent wilting point (mm)

    `Wevap_Dry`: `float` : Water storage in evaporation layer at air dry (mm)

    `Wevap_Act`: `float` : Actual water storage in evaporation layer (mm)



    """

    # Find soil compartments covered by evaporation layer
    comp_sto = np.sum(prof.dzsum < InitCond_EvapZ) + 1

    Wevap_Sat = 0
    Wevap_Fc = 0
    Wevap_Wp = 0
    Wevap_Dry = 0
    Wevap_Act = 0

    for ii in range(int(comp_sto)):

        # Determine fraction of soil compartment covered by evaporation layer
        if prof.dzsum[ii] > InitCond_EvapZ:
            factor = 1 - ((prof.dzsum[ii] - InitCond_EvapZ) / prof.dz[ii])
        else:
            factor = 1

        # Actual water storage in evaporation layer (mm)
        Wevap_Act += factor * 1000 * InitCond_th[ii] * prof.dz[ii]
        # Water storage in evaporation layer at saturation (mm)
        Wevap_Sat += factor * 1000 * prof.th_s[ii] * prof.dz[ii]
        # Water storage in evaporation layer at field capacity (mm)
        Wevap_Fc += factor * 1000 * prof.th_fc[ii] * prof.dz[ii]
        # Water storage in evaporation layer at permanent wilting point (mm)
        Wevap_Wp += factor * 1000 * prof.th_wp[ii] * prof.dz[ii]
        # Water storage in evaporation layer at air dry (mm)
        Wevap_Dry += factor * 1000 * prof.th_dry[ii] * prof.dz[ii]

    if Wevap_Act < 0:
        Wevap_Act = 0

    return Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act


# Cell
# @njit()
@cc.export(
    "_soil_evaporation", (i8,i8,i8,SoilProfileNT_typ_sig,
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
    Et0,
    Infl,
    Rain,
    Irr,
    GrowingSeason,
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

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `Et0`: `float` : daily reference evapotranspiration

    `Infl`: `float` : Infiltration on current day

    `Rain`: `float` : daily precipitation mm

    `Irr`: `float` : Irrigation applied on current day

    `GrowingSeason`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters

    `EsAct`: `float` : Actual surface evaporation current day

    `EsPot`: `float` : Potential surface evaporation current day





    """

    # Wevap = WevapClass()

    ## Store initial conditions in new structure that will be updated ##
    # NewCond = InitCond

    ## Prepare stage 2 evaporation (REW gone) ##
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
        Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act = _evap_layer_water_content(
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
            # Water stored in surface evaporation layer cannot exceed REW
            if NewCond_Wsurf > Soil_REW:
                NewCond_Wsurf = Soil_REW

            # Reset variables
            NewCond_Wstage2 = 0
            NewCond_EvapZ = Soil_EvapZmin
            NewCond_Stage2 = False

    ## Calculate potential soil evaporation rate (mm/day) ##
    if GrowingSeason == True:
        # Adjust time for any delayed development
        if Crop_CalendarType == 1:
            tAdj = NewCond_DAP - NewCond_DelayedCDs
        elif Crop_CalendarType == 2:
            tAdj = NewCond_GDDcum - NewCond_DelayedGDDs

        # Calculate maximum potential soil evaporation
        EsPotMax = Soil_Kex * Et0 * (1 - NewCond_CCxW * (Soil_fwcc / 100))
        # Calculate potential soil evaporation (given current canopy cover
        # size)
        EsPot = Soil_Kex * (1 - NewCond_CCadj) * Et0

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
            EsPotMin = Soil_Kex * (1 - CCxActAdj) * Et0
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
        EsPot = Soil_Kex * Et0

    ## Adjust potential soil evaporation for mulches and/or partial wetting ##
    # Mulches
    if NewCond_SurfaceStorage < 0.000001:
        if not FieldMngt_Mulches:
            # No mulches present
            EsPotMul = EsPot
        elif FieldMngt_Mulches:
            # Mulches present
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

    ## Stage 1 evaporation ##
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
            Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act = _evap_layer_water_content(
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

    ## Stage 2 evaporation ##
    # Extract water
    if ToExtract > 0:
        # Start stage 2
        NewCond_Stage2 = True
        # Get sub-daily evaporative demand
        Edt = ToExtract / ClockStruct_EvapTimeSteps
        # Loop sub-daily steps
        for jj in range(int(ClockStruct_EvapTimeSteps)):
            # Get current water storage (mm)
            Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act = _evap_layer_water_content(
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
                    Wevap_Sat, Wevap_Fc, Wevap_Wp, Wevap_Dry, Wevap_Act = _evap_layer_water_content(
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


# Cell
# @njit()
@cc.export("_aeration_stress", (f8,f8,thRZNT_type_sig))
def aeration_stress(NewCond_AerDays, Crop_LagAer, thRZ):
    """
    Function to calculate aeration stress coefficient

    <a href="../pdfs/ac_ref_man_3.pdf#page=90" target="_blank">Reference Manual: aeration stress</a> (pg. 89-90)


    *Arguments:*


    `NewCond_AerDays`: `int` : number aeration stress days

    `Crop_LagAer`: `int` : lag days before aeration stress

    `thRZ`: `thRZClass` : object that contains information on the total water in the root zone



    *Returns:*

    `Ksa_Aer`: `float` : aeration stress coefficient

    `NewCond_AerDays`: `float` : updated aer days



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


# Cell
# @njit()
def transpiration(
    Soil_Profile,
    Soil_nComp,
    Soil_zTop,
    Crop,
    IrrMngt_IrrMethod,
    IrrMngt_NetIrrSMT,
    InitCond,
    Et0,
    CO2,
    GrowingSeason,
    GDD,
):

    """
    Function to calculate crop transpiration on current day

    <a href="../pdfs/ac_ref_man_3.pdf#page=91" target="_blank">Reference Manual: transpiration equations</a> (pg. 82-91)



    *Arguments:*


    `Soil`: `SoilClass` : Soil object

    `Crop`: `CropClass` : Crop object

    `IrrMngt`: `IrrMngt`: object containing irrigation management params

    `InitCond`: `InitCondClass` : InitCond object

    `Et0`: `float` : reference evapotranspiration

    `CO2`: `CO2class` : CO2

    `GDD`: `float` : Growing Degree Days

    `GrowingSeason`:: `bool` : is it currently within the growing season (True, Flase)

    *Returns:*


    `TrAct`: `float` : Actual Transpiration on current day

    `TrPot_NS`: `float` : Potential Transpiration on current day with no water stress

    `TrPot0`: `float` : Potential Transpiration on current day

    `NewCond`: `InitCondClass` : updated InitCond object

    `IrrNet`: `float` : Net Irrigation (if required)







    """

    ## Store initial conditions ##
    NewCond = InitCond

    InitCond_th = InitCond.th

    prof = Soil_Profile

    ## Calculate transpiration (if in growing season) ##
    if GrowingSeason == True:
        ## Calculate potential transpiration ##
        # 1. No prior water stress
        # Update ageing days counter
        DAPadj = NewCond.DAP - NewCond.DelayedCDs
        if DAPadj > Crop.MaxCanopyCD:
            NewCond.AgeDays_NS = DAPadj - Crop.MaxCanopyCD

        # Update crop coefficient for ageing of canopy
        if NewCond.AgeDays_NS > 5:
            Kcb_NS = Crop.Kcb - ((NewCond.AgeDays_NS - 5) * (Crop.fage / 100)) * NewCond.CCxW_NS
        else:
            Kcb_NS = Crop.Kcb

        # Update crop coefficient for CO2 concentration
        CO2CurrentConc = CO2.CurrentConc
        CO2RefConc = CO2.RefConc
        if CO2CurrentConc > CO2RefConc:
            Kcb_NS = Kcb_NS * (1 - 0.05 * ((CO2CurrentConc - CO2RefConc) / (550 - CO2RefConc)))

        # Determine potential transpiration rate (no water stress)
        TrPot_NS = Kcb_NS * (NewCond.CCadj_NS) * Et0

        # Correct potential transpiration for dying green canopy effects
        if NewCond.CC_NS < NewCond.CCxW_NS:
            if (NewCond.CCxW_NS > 0.001) and (NewCond.CC_NS > 0.001):
                TrPot_NS = TrPot_NS * ((NewCond.CC_NS / NewCond.CCxW_NS) ** Crop.a_Tr)

        # 2. Potential prior water stress and/or delayed development
        # Update ageing days counter
        DAPadj = NewCond.DAP - NewCond.DelayedCDs
        if DAPadj > Crop.MaxCanopyCD:
            NewCond.AgeDays = DAPadj - Crop.MaxCanopyCD

        # Update crop coefficient for ageing of canopy
        if NewCond.AgeDays > 5:
            Kcb = Crop.Kcb - ((NewCond.AgeDays - 5) * (Crop.fage / 100)) * NewCond.CCxW
        else:
            Kcb = Crop.Kcb

        # Update crop coefficient for CO2 concentration
        if CO2CurrentConc > CO2RefConc:
            Kcb = Kcb * (1 - 0.05 * ((CO2CurrentConc - CO2RefConc) / (550 - CO2RefConc)))

        # Determine potential transpiration rate
        TrPot0 = Kcb * (NewCond.CCadj) * Et0
        # Correct potential transpiration for dying green canopy effects
        if NewCond.CC < NewCond.CCxW:
            if (NewCond.CCxW > 0.001) and (NewCond.CC > 0.001):
                TrPot0 = TrPot0 * ((NewCond.CC / NewCond.CCxW) ** Crop.a_Tr)

        # 3. Adjust potential transpiration for cold stress effects
        # Check if cold stress occurs on current day
        if Crop.TrColdStress == 0:
            # Cold temperature stress does not affect transpiration
            KsCold = 1
        elif Crop.TrColdStress == 1:
            # Transpiration can be affected by cold temperature stress
            if GDD >= Crop.GDD_up:
                # No cold temperature stress
                KsCold = 1
            elif GDD <= Crop.GDD_lo:
                # Transpiration fully inhibited by cold temperature stress
                KsCold = 0
            else:
                # Transpiration partially inhibited by cold temperature stress
                # Get parameters for logistic curve
                KsTr_up = 1
                KsTr_lo = 0.02
                fshapeb = (-1) * (
                    np.log(((KsTr_lo * KsTr_up) - 0.98 * KsTr_lo) / (0.98 * (KsTr_up - KsTr_lo)))
                )
                # Calculate cold stress level
                GDDrel = (GDD - Crop.GDD_lo) / (Crop.GDD_up - Crop.GDD_lo)
                KsCold = (KsTr_up * KsTr_lo) / (
                    KsTr_lo + (KsTr_up - KsTr_lo) * np.exp(-fshapeb * GDDrel)
                )
                KsCold = KsCold - KsTr_lo * (1 - GDDrel)

        # Correct potential transpiration rate (mm/day)
        TrPot0 = TrPot0 * KsCold
        TrPot_NS = TrPot_NS * KsCold

        # print(TrPot0,NewCond.DAP)

        ## Calculate surface layer transpiration ##
        if (NewCond.SurfaceStorage > 0) and (NewCond.DaySubmerged < Crop.LagAer):

            # Update submergence days counter
            NewCond.DaySubmerged = NewCond.DaySubmerged + 1
            # Update anerobic conditions counter for each compartment
            for ii in range(int(Soil_nComp)):
                # Increment aeration days counter for compartment ii
                NewCond.AerDaysComp[ii] = NewCond.AerDaysComp[ii] + 1
                if NewCond.AerDaysComp[ii] > Crop.LagAer:
                    NewCond.AerDaysComp[ii] = Crop.LagAer

            # Reduce actual transpiration that is possible to account for
            # aeration stress due to extended submergence
            fSub = 1 - (NewCond.DaySubmerged / Crop.LagAer)
            if NewCond.SurfaceStorage > (fSub * TrPot0):
                # Transpiration occurs from surface storage
                NewCond.SurfaceStorage = NewCond.SurfaceStorage - (fSub * TrPot0)
                TrAct0 = fSub * TrPot0
            else:
                # No transpiration from surface storage
                TrAct0 = 0

            if TrAct0 < (fSub * TrPot0):
                # More water can be extracted from soil profile for transpiration
                TrPot = (fSub * TrPot0) - TrAct0
                # print('now')

            else:
                # No more transpiration possible on current day
                TrPot = 0
                # print('here')

        else:

            # No surface transpiration occurs
            TrPot = TrPot0
            TrAct0 = 0

        # print(TrPot,NewCond.DAP)

        ## Update potential root zone transpiration for water stress ##
        # Determine root zone and top soil depletion, and root zone water
        # content

        TAW = TAWClass()
        Dr = DrClass()
        thRZ = thRZClass()
        (
            _,
            Dr.Zt,
            Dr.Rz,
            TAW.Zt,
            TAW.Rz,
            thRZ.Act,
            thRZ.S,
            thRZ.FC,
            thRZ.WP,
            thRZ.Dry,
            thRZ.Aer,
        ) = _root_zone_water(
            prof,
            float(NewCond.Zroot),
            NewCond.th,
            Soil_zTop,
            float(Crop.Zmin),
            Crop.Aer,
        )

        class_args = {key:value for key, value in thRZ.__dict__.items() if not key.startswith('__') and not callable(key)}
        thRZ = thRZNT(**class_args)

        # _,Dr,TAW,thRZ = root_zone_water(Soil_Profile,float(NewCond.Zroot),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
        # Check whether to use root zone or top soil depletions for calculating
        # water stress
        if (Dr.Rz / TAW.Rz) <= (Dr.Zt / TAW.Zt):
            # Root zone is wetter than top soil, so use root zone value
            Dr = Dr.Rz
            TAW = TAW.Rz
        else:
            # Top soil is wetter than root zone, so use top soil values
            Dr = Dr.Zt
            TAW = TAW.Zt

        # Calculate water stress coefficients
        beta = True
        Ksw = KswClass()
        Ksw.Exp, Ksw.Sto, Ksw.Sen, Ksw.Pol, Ksw.StoLin = _water_stress(
            Crop.p_up,
            Crop.p_lo,
            Crop.ETadj,
            Crop.beta,
            Crop.fshape_w,
            NewCond.tEarlySen,
            Dr,
            TAW,
            Et0,
            beta,
        )
        # Ksw = water_stress(Crop, NewCond, Dr, TAW, Et0, beta)

        # Calculate aeration stress coefficients
        Ksa_Aer, NewCond.AerDays = _aeration_stress(NewCond.AerDays, Crop.LagAer, thRZ)
        # Maximum stress effect
        Ks = min(Ksw.StoLin, Ksa_Aer)
        # Update potential transpiration in root zone
        if IrrMngt_IrrMethod != 4:
            # No adjustment to TrPot for water stress when in net irrigation mode
            TrPot = TrPot * Ks

        ## Determine compartments covered by root zone ##
        # Compartments covered by the root zone
        rootdepth = round(max(float(NewCond.Zroot), float(Crop.Zmin)), 2)
        comp_sto = min(np.sum(Soil_Profile.dzsum < rootdepth) + 1, int(Soil_nComp))
        RootFact = np.zeros(int(Soil_nComp))
        # Determine fraction of each compartment covered by root zone
        for ii in range(comp_sto):
            if Soil_Profile.dzsum[ii] > rootdepth:
                RootFact[ii] = 1 - ((Soil_Profile.dzsum[ii] - rootdepth) / Soil_Profile.dz[ii])
            else:
                RootFact[ii] = 1

        ## Determine maximum sink term for each compartment ##
        SxComp = np.zeros(int(Soil_nComp))
        if IrrMngt_IrrMethod == 4:
            # Net irrigation mode
            for ii in range(comp_sto):
                SxComp[ii] = (Crop.SxTop + Crop.SxBot) / 2

        else:
            # Maximum sink term declines linearly with depth
            SxCompBot = Crop.SxTop
            for ii in range(comp_sto):
                SxCompTop = SxCompBot
                if Soil_Profile.dzsum[ii] <= rootdepth:
                    SxCompBot = Crop.SxBot * NewCond.rCor + (
                        (Crop.SxTop - Crop.SxBot * NewCond.rCor)
                        * ((rootdepth - Soil_Profile.dzsum[ii]) / rootdepth)
                    )
                else:
                    SxCompBot = Crop.SxBot * NewCond.rCor

                SxComp[ii] = (SxCompTop + SxCompBot) / 2

        # print(TrPot,NewCond.DAP)
        ## Extract water ##
        ToExtract = TrPot
        comp = -1
        TrAct = 0
        while (ToExtract > 0) and (comp < comp_sto - 1):
            # Increment compartment
            comp = comp + 1
            # Specify layer number

            # Determine TAW (m3/m3) for compartment
            thTAW = prof.th_fc[comp] - prof.th_wp[comp]
            if Crop.ETadj == 1:
                # Adjust stomatal stress threshold for Et0 on current day
                p_up_sto = Crop.p_up[1] + (0.04 * (5 - Et0)) * (np.log10(10 - 9 * Crop.p_up[1]))

            # Determine critical water content at which stomatal closure will
            # occur in compartment
            thCrit = prof.th_fc[comp] - (thTAW * p_up_sto)

            # Check for soil water stress
            if NewCond.th[comp] >= thCrit:
                # No water stress effects on transpiration
                KsComp = 1
            elif NewCond.th[comp] > prof.th_wp[comp]:
                # Transpiration from compartment is affected by water stress
                Wrel = (prof.th_fc[comp] - NewCond.th[comp]) / (prof.th_fc[comp] - prof.th_wp[comp])
                pRel = (Wrel - Crop.p_up[1]) / (Crop.p_lo[1] - Crop.p_up[1])
                if pRel <= 0:
                    KsComp = 1
                elif pRel >= 1:
                    KsComp = 0
                else:
                    KsComp = 1 - (
                        (np.exp(pRel * Crop.fshape_w[1]) - 1) / (np.exp(Crop.fshape_w[1]) - 1)
                    )

                if KsComp > 1:
                    KsComp = 1
                elif KsComp < 0:
                    KsComp = 0

            else:
                # No transpiration is possible from compartment as water
                # content does not exceed wilting point
                KsComp = 0

            # Adjust compartment stress factor for aeration stress
            if NewCond.DaySubmerged >= Crop.LagAer:
                # Full aeration stress - no transpiration possible from
                # compartment
                AerComp = 0
            elif NewCond.th[comp] > (prof.th_s[comp] - (Crop.Aer / 100)):
                # Increment aeration stress days counter
                NewCond.AerDaysComp[comp] = NewCond.AerDaysComp[comp] + 1
                if NewCond.AerDaysComp[comp] >= Crop.LagAer:
                    NewCond.AerDaysComp[comp] = Crop.LagAer
                    fAer = 0
                else:
                    fAer = 1

                # Calculate aeration stress factor
                AerComp = (prof.th_s[comp] - NewCond.th[comp]) / (
                    prof.th_s[comp] - (prof.th_s[comp] - (Crop.Aer / 100))
                )
                if AerComp < 0:
                    AerComp = 0

                AerComp = (fAer + (NewCond.AerDaysComp[comp] - 1) * AerComp) / (
                    fAer + NewCond.AerDaysComp[comp] - 1
                )
            else:
                # No aeration stress as number of submerged days does not
                # exceed threshold for initiation of aeration stress
                AerComp = 1
                NewCond.AerDaysComp[comp] = 0

            # Extract water
            ThToExtract = (ToExtract / 1000) / Soil_Profile.dz[comp]
            if IrrMngt_IrrMethod == 4:
                # Don't reduce compartment sink for stomatal water stress if in
                # net irrigation mode. Stress only occurs due to deficient
                # aeration conditions
                Sink = AerComp * SxComp[comp] * RootFact[comp]
            else:
                # Reduce compartment sink for greatest of stomatal and aeration
                # stress
                if KsComp == AerComp:
                    Sink = KsComp * SxComp[comp] * RootFact[comp]
                else:
                    Sink = min(KsComp, AerComp) * SxComp[comp] * RootFact[comp]

            # Limit extraction to demand
            if ThToExtract < Sink:
                Sink = ThToExtract

            # Limit extraction to avoid compartment water content dropping
            # below air dry
            if (InitCond_th[comp] - Sink) < prof.th_dry[comp]:
                Sink = InitCond_th[comp] - prof.th_dry[comp]
                if Sink < 0:
                    Sink = 0

            # Update water content in compartment
            NewCond.th[comp] = InitCond_th[comp] - Sink
            # Update amount of water to extract
            ToExtract = ToExtract - (Sink * 1000 * prof.dz[comp])
            # Update actual transpiration
            TrAct = TrAct + (Sink * 1000 * prof.dz[comp])

        ## Add net irrigation water requirement (if this mode is specified) ##
        if (IrrMngt_IrrMethod == 4) and (TrPot > 0):
            # Initialise net irrigation counter
            IrrNet = 0
            # Get root zone water content

            TAW = TAWClass()
            Dr = DrClass()
            thRZ = thRZClass()
            (
                _,
                Dr.Zt,
                Dr.Rz,
                TAW.Zt,
                TAW.Rz,
                thRZ.Act,
                thRZ.S,
                thRZ.FC,
                thRZ.WP,
                thRZ.Dry,
                thRZ.Aer,
            ) = _root_zone_water(
                prof,
                float(NewCond.Zroot),
                NewCond.th,
                Soil_zTop,
                float(Crop.Zmin),
                Crop.Aer,
            )

            # _,_Dr,_TAW,thRZ = root_zone_water(Soil_Profile,float(NewCond.Zroot),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
            NewCond.Depletion = Dr.Rz
            NewCond.TAW = TAW.Rz
            # Determine critical water content for net irrigation
            thCrit = thRZ.WP + ((IrrMngt_NetIrrSMT / 100) * (thRZ.FC - thRZ.WP))
            # Check if root zone water content is below net irrigation trigger
            if thRZ.Act < thCrit:
                # Initialise layer counter
                prelayer = 0
                for ii in range(comp_sto):
                    # Get soil layer
                    layeri = Soil_Profile.Layer[ii]
                    if layeri > prelayer:
                        # If in new layer, update critical water content for
                        # net irrigation
                        thCrit = prof.th_wp[ii] + (
                            (IrrMngt_NetIrrSMT / 100) * (prof.th_fc[ii] - prof.th_wp[ii])
                        )
                        # Update layer counter
                        prelayer = layeri

                    # Determine necessary change in water content in
                    # compartments to reach critical water content
                    dWC = RootFact[ii] * (thCrit - NewCond.th[ii]) * 1000 * prof.dz[ii]
                    # Update water content
                    NewCond.th[ii] = NewCond.th[ii] + (dWC / (1000 * prof.dz[ii]))
                    # Update net irrigation counter
                    IrrNet = IrrNet + dWC

            # Update net irrigation counter for the growing season
            NewCond.IrrNetCum = NewCond.IrrNetCum + IrrNet
        elif (IrrMngt_IrrMethod == 4) and (TrPot <= 0):
            # No net irrigation as potential transpiration is zero
            IrrNet = 0
        else:
            # No net irrigation as not in net irrigation mode
            IrrNet = 0
            NewCond.IrrNetCum = 0

        ## Add any surface transpiration to root zone total ##
        TrAct = TrAct + TrAct0

        ## Feedback with canopy cover development ##
        # If actual transpiration is zero then no canopy cover growth can occur
        if ((NewCond.CC - NewCond.CCprev) > 0.005) and (TrAct == 0):
            NewCond.CC = NewCond.CCprev

        ## Update transpiration ratio ##
        if TrPot0 > 0:
            if TrAct < TrPot0:
                NewCond.TrRatio = TrAct / TrPot0
            else:
                NewCond.TrRatio = 1

        else:
            NewCond.TrRatio = 1

        if NewCond.TrRatio < 0:
            NewCond.TrRatio = 0
        elif NewCond.TrRatio > 1:
            NewCond.TrRatio = 1

    else:
        # No transpiration if not in growing season
        TrAct = 0
        TrPot0 = 0
        TrPot_NS = 0
        # No irrigation if not in growing season
        IrrNet = 0
        NewCond.IrrNetCum = 0

    ## Store potential transpiration for irrigation calculations on next day ##
    NewCond.Tpot = TrPot0

    return TrAct, TrPot_NS, TrPot0, NewCond, IrrNet


# Cell
# @njit()
def groundwater_inflow(prof, NewCond):
    """
    Function to calculate capillary rise in the presence of a shallow groundwater table

    <a href="../pdfs/ac_ref_man_3.pdf#page=61" target="_blank">Reference Manual: capillary rise calculations</a> (pg. 52-61)


    *Arguments:*



    `Soil`: `SoilClass` : Soil object containing soil paramaters

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters

    `GwIn`: `float` : Groundwater inflow


    """

    ## Store initial conditions for updating ##
    GwIn = 0

    ## Perform calculations ##
    if NewCond.WTinSoil == True:
        # Water table in soil profile. Calculate horizontal inflow.
        # Get groundwater table elevation on current day
        zGW = NewCond.zGW

        # Find compartment mid-points
        zMid = prof.zMid
        # For compartments below water table, set to saturation #
        idx = np.argwhere(zMid >= zGW).flatten()[0]
        for ii in range(idx, len(prof.Comp)):
            # Get soil layer
            if NewCond.th[ii] < prof.th_s[ii]:
                # Update water content
                dth = prof.th_s[ii] - NewCond.th[ii]
                NewCond.th[ii] = prof.th_s[ii]
                # Update groundwater inflow
                GwIn = GwIn + (dth * 1000 * prof.dz[ii])

    return NewCond, GwIn


# Cell
# @njit()
@cc.export("_HIref_current_day", (f8,i8,i8,b1,f8,f8,CropStructNT_type_sig,b1))
def HIref_current_day(
    NewCond_HIref,
    NewCond_DAP,
    NewCond_DelayedCDs,
    NewCond_YieldForm,
    NewCond_PctLagPhase,
    NewCond_CCprev,
    Crop,
    GrowingSeason):
    """
    Function to calculate reference (no adjustment for stress effects)
    harvest index on current day

    <a href="../pdfs/ac_ref_man_3.pdf#page=119" target="_blank">Reference Manual: harvest index calculations</a> (pg. 110-126)



    *Arguments:*



    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `Crop`: `CropClass` : Crop object containing Crop paramaters

    `GrowingSeason`: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters




    """

    ## Store initial conditions for updating ##
    # NewCond = InitCond

    InitCond_HIref = NewCond_HIref*1

    # NewCond.HIref = 0.

    ## Calculate reference harvest index (if in growing season) ##
    if GrowingSeason == True:
        # Check if in yield formation period
        tAdj = NewCond_DAP - NewCond_DelayedCDs
        if tAdj > Crop.HIstartCD:

            NewCond_YieldForm = True
        else:
            NewCond_YieldForm = False

        # Get time for harvest index calculation
        HIt = NewCond_DAP - NewCond_DelayedCDs - Crop.HIstartCD - 1

        if HIt <= 0:
            # Yet to reach time for HI build-up
            NewCond_HIref = 0
            NewCond_PctLagPhase = 0
        else:
            if NewCond_CCprev <= (Crop.CCmin * Crop.CCx):
                # HI cannot develop further as canopy cover is too small
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

                # Limit HIref and round off computed value
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


# Cell
# @njit()
@cc.export("_biomass_accumulation", (CropStructNT_type_sig,i8,i8,f8,f8,f8,f8,f8,f8,f8,b1))
def biomass_accumulation(
                        Crop,
                        NewCond_DAP,
                        NewCond_DelayedCDs,
                        NewCond_HIref,
                        NewCond_PctLagPhase,
                        NewCond_B,
                        NewCond_B_NS,
                        Tr, 
                        TrPot, 
                        Et0, 
                        GrowingSeason):
    """
    Function to calculate biomass accumulation

    <a href="../pdfs/ac_ref_man_3.pdf#page=107" target="_blank">Reference Manual: biomass accumulaiton</a> (pg. 98-108)


    *Arguments:*



    `Crop`: `CropClass` : Crop object

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `Tr`: `float` : Daily transpiration

    `TrPot`: `float` : Daily potential transpiration

    `Et0`: `float` : Daily reference evapotranspiration

    `GrowingSeason`:: `bool` : is Growing season? (True, False)

    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters




    """

    ## Store initial conditions in a new structure for updating ##
    # NewCond = InitCond

    ## Calculate biomass accumulation (if in growing season) ##
    if GrowingSeason == True:
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

        # print(WPadj)

        # Adjust WP for CO2 effects
        WPadj = WPadj * Crop.fCO2

        # print(WPadj)

        # Calculate biomass accumulation on current day
        # No water stress
        dB_NS = WPadj * (TrPot / Et0)
        # With water stress
        dB = WPadj * (Tr / Et0)
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


# Cell
# @njit()
@cc.export("_temperature_stress", (CropStructNT_type_sig,f8,f8))
def temperature_stress(Crop, Tmax, Tmin):
    # Function to calculate temperature stress coefficients
    """
    Function to get irrigation depth for current day

    <a href="../pdfs/ac_ref_man_3.pdf#page=23" target="_blank">Reference Manual: temperature stress</a> (pg. 14)



    *Arguments:*



    `Crop`: `CropClass` : Crop object containing Crop paramaters

    `Tmax`: `float` : max tempatature on current day (celcius)

    `Tmin`: `float` : min tempature on current day (celcius)


    *Returns:*


    `Kst`: `KstClass` : Kst object containing tempature stress paramators







    """

    ## Calculate temperature stress coefficients affecting crop pollination ##
    # Get parameters for logistic curve
    KsPol_up = 1
    KsPol_lo = 0.001

    # Kst = KstClass()

    # Calculate effects of heat stress on pollination
    if Crop.PolHeatStress == 0:
        # No heat stress effects on pollination
        Kst_PolH = 1
    elif Crop.PolHeatStress == 1:
        # Pollination affected by heat stress
        if Tmax <= Crop.Tmax_lo:
            Kst_PolH = 1
        elif Tmax >= Crop.Tmax_up:
            Kst_PolH = 0
        else:
            Trel = (Tmax - Crop.Tmax_lo) / (Crop.Tmax_up - Crop.Tmax_lo)
            Kst_PolH = (KsPol_up * KsPol_lo) / (
                KsPol_lo + (KsPol_up - KsPol_lo) * np.exp(-Crop.fshape_b * (1 - Trel))
            )

    # Calculate effects of cold stress on pollination
    if Crop.PolColdStress == 0:
        # No cold stress effects on pollination
        Kst_PolC = 1
    elif Crop.PolColdStress == 1:
        # Pollination affected by cold stress
        if Tmin >= Crop.Tmin_up:
            Kst_PolC = 1
        elif Tmin <= Crop.Tmin_lo:
            Kst_PolC = 0
        else:
            Trel = (Crop.Tmin_up - Tmin) / (Crop.Tmin_up - Crop.Tmin_lo)
            Kst_PolC = (KsPol_up * KsPol_lo) / (
                KsPol_lo + (KsPol_up - KsPol_lo) * np.exp(-Crop.fshape_b * (1 - Trel))
            )

    return (Kst_PolH,Kst_PolC)


# Cell
# @njit()
@cc.export("_HIadj_pre_anthesis", (f8,f8,f8,f8))
def HIadj_pre_anthesis(
    NewCond_B,
    NewCond_B_NS,
    NewCond_CC,
    Crop_dHI_pre):
    """
    Function to calculate adjustment to harvest index for pre-anthesis water
    stress

    <a href="../pdfs/ac_ref_man_3.pdf#page=119" target="_blank">Reference Manual: harvest index calculations</a> (pg. 110-126)


    *Arguments:*



    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `Crop`: `CropClass` : Crop object containing Crop paramaters


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters


    """

    ## Store initial conditions in structure for updating ##
    # NewCond = InitCond

    # check that there is an adjustment to be made
    if Crop_dHI_pre > 0:
        ## Calculate adjustment ##
        # Get parameters
        Br = NewCond_B / NewCond_B_NS
        Br_range = np.log(Crop_dHI_pre) / 5.62
        Br_upp = 1
        Br_low = 1 - Br_range
        Br_top = Br_upp - (Br_range / 3)

        # Get biomass ratios
        ratio_low = (Br - Br_low) / (Br_top - Br_low)
        ratio_upp = (Br - Br_top) / (Br_upp - Br_top)

        # Calculate adjustment factor
        if (Br >= Br_low) and (Br < Br_top):
            NewCond_Fpre = 1 + (
                ((1 + np.sin((1.5 - ratio_low) * np.pi)) / 2) * (Crop_dHI_pre / 100)
            )
        elif (Br > Br_top) and (Br <= Br_upp):
            NewCond_Fpre = 1 + (
                ((1 + np.sin((0.5 + ratio_upp) * np.pi)) / 2) * (Crop_dHI_pre / 100)
            )
        else:
            NewCond_Fpre = 1
    else:
        NewCond_Fpre = 1

    if NewCond_CC <= 0.01:
        # No green canopy cover left at start of flowering so no harvestable
        # crop will develop
        NewCond_Fpre = 0

    return NewCond_Fpre


# Cell
# @njit()
@cc.export("_HIadj_pollination", (f8,f8,f8,f8,f8,KswNT_type_sig,KstNT_type_sig,f8))
def HIadj_pollination(
    NewCond_CC,
    NewCond_Fpol,
    Crop_FloweringCD, 
    Crop_CCmin, 
    Crop_exc, 
    Ksw, 
    Kst, 
    HIt
):
    """
    Function to calculate adjustment to harvest index for failure of
    pollination due to water or temperature stress

    <a href="../pdfs/ac_ref_man_3.pdf#page=119" target="_blank">Reference Manual: harvest index calculations</a> (pg. 110-126)


    *Arguments:*



    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `Crop`: `CropClass` : Crop object containing Crop paramaters

    `Ksw`: `KswClass` : Ksw object containing water stress paramaters

    `Kst`: `KstClass` : Kst object containing tempature stress paramaters

    `HIt`: `float` : time for harvest index build-up (calander days)


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters



    """

    ## Caclulate harvest index adjustment for pollination ##
    # Get fractional flowering
    if HIt == 0:
        # No flowering yet
        FracFlow = 0
    elif HIt > 0:
        # Fractional flowering on previous day
        t1 = HIt - 1
        if t1 == 0:
            F1 = 0
        else:
            t1Pct = 100 * (t1 / Crop_FloweringCD)
            if t1Pct > 100:
                t1Pct = 100

            F1 = 0.00558 * np.exp(0.63 * np.log(t1Pct)) - (0.000969 * t1Pct) - 0.00383

        if F1 < 0:
            F1 = 0

        # Fractional flowering on current day
        t2 = HIt
        if t2 == 0:
            F2 = 0
        else:
            t2Pct = 100 * (t2 / Crop_FloweringCD)
            if t2Pct > 100:
                t2Pct = 100

            F2 = 0.00558 * np.exp(0.63 * np.log(t2Pct)) - (0.000969 * t2Pct) - 0.00383

        if F2 < 0:
            F2 = 0

        # Weight values
        if abs(F1 - F2) < 0.0000001:
            F = 0
        else:
            F = 100 * ((F1 + F2) / 2) / Crop_FloweringCD

        FracFlow = F

    # Calculate pollination adjustment for current day
    if NewCond_CC < Crop_CCmin:
        # No pollination can occur as canopy cover is smaller than minimum
        # threshold
        dFpol = 0
    else:
        Ks = min([Ksw.Pol, Kst.PolC, Kst.PolH])
        dFpol = Ks * FracFlow * (1 + (Crop_exc / 100))

    # Calculate pollination adjustment to date
    NewCond_Fpol = NewCond_Fpol + dFpol
    if NewCond_Fpol > 1:
        # Crop has fully pollinated
        NewCond_Fpol = 1

    return NewCond_Fpol


# Cell
# @njit()
@cc.export("_HIadj_post_anthesis", (i8,f8,f8,i8,f8,f8,f8,f8,CropStructNT_type_sig,KswNT_type_sig,))
def HIadj_post_anthesis(
                    NewCond_DelayedCDs,
                    NewCond_sCor1,
                    NewCond_sCor2,
                    NewCond_DAP,
                    NewCond_Fpre,
                    NewCond_CC,
                    NewCond_fpost_upp,
                    NewCond_fpost_dwn,
                    Crop, 
                    Ksw):
    """
    Function to calculate adjustment to harvest index for post-anthesis water
    stress

    <a href="../pdfs/ac_ref_man_3.pdf#page=119" target="_blank">Reference Manual: harvest index calculations</a> (pg. 110-126)


    *Arguments:*



    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `Crop`: `CropClass` : Crop object containing Crop paramaters

    `Ksw`: `KswClass` : Ksw object containing water stress paramaters

    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters


    """

    ## Store initial conditions in a structure for updating ##
    # NewCond = InitCond

    InitCond_DelayedCDs = NewCond_DelayedCDs*1
    InitCond_sCor1 = NewCond_sCor1*1
    InitCond_sCor2 = NewCond_sCor2*1

    ## Calculate harvest index adjustment ##
    # 1. Adjustment for leaf expansion
    tmax1 = Crop.CanopyDevEndCD - Crop.HIstartCD
    DAP = NewCond_DAP - InitCond_DelayedCDs
    if (
        (DAP <= (Crop.CanopyDevEndCD + 1))
        and (tmax1 > 0)
        and (NewCond_Fpre > 0.99)
        and (NewCond_CC > 0.001)
        and (Crop.a_HI > 0)
    ):
        dCor = 1 + (1 - Ksw.Exp) / Crop.a_HI
        NewCond_sCor1 = InitCond_sCor1 + (dCor / tmax1)
        DayCor = DAP - 1 - Crop.HIstartCD
        NewCond_fpost_upp = (tmax1 / DayCor) * NewCond_sCor1

    # 2. Adjustment for stomatal closure
    tmax2 = Crop.YldFormCD
    DAP = NewCond_DAP - InitCond_DelayedCDs
    if (
        (DAP <= (Crop.HIendCD + 1))
        and (tmax2 > 0)
        and (NewCond_Fpre > 0.99)
        and (NewCond_CC > 0.001)
        and (Crop.b_HI > 0)
    ):
        # print(Ksw.Sto)
        dCor = np.power(Ksw.Sto, 0.1) * (1 - (1 - Ksw.Sto) / Crop.b_HI)
        NewCond_sCor2 = InitCond_sCor2 + (dCor / tmax2)
        DayCor = DAP - 1 - Crop.HIstartCD
        NewCond_fpost_dwn = (tmax2 / DayCor) * NewCond_sCor2

    # Determine total multiplier
    if (tmax1 == 0) and (tmax2 == 0):
        NewCond_Fpost = 1
    else:
        if tmax2 == 0:
            NewCond_Fpost = NewCond_fpost_upp
        else:
            if tmax1 == 0:
                NewCond_Fpost = NewCond_fpost_dwn
            elif tmax1 <= tmax2:
                NewCond_Fpost = NewCond_fpost_dwn * (
                    ((tmax1 * NewCond_fpost_upp) + (tmax2 - tmax1)) / tmax2
                )
            else:
                NewCond_Fpost = NewCond_fpost_upp * (
                    ((tmax2 * NewCond_fpost_dwn) + (tmax1 - tmax2)) / tmax1
                )

    return (
            NewCond_sCor1,
            NewCond_sCor2,
            NewCond_fpost_upp,
            NewCond_fpost_dwn,
            NewCond_Fpost)


# Cell
# @njit()
def harvest_index(prof, Soil_zTop, Crop, InitCond, Et0, Tmax, Tmin, GrowingSeason):

    """
    Function to simulate build up of harvest index


     <a href="../pdfs/ac_ref_man_3.pdf#page=119" target="_blank">Reference Manual: harvest index calculations</a> (pg. 110-126)

    *Arguments:*


    `Soil`: `SoilClass` : Soil object containing soil paramaters

    `Crop`: `CropClass` : Crop object containing Crop paramaters

    `InitCond`: `InitCondClass` : InitCond object containing model paramaters

    `Et0`: `float` : reference evapotranspiration on current day

    `Tmax`: `float` : maximum tempature on current day (celcius)

    `Tmin`: `float` : minimum tempature on current day (celcius)

    `GrowingSeason`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitCondClass` : InitCond object containing updated model paramaters



    """

    ## Store initial conditions for updating ##
    NewCond = InitCond

    InitCond_HI = InitCond.HI
    InitCond_HIadj = InitCond.HIadj
    InitCond_PreAdj = InitCond.PreAdj

    ## Calculate harvest index build up (if in growing season) ##
    if GrowingSeason == True:
        # Calculate root zone water content

        TAW = TAWClass()
        Dr = DrClass()
        # thRZ = thRZClass()
        _, Dr.Zt, Dr.Rz, TAW.Zt, TAW.Rz, _,_,_,_,_,_, = _root_zone_water(
            prof,
            float(NewCond.Zroot),
            NewCond.th,
            Soil_zTop,
            float(Crop.Zmin),
            Crop.Aer,
        )

        # _,Dr,TAW,_ = root_zone_water(Soil_Profile,float(NewCond.Zroot),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
        # Check whether to use root zone or top soil depletions for calculating
        # water stress
        if (Dr.Rz / TAW.Rz) <= (Dr.Zt / TAW.Zt):
            # Root zone is wetter than top soil, so use root zone value
            Dr = Dr.Rz
            TAW = TAW.Rz
        else:
            # Top soil is wetter than root zone, so use top soil values
            Dr = Dr.Zt
            TAW = TAW.Zt

        # Calculate water stress
        beta = True
        # Ksw = water_stress(Crop, NewCond, Dr, TAW, Et0, beta)
        # Ksw = KswClass()
        Ksw_Exp, Ksw_Sto, Ksw_Sen, Ksw_Pol, Ksw_StoLin = _water_stress(
            Crop.p_up,
            Crop.p_lo,
            Crop.ETadj,
            Crop.beta,
            Crop.fshape_w,
            NewCond.tEarlySen,
            Dr,
            TAW,
            Et0,
            beta,
        )
        Ksw = KswNT(Exp=Ksw_Exp, Sto=Ksw_Sto, Sen=Ksw_Sen, Pol=Ksw_Pol, StoLin=Ksw_StoLin )
        # Calculate temperature stress
        (Kst_PolH,Kst_PolC) = _temperature_stress(Crop, Tmax, Tmin)
        Kst = KstNT(PolH=Kst_PolH,PolC=Kst_PolC)
        # Get reference harvest index on current day
        HIi = NewCond.HIref

        # Get time for harvest index build-up
        HIt = NewCond.DAP - NewCond.DelayedCDs - Crop.HIstartCD - 1

        # Calculate harvest index
        if (NewCond.YieldForm == True) and (HIt >= 0):
            # print(NewCond.DAP)
            # Root/tuber or fruit/grain crops
            if (Crop.CropType == 2) or (Crop.CropType == 3):
                # Detemine adjustment for water stress before anthesis
                if InitCond_PreAdj == False:
                    InitCond.PreAdj = True
                    NewCond.Fpre = _HIadj_pre_anthesis(NewCond.B,
                                                NewCond.B_NS,
                                                NewCond.CC,
                                                Crop.dHI_pre)

                # Determine adjustment for crop pollination failure
                if Crop.CropType == 3:  # Adjustment only for fruit/grain crops
                    if (HIt > 0) and (HIt <= Crop.FloweringCD):

                        NewCond.Fpol = _HIadj_pollination(
                            NewCond.CC,
                            NewCond.Fpol,
                            Crop.FloweringCD,
                            Crop.CCmin,
                            Crop.exc,
                            Ksw,
                            Kst,
                            HIt,
                        )

                    HImax = NewCond.Fpol * Crop.HI0
                else:
                    # No pollination adjustment for root/tuber crops
                    HImax = Crop.HI0

                # Determine adjustments for post-anthesis water stress
                if HIt > 0:
                    (NewCond.sCor1,
                    NewCond.sCor2,
                    NewCond.fpost_upp,
                    NewCond.fpost_dwn,
                    NewCond.Fpost) = _HIadj_post_anthesis(NewCond.DelayedCDs,
                                                        NewCond.sCor1,
                                                        NewCond.sCor2,
                                                        NewCond.DAP,
                                                        NewCond.Fpre,
                                                        NewCond.CC,
                                                        NewCond.fpost_upp,
                                                        NewCond.fpost_dwn,
                                                        Crop, 
                                                        Ksw)

                # Limit HI to maximum allowable increase due to pre- and
                # post-anthesis water stress combinations
                HImult = NewCond.Fpre * NewCond.Fpost
                if HImult > 1 + (Crop.dHI0 / 100):
                    HImult = 1 + (Crop.dHI0 / 100)

                # Determine harvest index on current day, adjusted for stress
                # effects
                if HImax >= HIi:
                    HIadj = HImult * HIi
                else:
                    HIadj = HImult * HImax

            elif Crop.CropType == 1:
                # Leafy vegetable crops - no adjustment, harvest index equal to
                # reference value for current day
                HIadj = HIi

        else:

            # No build-up of harvest index if outside yield formation period
            HIi = InitCond_HI
            HIadj = InitCond_HIadj

        # Store final values for current time step
        NewCond.HI = HIi
        NewCond.HIadj = HIadj

    else:
        # No harvestable crop outside of a growing season
        NewCond.HI = 0
        NewCond.HIadj = 0

    # print([NewCond.DAP , Crop.YldFormCD])
    return NewCond


if __name__ == "__main__":
    cc.compile()
