
import os
import numpy as np

from ..entities.totalAvailableWater import TAW
from ..entities.moistureDepletion import Dr

from ..entities.waterStressCoefficients import  Ksw
from .adjust_CCx import adjust_CCx

if __name__ != "__main__":
    if os.getenv("DEVELOPMENT"):
        from .water_stress import water_stress
        from .root_zone_water import root_zone_water
        from .cc_development import cc_development
        from .update_CCx_CDC import update_CCx_CDC
        from .cc_required_time import cc_required_time
    else:
        from .solution_water_stress import water_stress
        from .solution_root_zone_water import root_zone_water
        from .solution_cc_development import cc_development
        from .solution_update_CCx_CDC import update_CCx_CDC
        from .solution_cc_required_time import cc_required_time
else:
    from .water_stress import water_stress
    from .root_zone_water import root_zone_water
    from .cc_development import cc_development
    from .update_CCx_CDC import update_CCx_CDC
    from .cc_required_time import cc_required_time




def canopy_cover(Crop, prof, Soil_zTop, InitCond, gdd, et0, growing_season):
    # def CCCrop,Soil_Profile,Soil_zTop,InitCond,gdd,et0,growing_season):

    """
    Function to simulate canopy growth/decline

    <a href="../pdfs/ac_ref_man_3.pdf#page=30" target="_blank">Reference Manual: canopy_cover equations</a> (pg. 21-33)


    *Arguments:*


    `Crop`: `Crop` : Crop object

    `prof`: `SoilProfile` : Soil object

    `Soil_zTop`: `float` : top soil depth

    `InitCond`: `InitialCondition` : InitCond object

    `gdd`: `float` : Growing Degree Days

    `et0`: `float` : reference evapotranspiration

    `growing_season`:: `bool` : is it currently within the growing season (True, Flase)

    *Returns:*


    `NewCond`: `InitialCondition` : updated InitCond object


    """

    # Function to simulate canopy growth/decline

    InitCond_CC_NS = InitCond.canopy_cover_ns
    InitCond_CC = InitCond.canopy_cover
    InitCond_ProtectedSeed = InitCond.protected_seed
    InitCond_CCxAct = InitCond.ccx_act
    InitCond_CropDead = InitCond.crop_dead
    InitCond_tEarlySen = InitCond.t_early_sen
    InitCond_CCxW = InitCond.ccx_w

    ## Store initial conditions in a new structure for updating ##
    NewCond = InitCond
    NewCond.cc_prev = InitCond.canopy_cover

    ## Calculate canopy development (if in growing season) ##
    if growing_season == True:
        # Calculate root zone water content
        taw = TAW()
        root_zone_depletion = Dr()
        # thRZ = RootZoneWater()
        _, root_zone_depletion.Zt, root_zone_depletion.Rz, taw.Zt, taw.Rz, _,_,_,_,_,_ = root_zone_water(
            prof,
            float(NewCond.z_root),
            NewCond.th,
            Soil_zTop,
            float(Crop.Zmin),
            Crop.Aer,
        )

        # _,root_zone_depletion,taw,_ = root_zone_water(Soil_Profile,float(NewCond.z_root),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
        # Check whether to use root zone or top soil depletions for calculating
        # water stress
        if (root_zone_depletion.Rz / taw.Rz) <= (root_zone_depletion.Zt / taw.Zt):
            # Root zone is wetter than top soil, so use root zone value
            root_zone_depletion = root_zone_depletion.Rz
            taw = taw.Rz
        else:
            # Top soil is wetter than root zone, so use top soil values
            root_zone_depletion = root_zone_depletion.Zt
            taw = taw.Zt

        # Determine if water stress is occurring
        beta = True
        water_stress_coef = Ksw()
        water_stress_coef.exp, water_stress_coef.sto, water_stress_coef.sen, water_stress_coef.pol, water_stress_coef.sto_lin = water_stress(
            Crop.p_up,
            Crop.p_lo,
            Crop.ETadj,
            Crop.beta,
            Crop.fshape_w,
            NewCond.t_early_sen,
            root_zone_depletion,
            taw,
            et0,
            beta,
        )

        # water_stress(Crop, NewCond, root_zone_depletion, taw, et0, beta)

        # Get canopy cover growth time
        if Crop.CalendarType == 1:
            dtCC = 1
            tCCadj = NewCond.dap - NewCond.delayed_cds
        elif Crop.CalendarType == 2:
            dtCC = gdd
            tCCadj = NewCond.gdd_cum - NewCond.delayed_gdds

        ## Canopy development (potential) ##
        if (tCCadj < Crop.Emergence) or (round(tCCadj) > Crop.Maturity):
            # No canopy development before emergence/germination or after
            # maturity
            NewCond.canopy_cover_ns = 0
        elif tCCadj < Crop.CanopyDevEnd:
            # Canopy growth can occur
            if InitCond_CC_NS <= Crop.CC0:
                # Very small initial canopy_cover.
                NewCond.canopy_cover_ns = Crop.CC0 * np.exp(Crop.CGC * dtCC)
                # print(Crop.CC0,np.exp(Crop.CGC*dtCC))
            else:
                # Canopy growing
                tmp_tCC = tCCadj - Crop.Emergence
                NewCond.canopy_cover_ns = cc_development(
                    Crop.CC0, 0.98 * Crop.CCx, Crop.CGC, Crop.CDC, tmp_tCC, "Growth", Crop.CCx
                )

            # Update maximum canopy cover size in growing season
            NewCond.ccx_act_ns = NewCond.canopy_cover_ns
        elif tCCadj > Crop.CanopyDevEnd:
            # No more canopy growth is possible or canopy in decline
            # Set CCx for calculation of withered canopy effects
            NewCond.ccx_w_ns = NewCond.ccx_act_ns
            if tCCadj < Crop.Senescence:
                # Mid-season stage - no canopy growth
                NewCond.canopy_cover_ns = InitCond_CC_NS
                # Update maximum canopy cover size in growing season
                NewCond.ccx_act_ns = NewCond.canopy_cover_ns
            else:
                # Late-season stage - canopy decline
                tmp_tCC = tCCadj - Crop.Senescence
                NewCond.canopy_cover_ns = cc_development(
                    Crop.CC0,
                    NewCond.ccx_act_ns,
                    Crop.CGC,
                    Crop.CDC,
                    tmp_tCC,
                    "Decline",
                    NewCond.ccx_act_ns,
                )

        ## Canopy development (actual) ##
        if (tCCadj < Crop.Emergence) or (round(tCCadj) > Crop.Maturity):
            # No canopy development before emergence/germination or after
            # maturity
            NewCond.canopy_cover = 0
            NewCond.cc0_adj = Crop.CC0
        elif tCCadj < Crop.CanopyDevEnd:
            # Canopy growth can occur
            if InitCond_CC <= NewCond.cc0_adj or (
                (InitCond_ProtectedSeed == True) and (InitCond_CC <= (1.25 * NewCond.cc0_adj))
            ):
                # Very small initial canopy_cover or seedling in protected phase of
                # growth. In this case, assume no leaf water expansion stress
                if InitCond_ProtectedSeed == True:
                    tmp_tCC = tCCadj - Crop.Emergence
                    NewCond.canopy_cover = cc_development(
                        Crop.CC0, Crop.CCx, Crop.CGC, Crop.CDC, tmp_tCC, "Growth", Crop.CCx
                    )
                    # Check if seed protection should be turned off
                    if NewCond.canopy_cover > (1.25 * NewCond.cc0_adj):
                        # Turn off seed protection - lead expansion stress can
                        # occur on future time steps.
                        NewCond.protected_seed = False

                else:
                    NewCond.canopy_cover = NewCond.cc0_adj * np.exp(Crop.CGC * dtCC)

            else:
                # Canopy growing

                if InitCond_CC < (0.9799 * Crop.CCx):
                    # Adjust canopy growth coefficient for leaf expansion water
                    # stress effects
                    CGCadj = Crop.CGC * water_stress_coef.exp
                    if CGCadj > 0:

                        # Adjust CCx for change in CGC
                        CCXadj = adjust_CCx(
                            InitCond_CC,
                            NewCond.cc0_adj,
                            Crop.CCx,
                            CGCadj,
                            Crop.CDC,
                            dtCC,
                            tCCadj,
                            Crop.CanopyDevEnd,
                            Crop.CCx,
                        )
                        if CCXadj < 0:

                            NewCond.canopy_cover = InitCond_CC
                        elif abs(InitCond_CC - (0.9799 * Crop.CCx)) < 0.001:

                            # Approaching maximum canopy cover size
                            tmp_tCC = tCCadj - Crop.Emergence
                            NewCond.canopy_cover = cc_development(
                                Crop.CC0, Crop.CCx, Crop.CGC, Crop.CDC, tmp_tCC, "Growth", Crop.CCx
                            )
                        else:

                            # Determine time required to reach canopy_cover on previous,
                            # day, given CGCAdj value
                            tReq = cc_required_time(
                                InitCond_CC, NewCond.cc0_adj, CCXadj, CGCadj, Crop.CDC, "CGC"
                            )
                            if tReq > 0:

                                # Calclate gdd's for canopy growth
                                tmp_tCC = tReq + dtCC
                                # Determine new canopy size
                                NewCond.canopy_cover = cc_development(
                                    NewCond.cc0_adj,
                                    CCXadj,
                                    CGCadj,
                                    Crop.CDC,
                                    tmp_tCC,
                                    "Growth",
                                    Crop.CCx,
                                )
                                # print(NewCond.dap,CCXadj,tReq)

                            else:
                                # No canopy growth
                                NewCond.canopy_cover = InitCond_CC

                    else:

                        # No canopy growth
                        NewCond.canopy_cover = InitCond_CC
                        # Update CC0
                        if NewCond.canopy_cover > NewCond.cc0_adj:
                            NewCond.cc0_adj = Crop.CC0
                        else:
                            NewCond.cc0_adj = NewCond.canopy_cover

                else:
                    # Canopy approaching maximum size
                    tmp_tCC = tCCadj - Crop.Emergence
                    NewCond.canopy_cover = cc_development(
                        Crop.CC0, Crop.CCx, Crop.CGC, Crop.CDC, tmp_tCC, "Growth", Crop.CCx
                    )
                    NewCond.cc0_adj = Crop.CC0

            if NewCond.canopy_cover > InitCond_CCxAct:
                # Update actual maximum canopy cover size during growing season
                NewCond.ccx_act = NewCond.canopy_cover

        elif tCCadj > Crop.CanopyDevEnd:

            # No more canopy growth is possible or canopy is in decline
            if tCCadj < Crop.Senescence:
                # Mid-season stage - no canopy growth
                NewCond.canopy_cover = InitCond_CC
                if NewCond.canopy_cover > InitCond_CCxAct:
                    # Update actual maximum canopy cover size during growing
                    # season
                    NewCond.ccx_act = NewCond.canopy_cover

            else:
                # Late-season stage - canopy decline
                # Adjust canopy decline coefficient for difference between actual
                # and potential CCx
                CDCadj = Crop.CDC * ((NewCond.ccx_act + 2.29) / (Crop.CCx + 2.29))
                # Determine new canopy size
                tmp_tCC = tCCadj - Crop.Senescence
                NewCond.canopy_cover = cc_development(
                    NewCond.cc0_adj,
                    NewCond.ccx_act,
                    Crop.CGC,
                    CDCadj,
                    tmp_tCC,
                    "Decline",
                    NewCond.ccx_act,
                )

            # Check for crop growth termination
            if (NewCond.canopy_cover < 0.001) and (InitCond_CropDead == False):
                # Crop has died
                NewCond.canopy_cover = 0
                NewCond.crop_dead = True

        ## Canopy senescence due to water stress (actual) ##
        if tCCadj >= Crop.Emergence:
            if (tCCadj < Crop.Senescence) or (InitCond_tEarlySen > 0):
                # Check for early canopy senescence  due to severe water
                # stress.
                if (water_stress_coef.sen < 1) and (InitCond_ProtectedSeed == False):

                    # Early canopy senescence
                    NewCond.premat_senes = True
                    if InitCond_tEarlySen == 0:
                        # No prior early senescence
                        NewCond.ccx_early_sen = InitCond_CC

                    # Increment early senescence gdd counter
                    NewCond.t_early_sen = InitCond_tEarlySen + dtCC
                    # Adjust canopy decline coefficient for water stress
                    beta = False

                    water_stress_coef = Ksw()
                    water_stress_coef.exp, water_stress_coef.sto, water_stress_coef.sen, water_stress_coef.pol, water_stress_coef.sto_lin = water_stress(
                        Crop.p_up,
                        Crop.p_lo,
                        Crop.ETadj,
                        Crop.beta,
                        Crop.fshape_w,
                        NewCond.t_early_sen,
                        root_zone_depletion,
                        taw,
                        et0,
                        beta,
                    )

                    # water_stress_coef = water_stress(Crop, NewCond, root_zone_depletion, taw, et0, beta)
                    if water_stress_coef.sen > 0.99999:
                        CDCadj = 0.0001
                    else:
                        CDCadj = (1 - (water_stress_coef.sen ** 8)) * Crop.CDC

                    # Get new canpy cover size after senescence
                    if NewCond.ccx_early_sen < 0.001:
                        CCsen = 0
                    else:
                        # Get time required to reach canopy_cover at end of previous day, given
                        # CDCadj
                        tReq = (np.log(1 + (1 - InitCond_CC / NewCond.ccx_early_sen) / 0.05)) / (
                            (CDCadj * 3.33) / (NewCond.ccx_early_sen + 2.29)
                        )
                        # Calculate gdd's for canopy decline
                        tmp_tCC = tReq + dtCC
                        # Determine new canopy size
                        CCsen = NewCond.ccx_early_sen * (
                            1
                            - 0.05
                            * (
                                np.exp(tmp_tCC * ((CDCadj * 3.33) / (NewCond.ccx_early_sen + 2.29)))
                                - 1
                            )
                        )
                        if CCsen < 0:
                            CCsen = 0

                    # Update canopy cover size
                    if tCCadj < Crop.Senescence:
                        # Limit canopy_cover to CCx
                        if CCsen > Crop.CCx:
                            CCsen = Crop.CCx

                        # canopy_cover cannot be greater than value on previous day
                        NewCond.canopy_cover = CCsen
                        if NewCond.canopy_cover > InitCond_CC:
                            NewCond.canopy_cover = InitCond_CC

                        # Update maximum canopy cover size during growing
                        # season
                        NewCond.ccx_act = NewCond.canopy_cover
                        # Update CC0 if current canopy_cover is less than initial canopy
                        # cover size at planting
                        if NewCond.canopy_cover < Crop.CC0:
                            NewCond.cc0_adj = NewCond.canopy_cover
                        else:
                            NewCond.cc0_adj = Crop.CC0

                    else:
                        # Update canopy_cover to account for canopy cover senescence due
                        # to water stress
                        if CCsen < NewCond.canopy_cover:
                            NewCond.canopy_cover = CCsen

                    # Check for crop growth termination
                    if (NewCond.canopy_cover < 0.001) and (InitCond_CropDead == False):
                        # Crop has died
                        NewCond.canopy_cover = 0
                        NewCond.crop_dead = True

                else:
                    # No water stress
                    NewCond.premat_senes = False
                    if (tCCadj > Crop.Senescence) and (InitCond_tEarlySen > 0):
                        # Rewatering of canopy in late season
                        # Get new values for CCx and CDC
                        tmp_tCC = tCCadj - dtCC - Crop.Senescence
                        CCXadj, CDCadj = update_CCx_CDC(InitCond_CC, Crop.CDC, Crop.CCx, tmp_tCC)
                        NewCond.ccx_act = CCXadj
                        # Get new canopy_cover value for end of current day
                        tmp_tCC = tCCadj - Crop.Senescence
                        NewCond.canopy_cover = cc_development(
                            NewCond.cc0_adj, CCXadj, Crop.CGC, CDCadj, tmp_tCC, "Decline", CCXadj
                        )
                        # Check for crop growth termination
                        if (NewCond.canopy_cover < 0.001) and (InitCond_CropDead == False):
                            NewCond.canopy_cover = 0
                            NewCond.crop_dead = True

                    # Reset early senescence counter
                    NewCond.t_early_sen = 0

                # Adjust CCx for effects of withered canopy
                if NewCond.canopy_cover > InitCond_CCxW:
                    NewCond.ccx_w = NewCond.canopy_cover

        ## Calculate canopy size adjusted for micro-advective effects ##
        # Check to ensure potential canopy_cover is not slightly lower than actual
        if NewCond.canopy_cover_ns < NewCond.canopy_cover:
            NewCond.canopy_cover_ns = NewCond.canopy_cover
            if tCCadj < Crop.CanopyDevEnd:
                NewCond.ccx_act_ns = NewCond.canopy_cover_ns

        # Actual (with water stress)
        NewCond.canopy_cover_adj = (1.72 * NewCond.canopy_cover) - (NewCond.canopy_cover ** 2) + (0.3 * (NewCond.canopy_cover ** 3))
        # Potential (without water stress)
        NewCond.canopy_cover_adj_ns = (
            (1.72 * NewCond.canopy_cover_ns) - (NewCond.canopy_cover_ns ** 2) + (0.3 * (NewCond.canopy_cover_ns ** 3))
        )

    else:
        # No canopy outside growing season - set various values to zero
        NewCond.canopy_cover = 0
        NewCond.canopy_cover_adj = 0
        NewCond.canopy_cover_ns = 0
        NewCond.canopy_cover_adj_ns = 0
        NewCond.ccx_w = 0
        NewCond.ccx_act = 0
        NewCond.ccx_w_ns = 0
        NewCond.ccx_act_ns = 0

    return NewCond

