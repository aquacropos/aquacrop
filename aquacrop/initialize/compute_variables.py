import numpy as np
import pandas as pd

from .compute_crop_calendar import compute_crop_calendar
from .calculate_HIGC import calculate_HIGC
from .calculate_HI_linear import calculate_HI_linear
from ..entities.co2 import CO2
from ..entities.crop import CropStruct
from copy import deepcopy
from os.path import dirname, abspath

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from pandas import DataFrame
    from aquacrop.entities.clockStruct import ClockStruct
    from aquacrop.entities.paramStruct import ParamStruct

# print("dirname = ", dirname(dirname(abspath(__file__))))


def compute_variables(
    param_struct: "ParamStruct",
    weather_df: "DataFrame",
    clock_struct: "ClockStruct",
    acfp: str = dirname(dirname(abspath(__file__))),
) -> "ParamStruct":
    """
    Function to compute additional variables needed to run the model eg. CO2
    Creates cropstruct jit class objects

    Arguments:

        param_struct (ParamStruct):  Contains model paramaters

        weather_df (DataFrame):  weather data

        clock_struct (ClockStruct):  time params

        acfp (Path):  path to aquacrop directory containing co2 data

    Returns:

        param_struct (ParamStruct):  updated model params


    """

    if param_struct.water_table == 1:

        param_struct.Soil.add_capillary_rise_params()

    # Calculate readily evaporable water in surface layer
    if param_struct.Soil.adj_rew == 0:
        param_struct.Soil.rew = round(
            (
                1000
                * (
                    param_struct.Soil.profile.th_fc.iloc[0]
                    - param_struct.Soil.profile.th_dry.iloc[0]
                )
                * param_struct.Soil.evap_z_surf
            ),
            2,
        )

    if param_struct.Soil.calc_cn == 1:
        # adjust curve number
        ksat = param_struct.Soil.profile.Ksat.iloc[0]
        if ksat > 864:
            param_struct.Soil.cn = 46
        elif ksat > 347:
            param_struct.Soil.cn = 61
        elif ksat > 36:
            param_struct.Soil.cn = 72
        elif ksat > 0:
            param_struct.Soil.cn = 77

        assert ksat > 0

    for i in range(param_struct.NCrops):

        crop = param_struct.CropList[i]
        # crop.calculate_additional_params()

        # Crop calander
        crop = compute_crop_calendar(
            crop,
            clock_struct.planting_dates,
            clock_struct.simulation_start_date,
            clock_struct.simulation_end_date,
            clock_struct.time_span,
            weather_df,
        )

        # Harvest index param_struct.Seasonal_Crop_List[clock_struct.season_counter].Paramsgrowth coefficient
        crop.HIGC = calculate_HIGC(
            crop.YldFormCD,
            crop.HI0,
            crop.HIini,
        )

        # Days to linear harvest_index switch point
        if crop.CropType == 3:
            # Determine linear switch point and HIGC rate for fruit/grain crops
            crop.tLinSwitch, crop.dHILinear = calculate_HI_linear(
                crop.YldFormCD, crop.HIini, crop.HI0, crop.HIGC
            )
        else:
            # No linear switch for leafy vegetable or root/tiber crops
            crop.tLinSwitch = 0
            crop.dHILinear = 0.0

        param_struct.CropList[i] = crop

    # Calculate WP adjustment factor for elevation in CO2 concentration
    # Load CO2 data
    co2Data = param_struct.CO2.co2_data

    # Years
    start_year, end_year = pd.DatetimeIndex(
        [clock_struct.simulation_start_date, clock_struct.simulation_end_date]
    ).year
    sim_years = np.arange(start_year, end_year + 1)

    # Interpolate data
    CO2conc_interp = np.interp(sim_years, co2Data.year, co2Data.ppm)

    # Store data
    param_struct.CO2.co2_data_processed = pd.Series(CO2conc_interp, index=sim_years)  # maybe get rid of this

    # Get CO2 concentration for first year
    CO2conc = param_struct.CO2.co2_data_processed.iloc[0]

    # param_struct.CO2 = param_struct.co2_concentration_adj

    # if user specified constant concentration
    if  param_struct.CO2.constant_conc is True:
        if param_struct.CO2.current_concentration > 0.:
            CO2conc = param_struct.CO2.current_concentration
        else:
            CO2conc = param_struct.CO2.co2_data_processed.iloc[0]

    param_struct.CO2.current_concentration = CO2conc

    CO2ref = param_struct.CO2.ref_concentration

    # Get CO2 weighting factor for first year
    if CO2conc <= CO2ref:
        fw = 0
    else:
        if CO2conc >= 550:
            fw = 1
        else:
            fw = 1 - ((550 - CO2conc) / (550 - CO2ref))

    # Determine adjustment for each crop in first year of simulation
    for i in range(param_struct.NCrops):
        crop = param_struct.CropList[i]
        # Determine initial adjustment
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
    elif ((CO2conc <= 550) and (fCO2old < fCO2new)):
        fCO2 = fCO2old
    else:
        fCO2 = fCO2new

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

    param_struct.CropList[i] = crop


    # change this later
    if param_struct.NCrops == 1:
        crop_list = [
            deepcopy(param_struct.CropList[0])
            for i in range(len(param_struct.CropChoices))
        ]
        # param_struct.Seasonal_Crop_List = [deepcopy(param_struct.CropList[0]) for i in range(len(param_struct.CropChoices))]

    else:
        crop_list = param_struct.CropList

    # add crop for out of growing season
    # param_struct.Fallow_Crop = deepcopy(param_struct.Seasonal_Crop_List[0])
    Fallow_Crop = deepcopy(crop_list[0])

    param_struct.Seasonal_Crop_List = []
    for crop in crop_list:
        crop_struct = CropStruct()
        for a, v in crop.__dict__.items():
            if hasattr(crop_struct, a):
                crop_struct.__setattr__(a, v)

        param_struct.Seasonal_Crop_List.append(crop_struct)

    fallow_struct = CropStruct()
    for a, v in Fallow_Crop.__dict__.items():
        if hasattr(fallow_struct, a):
            fallow_struct.__setattr__(a, v)

    param_struct.Fallow_Crop = fallow_struct

    return param_struct
