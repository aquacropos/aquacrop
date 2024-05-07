import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC
# temporary name for compiled module
cc = CC("solution_biomass_accumulation")
cc.verbose = False


try:
    from ..entities.crop import CropStructNT_type_sig
except:
    from entities.crop import CropStructNT_type_sig

from typing import NamedTuple, Tuple


@cc.export("biomass_accumulation", (CropStructNT_type_sig,i8,i8,f8,f8,f8,f8,f8,f8,f8,b1,f8,f8,f8,f8))
def biomass_accumulation(
    Crop: NamedTuple,
    NewCond_DAP: int,
    NewCond_DelayedCDs: int,
    NewCond_HIref: float,
    NewCond_PctLagPhase: float,
    NewCond_B: float,
    NewCond_B_NS: float,
    Tr: float,
    TrPot: float,
    et0: float,
    growing_season: bool,
    NewCond_StressSFadjNEW: float,
    NewCond_StressSFadjpre: float,
    NewCond_Tr_ET0_accum: float,
    NewCond_WPadj: float,
    ) -> Tuple[float, float, float, float, float, float, NamedTuple]:
    """
    Function to calculate biomass accumulation

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=107" target="_blank">Reference Manual: biomass accumulaiton</a> (pg. 98-108)


    Arguments:

        Crop (NamedTuple): Crop object

        NewCond_DAP (int): days since planting

        NewCond_DelayedCDs (int): Delayed calendar days

        NewCond_HIref (float): reference harvest index

        NewCond_PctLagPhase (float): percentage of way through early HI development stage

        NewCond_B (float): Current biomass growth

        NewCond_B_NS (float): current no stress biomass growth

        TrPot (float): Daily crop transpiration

        TrPot (float): Daily potential transpiration

        et0 (float): Daily reference evapotranspiration

        growing_season (bool): is Growing season? (True, False)

    Returns:

        NewCond_B (float): new biomass growth

        NewCond_B_NS (float): new (No stress) biomass growth


    """

    ## Store initial conditions in a new structure for updating ##
    # NewCond = InitCond

    ## Calculate biomass accumulation (if in growing season) ##
    if growing_season == True:
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
        if NewCond_StressSFadjNEW==0:
            NewCond_StressSFadjNEW = Crop.sfertstress
            NewCond_StressSFadjpre = Crop.sfertstress
        
        #update parameters according to NewCond_StressSFadjNEW
        TopStress=Crop.TR_ET0_fertstress*(1-NewCond_StressSFadjNEW)

        if NewCond_Tr_ET0_accum<TopStress:
            #adjust for soil fertility stress 
            NewCond_Tr_ET0_accum=NewCond_Tr_ET0_accum+Tr/et0
            Kswp=1-(1-Crop.Kswp)*(NewCond_Tr_ET0_accum/TopStress)*(NewCond_Tr_ET0_accum/TopStress)
        else:
            Kswp=1-(1-Crop.Kswp)

        NewCond_WPadj=Kswp*WPadj

        # Calculate biomass accumulation on current day
        # No water stress
        dB_NS = Kswp*WPadj * (TrPot / et0)
        # With water stress
        dB = Kswp*WPadj * (Tr / et0)
        if np.isnan(dB) == True:
            dB = 0

        # Update biomass accumulation
        NewCond_B = NewCond_B + dB
        NewCond_B_NS = NewCond_B_NS + dB_NS
        
        #update NewCond_StressSFadjNEW based on B
        loc_=np.argmin(np.abs(Crop.sf_es[0:100]-Crop.sfertstress))
        FracBiomassPotSF=Crop.relbio_es[loc_]

        try:
            BioAdj=FracBiomassPotSF+FracBiomassPotSF-NewCond_B/(Crop.Bio_top[NewCond_DAP]*WPadj)
        except:
            BioAdj=FracBiomassPotSF
        NewCond_B_NS=Crop.Bio_top[NewCond_DAP]*WPadj*FracBiomassPotSF
        
        if BioAdj>=1 or Crop.sfertstress==0 :
            NewCond_StressSFadjNEW=0
        else:
            if BioAdj<=0.0001:
                NewCond_StressSFadjNEW=0.8
            else:
                loc_=np.argmin(np.abs(Crop.relbio_es[0:100]-BioAdj))
                NewCond_StressSFadjNEW=Crop.sf_es[loc_]
                if NewCond_StressSFadjNEW<0:
                    NewCond_StressSFadjNEW= Crop.sfertstress
                if NewCond_StressSFadjNEW>0.8:
                    NewCond_StressSFadjNEW=0.8
                if NewCond_StressSFadjNEW>Crop.sfertstress:
                    NewCond_StressSFadjNEW=Crop.sfertstress
                    
                if Crop.CropType== 3 and Crop.Determinant==1 and NewCond_DAP-NewCond_DelayedCDs>=Crop.CanopyDevEndCD:
                    if NewCond_StressSFadjNEW<NewCond_StressSFadjpre:
                        NewCond_StressSFadjNEW=NewCond_StressSFadjpre
                    if NewCond_StressSFadjNEW>Crop.sfertstress:
                        NewCond_StressSFadjNEW=Crop.sfertstress
        
        NewCond_StressSFadjpre = NewCond_StressSFadjNEW

        #update parameters according to NewCond_StressSFadjNEW
        loc_=np.argmin(np.abs(Crop.sf_es[0:100]-NewCond_StressSFadjNEW))
        
        #need tp return crop to update crop outside the function, but also need to pass the new value to NewCpnd and then read from NewCond for day+1, new for seperated version

        Crop=Crop._replace(Ksccx=Crop.Ksccx_es[loc_],Ksexpf=Crop.Ksexpf_es[loc_],Kswp=Crop.Kswp_es[loc_],fcdecline=Crop.fcdecline_es[loc_])

        if Crop.Ksccx<1 or Crop.Ksexpf<1:
            Crop=Crop._replace(MaxCanopyCD = round(Crop.EmergenceCD+(np.log((0.25*Crop.CCx*Crop.Ksccx*Crop.CCx*Crop.Ksccx/Crop.CC0)
                                                                        /(Crop.CCx*Crop.Ksccx-(0.98*Crop.CCx*Crop.Ksccx)))/Crop.CGC_CD/Crop.Ksexpf)))
            if Crop.MaxCanopyCD>Crop.CanopyDevEndCD:
                while Crop.MaxCanopyCD>Crop.CanopyDevEndCD and Crop.Ksexpf<1:
                    Crop=Crop._replace(Ksexpf=Crop.Ksexpf+0.01)
                    Crop=Crop._replace(MaxCanopyCD = round(Crop.EmergenceCD+(np.log((0.25*Crop.CCx*Crop.Ksccx*Crop.CCx*Crop.Ksccx/Crop.CC0)
                                                                    /(Crop.CCx*Crop.Ksccx-(0.98*Crop.CCx*Crop.Ksccx)))/Crop.CGC_CD/Crop.Ksexpf)))
                while Crop.MaxCanopyCD>Crop.CanopyDevEndCD and Crop.CCx*Crop.Ksccx>0.1 and Crop.Ksccx>0.5:
                    Crop=Crop._replace(Ksccx=Crop.Ksccx-0.01)
                    Crop=Crop._replace(MaxCanopyCD = round(Crop.EmergenceCD+(np.log((0.25*Crop.CCx*Crop.Ksccx*Crop.CCx*Crop.Ksccx/Crop.CC0)
                                                                    /(Crop.CCx*Crop.Ksccx-(0.98*Crop.CCx*Crop.Ksccx)))/Crop.CGC_CD/Crop.Ksexpf)))
        
        
    else:
        # No biomass accumulation outside of growing season
        NewCond_B = 0
        NewCond_B_NS = 0
        NewCond_Tr_ET0_accum=0
        NewCond_StressSFadjNEW = Crop.sfertstress
        NewCond_StressSFadjpre = Crop.sfertstress

    return (NewCond_B,
            NewCond_B_NS,
            NewCond_StressSFadjNEW,
            NewCond_StressSFadjpre,
            NewCond_Tr_ET0_accum,
            NewCond_WPadj,
            Crop,)

if __name__ == "__main__":
    cc.compile()
