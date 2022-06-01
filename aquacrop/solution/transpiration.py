
import os
import numpy as np
from ..entities.totalAvailableWater import TAW
from ..entities.moistureDepletion import Dr
from ..entities.rootZoneWaterContent import RootZoneWater, thRZNT
from ..entities.waterStressCoefficients import  Ksw,  KswNT


# This compiled function is called a few times inside other functions

if __name__ != "__main__":
    if os.getenv("DEVELOPMENT"):
        from .water_stress import water_stress
        from .root_zone_water import root_zone_water
        from .aeration_stress import aeration_stress
    else:
        from .solution_water_stress import water_stress
        from .solution_root_zone_water import root_zone_water
        from .solution_aeration_stress import aeration_stress
else:
    from .water_stress import water_stress
    from .root_zone_water import root_zone_water
    from .aeration_stress import aeration_stress
     




def transpiration(
    Soil_Profile,
    Soil_nComp,
    Soil_zTop,
    Crop,
    IrrMngt_IrrMethod,
    IrrMngt_NetIrrSMT,
    InitCond,
    et0,
    CO2,
    growing_season,
    gdd,
):

    """
    Function to calculate crop transpiration on current day

    <a href="../pdfs/ac_ref_man_3.pdf#page=91" target="_blank">Reference Manual: transpiration equations</a> (pg. 82-91)



    *Arguments:*


    `Soil`: `Soil` : Soil object

    `Crop`: `Crop` : Crop object

    `IrrMngt`: `IrrMngt`: object containing irrigation management params

    `InitCond`: `InitialCondition` : InitCond object

    `et0`: `float` : reference evapotranspiration

    `CO2`: `CO2` : CO2

    `gdd`: `float` : Growing Degree Days

    `growing_season`:: `bool` : is it currently within the growing season (True, Flase)

    *Returns:*


    `TrAct`: `float` : Actual Transpiration on current day

    `TrPot_NS`: `float` : Potential Transpiration on current day with no water stress

    `TrPot0`: `float` : Potential Transpiration on current day

    `NewCond`: `InitialCondition` : updated InitCond object

    `IrrNet`: `float` : Net Irrigation (if required)







    """

    ## Store initial conditions ##
    NewCond = InitCond

    InitCond_th = InitCond.th

    prof = Soil_Profile

    ## Calculate transpiration (if in growing season) ##
    if growing_season == True:
        ## Calculate potential transpiration ##
        # 1. No prior water stress
        # Update ageing days counter
        DAPadj = NewCond.dap - NewCond.delayed_cds
        if DAPadj > Crop.MaxCanopyCD:
            NewCond.age_days_ns = DAPadj - Crop.MaxCanopyCD

        # Update crop coefficient for ageing of canopy
        if NewCond.age_days_ns > 5:
            Kcb_NS = Crop.Kcb - ((NewCond.age_days_ns - 5) * (Crop.fage / 100)) * NewCond.ccx_w_ns
        else:
            Kcb_NS = Crop.Kcb

        # Update crop coefficient for CO2 concentration
        CO2CurrentConc = CO2.current_concentration
        CO2RefConc = CO2.ref_concentration
        if CO2CurrentConc > CO2RefConc:
            Kcb_NS = Kcb_NS * (1 - 0.05 * ((CO2CurrentConc - CO2RefConc) / (550 - CO2RefConc)))

        # Determine potential transpiration rate (no water stress)
        TrPot_NS = Kcb_NS * (NewCond.canopy_cover_adj_ns) * et0

        # Correct potential transpiration for dying green canopy effects
        if NewCond.canopy_cover_ns < NewCond.ccx_w_ns:
            if (NewCond.ccx_w_ns > 0.001) and (NewCond.canopy_cover_ns > 0.001):
                TrPot_NS = TrPot_NS * ((NewCond.canopy_cover_ns / NewCond.ccx_w_ns) ** Crop.a_Tr)

        # 2. Potential prior water stress and/or delayed development
        # Update ageing days counter
        DAPadj = NewCond.dap - NewCond.delayed_cds
        if DAPadj > Crop.MaxCanopyCD:
            NewCond.age_days = DAPadj - Crop.MaxCanopyCD

        # Update crop coefficient for ageing of canopy
        if NewCond.age_days > 5:
            Kcb = Crop.Kcb - ((NewCond.age_days - 5) * (Crop.fage / 100)) * NewCond.ccx_w
        else:
            Kcb = Crop.Kcb

        # Update crop coefficient for CO2 concentration
        if CO2CurrentConc > CO2RefConc:
            Kcb = Kcb * (1 - 0.05 * ((CO2CurrentConc - CO2RefConc) / (550 - CO2RefConc)))

        # Determine potential transpiration rate
        TrPot0 = Kcb * (NewCond.canopy_cover_adj) * et0
        # Correct potential transpiration for dying green canopy effects
        if NewCond.canopy_cover < NewCond.ccx_w:
            if (NewCond.ccx_w > 0.001) and (NewCond.canopy_cover > 0.001):
                TrPot0 = TrPot0 * ((NewCond.canopy_cover / NewCond.ccx_w) ** Crop.a_Tr)

        # 3. Adjust potential transpiration for cold stress effects
        # Check if cold stress occurs on current day
        if Crop.TrColdStress == 0:
            # Cold temperature stress does not affect transpiration
            KsCold = 1
        elif Crop.TrColdStress == 1:
            # Transpiration can be affected by cold temperature stress
            if gdd >= Crop.GDD_up:
                # No cold temperature stress
                KsCold = 1
            elif gdd <= Crop.GDD_lo:
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
                GDDrel = (gdd - Crop.GDD_lo) / (Crop.GDD_up - Crop.GDD_lo)
                KsCold = (KsTr_up * KsTr_lo) / (
                    KsTr_lo + (KsTr_up - KsTr_lo) * np.exp(-fshapeb * GDDrel)
                )
                KsCold = KsCold - KsTr_lo * (1 - GDDrel)

        # Correct potential transpiration rate (mm/day)
        TrPot0 = TrPot0 * KsCold
        TrPot_NS = TrPot_NS * KsCold

        # print(TrPot0,NewCond.dap)

        ## Calculate surface layer transpiration ##
        if (NewCond.surface_storage > 0) and (NewCond.day_submerged < Crop.LagAer):

            # Update submergence days counter
            NewCond.day_submerged = NewCond.day_submerged + 1
            # Update anerobic conditions counter for each compartment
            for ii in range(int(Soil_nComp)):
                # Increment aeration days counter for compartment ii
                NewCond.aer_days_comp[ii] = NewCond.aer_days_comp[ii] + 1
                if NewCond.aer_days_comp[ii] > Crop.LagAer:
                    NewCond.aer_days_comp[ii] = Crop.LagAer

            # Reduce actual transpiration that is possible to account for
            # aeration stress due to extended submergence
            fSub = 1 - (NewCond.day_submerged / Crop.LagAer)
            if NewCond.surface_storage > (fSub * TrPot0):
                # Transpiration occurs from surface storage
                NewCond.surface_storage = NewCond.surface_storage - (fSub * TrPot0)
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

        # print(TrPot,NewCond.dap)

        ## Update potential root zone transpiration for water stress ##
        # Determine root zone and top soil depletion, and root zone water
        # content

        taw = TAW()
        water_root_depletion = Dr()
        thRZ = RootZoneWater()
        (
            _,
            water_root_depletion.Zt,
            water_root_depletion.Rz,
            taw.Zt,
            taw.Rz,
            thRZ.Act,
            thRZ.S,
            thRZ.FC,
            thRZ.WP,
            thRZ.Dry,
            thRZ.Aer,
        ) = root_zone_water(
            prof,
            float(NewCond.z_root),
            NewCond.th,
            Soil_zTop,
            float(Crop.Zmin),
            Crop.Aer,
        )

        class_args = {key:value for key, value in thRZ.__dict__.items() if not key.startswith('__') and not callable(key)}
        thRZ = thRZNT(**class_args)

        # _,water_root_depletion,taw,thRZ = root_zone_water(Soil_Profile,float(NewCond.z_root),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
        # Check whether to use root zone or top soil depletions for calculating
        # water stress
        if (water_root_depletion.Rz / taw.Rz) <= (water_root_depletion.Zt / taw.Zt):
            # Root zone is wetter than top soil, so use root zone value
            water_root_depletion = water_root_depletion.Rz
            taw = taw.Rz
        else:
            # Top soil is wetter than root zone, so use top soil values
            water_root_depletion = water_root_depletion.Zt
            taw = taw.Zt

        # Calculate water stress coefficients
        beta = True
        water_stress_coef = Ksw()
        water_stress_coef.exp, water_stress_coef.sto, water_stress_coef.sen, water_stress_coef.pol, water_stress_coef.sto_lin = water_stress(
            Crop.p_up,
            Crop.p_lo,
            Crop.ETadj,
            Crop.beta,
            Crop.fshape_w,
            NewCond.t_early_sen,
            water_root_depletion,
            taw,
            et0,
            beta,
        )
        # water_stress_coef = water_stress(Crop, NewCond, water_root_depletion, taw, et0, beta)

        # Calculate aeration stress coefficients
        Ksa_Aer, NewCond.aer_days = aeration_stress(NewCond.aer_days, Crop.LagAer, thRZ)
        # Maximum stress effect
        Ks = min(water_stress_coef.sto_lin, Ksa_Aer)
        # Update potential transpiration in root zone
        if IrrMngt_IrrMethod != 4:
            # No adjustment to TrPot for water stress when in net irrigation mode
            TrPot = TrPot * Ks

        ## Determine compartments covered by root zone ##
        # Compartments covered by the root zone
        rootdepth = round(max(float(NewCond.z_root), float(Crop.Zmin)), 2)
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
                    SxCompBot = Crop.SxBot * NewCond.r_cor + (
                        (Crop.SxTop - Crop.SxBot * NewCond.r_cor)
                        * ((rootdepth - Soil_Profile.dzsum[ii]) / rootdepth)
                    )
                else:
                    SxCompBot = Crop.SxBot * NewCond.r_cor

                SxComp[ii] = (SxCompTop + SxCompBot) / 2

        # print(TrPot,NewCond.dap)
        ## Extract water ##
        ToExtract = TrPot
        comp = -1
        TrAct = 0
        while (ToExtract > 0) and (comp < comp_sto - 1):
            # Increment compartment
            comp = comp + 1
            # Specify layer number

            # Determine taw (m3/m3) for compartment
            thTAW = prof.th_fc[comp] - prof.th_wp[comp]
            if Crop.ETadj == 1:
                # Adjust stomatal stress threshold for et0 on current day
                p_up_sto = Crop.p_up[1] + (0.04 * (5 - et0)) * (np.log10(10 - 9 * Crop.p_up[1]))

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
            if NewCond.day_submerged >= Crop.LagAer:
                # Full aeration stress - no transpiration possible from
                # compartment
                AerComp = 0
            elif NewCond.th[comp] > (prof.th_s[comp] - (Crop.Aer / 100)):
                # Increment aeration stress days counter
                NewCond.aer_days_comp[comp] = NewCond.aer_days_comp[comp] + 1
                if NewCond.aer_days_comp[comp] >= Crop.LagAer:
                    NewCond.aer_days_comp[comp] = Crop.LagAer
                    fAer = 0
                else:
                    fAer = 1

                # Calculate aeration stress factor
                AerComp = (prof.th_s[comp] - NewCond.th[comp]) / (
                    prof.th_s[comp] - (prof.th_s[comp] - (Crop.Aer / 100))
                )
                if AerComp < 0:
                    AerComp = 0

                AerComp = (fAer + (NewCond.aer_days_comp[comp] - 1) * AerComp) / (
                    fAer + NewCond.aer_days_comp[comp] - 1
                )
            else:
                # No aeration stress as number of submerged days does not
                # exceed threshold for initiation of aeration stress
                AerComp = 1
                NewCond.aer_days_comp[comp] = 0

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

            taw = TAW()
            water_root_depletion = Dr()
            thRZ = RootZoneWater()
            (
                _,
                water_root_depletion.Zt,
                water_root_depletion.Rz,
                taw.Zt,
                taw.Rz,
                thRZ.Act,
                thRZ.S,
                thRZ.FC,
                thRZ.WP,
                thRZ.Dry,
                thRZ.Aer,
            ) = root_zone_water(
                prof,
                float(NewCond.z_root),
                NewCond.th,
                Soil_zTop,
                float(Crop.Zmin),
                Crop.Aer,
            )

            # _,_Dr,_TAW,thRZ = root_zone_water(Soil_Profile,float(NewCond.z_root),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
            NewCond.depletion = water_root_depletion.Rz
            NewCond.taw = taw.Rz
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
            NewCond.irr_net_cum = NewCond.irr_net_cum + IrrNet
        elif (IrrMngt_IrrMethod == 4) and (TrPot <= 0):
            # No net irrigation as potential transpiration is zero
            IrrNet = 0
        else:
            # No net irrigation as not in net irrigation mode
            IrrNet = 0
            NewCond.irr_net_cum = 0

        ## Add any surface transpiration to root zone total ##
        TrAct = TrAct + TrAct0

        ## Feedback with canopy cover development ##
        # If actual transpiration is zero then no canopy cover growth can occur
        if ((NewCond.canopy_cover - NewCond.cc_prev) > 0.005) and (TrAct == 0):
            NewCond.canopy_cover = NewCond.cc_prev

        ## Update transpiration ratio ##
        if TrPot0 > 0:
            if TrAct < TrPot0:
                NewCond.tr_ratio = TrAct / TrPot0
            else:
                NewCond.tr_ratio = 1

        else:
            NewCond.tr_ratio = 1

        if NewCond.tr_ratio < 0:
            NewCond.tr_ratio = 0
        elif NewCond.tr_ratio > 1:
            NewCond.tr_ratio = 1

    else:
        # No transpiration if not in growing season
        TrAct = 0
        TrPot0 = 0
        TrPot_NS = 0
        # No irrigation if not in growing season
        IrrNet = 0
        NewCond.irr_net_cum = 0

    ## Store potential transpiration for irrigation calculations on next day ##
    NewCond.t_pot = TrPot0

    return TrAct, TrPot_NS, TrPot0, NewCond, IrrNet