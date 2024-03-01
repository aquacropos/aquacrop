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
    from aquacrop.entities.crop import Crop

def reset_initial_conditions(
    ClockStruct: "ClockStruct",
    InitCond: "InitialCondition",
    ParamStruct: "ParamStruct",
    weather: "ndarray",
    crop: "Crop") -> Tuple["InitialCondition", "ParamStruct"]:

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
    InitCond.sumET0EarlySen = 0
    InitCond.HIfinal = crop.HI0
    InitCond.DryYield = 0
    InitCond.FreshYield = 0

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
    if CO2conc <= 550:
        # Set weighting factor for CO2
        if CO2conc <= CO2ref:
            fw = 0
        elif CO2conc >= 550:
            fw = 1
        else:
            fw = 1 - ((550 - CO2conc) / (550 - CO2ref))
        # Set fCO2old within the 'if CO2conc <= 550' block:
        fCO2old = (CO2conc / CO2ref) / (
            1
            + (CO2conc - CO2ref)
            * (
                (1 - fw) * crop.bsted
                + fw * ((crop.bsted * crop.fsink) + (crop.bface * (1 - crop.fsink)))
            )
        )
    # New adjusted correction coefficient for CO2 (version 7 of AquaCrop)
    if (CO2conc > CO2ref):
        # Calculate shape factor
        fshape = -4.61824 - 3.43831*crop.fsink - 5.32587*crop.fsink*crop.fsink
        # Determine adjustment for CO2
        if (CO2conc >= 2000):
            fCO2new = 1.58  # Maximum CO2 adjustment 
        else:
            CO2rel = (CO2conc-CO2ref)/(2000-CO2ref)
            fCO2new = 1 + 0.58 * ((np.exp(CO2rel*fshape) - 1)/(np.exp(fshape) - 1))


    # Select adjusted coefficient for CO2
    if (CO2conc <= CO2ref):
        fCO2 = fCO2old
    else:
        fCO2 = fCO2new
        if ((CO2conc <= 550) and (fCO2old < fCO2new)): 
            fCO2 = fCO2old
    

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
        if crop.CropType == 3:
            # 1. Calendar days from sowing to end of flowering
            FloweringEnd = (gdd_cum > crop.FloweringEnd).argmax() + 1
            # 2. Duration of flowering in calendar days
            crop.FloweringCD = FloweringEnd - crop.HIstartCD
        else:
            crop.FloweringCD = ModelConstants.NO_VALUE

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

    # Update global variables
    ParamStruct.Seasonal_Crop_List[ClockStruct.season_counter] = crop

    return InitCond, ParamStruct
