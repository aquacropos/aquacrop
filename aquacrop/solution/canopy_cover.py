
import os
import numpy as np

from ..entities.totalAvailableWater import TAWClass
from ..entities.moistureDepletion import DrClass

from ..entities.waterStressCoefficients import  KswClass
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
        _, Dr.Zt, Dr.Rz, TAW.Zt, TAW.Rz, _,_,_,_,_,_ = root_zone_water(
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
        Ksw.Exp, Ksw.Sto, Ksw.Sen, Ksw.Pol, Ksw.StoLin = water_stress(
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
                NewCond.CC_NS = cc_development(
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
                NewCond.CC_NS = cc_development(
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
                    NewCond.CC = cc_development(
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
                            NewCond.CC = cc_development(
                                Crop.CC0, Crop.CCx, Crop.CGC, Crop.CDC, tmp_tCC, "Growth", Crop.CCx
                            )
                        else:

                            # Determine time required to reach CC on previous,
                            # day, given CGCAdj value
                            tReq = cc_required_time(
                                InitCond_CC, NewCond.CC0adj, CCXadj, CGCadj, Crop.CDC, "CGC"
                            )
                            if tReq > 0:

                                # Calclate GDD's for canopy growth
                                tmp_tCC = tReq + dtCC
                                # Determine new canopy size
                                NewCond.CC = cc_development(
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
                    NewCond.CC = cc_development(
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
                NewCond.CC = cc_development(
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
                    Ksw.Exp, Ksw.Sto, Ksw.Sen, Ksw.Pol, Ksw.StoLin = water_stress(
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
                        CCXadj, CDCadj = update_CCx_CDC(InitCond_CC, Crop.CDC, Crop.CCx, tmp_tCC)
                        NewCond.CCxAct = CCXadj
                        # Get new CC value for end of current day
                        tmp_tCC = tCCadj - Crop.Senescence
                        NewCond.CC = cc_development(
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

