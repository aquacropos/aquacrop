import numpy as np
import pandas as pd

from ..entities.modelConstants import ModelConstants
from ..initialize.calculate_HI_linear import calculate_HI_linear
from ..initialize.calculate_HIGC import calculate_HIGC

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from numpy import ndarray
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.initParamVariables import InitialCondition
    from aquacrop.entities.paramStruct import ParamStruct

def reset_initial_conditions(
    ClockStruct: "ClockStruct",
    InitCond: "InitialCondition",
    ParamStruct: "ParamStruct",
    weather: "ndarray") -> Tuple["InitialCondition", "ParamStruct"]:

    """
    Function to reset initial model conditions for start of growing
    season (when running model over multiple seasons)

    Arguments:

        ClockStruct (ClockStruct):  model time paramaters

        InitCond (InitialCondition):  containing current model paramaters

        ParamStruct (ParamStruct):  containing current model paramaters

        weather (numpy.ndarray):  weather data for simulation period


    Returns:

        InitCond (InitialCondition):  containing reset simulation variables and counters

        ParamStruct (ParamStruct):  contains all model params



    """

    # Extract crop type
    # TODO: This is necessary?
    CropType = ParamStruct.CropChoices[ClockStruct.season_counter]

    # Extract structures for updating
    Soil = ParamStruct.Soil
    crop = ParamStruct.Seasonal_Crop_List[ClockStruct.season_counter]
    FieldMngt = ParamStruct.FieldMngt

    # Reset counters
    InitCond.age_days = 0
    InitCond.age_days_ns = 0
    InitCond.aer_days = 0
    InitCond.irr_cum = 0
    InitCond.delayed_gdds = 0
    InitCond.delayed_cds = 0
    InitCond.pct_lag_phase = 0
    InitCond.t_early_sen = 0
    InitCond.gdd_cum = 0
    InitCond.day_submerged = 0
    InitCond.irr_net_cum = 0
    InitCond.dap = 0

    InitCond.aer_days_comp = np.zeros(int(Soil.nComp))

    # Reset states
    # States
    InitCond.pre_adj = False
    InitCond.crop_mature = False
    InitCond.crop_dead = False
    InitCond.germination = False
    InitCond.premat_senes = False
    InitCond.harvest_flag = False

    # Harvest index
    # harvest_index
    InitCond.stage = 1
    InitCond.f_pre = 1
    InitCond.f_post = 1
    InitCond.fpost_dwn = 1
    InitCond.fpost_upp = 1

    InitCond.h1_cor_asum = 0
    InitCond.h1_cor_bsum = 0
    InitCond.f_pol = 0
    InitCond.s_cor1 = 0
    InitCond.s_cor2 = 0

    # Growth stage
    InitCond.growth_stage = 0

    # Transpiration
    InitCond.tr_ratio = 1

    # crop growth
    InitCond.r_cor = 1

    InitCond.canopy_cover = 0
    InitCond.canopy_cover_adj = 0
    InitCond.canopy_cover_ns = 0
    InitCond.canopy_cover_adj_ns = 0
    InitCond.biomass = 0
    InitCond.biomass_ns = 0
    InitCond.harvest_index = 0
    InitCond.harvest_index_adj = 0
    InitCond.ccx_act = 0
    InitCond.ccx_act_ns = 0
    InitCond.ccx_w = 0
    InitCond.ccx_w_ns = 0
    InitCond.ccx_early_sen = 0
    InitCond.cc_prev = 0
    InitCond.protected_seed = 0

    #add a parameter to record the CCx after consider the decline due to soil-fertility stress
    InitCond.CCx_fertstress = 0
    #add a parameter to record the time to reach ccx_adj (GDD)
    InitCond.CCxadj_dayCD = 0
    #add a parameter to record the accumulated Tr/ET0
    InitCond.Tr_ET0_accum = 0
    InitCond.WPadj=0
    InitCond.StressSFadjNEW = 0
    InitCond.StressSFadjpre = 0

    # Update CO2 concentration ##
    # Get CO2 concentration

    # if user specified constant concentration
    if  ParamStruct.CO2.constant_conc is True:
        if ParamStruct.CO2.current_concentration > 0.:
            CO2conc = ParamStruct.CO2.current_concentration
        else:
            CO2conc = ParamStruct.CO2.co2_data_processed.iloc[0]
    else:
        Yri = pd.DatetimeIndex([ClockStruct.step_start_time]).year[0]
        CO2conc = ParamStruct.CO2.co2_data_processed.loc[Yri]

    ParamStruct.CO2.current_concentration = CO2conc

    # Get CO2 weighting factor for first year
    CO2conc = ParamStruct.CO2.current_concentration
    CO2ref = ParamStruct.CO2.ref_concentration
    
    if CO2conc <= CO2ref:
        fw = 0
    else:
        if CO2conc >= 550:
            fw = 1
        else:
            fw = 1 - ((550 - CO2conc) / (550 - CO2ref))

    # Determine initial adjustment
    fCO2 = (CO2conc / CO2ref) / (
        1
        + (CO2conc - CO2ref)
        * (
            (1 - fw) * crop.bsted
            + fw * ((crop.bsted * crop.fsink) + (crop.bface * (1 - crop.fsink)))
        )
    )

    # Consider crop type
    if crop.WP >= 40:
        # No correction for C4 crops
        ftype = 0
    elif crop.WP <= 20:
        # Full correction for C3 crops
        ftype = 1
    else:
        ftype = (40 - crop.WP) / (40 - 20)

    # Total adjustment
    crop.fCO2 = 1 + ftype * (fCO2 - 1)

    # Reset soil water conditions (if not running off-season)
    if ClockStruct.sim_off_season is False:
        # Reset water content to starting conditions
        InitCond.th = InitCond.thini
        # Reset surface storage
        if (FieldMngt.bunds) and (FieldMngt.z_bund > 0.001):
            # Get initial storage between surface bunds
            InitCond.surface_storage = min(FieldMngt.bund_water, FieldMngt.z_bund)
        else:
            # No surface bunds
            InitCond.surface_storage = 0

    # Update crop parameters (if in gdd mode)
    if crop.CalendarType == 2:
        # Extract weather data for upcoming growing season
        weather_df = weather[
            weather[:, 4] >= ClockStruct.planting_dates[ClockStruct.season_counter]
        ]

        temp_min = weather_df[:, 0]
        temp_max = weather_df[:, 1]

        # Calculate gdd's
        if crop.GDDmethod == 1:
            Tmean = (temp_max + temp_min) / 2
            Tmean[Tmean > crop.Tupp] = crop.Tupp
            Tmean[Tmean < crop.Tbase] = crop.Tbase
            gdd = Tmean - crop.Tbase
        elif crop.GDDmethod == 2:
            temp_max[temp_max > crop.Tupp] = crop.Tupp
            temp_max[temp_max < crop.Tbase] = crop.Tbase
            temp_min[temp_min > crop.Tupp] = crop.Tupp
            temp_min[temp_min < crop.Tbase] = crop.Tbase
            Tmean = (temp_max + temp_min) / 2
            gdd = Tmean - crop.Tbase
        elif crop.GDDmethod == 3:
            temp_max[temp_max > crop.Tupp] = crop.Tupp
            temp_max[temp_max < crop.Tbase] = crop.Tbase
            temp_min[temp_min > crop.Tupp] = crop.Tupp
            Tmean = (temp_max + temp_min) / 2
            Tmean[Tmean < crop.Tbase] = crop.Tbase
            gdd = Tmean - crop.Tbase

        gdd_cum = np.cumsum(gdd)

        assert (
            gdd_cum[-1] > crop.Maturity
        ), f"not enough growing degree days in simulation ({gdd_cum[-1]}) to reach maturity ({crop.Maturity})"

        crop.MaturityCD = np.argmax((gdd_cum > crop.Maturity)) + 1

        assert crop.MaturityCD < 365, "crop will take longer than 1 year to mature"

        # 1. gdd's from sowing to maximum canopy cover
        crop.MaxCanopyCD = (gdd_cum > crop.MaxCanopy).argmax() + 1
        # 2. gdd's from sowing to end of vegetative growth
        crop.CanopyDevEndCD = (gdd_cum > crop.CanopyDevEnd).argmax() + 1
        # 3. Calendar days from sowing to start of yield_ formation
        crop.HIstartCD = (gdd_cum > crop.HIstart).argmax() + 1
        # 4. Calendar days from sowing to end of yield_ formation
        crop.HIendCD = (gdd_cum > crop.HIend).argmax() + 1
        # 5. Duration of yield_ formation in calendar days
        crop.YldFormCD = crop.HIendCD - crop.HIstartCD
        
        #used for soil fertility stress
        crop.SenescenceCD = (gdd_cum>crop.Senescence).argmax()+1
        crop.EmergenceCD = (gdd_cum>crop.Emergence).argmax()+1
        
        #Aquacrop-win has this strage correction for the crop canlendar, otherwise for some cases, the simulation will not be the same, especially when both GDD and CD are available for crops
        if crop.Ksccx<1 or crop.Ksexpf<1:
            if crop.CGC_CD==-1:
                crop.CGC_CD=crop.MaxCanopy/crop.MaxCanopyCD*crop.CGC
            
            crop.MaxCanopyCD = round(crop.EmergenceCD+(np.log((0.25*crop.CCx*crop.Ksccx*crop.CCx*crop.Ksccx/crop.CC0)
                                                                        /(crop.CCx*crop.Ksccx-(0.98*crop.CCx*crop.Ksccx)))/crop.CGC_CD/crop.Ksexpf))

            if crop.MaxCanopyCD>crop.CanopyDevEndCD:
                while crop.MaxCanopyCD>crop.CanopyDevEndCD and crop.Ksexpf<1:
                    crop.Ksexpf=crop.Ksexpf+0.01
                    crop.MaxCanopyCD = round(crop.EmergenceCD+(np.log((0.25*crop.CCx*crop.Ksccx*crop.CCx*crop.Ksccx/crop.CC0)
                                                                    /(crop.CCx*crop.Ksccx-(0.98*crop.CCx*crop.Ksccx)))/crop.CGC_CD/crop.Ksexpf))
                while crop.MaxCanopyCD>crop.CanopyDevEndCD and crop.CCx*crop.Ksccx>0.1 and crop.Ksccx>0.5:
                    crop.Ksccx=crop.Ksccx-0.01
                    crop.MaxCanopyCD = round(crop.EmergenceCD+(np.log((0.25*crop.CCx*crop.Ksccx*crop.CCx*crop.Ksccx/crop.CC0)
                                                                    /(crop.CCx*crop.Ksccx-(0.98*crop.CCx*crop.Ksccx)))/crop.CGC_CD/crop.Ksexpf))
            crop.MaxCanopy=gdd_cum[crop.MaxCanopyCD-1]

        if crop.CropType == 3:
            # 1. Calendar days from sowing to end of flowering
            FloweringEnd = (gdd_cum > crop.FloweringEnd).argmax() + 1
            # 2. Duration of flowering in calendar days
            crop.FloweringCD = FloweringEnd - crop.HIstartCD
        else:
            crop.FloweringCD = ModelConstants.NO_VALUE
        
        
        #calculate the normalized Tr for soil fertility stress, it is a theritically one, could be derived without simulation 
        CCx=crop.CCx#*crop.Ksccx
        CGC=crop.CGC#*crop.Ksexpf
        
        Half_CCx = round(crop.Emergence+(np.log(0.5*CCx/crop.CC0)/CGC))
        Full_CCx = round(crop.Emergence+(np.log((0.25*CCx*CCx/crop.CC0)
                                                                    /(CCx-(0.98*CCx)))/CGC))
        
        
        if gdd_cum[-1] < crop.Maturity:
            Half_CCx = Half_CCx*gdd_cum[-1]/crop.Maturity
            Full_CCx = Full_CCx*gdd_cum[-1]/crop.Maturity

        Half_CCxCD = (gdd_cum>Half_CCx).argmax()+1
        Full_CCxCD = (gdd_cum>Full_CCx).argmax()+1
        
        #Full_CCxCD=crop.MaxCanopyCD

        Ks_Tr=[]# cold stress 
        Kc_Tr=[]# crop transpiration coefficient with soil fertility stress 
        Ksc_Total=[]
        max_cc=0

        for day_ in range(1,np.min([crop.MaturityCD+1,len(gdd_cum)])):
            #cold tress
            GDD_=gdd_cum[day_]-gdd_cum[day_-1]
            
            #copy from solution.py
            if crop.TrColdStress == 0:
            # Cold temperature stress does not affect transpiration
                KsCold = 1
            elif crop.TrColdStress == 1:
                # Transpiration can be affected by cold temperature stress
                if GDD_ >= crop.GDD_up:
                    # No cold temperature stress
                    KsCold = 1
                elif GDD_ <= crop.GDD_lo:
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
                    GDDrel = (GDD_ - crop.GDD_lo) / (crop.GDD_up - crop.GDD_lo)
                    KsCold = (KsTr_up * KsTr_lo) / (
                        KsTr_lo + (KsTr_up - KsTr_lo) * np.exp(-fshapeb * GDDrel)
                    )
                    KsCold = KsCold - KsTr_lo * (1 - GDDrel)
            #record cold stress 
            Ks_Tr.append(KsCold)

            if gdd_cum[day_]<crop.Emergence:
                CC=0
                Kctr=crop.Kcb
            
            elif gdd_cum[day_] <= Half_CCx:
                CC=crop.CC0*np.exp((gdd_cum[day_]-crop.Emergence)*CGC)
                if CC>CCx/2:
                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum[day_]-crop.Emergence)*CGC)
                Kctr=crop.Kcb

                max_cc=CC

            elif gdd_cum[day_] > Half_CCx and gdd_cum[day_] <= Full_CCx:
                CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum[day_]-crop.Emergence)*CGC)
                Kctr=crop.Kcb
                
                max_cc=CC
                 
            elif gdd_cum[day_] > Full_CCx and gdd_cum[day_-5] <= Full_CCx:
                
                if gdd_cum[day_]<crop.CanopyDevEnd:
                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum[day_]-crop.Emergence)*CGC)
                    max_cc=CC
                else:
                    CC=max_cc

                Kctr=crop.Kcb

            elif gdd_cum[day_-5] > Full_CCx and gdd_cum[day_] <= crop.Senescence:
                
                if gdd_cum[day_]<crop.CanopyDevEnd:
                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum[day_]-crop.Emergence)*CGC)
                    max_cc=CC
                else:
                    CC=max_cc
                    
                Kctr=crop.Kcb-(day_-Full_CCxCD-5)*(crop.fage / 100)*max_cc

            elif gdd_cum[day_] > crop.Senescence and gdd_cum[day_] <= crop.Maturity:
                
                CDC = crop.CDC*((max_cc+2.29)/(crop.CCx+2.29))
                CC_adj=max_cc#-crop.fcdecline*(crop.SenescenceCD-Full_CCxCD)#*(day_-Full_CCxCD)/(crop.SenescenceCD-Full_CCxCD)
                CC=CC_adj*(1-0.05*(np.exp(3.33*CDC*(gdd_cum[day_]-crop.Senescence)/(CC_adj+2.29))-1))
                Kctr=(crop.Kcb-(day_-Full_CCxCD-5)*(crop.fage / 100)*max_cc)*(CC/max_cc)**crop.a_Tr
                
            if CC<=0:
                CC=0
            CC_star=1.72*CC-CC*CC+0.3*CC*CC*CC
            
            Kc_TrCo2=1            
            if CO2conc>369.41:
                Kc_TrCo2=1-0.05*(CO2conc-369.41)/(550-369.41)
            
            Kc_Tr_=CC_star*Kctr*Kc_TrCo2
            Kc_Tr.append(Kc_Tr_)

            Ksc_Total.append(Kc_Tr_*KsCold)
        crop.TR_ET0_fertstress=np.sum(Ksc_Total[:])


        # Update harvest index growth coefficient
        crop.HIGC = calculate_HIGC(
            crop.YldFormCD,
            crop.HI0,
            crop.HIini,
        )

        # Update day to switch to linear harvest_index build-up
        if crop.CropType == 3:
            # Determine linear switch point and HIGC rate for fruit/grain crops
            crop.tLinSwitch, crop.dHILinear = calculate_HI_linear(
                crop.YldFormCD, crop.HIini, crop.HI0, crop.HIGC
            )

        else:
            # No linear switch for leafy vegetable or root/tiber crops
            crop.tLinSwitch = 0
            crop.dHILinear = 0.0
        
        #define the maximum biomass in theory    
        Bio_top=0
        for i_ in range(len(Ksc_Total)):
            #print(Bio_top)
            crop.Bio_top[i_]=Bio_top
            if i_>=crop.HIstartCD:

                if ((crop.CropType == 2) or (crop.CropType == 3)):
                
                    if crop.CropType == 2:
                        PctLagPhase_=100
                    else:
                        if (i_-crop.HIstartCD) < crop.tLinSwitch:
                            PctLagPhase_ = 100*((i_-crop.HIstartCD)/crop.tLinSwitch)
                        else:
                            PctLagPhase_=100

                    # Adjust WP for reproductive stage
                    if crop.Determinant == 1:
                        fswitch = PctLagPhase_/100
                    else:
                        if (i_-crop.HIstartCD) < (crop.YldFormCD/3):
                            fswitch = (i_-crop.HIstartCD)/(crop.YldFormCD/3)
                        else:
                            fswitch = 1

                    if fswitch>1:
                        fswitch=1
                        
                    Bio_top+= Ksc_Total[i_]*(1-(1-crop.WPy/100)*fswitch)
                else:
                    Bio_top+= Ksc_Total[i_]
            else:
                Bio_top+= Ksc_Total[i_]
        crop.Bio_top[len(Ksc_Total):len(Ksc_Total)+100]=Bio_top

    # Update global variables
    ParamStruct.Seasonal_Crop_List[ClockStruct.season_counter] = crop

    return InitCond, ParamStruct
