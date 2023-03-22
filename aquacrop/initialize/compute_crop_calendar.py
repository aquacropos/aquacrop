import numpy as np
import pandas as pd

from ..entities.modelConstants import ModelConstants
from typing import TYPE_CHECKING

from .calculate_HIGC import calculate_HIGC
from .calculate_HI_linear import calculate_HI_linear

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.crop import Crop
    from pandas import DatetimeIndex, DataFrame


def compute_crop_calendar(
    crop: "Crop",
    clock_struct_planting_dates: "DatetimeIndex",
    clock_struct_simulation_start_date: str,
    clock_struct_time_span: "DatetimeIndex",
    weather_df: "DataFrame",
    ParamStruct:"ParamStruct",
) -> "Crop":
    """
    Function to compute additional parameters needed to define crop phenological calendar

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=28" target="_blank">Reference Manual</a> (pg. 19-20)


    Arguments:

        crop (Crop):  Crop object containing crop paramaters

        clock_struct_planting_dates (DatetimeIndex):  list of planting dates

        clock_struct_simulation_start_date (str):  sim start date

        clock_struct_time_span (DatetimeIndex):  all dates between sim start and end dates

        weather_df (DataFrame):  weather data for simulation period


    Returns:

        crop (Crop): updated Crop object



    """

    if len(clock_struct_planting_dates) == 0:
        plant_year = pd.DatetimeIndex([clock_struct_simulation_start_date]).year[0]
        if (
            pd.to_datetime(str(plant_year) + "/" + crop.planting_date)
            < clock_struct_simulation_start_date
        ):
            pl_date = str(plant_year + 1) + "/" + crop.planting_date
        else:
            pl_date = str(plant_year) + "/" + crop.planting_date
    else:
        pl_date = clock_struct_planting_dates[0]

    # Define crop calendar mode
    Mode = crop.CalendarType

    # Calculate variables %%
    if Mode == 1:  # Growth in calendar days

        # Time from sowing to end of vegatative growth period
        if crop.Determinant == 1:
            crop.CanopyDevEndCD = round(crop.HIstartCD + (crop.FloweringCD / 2))
        else:
            crop.CanopyDevEndCD = crop.SenescenceCD

        # Time from sowing to 10% canopy cover (non-stressed conditions)
        crop.Canopy10PctCD = round(
            crop.EmergenceCD + (np.log(0.1 / crop.CC0) / crop.CGC_CD)
        )

        # Time from sowing to maximum canopy cover (non-stressed conditions)
        crop.MaxCanopyCD = round(
            crop.EmergenceCD
            + (
                np.log(
                    (0.25 * crop.CCx * crop.CCx / crop.CC0)
                    / (crop.CCx - (0.98 * crop.CCx))
                )
                / crop.CGC_CD
            )
        )

        # Time from sowing to end of yield_ formation
        crop.HIendCD = crop.HIstartCD + crop.YldFormCD

        # Duplicate calendar values (needed to minimise if
        # statements when switching between gdd and CD runs)
        crop.Emergence = crop.EmergenceCD
        crop.Canopy10Pct = crop.Canopy10PctCD
        crop.MaxRooting = crop.MaxRootingCD
        crop.Senescence = crop.SenescenceCD
        crop.Maturity = crop.MaturityCD
        crop.MaxCanopy = crop.MaxCanopyCD
        crop.CanopyDevEnd = crop.CanopyDevEndCD
        crop.HIstart = crop.HIstartCD
        crop.HIend = crop.HIendCD
        crop.YldForm = crop.YldFormCD
        if crop.CropType == 3:
            crop.FloweringEndCD = crop.HIstartCD + crop.FloweringCD
            # crop.FloweringEndCD = crop.FloweringEnd
            # crop.FloweringCD = crop.Flowering
        else:
            crop.FloweringEnd = ModelConstants.NO_VALUE
            crop.FloweringEndCD = ModelConstants.NO_VALUE
            crop.FloweringCD = ModelConstants.NO_VALUE

        # Check if converting crop calendar to gdd mode
        if crop.SwitchGDD == 1:
            #             # Extract weather data for first growing season that crop is planted
            #             for i,n in enumerate(ParamStruct.CropChoices):
            #                 if n == crop.Name:
            #                     idx = i
            #                     break
            #                 else:
            #                     idx = -1
            #             assert idx > -1

            date_range = pd.date_range(pl_date, clock_struct_time_span[-1])
            weather_df = weather_df.copy()
            weather_df.index = weather_df.Date
            weather_df = weather_df.loc[date_range]
            temp_min = weather_df.MinTemp
            temp_max = weather_df.MaxTemp

            # Calculate gdd's
            if crop.GDDmethod == 1:

                Tmean = (temp_max + temp_min) / 2
                Tmean = Tmean.clip(lower=crop.Tbase, upper=crop.Tupp)
                gdd = Tmean - crop.Tbase

            elif crop.GDDmethod == 2:

                temp_max = temp_max.clip(lower=crop.Tbase, upper=crop.Tupp)
                temp_min = temp_min.clip(lower=crop.Tbase, upper=crop.Tupp)
                Tmean = (temp_max + temp_min) / 2
                gdd = Tmean - crop.Tbase

            elif crop.GDDmethod == 3:

                temp_max = temp_max.clip(lower=crop.Tbase, upper=crop.Tupp)
                temp_min = temp_min.clip(upper=crop.Tupp)
                Tmean = (temp_max + temp_min) / 2
                Tmean = Tmean.clip(lower=crop.Tbase)
                gdd = Tmean - crop.Tbase

            gdd_cum = np.cumsum(gdd)
            # Find gdd equivalent for each crop calendar variable
            # 1. gdd's from sowing to emergence
            crop.Emergence = gdd_cum.iloc[int(crop.EmergenceCD)]
            # 2. gdd's from sowing to 10# canopy cover
            crop.Canopy10Pct = gdd_cum.iloc[int(crop.Canopy10PctCD)]
            # 3. gdd's from sowing to maximum rooting
            crop.MaxRooting = gdd_cum.iloc[int(crop.MaxRootingCD)]
            # 4. gdd's from sowing to maximum canopy cover
            crop.MaxCanopy = gdd_cum.iloc[int(crop.MaxCanopyCD)]
            # 5. gdd's from sowing to end of vegetative growth
            crop.CanopyDevEnd = gdd_cum.iloc[int(crop.CanopyDevEndCD)]
            # 6. gdd's from sowing to senescence
            crop.Senescence = gdd_cum.iloc[int(crop.SenescenceCD)]
            # 7. gdd's from sowing to maturity
            crop.Maturity = gdd_cum.iloc[int(crop.MaturityCD)]
            # 8. gdd's from sowing to start of yield_ formation
            crop.HIstart = gdd_cum.iloc[int(crop.HIstartCD)]
            # 9. gdd's from sowing to start of yield_ formation
            crop.HIend = gdd_cum.iloc[int(crop.HIendCD)]
            # 10. Duration of yield_ formation (gdd's)
            crop.YldForm = crop.HIend - crop.HIstart

            # 11. Duration of flowering (gdd's) - (fruit/grain crops only)
            if crop.CropType == 3:
                # gdd's from sowing to end of flowering
                crop.FloweringEnd = gdd_cum.iloc[int(crop.FloweringEndCD)]
                # Duration of flowering (gdd's)
                crop.Flowering = crop.FloweringEnd - crop.HIstart

            # Convert CGC to gdd mode
            # crop.CGC_CD = crop.CGC
            crop.CGC = (
                np.log(
                    (((0.98 * crop.CCx) - crop.CCx) * crop.CC0)
                    / (-0.25 * (crop.CCx**2))
                )
            ) / (-(crop.MaxCanopy - crop.Emergence))

            # Convert CDC to gdd mode
            # crop.CDC_CD = crop.CDC
            tCD = crop.MaturityCD - crop.SenescenceCD
            if tCD <= 0:
                tCD = 1

            CCi = crop.CCx * (1 - 0.05 * (np.exp((crop.CDC_CD / crop.CCx) * tCD) - 1))
            if CCi < 0:
                CCi = 0

            tGDD = crop.Maturity - crop.Senescence
            if tGDD <= 0:
                tGDD = 5

            crop.CDC = (crop.CCx / tGDD) * np.log(1 + ((1 - CCi / crop.CCx) / 0.05))
            # Set calendar type to gdd mode
            crop.CalendarType = 2

        else:
            crop.CDC = crop.CDC_CD
            crop.CGC = crop.CGC_CD

        # print(crop.__dict__)
    elif Mode == 2:
        # Growth in growing degree days
        # Time from sowing to end of vegatative growth period
        if crop.Determinant == 1:
            crop.CanopyDevEnd = round(crop.HIstart + (crop.Flowering / 2))
        else:
            crop.CanopyDevEnd = crop.Senescence

        # Time from sowing to 10# canopy cover (non-stressed conditions)
        crop.Canopy10Pct = round(crop.Emergence + (np.log(0.1 / crop.CC0) / crop.CGC))

        # Time from sowing to maximum canopy cover (non-stressed conditions)
        crop.MaxCanopy = round(crop.Emergence+(np.log((0.25*crop.CCx*crop.Ksccx*crop.CCx*crop.Ksccx/crop.CC0)
                                                                    /(crop.CCx*crop.Ksccx-(0.98*crop.CCx*crop.Ksccx)))/crop.CGC/crop.Ksexpf))

        # Time from sowing to end of yield_ formation
        crop.HIend = crop.HIstart + crop.YldForm

        # Time from sowing to end of flowering (if fruit/grain crop)
        if crop.CropType == 3:
            crop.FloweringEnd = crop.HIstart + crop.Flowering

        # Extract weather data for first growing season that crop is planted
        #         for i,n in enumerate(ParamStruct.CropChoices):
        #             if n == crop.Name:
        #                 idx = i
        #                 break
        #             else:
        #                 idx = -1
        #         assert idx> -1
        date_range = pd.date_range(pl_date, clock_struct_time_span[-1])
        weather_df = weather_df.copy()
        weather_df.index = weather_df.Date

        weather_df = weather_df.loc[date_range]
        temp_min = weather_df.MinTemp
        temp_max = weather_df.MaxTemp

        # Calculate gdd's
        if crop.GDDmethod == 1:

            Tmean = (temp_max + temp_min) / 2
            Tmean = Tmean.clip(lower=crop.Tbase, upper=crop.Tupp)
            gdd = Tmean - crop.Tbase

        elif crop.GDDmethod == 2:

            temp_max = temp_max.clip(lower=crop.Tbase, upper=crop.Tupp)
            temp_min = temp_min.clip(lower=crop.Tbase, upper=crop.Tupp)
            Tmean = (temp_max + temp_min) / 2
            gdd = Tmean - crop.Tbase

        elif crop.GDDmethod == 3:

            temp_max = temp_max.clip(lower=crop.Tbase, upper=crop.Tupp)
            temp_min = temp_min.clip(upper=crop.Tupp)
            Tmean = (temp_max + temp_min) / 2
            Tmean = Tmean.clip(lower=crop.Tbase)
            gdd = Tmean - crop.Tbase

        gdd_cum = np.cumsum(gdd).reset_index(drop=True)

        assert (
            gdd_cum.values[-1] > crop.Maturity
        ), f"not enough growing degree days in simulation ({gdd_cum.values[-1]}) to reach maturity ({crop.Maturity})"

        crop.MaturityCD = (gdd_cum > crop.Maturity).idxmax() + 1

        assert crop.MaturityCD < 365, "crop will take longer than 1 year to mature"

        # 1. gdd's from sowing to maximum canopy cover
        crop.MaxCanopyCD = (gdd_cum > crop.MaxCanopy).idxmax() + 1
        # 2. gdd's from sowing to end of vegetative growth
        crop.CanopyDevEndCD = (gdd_cum > crop.CanopyDevEnd).idxmax() + 1
        # 3. Calendar days from sowing to start of yield_ formation
        crop.HIstartCD = (gdd_cum > crop.HIstart).idxmax() + 1
        # 4. Calendar days from sowing to end of yield_ formation
        crop.HIendCD = (gdd_cum > crop.HIend).idxmax() + 1
        # 5. Duration of yield_ formation in calendar days
        crop.YldFormCD = crop.HIendCD - crop.HIstartCD
        
        crop.SenescenceCD = (gdd_cum>crop.Senescence).idxmax()+1
        crop.EmergenceCD = (gdd_cum>crop.Emergence).idxmax()+1
        
        #look unnecessary, but cannot get the same results with AquaCrop-win without it
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
            crop.MaxCanopy=gdd_cum.values[crop.MaxCanopyCD-1]  
        
        if crop.CropType == 3:
            # 1. Calendar days from sowing to end of flowering
            FloweringEnd = (gdd_cum > crop.FloweringEnd).idxmax() + 1
            # 2. Duration of flowering in calendar days
            crop.FloweringCD = FloweringEnd - crop.HIstartCD
        else:
            crop.FloweringCD = ModelConstants.NO_VALUE
        
        
        #soil fertility stress initialization and calibration, basically calculate the whole crop growth under ideal conditions (no water stress)  

        #This part can be optimized(shorten) later for the final version
        
        #print(crop.EmergenceCD)
        #print(crop.MaxCanopy)
        #print(crop.MaxCanopyCD)
        #print(crop.CanopyDevEndCD)

        #calculate the normalized Tr for soil fertility stress, it is a theritically one, could be derived without simulation 
        CCx=crop.CCx#*crop.Ksccx
        CGC=crop.CGC#*crop.Ksexpf
        
        Half_CCx = round(crop.Emergence+(np.log(0.5*CCx/crop.CC0)/CGC))
            
            
        Full_CCx = round(crop.Emergence+(np.log((0.25*CCx*CCx/crop.CC0)
                                                                    /(CCx-(0.98*CCx)))/CGC))
        
        if gdd_cum.values[-1] < crop.Maturity:
            Half_CCx = Half_CCx*gdd_cum.values[-1]/crop.Maturity
            Full_CCx = Full_CCx*gdd_cum.values[-1]/crop.Maturity

        Half_CCxCD = (gdd_cum>Half_CCx).idxmax()+1
        Full_CCxCD = (gdd_cum>Full_CCx).idxmax()+1
        #Full_CCxCD=crop.MaxCanopyCD

        Ks_Tr=[]# cold stress 
        Kc_Tr=[]# crop transpiration coefficient with soil fertility stress 
        Ksc_Total=[]
        max_cc=0

        for day_ in range(1,np.min([crop.MaturityCD+1,len(gdd_cum)])):
            #cold tress
            GDD_=gdd_cum.values[day_]-gdd_cum.values[day_-1]
            
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

            if gdd_cum.values[day_]<crop.Emergence:
                CC=0
                Kctr=crop.Kcb
            
            elif gdd_cum.values[day_] <= Half_CCx:
                CC=crop.CC0*np.exp((gdd_cum.values[day_]-crop.Emergence)*CGC)
                if CC>CCx/2:
                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                Kctr=crop.Kcb
                
                max_cc=CC

            elif gdd_cum.values[day_] > Half_CCx and gdd_cum.values[day_] <= Full_CCx:
                CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                Kctr=crop.Kcb
                
                max_cc=CC
                 
            elif gdd_cum.values[day_] > Full_CCx and gdd_cum.values[day_-5] <= Full_CCx:
            
                if gdd_cum.values[day_]<crop.CanopyDevEnd:
                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                    max_cc=CC
                else:
                    CC=max_cc
                    
                Kctr=crop.Kcb

            elif gdd_cum.values[day_-5] > Full_CCx and gdd_cum.values[day_] <= crop.Senescence:
                
                if gdd_cum.values[day_]<crop.CanopyDevEnd:
                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                    max_cc=CC
                else:
                    CC=max_cc

                Kctr=crop.Kcb-(day_-Full_CCxCD-5)*(crop.fage / 100)*max_cc

            elif gdd_cum.values[day_] > crop.Senescence and gdd_cum.values[day_] <= crop.Maturity:
                CC_adj=max_cc
                
                CDC = crop.CDC*((CC_adj+2.29)/(crop.CCx+2.29))
                CC=CC_adj*(1-0.05*(np.exp(3.33*CDC*(gdd_cum.values[day_]-crop.Senescence)/(CC_adj+2.29))-1))
                Kctr=(crop.Kcb-(day_-Full_CCxCD-5)*(crop.fage / 100)*max_cc)*(CC/max_cc)**crop.a_Tr
                
            if CC<=0:
                CC=0
            CC_star=1.72*CC-CC*CC+0.3*CC*CC*CC

            #print(CC)
            #print(ParamStruct.CO2.CurrentConc)
            try:
                CO2conc=ParamStruct.CO2.current_concentration 
            except:
                CO2conc=ParamStruct.CO2.co2_data_processed.iloc[0]
            Kc_TrCo2=1            
            if CO2conc>369.41:
                Kc_TrCo2=1-0.05*(CO2conc-369.41)/(550-369.41)
            
            Kc_Tr_=CC_star*Kctr*Kc_TrCo2
            #print(day_)
            #print(CC_star)
            #print(Kctr)
            #print(Kc_TrCo2)
            #print(Kc_Tr_)
            Kc_Tr.append(Kc_Tr_)

            Ksc_Total.append(Kc_Tr_*KsCold)
        
        crop.TR_ET0_fertstress=np.sum(Ksc_Total[:])
        #print(Ksc_Total[:])
        #print(crop.MaturityCD)
        
        crop.HIGC = calculate_HIGC(
            crop.YldFormCD,
            crop.HI0,
            crop.HIini,
        )
        if crop.CropType == 3:
            # Determine linear switch point and HIGC rate for fruit/grain crops
            crop.tLinSwitch, crop.dHILinear = calculate_HI_linear(
                crop.YldFormCD, crop.HIini, crop.HI0, crop.HIGC
            )
        else:
            # No linear switch for leafy vegetable or root/tiber crops
            crop.tLinSwitch = 0
            crop.dHILinear = 0.
        
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
        
        
        def Biomas_ini_es(Bio_mul,TopStress,Ksccx_temp,Ksexpf_temp,fcdecline_temp,Kswp_temp):
            CCx=crop.CCx*Ksccx_temp
        
            CGC=crop.CGC*Ksexpf_temp
            
            Half_CCx = round(crop.Emergence+(np.log(0.5*CCx/crop.CC0)/CGC))
            
            
            Full_CCx = round(crop.Emergence+(np.log((0.25*CCx*CCx/crop.CC0)
                                                                        /(CCx-(0.98*CCx)))/CGC))
            
            if gdd_cum.values[-1] < crop.Maturity:
                Half_CCx = Half_CCx*gdd_cum.values[-1]/crop.Maturity
                Full_CCx = Full_CCx*gdd_cum.values[-1]/crop.Maturity
    
            Half_CCxCD = (gdd_cum>Half_CCx).idxmax()+1
            Full_CCxCD = (gdd_cum>Full_CCx).idxmax()+1

            Kc_Tr_es=[]# crop transpiration coefficient with soil fertility stress 
            max_cc=0

            for day_ in range(1,np.min([crop.MaturityCD+1,len(gdd_cum)])):

                # crop transpiration coefficient
                if gdd_cum.values[day_]<crop.Emergence:
                    CC=0
                    Kctr=crop.Kcb
                
                elif gdd_cum.values[day_] <= Half_CCx:
                    CC=crop.CC0*np.exp((gdd_cum.values[day_]-crop.Emergence)*CGC)
                    if CC>CCx/2:
                        CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                    Kctr=crop.Kcb
                    
                    max_cc=CC

                elif gdd_cum.values[day_] > Half_CCx and gdd_cum.values[day_] <= Full_CCx:
                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                    Kctr=crop.Kcb
                    
                    max_cc=CC
                     
                elif gdd_cum.values[day_] > Full_CCx and gdd_cum.values[day_-5] <= Full_CCx:
                    
                    if gdd_cum.values[day_]<crop.CanopyDevEnd:
                        CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                        max_cc=CC
                    else:
                        CC=max_cc

                    if crop.SenescenceCD>Full_CCxCD:
                        CC=max_cc-fcdecline_temp*(day_-Full_CCxCD)*(day_-Full_CCxCD)/(crop.SenescenceCD-Full_CCxCD)
                    Kctr=crop.Kcb
                    if CC<0:
                        CC=0

                elif gdd_cum.values[day_-5] > Full_CCx and gdd_cum.values[day_] <= crop.Senescence:
                    
                    if gdd_cum.values[day_]<crop.CanopyDevEnd:
                        CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                        max_cc=CC
                    else:
                        CC=max_cc


                    if crop.SenescenceCD>Full_CCxCD:
                        CC=max_cc-fcdecline_temp*(day_-Full_CCxCD)*(day_-Full_CCxCD)/(crop.SenescenceCD-Full_CCxCD)
                    Kctr=crop.Kcb-(day_-Full_CCxCD-5)*(crop.fage / 100)*max_cc
                    if CC<0:
                        CC=0

                elif gdd_cum.values[day_] > crop.Senescence and gdd_cum.values[day_] <= crop.Maturity:
                    if crop.SenescenceCD>Full_CCxCD:
                        CC_fs=max_cc-fcdecline_temp*(day_-Full_CCxCD)*(day_-Full_CCxCD)/(crop.SenescenceCD-Full_CCxCD)

                        CC_adj=max_cc-fcdecline_temp*(crop.SenescenceCD-Full_CCxCD)
                    else:
                        CC_fs=max_cc
                        CC_adj=max_cc
                    CDC = crop.CDC*((CC_adj+2.29)/(crop.CCx+2.29))
                    CC=CC_adj*(1-0.05*(np.exp(3.33*CDC*(gdd_cum.values[day_]-crop.Senescence)/(CC_adj+2.29))-1))
                    
                    #if CC_fs<CC:#not in AquaCrop v6
                    #    CC=CC_fs
                    if CC<0:
                        CC=0
                    
                    Kctr=(crop.Kcb-(day_-Full_CCxCD-5)*(crop.fage / 100)*max_cc)*(CC/max_cc)**crop.a_Tr
                
                #print(Full_CCxCD)
                #print(Kc_Tr_es)
                #print(Kc_Tr)
                
                if CC<=0:
                    CC=0
                CC_star=1.72*CC-CC*CC+0.3*CC*CC*CC
                
                #print(ParamStruct.CO2.CurrentConc)
                try:
                    CO2conc=ParamStruct.CO2.current_concentration 
                except:
                    CO2conc=ParamStruct.CO2.co2_data_processed.iloc[0]
                Kc_TrCo2=1            
                if CO2conc>369.41:
                    Kc_TrCo2=1-0.05*(CO2conc-369.41)/(550-369.41)
                
                Kc_Tr_=CC_star*Kctr*Kc_TrCo2
                #if Kc_Tr_==0:
                #    print("Zero"+str(day_))
                #    print(CC_star)
                #    print(Kctr)
                Kc_Tr_es.append(Kc_Tr_)
  
            Bio_cur=0
            Curstress=0
            #print(len(Kc_Tr_es))
            #print(len(Kc_Tr))
            #print(len(Bio_mul))
            for i in range(len(Kc_Tr_es)):
                if Curstress<TopStress:
                    Curstress+=Kc_Tr_es[i]*Ks_Tr[i]
                    Kswp_=1-(1-Kswp_temp)*(Curstress/TopStress)*(Curstress/TopStress)
                else:
                    Kswp_=1-(1-Kswp_temp)
                Bio_cur+=Kswp_*Kc_Tr_es[i]*Ks_Tr[i]*Bio_mul[i]
            
            return Bio_cur
        
        
        if crop.need_calib==1:
            
            crop.HIGC = calculate_HIGC(
            crop.YldFormCD,
            crop.HI0,
            crop.HIini,
        )
            if crop.CropType == 3:
                # Determine linear switch point and HIGC rate for fruit/grain crops
                crop.tLinSwitch, crop.dHILinear = calculate_HI_linear(
                crop.YldFormCD, crop.HIini, crop.HI0, crop.HIGC
            )
            else:
                # No linear switch for leafy vegetable or root/tiber crops
                crop.tLinSwitch = 0
                crop.dHILinear = 0.

            TopStress=crop.TR_ET0_fertstress*crop.RelativeBio
            
            Bio_top=0
            Bio_mul=[]
            #print('TOtal')
            #print(len(Ksc_Total))
            for i_ in range(len(Ksc_Total)):
                #print(i_)
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
                        Bio_mul.append(1-(1-crop.WPy/100)*fswitch)
                        
                    else:
                        Bio_top+= Ksc_Total[i_]
                        Bio_mul.append(1)
                else:
                    Bio_top+= Ksc_Total[i_]
                    Bio_mul.append(1)
            
            #initialze parameters
            adj_flag=True
            Ksccx_temp=crop.Ksccx_in
            L123=crop.SenescenceCD
            L12=crop.MaxCanopyCD
            kk_=0#avoid periodic loop
            while adj_flag and kk_<100:
                kk_+=1

                CCx_temp=crop.CCx*Ksccx_temp
                if crop.fcdecline_in==0:
                    CCxfinal=0.92*crop.CCx
                elif crop.fcdecline_in==1:
                    CCxfinal=0.85*crop.CCx
                else:
                    CCxfinal=0.77*crop.CCx
                    
                if L123>L12:
                    fcdecline_temp=(1-Ksccx_temp)*(crop.CCx-CCxfinal)/(L123-L12)
                    if fcdecline_temp>0.01:
                        fcdecline_temp=0.009
                else:
                    fcdecline_temp=0
                
                Ksexpf_temp=np.round((1-(1-Ksccx_temp)*0.6)*100)/100
                Kswp_temp=np.round((1-(1-Ksccx_temp)*0.5)*100)/100 
                
                full_temp = round(crop.EmergenceCD+(np.log((0.25*crop.CCx*Ksccx_temp*crop.CCx*Ksccx_temp/crop.CC0)
                                                                    /(crop.CCx*Ksccx_temp-(0.98*crop.CCx*Ksccx_temp)))/crop.CGC_CD/Ksexpf_temp))
                

                if full_temp>crop.CanopyDevEndCD:

                    while Ksexpf_temp<0.99 and full_temp>crop.CanopyDevEndCD:
                        Ksexpf_temp=Ksexpf_temp+0.01
                        full_temp = round(crop.EmergenceCD+(np.log((0.25*crop.CCx*Ksccx_temp*crop.CCx*Ksccx_temp/crop.CC0)
                                                                    /(crop.CCx*Ksccx_temp-(0.98*crop.CCx*Ksccx_temp)))/crop.CGC_CD/Ksexpf_temp))
                                                            
                    while full_temp>crop.CanopyDevEndCD and crop.CCx*Ksccx_temp>0.1 and Ksccx_temp>0.5:
                        Ksccx_temp=Ksccx_temp-0.01
                        full_temp = round(crop.EmergenceCD+(np.log((0.25*crop.CCx*Ksccx_temp*crop.CCx*Ksccx_temp/crop.CC0)
                                                                    /(crop.CCx*Ksccx_temp-(0.98*crop.CCx*Ksccx_temp)))/crop.CGC_CD/Ksexpf_temp))

                adj_wp=True
                k_=0#avoid periodic loop
                while adj_wp and k_<100:
                    #print('wp')
                    k_+=1
                    bio_cur=Biomas_ini_es(Bio_mul,TopStress,Ksccx_temp,Ksexpf_temp,fcdecline_temp,Kswp_temp)
                    #print(Kswp_temp)
                    #print(int(bio_cur/Bio_top*100))
                    if int(bio_cur/Bio_top*100)==int(crop.RelativeBio*100):
                        adj_flag=False
                        adj_wp=False
                    elif bio_cur/Bio_top<crop.RelativeBio:
                        Kswp_temp=Kswp_temp+0.01
                    else:
                        Kswp_temp=Kswp_temp-0.01
                    
                    if Kswp_temp<0.3-0.001:
                        Kswp_temp=Kswp_temp+0.01
                        adj_wp=False
                    if Kswp_temp>0.99+0.001:
                        Kswp_temp=Kswp_temp-0.01
                        adj_wp=False
                        
                    #print(Ksccx_temp)
                    #print(Ksexpf_temp)
                    #print(Kswp_temp)
                    #print(int(bio_cur/Bio_top*100))
                    #print(bio_cur)
                    #print(Bio_top)
                    #print(int(crop.RelativeBio*100))
                
                if adj_flag:
                    adj_Ksexpf=True
                    k_=0
                    while adj_Ksexpf and k_<100:
                        k_+=1
                        bio_cur=Biomas_ini_es(Bio_mul,TopStress,Ksccx_temp,Ksexpf_temp,fcdecline_temp,Kswp_temp)
                        if int(bio_cur/Bio_top*100)==int(crop.RelativeBio*100):
                            adj_flag=False
                            adj_Ksexpf=False
                        elif bio_cur/Bio_top<crop.RelativeBio:
                            Ksexpf_temp=Ksexpf_temp+0.01
                        else:
                            Ksexpf_temp=Ksexpf_temp-0.01
                        
                        full_temp = round(crop.EmergenceCD+(np.log((0.25*crop.CCx*Ksccx_temp*crop.CCx*Ksccx_temp/crop.CC0)
                                                                    /(crop.CCx*Ksccx_temp-(0.98*crop.CCx*Ksccx_temp)))/crop.CGC_CD/Ksexpf_temp))
                
                        if full_temp>crop.CanopyDevEndCD:
                            while Ksexpf_temp<0.99 and full_temp>crop.CanopyDevEndCD:
                                Ksexpf_temp=Ksexpf_temp+0.01
                                full_temp = round(crop.EmergenceCD+(np.log((0.25*crop.CCx*Ksccx_temp*crop.CCx*Ksccx_temp/crop.CC0)
                                                                    /(crop.CCx*Ksccx_temp-(0.98*crop.CCx*Ksccx_temp)))/crop.CGC_CD/Ksexpf_temp))
                            while full_temp>crop.CanopyDevEndCD and crop.CCx*Ksccx_temp>0.1 and Ksccx_temp>0.5:
                                Ksccx_temp=Ksccx_temp-0.01
                                full_temp = round(crop.EmergenceCD+(np.log((0.25*crop.CCx*Ksccx_temp*crop.CCx*Ksccx_temp/crop.CC0)
                                                                    /(crop.CCx*Ksccx_temp-(0.98*crop.CCx*Ksccx_temp)))/crop.CGC_CD/Ksexpf_temp))

                            adj_Ksexpf=False
                        
                        if (1-Ksexpf_temp)<0.1*(1-Ksccx_temp)-0.001:
                            Ksexpf_temp=Ksexpf_temp-0.01
                            adj_Ksexpf=False
                        if (1-Ksexpf_temp)>0.8*(1-Ksccx_temp)+0.001:
                            Ksexpf_temp=Ksexpf_temp+0.01
                            adj_Ksexpf=False
                            
                if adj_flag:
                    adj_fcdecline=True
                    k_=0
                    while adj_fcdecline and k_<100:
                        k_+=1
                        #print('fcdecline')
                        bio_cur=Biomas_ini_es(Bio_mul,TopStress,Ksccx_temp,Ksexpf_temp,fcdecline_temp,Kswp_temp)

                        if int(bio_cur/Bio_top*100)==int(crop.RelativeBio*100):
                            adj_flag=False
                            adj_fcdecline=False
                        elif bio_cur/Bio_top<crop.RelativeBio:
                            fcdecline_temp=fcdecline_temp-0.0001
                        else:
                            fcdecline_temp=fcdecline_temp+0.0001
                        
                        if fcdecline_temp<0.0001-0.00001:
                            fcdecline_temp=fcdecline_temp+0.0001
                            adj_fcdecline=False
                        if fcdecline_temp>0.009+0.00001:
                            fcdecline_temp=fcdecline_temp-0.0001
                            adj_fcdecline=False
                        
                if adj_flag:

                    if bio_cur/Bio_top<crop.RelativeBio:
                        Ksccx_temp=Ksccx_temp+0.01
                    else:
                        Ksccx_temp=Ksccx_temp-0.01
                        
                    if Ksccx_temp<0:
                        Ksccx_temp=Ksccx_temp+0.01
                        adj_flag=False
                    if Ksccx_temp>1:
                        Ksccx_temp=Ksccx_temp-0.01
                        adj_flag=False
                
                #print(int(bio_cur/Bio_top*100))
                #print(int(crop.RelativeBio*100))
                #print(adj_flag)
                CCx=crop.CCx*Ksccx_temp
        
                CGC=crop.CGC*Ksexpf_temp
   
                Full_CCx = round(crop.Emergence+(np.log((0.25*CCx*CCx/crop.CC0)
                                                                            /(CCx-(0.98*CCx)))/CGC))
                if gdd_cum.values[-1] < crop.Maturity:

                    Full_CCx = Full_CCx*gdd_cum.values[-1]/crop.Maturity
        
                Full_CCxCD = (gdd_cum>Full_CCx).idxmax()+1
                L12=Full_CCxCD
                
                #if L12>L123:
                #    print("L12>L123")


            if (int(bio_cur/Bio_top*100)==int(crop.RelativeBio*100)) or (kk_>=100 and np.abs(int(bio_cur/Bio_top*100)-int(crop.RelativeBio*100))<5):
            #accept some errors when exit because of maximum loop, in theory, the above can ensure ==

                crop.Ksccx_in=Ksccx_temp
                crop.Ksccx_es[0]=Ksccx_temp
                crop.Ksexpf_es[0]=Ksexpf_temp
                crop.fcdecline_es[0]=fcdecline_temp
                crop.Kswp_es[0]=Kswp_temp
                crop.sf_es[0]=1-bio_cur/Bio_top
                crop.relbio_es[0]=bio_cur/Bio_top
                
                def get_shape(ks,sf):
                    if ks>1-sf:
                        up_=50
                        low_=0
                    else:
                        up_=0
                        low_=-50
                    flag_=True
                    while flag_:
                        shape_=(up_+low_)/2
                        ks_=1-(np.exp(sf*shape_)-1)/(np.exp(shape_)-1)
                        
                        if np.abs(ks_-ks)<0.0001 or np.abs(up_-low_)<0.0001:
                            flag_=False
                        elif ks_<ks:
                            low_=shape_
                        else:
                            up_=shape_
                    return shape_
                
                Ksccx_shape=get_shape(Ksccx_temp,crop.sf_es[0])
                Ksexpf_shape=get_shape(Ksexpf_temp,crop.sf_es[0])
                Kswp_shape=get_shape(Kswp_temp,crop.sf_es[0])
                fcdecline_shape=get_shape(1-fcdecline_temp*100,crop.sf_es[0])
                
                for i in range(0,100):
                    crop.sf_es[i+1]=i/100
                    Ksccx_temp=1-(np.exp(crop.sf_es[i+1]*Ksccx_shape)-1)/(np.exp(Ksccx_shape)-1)
                    Ksexpf_temp=1-(np.exp(crop.sf_es[i+1]*Ksexpf_shape)-1)/(np.exp(Ksexpf_shape)-1)
                    Kswp_temp=1-(np.exp(crop.sf_es[i+1]*Kswp_shape)-1)/(np.exp(Kswp_shape)-1)
                    fcdecline_temp=(np.exp(crop.sf_es[i+1]*fcdecline_shape)-1)/(np.exp(fcdecline_shape)-1)/100
                    bio_temp=Biomas_ini_es(Bio_mul,crop.TR_ET0_fertstress*(1-crop.sf_es[i+1]),Ksccx_temp,Ksexpf_temp,fcdecline_temp,Kswp_temp)

                    crop.Ksccx_es[i+1]=Ksccx_temp
                    crop.Ksexpf_es[i+1]=Ksexpf_temp
                    crop.fcdecline_es[i+1]=fcdecline_temp
                    crop.Kswp_es[i+1]=Kswp_temp
                    crop.relbio_es[i+1]=bio_temp/Bio_top


        if crop.need_calib==2:
            
            crop.HIGC = calculate_HIGC(
            crop.YldFormCD,
            crop.HI0,
            crop.HIini,
        )
            if crop.CropType == 3:
                # Determine linear switch point and HIGC rate for fruit/grain crops
                crop.tLinSwitch, crop.dHILinear = calculate_HI_linear(
                crop.YldFormCD, crop.HIini, crop.HI0, crop.HIGC
            )
            else:
                # No linear switch for leafy vegetable or root/tiber crops
                crop.tLinSwitch = 0
                crop.dHILinear = 0.

            TopStress=crop.TR_ET0_fertstress*crop.RelativeBio
            
            possible_flag=1
            crop.Ksccx_in=crop.Ksccx_in-0.01
            ind_=0
            
            while possible_flag:
                crop.Ksccx_in=crop.Ksccx_in+0.01
                CCx=crop.CCx*crop.Ksccx_in
                
                Bio_top=0
                Bio_mul=[]
                for i_ in range(len(Ksc_Total)):
                    #print(Bio_top)
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
                            Bio_mul.append(1-(1-crop.WPy/100)*fswitch)
                        else:
                            Bio_top+= Ksc_Total[i_]
                            Bio_mul.append(1)
                    else:
                        Bio_top+= Ksc_Total[i_]
                        Bio_mul.append(1)


                for Ksexpf in np.arange(1,101,2)/100:
                    for fcdecline in np.arange(0,100,2)/100/100:
                        
                        #Ksexpf=0.79
                        #fcdecline=0.0006
                    
                        
                        CGC=crop.CGC*Ksexpf
                        Half_CCx = round(crop.Emergence+(np.log(0.5*CCx/crop.CC0)/CGC))
            
            
                        Full_CCx = round(crop.Emergence+(np.log((0.25*CCx*CCx/crop.CC0)
                                                                                    /(CCx-(0.98*CCx)))/CGC))
                        
                        if gdd_cum.values[-1] < crop.Maturity:
                            Half_CCx = Half_CCx*gdd_cum.values[-1]/crop.Maturity
                            Full_CCx = Full_CCx*gdd_cum.values[-1]/crop.Maturity
                
                        Half_CCxCD = (gdd_cum>Half_CCx).idxmax()+1
                        Full_CCxCD = (gdd_cum>Full_CCx).idxmax()+1
                        
                        if Full_CCxCD>=crop.SenescenceCD:
                            break
                        
                        #Full_CCxCD=crop.MaxCanopyCD

                        Kc_Tr_es=[]# crop transpiration coefficient with soil fertility stress 
                        max_cc=0

                        for day_ in range(1,np.min([crop.MaturityCD+1,len(gdd_cum)])):

                            # crop transpiration coefficient
                            if gdd_cum.values[day_]<crop.Emergence:
                                CC=0
                                Kctr=crop.Kcb
                            
                            elif gdd_cum.values[day_] <= Half_CCx:
                                CC=crop.CC0*np.exp((gdd_cum.values[day_]-crop.Emergence)*CGC)
                                if CC>CCx/2:
                                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                                Kctr=crop.Kcb
                                
                                max_cc=CC
            
                            elif gdd_cum.values[day_] > Half_CCx and gdd_cum.values[day_] <= Full_CCx:
                                CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                                Kctr=crop.Kcb
                                
                                max_cc=CC
                                 
                            elif gdd_cum.values[day_] > Full_CCx and gdd_cum.values[day_-5] <= Full_CCx:
                            
                                if gdd_cum.values[day_]<crop.CanopyDevEnd:
                                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                                    max_cc=CC
                                else:
                                    CC=max_cc
                            
                                if crop.SenescenceCD>Full_CCxCD:
                                    CC=max_cc-fcdecline_temp*(day_-Full_CCxCD)*(day_-Full_CCxCD)/(crop.SenescenceCD-Full_CCxCD)
                                Kctr=crop.Kcb
                                if CC<0:
                                    CC=0
            
                            elif gdd_cum.values[day_-5] > Full_CCx and gdd_cum.values[day_] <= crop.Senescence:
                            
                                if gdd_cum.values[day_]<crop.CanopyDevEnd:
                                    CC=CCx-0.25*CCx*CCx/crop.CC0*np.exp(-(gdd_cum.values[day_]-crop.Emergence)*CGC)
                                    max_cc=CC
                                else:
                                    CC=max_cc
                            
                                if crop.SenescenceCD>Full_CCxCD:
                                    CC=max_cc-fcdecline_temp*(day_-Full_CCxCD)*(day_-Full_CCxCD)/(crop.SenescenceCD-Full_CCxCD)
                                Kctr=crop.Kcb-(day_-Full_CCxCD-5)*(crop.fage / 100)*max_cc
                                if CC<0:
                                    CC=0
            
                            elif gdd_cum.values[day_] > crop.Senescence and gdd_cum.values[day_] <= crop.Maturity:
                                if crop.SenescenceCD>Full_CCxCD:
                                    CC_fs=max_cc-fcdecline_temp*(day_-Full_CCxCD)*(day_-Full_CCxCD)/(crop.SenescenceCD-Full_CCxCD)
            
                                    CC_adj=max_cc-fcdecline_temp*(crop.SenescenceCD-Full_CCxCD)
                                else:
                                    CC_fs=max_cc
                                    CC_adj=max_cc
                                CDC = crop.CDC*((CC_adj+2.29)/(crop.CCx+2.29))
                                CC=CC_adj*(1-0.05*(np.exp(3.33*CDC*(gdd_cum.values[day_]-crop.Senescence)/(CC_adj+2.29))-1))
                                
                                #if CC_fs<CC:
                                #    CC=CC_fs
                                if CC<0:
                                    CC=0
                                
                                Kctr=(crop.Kcb-(day_-Full_CCxCD-5)*(crop.fage / 100)*max_cc)*(CC/max_cc)**crop.a_Tr
            
                            if CC<=0:
                                CC=0
                            CC_star=1.72*CC-CC*CC+0.3*CC*CC*CC
                            
                            #print(ParamStruct.CO2.CurrentConc)
                            try:
                                CO2conc=ParamStruct.CO2.current_concentration 
                            except:
                                CO2conc=ParamStruct.CO2.co2_data_processed.iloc[0]
                            Kc_TrCo2=1            
                            if CO2conc>369.41:
                                Kc_TrCo2=1-0.05*(CO2conc-369.41)/(550-369.41)
                            
                            Kc_Tr_=CC_star*Kctr*Kc_TrCo2
                            #if Kc_Tr_==0:
                            #    print("Zero"+str(day_))
                            #    print(CC_star)
                            #    print(Kctr)
                            Kc_Tr_es.append(Kc_Tr_)
                        
                        Bio_up=0
                        for i in range(len(Kc_Tr_es)):
                            Bio_up+=Kc_Tr_es[i]*Ks_Tr[i]*Bio_mul[i]
                            #print(Bio_up)
                            
                        if int(Bio_up/Bio_top*100)<int(crop.RelativeBio*100):
                            #pass
                            break
                            
                        Kswp_l=0
                        Kswp_u=1
                        con_=True
                        
                        while con_:
                            
                            Kswp=(Kswp_l+Kswp_u)/2
                            #Kswp=0.6

                            Bio_cur=0
                            Curstress=0
                            
                            for i in range(len(Kc_Tr_es)):
                                if Curstress<TopStress:
                                    Curstress+=Kc_Tr_es[i]*Ks_Tr[i]
                                    Kswp_=1-(1-Kswp)*(Curstress/TopStress)*(Curstress/TopStress)
                                else:
                                    Kswp_=1-(1-Kswp)
                                Bio_cur+=Kswp_*Kc_Tr_es[i]*Ks_Tr[i]*Bio_mul[i]
                                #print(Bio_cur)
                                

                            if int(Bio_cur/Bio_top*100)==crop.RelativeBio*100:
                                con_=False
                                possible_flag=0
                                crop.Ksexpf_es[ind_]=Ksexpf
                                crop.fcdecline_es[ind_]=fcdecline
                                crop.Kswp_es[ind_]=Kswp

                                ind_+=1
                                
                                break
                            else:
                                if Bio_cur/Bio_top>crop.RelativeBio:
                                    Kswp_u=Kswp
                                else:
                                    Kswp_l=Kswp

    return crop
