import os

if __name__ != "__main__":
    if os.getenv("DEVELOPMENT"):
        from .root_zone_water import root_zone_water
    else:
        from .solution_root_zone_water import root_zone_water

else:
   from .root_zone_water import root_zone_water
   



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
    Crop, prof, Soil_zTop, growing_season, Rain, Runoff):
    """
    Function to get irrigation depth for current day



    <a href="../pdfs/ac_ref_man_1.pdf#page=40" target="_blank">Reference Manual: irrigation description</a> (pg. 31-32)


    *Arguments:*


    `InitCond`: `InitialCondition` : InitCond object containing model paramaters

    `IrrMngt`: `IrrMngtStruct`: jit class object containing irrigation management paramaters

    `Crop`: `Crop` : Crop object containing Crop paramaters

    `Soil`: `Soil` : Soil object containing soil paramaters

    `growing_season`: `bool` : is growing season (True or Flase)

    `Rain`: `float` : daily precipitation mm

    `Runoff`: `float` : surface runoff on current day


    *Returns:*


    `NewCond`: `InitialCondition` : InitCond object containing updated model paramaters

    `Irr`: `float` : Irrigaiton applied on current day mm

"""
    ## Store intial conditions for updating ##
    # NewCond = InitCond

    ## Determine irrigation depth (mm/day) to be applied ##
    if growing_season == True:
        # Calculate root zone water content and depletion
        # TAW_ = TAW()
        # Dr_ = Dr()
        # thRZ = RootZoneWater()
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
        ) = root_zone_water(
            prof,
            float(NewCond_Zroot),
            NewCond_th,
            Soil_zTop,
            float(Crop.Zmin),
            Crop.Aer,
        )
        # WrAct,Dr_,TAW_,thRZ = root_zone_water(prof,float(NewCond.z_root),NewCond.th,Soil_zTop,float(Crop.Zmin),Crop.Aer)
        # Use root zone depletions and taw only for triggering irrigation
        Dr = Dr_Rz
        taw = TAW_Rz

        # Determine adjustment for inflows and outflows on current day #
        if thRZ_Act > thRZ_FC:
            rootdepth = max(NewCond_Zroot, Crop.Zmin)
            AbvFc = (thRZ_Act - thRZ_FC) * 1000 * rootdepth
        else:
            AbvFc = 0

        WCadj = NewCond_Tpot + NewCond_Epot - Rain + Runoff - AbvFc

        NewCond_Depletion = Dr + WCadj
        NewCond_TAW = taw

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
        #             assert 1 ==2, f'somethings gone wrong in irrigation method:{IrrMngt.irrigation_method}'

        Irr = max(0, Irr)

    elif growing_season == False:
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

