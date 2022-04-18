

import os
import numpy as np
from ..entities.totalAvailableWater import TAWClass
from ..entities.moistureDepletion import DrClass
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
        _, Dr.Zt, Dr.Rz, TAW.Zt, TAW.Rz, _,_,_,_,_,_, = root_zone_water(
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
        Ksw_Exp, Ksw_Sto, Ksw_Sen, Ksw_Pol, Ksw_StoLin = water_stress(
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
        (Kst_PolH,Kst_PolC) = temperature_stress(Crop, Tmax, Tmin)
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
                    NewCond.Fpre = HIadj_pre_anthesis(NewCond.B,
                                                NewCond.B_NS,
                                                NewCond.CC,
                                                Crop.dHI_pre)

                # Determine adjustment for crop pollination failure
                if Crop.CropType == 3:  # Adjustment only for fruit/grain crops
                    if (HIt > 0) and (HIt <= Crop.FloweringCD):

                        NewCond.Fpol = HIadj_pollination(
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
                    NewCond.Fpost) = HIadj_post_anthesis(NewCond.DelayedCDs,
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