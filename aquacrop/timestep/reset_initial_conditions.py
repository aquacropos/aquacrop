import numpy as np
import pandas as pd

from ..initialize.calculate_HI_linear import calculate_HI_linear
from ..initialize.calculate_HIGC import calculate_HIGC


def reset_initial_conditions(ClockStruct, InitCond, ParamStruct, weather):

    """
    Function to reset initial model conditions for start of growing
    season (when running model over multiple seasons)

    *Arguments:*\n

    `ClockStruct` : `ClockStructClass` :  model time paramaters

    `InitCond` : `InitCondClass` :  containing current model paramaters

    `weather`: `np.array` :  weather data for simulation period


    *Returns:*

    `InitCond` : `InitCondClass` :  containing reset model paramaters



    """

    # Extract crop type
    # TODO: This is necessary?
    CropType = ParamStruct.CropChoices[ClockStruct.season_counter]

    # Extract structures for updating
    Soil = ParamStruct.Soil
    crop = ParamStruct.Seasonal_Crop_List[ClockStruct.season_counter]
    FieldMngt = ParamStruct.FieldMngt
    CO2 = ParamStruct.CO2
    CO2_data = ParamStruct.CO2data

    # Reset counters
    InitCond.AgeDays = 0
    InitCond.AgeDays_NS = 0
    InitCond.AerDays = 0
    InitCond.IrrCum = 0
    InitCond.DelayedGDDs = 0
    InitCond.DelayedCDs = 0
    InitCond.PctLagPhase = 0
    InitCond.tEarlySen = 0
    InitCond.GDDcum = 0
    InitCond.DaySubmerged = 0
    InitCond.IrrNetCum = 0
    InitCond.DAP = 0

    InitCond.AerDaysComp = np.zeros(int(Soil.nComp))

    # Reset states
    # States
    InitCond.PreAdj = False
    InitCond.CropMature = False
    InitCond.CropDead = False
    InitCond.Germination = False
    InitCond.PrematSenes = False
    InitCond.HarvestFlag = False

    # Harvest index
    # HI
    InitCond.Stage = 1
    InitCond.Fpre = 1
    InitCond.Fpost = 1
    InitCond.fpost_dwn = 1
    InitCond.fpost_upp = 1

    InitCond.HIcor_Asum = 0
    InitCond.HIcor_Bsum = 0
    InitCond.Fpol = 0
    InitCond.sCor1 = 0
    InitCond.sCor2 = 0

    # Growth stage
    InitCond.GrowthStage = 0

    # Transpiration
    InitCond.TrRatio = 1

    # crop growth
    InitCond.rCor = 1

    InitCond.CC = 0
    InitCond.CCadj = 0
    InitCond.CC_NS = 0
    InitCond.CCadj_NS = 0
    InitCond.B = 0
    InitCond.B_NS = 0
    InitCond.HI = 0
    InitCond.HIadj = 0
    InitCond.CCxAct = 0
    InitCond.CCxAct_NS = 0
    InitCond.CCxW = 0
    InitCond.CCxW_NS = 0
    InitCond.CCxEarlySen = 0
    InitCond.CCprev = 0
    InitCond.ProtectedSeed = 0

    # Update CO2 concentration ##
    # Get CO2 concentration

    if ParamStruct.CO2concAdj is not None:
        CO2.current_concentration = ParamStruct.CO2concAdj
    else:
        Yri = pd.DatetimeIndex([ClockStruct.step_start_time]).year[0]
        CO2.current_concentration = CO2_data.loc[Yri]
    # Get CO2 weighting factor for first year
    CO2conc = CO2.current_concentration
    CO2ref = CO2.ref_concentration
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
        if (FieldMngt.Bunds) and (FieldMngt.zBund > 0.001):
            # Get initial storage between surface bunds
            InitCond.SurfaceStorage = min(FieldMngt.BundWater, FieldMngt.zBund)
        else:
            # No surface bunds
            InitCond.SurfaceStorage = 0

    # Update crop parameters (if in GDD mode)
    if crop.CalendarType == 2:
        # Extract weather data for upcoming growing season
        weather_df = weather[
            weather[:, 4] >= ClockStruct.planting_dates[ClockStruct.season_counter]
        ]

        Tmin = weather_df[:, 0]
        Tmax = weather_df[:, 1]

        # Calculate GDD's
        if crop.GDDmethod == 1:
            Tmean = (Tmax + Tmin) / 2
            Tmean[Tmean > crop.Tupp] = crop.Tupp
            Tmean[Tmean < crop.Tbase] = crop.Tbase
            GDD = Tmean - crop.Tbase
        elif crop.GDDmethod == 2:
            Tmax[Tmax > crop.Tupp] = crop.Tupp
            Tmax[Tmax < crop.Tbase] = crop.Tbase
            Tmin[Tmin > crop.Tupp] = crop.Tupp
            Tmin[Tmin < crop.Tbase] = crop.Tbase
            Tmean = (Tmax + Tmin) / 2
            GDD = Tmean - crop.Tbase
        elif crop.GDDmethod == 3:
            Tmax[Tmax > crop.Tupp] = crop.Tupp
            Tmax[Tmax < crop.Tbase] = crop.Tbase
            Tmin[Tmin > crop.Tupp] = crop.Tupp
            Tmean = (Tmax + Tmin) / 2
            Tmean[Tmean < crop.Tbase] = crop.Tbase
            GDD = Tmean - crop.Tbase

        GDDcum = np.cumsum(GDD)

        assert (
            GDDcum[-1] > crop.Maturity
        ), f"not enough growing degree days in simulation ({GDDcum[-1]}) to reach maturity ({crop.Maturity})"

        crop.MaturityCD = np.argmax((GDDcum > crop.Maturity)) + 1

        assert crop.MaturityCD < 365, "crop will take longer than 1 year to mature"

        # 1. GDD's from sowing to maximum canopy cover
        crop.MaxCanopyCD = (GDDcum > crop.MaxCanopy).argmax() + 1
        # 2. GDD's from sowing to end of vegetative growth
        crop.CanopyDevEndCD = (GDDcum > crop.CanopyDevEnd).argmax() + 1
        # 3. Calendar days from sowing to start of yield formation
        crop.HIstartCD = (GDDcum > crop.HIstart).argmax() + 1
        # 4. Calendar days from sowing to end of yield formation
        crop.HIendCD = (GDDcum > crop.HIend).argmax() + 1
        # 5. Duration of yield formation in calendar days
        crop.YldFormCD = crop.HIendCD - crop.HIstartCD
        if crop.CropType == 3:
            # 1. Calendar days from sowing to end of flowering
            FloweringEnd = (GDDcum > crop.FloweringEnd).argmax() + 1
            # 2. Duration of flowering in calendar days
            crop.FloweringCD = FloweringEnd - crop.HIstartCD
        else:
            crop.FloweringCD = -999

        # Update harvest index growth coefficient
        crop = calculate_HIGC(crop)

        # Update day to switch to linear HI build-up
        if crop.CropType == 3:
            # Determine linear switch point and HIGC rate for fruit/grain crops
           crop.tLinSwitch, crop.dHILinear = calculate_HI_linear(
                crop.YldFormCD, crop.HIini, crop.HI0, crop.HIGC
            )

        else:
            # No linear switch for leafy vegetable or root/tiber crops
            crop.tLinSwitch = 0
            crop.dHILinear = 0.0

    # Update global variables
    ParamStruct.Seasonal_Crop_List[ClockStruct.season_counter] = crop
    ParamStruct.CO2 = CO2

    return InitCond, ParamStruct
