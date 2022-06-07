import numpy as np
import pandas as pd

from ..entities.modelConstants import ModelConstants


def compute_crop_calendar(
    crop,
    clock_struct_planting_dates,
    clock_struct_simulation_start_date,
    clock_struct_time_span,
    weather_df,
):
    """
    Function to compute additional parameters needed to define crop phenological calendar



    *Arguments:*\n

    `crop` : `Crop` :  Crop object containing crop paramaters

    `clock_struct` : `ClockStruct` :  model time paramaters

    `weather_df`: `pandas.DataFrame` :  weather data for simulation period


    *Returns:*

    `crop` : `Crop` : updated Crop object



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
        crop.MaxCanopy = round(
            crop.Emergence
            + (
                np.log(
                    (0.25 * crop.CCx * crop.CCx / crop.CC0)
                    / (crop.CCx - (0.98 * crop.CCx))
                )
                / crop.CGC
            )
        )

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
        if crop.CropType == 3:
            # 1. Calendar days from sowing to end of flowering
            FloweringEnd = (gdd_cum > crop.FloweringEnd).idxmax() + 1
            # 2. Duration of flowering in calendar days
            crop.FloweringCD = FloweringEnd - crop.HIstartCD
        else:
            crop.FloweringCD = ModelConstants.NO_VALUE

    return crop
