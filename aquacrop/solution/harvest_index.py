

import os
import numpy as np
from ..entities.totalAvailableWater import TAW
from ..entities.moistureDepletion import Dr
from ..entities.waterStressCoefficients import  KswNT
from ..entities.temperatureStressCoefficients import   KstNT

if __name__ != "__main__":
    if os.getenv("DEVELOPMENT"):
        from .water_stress import water_stress
        from .root_zone_water import root_zone_water
        from .temperature_stress import temperature_stress
        from .HIadj_pre_anthesis import HIadj_pre_anthesis
        from .HIadj_post_anthesis import HIadj_post_anthesis
        from .HIadj_pollination import HIadj_pollination
    else:
        from .solution_water_stress import water_stress
        from .solution_root_zone_water import root_zone_water
        from .solution_temperature_stress import temperature_stress
        from .solution_HIadj_pre_anthesis import HIadj_pre_anthesis
        from .solution_HIadj_post_anthesis import HIadj_post_anthesis
        from .solution_HIadj_pollination import HIadj_pollination
else:
    from .water_stress import water_stress
    from .root_zone_water import root_zone_water
    from .temperature_stress import temperature_stress
    from .HIadj_pre_anthesis import HIadj_pre_anthesis
    from .HIadj_post_anthesis import HIadj_post_anthesis
    from .HIadj_pollination import HIadj_pollination





def harvest_index(prof, Soil_zTop, Crop, InitCond, et0, temp_max, temp_min, growing_season):

    """
    Function to simulate build up of harvest index


     <a href="../pdfs/ac_ref_man_3.pdf#page=119" target="_blank">Reference Manual: harvest index calculations</a> (pg. 110-126)

    *Arguments:*


    `Soil`: `Soil` : Soil object containing soil paramaters

    `Crop`: `Crop` : Crop object containing Crop paramaters

    `InitCond`: `InitialCondition` : InitCond object containing model paramaters

    `et0`: `float` : reference evapotranspiration on current day

    `temp_max`: `float` : maximum tempature on current day (celcius)

    `temp_min`: `float` : minimum tempature on current day (celcius)

    `growing_season`:: `bool` : is growing season (True or Flase)


    *Returns:*


    `NewCond`: `InitialCondition` : InitCond object containing updated model paramaters



    """

    ## Store initial conditions for updating ##
    NewCond = InitCond

    InitCond_HI = InitCond.harvest_index
    InitCond_HIadj = InitCond.harvest_index_adj
    InitCond_PreAdj = InitCond.pre_adj

    ## Calculate harvest index build up (if in growing season) ##
    if growing_season == True:
        # Calculate root zone water content

        taw = TAW()
        water_root_depletion = Dr()
        # thRZ = RootZoneWater()
        _, water_root_depletion.Zt, water_root_depletion.Rz, taw.Zt, taw.Rz, _,_,_,_,_,_, = root_zone_water(
            prof,
            float(NewCond.z_root),
            NewCond.th,
            Soil_zTop,
            float(Crop.Zmin),
            Crop.Aer,
        )

        # _,water_root_depletion,taw,_ = root_zone_water(Soil_Profile,float(NewCond.z_root),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
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

        # Calculate water stress
        beta = True
        # Ksw = water_stress(Crop, NewCond, water_root_depletion, taw, et0, beta)
        # Ksw = Ksw()
        Ksw_Exp, Ksw_Sto, Ksw_Sen, Ksw_Pol, Ksw_StoLin = water_stress(
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
        Ksw = KswNT(exp=Ksw_Exp, sto=Ksw_Sto, sen=Ksw_Sen, pol=Ksw_Pol, sto_lin=Ksw_StoLin )
        # Calculate temperature stress
        (Kst_PolH,Kst_PolC) = temperature_stress(Crop, temp_max, temp_min)
        Kst = KstNT(PolH=Kst_PolH,PolC=Kst_PolC)
        # Get reference harvest index on current day
        HIi = NewCond.hi_ref

        # Get time for harvest index build-up
        HIt = NewCond.dap - NewCond.delayed_cds - Crop.HIstartCD - 1

        # Calculate harvest index
        if (NewCond.yield_form == True) and (HIt >= 0):
            # print(NewCond.dap)
            # Root/tuber or fruit/grain crops
            if (Crop.CropType == 2) or (Crop.CropType == 3):
                # Detemine adjustment for water stress before anthesis
                if InitCond_PreAdj == False:
                    InitCond.pre_adj = True
                    NewCond.f_pre = HIadj_pre_anthesis(NewCond.biomass,
                                                NewCond.biomass_ns,
                                                NewCond.canopy_cover,
                                                Crop.dHI_pre)

                # Determine adjustment for crop pollination failure
                if Crop.CropType == 3:  # Adjustment only for fruit/grain crops
                    if (HIt > 0) and (HIt <= Crop.FloweringCD):

                        NewCond.f_pol = HIadj_pollination(
                            NewCond.canopy_cover,
                            NewCond.f_pol,
                            Crop.FloweringCD,
                            Crop.CCmin,
                            Crop.exc,
                            Ksw,
                            Kst,
                            HIt,
                        )

                    HImax = NewCond.f_pol * Crop.HI0
                else:
                    # No pollination adjustment for root/tuber crops
                    HImax = Crop.HI0

                # Determine adjustments for post-anthesis water stress
                if HIt > 0:
                    (NewCond.s_cor1,
                    NewCond.s_cor2,
                    NewCond.fpost_upp,
                    NewCond.fpost_dwn,
                    NewCond.f_post) = HIadj_post_anthesis(NewCond.delayed_cds,
                                                        NewCond.s_cor1,
                                                        NewCond.s_cor2,
                                                        NewCond.dap,
                                                        NewCond.f_pre,
                                                        NewCond.canopy_cover,
                                                        NewCond.fpost_upp,
                                                        NewCond.fpost_dwn,
                                                        Crop, 
                                                        Ksw)

                # Limit harvest_index to maximum allowable increase due to pre- and
                # post-anthesis water stress combinations
                HImult = NewCond.f_pre * NewCond.f_post
                if HImult > 1 + (Crop.dHI0 / 100):
                    HImult = 1 + (Crop.dHI0 / 100)

                # Determine harvest index on current day, adjusted for stress
                # effects
                if HImax >= HIi:
                    harvest_index_adj = HImult * HIi
                else:
                    harvest_index_adj = HImult * HImax

            elif Crop.CropType == 1:
                # Leafy vegetable crops - no adjustment, harvest index equal to
                # reference value for current day
                harvest_index_adj = HIi

        else:

            # No build-up of harvest index if outside yield_ formation period
            HIi = InitCond_HI
            harvest_index_adj = InitCond_HIadj

        # Store final values for current time step
        NewCond.harvest_index = HIi
        NewCond.harvest_index_adj = harvest_index_adj

    else:
        # No harvestable crop outside of a growing season
        NewCond.harvest_index = 0
        NewCond.harvest_index_adj = 0

    # print([NewCond.dap , Crop.YldFormCD])
    return NewCond