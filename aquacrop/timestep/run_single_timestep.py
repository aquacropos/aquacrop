import os
import numpy as np


from ..entities.totalAvailableWater import TAWClass
from ..entities.moistureDepletion import DrClass
from ..entities.crop import CropStructNT

from ..solution.pre_irrigation import pre_irrigation
from ..solution.irrigation import irrigation
from ..solution.capillary_rise import capillary_rise
from ..solution.germination import germination
from ..solution.growth_stage import growth_stage
from ..solution.canopy_cover import canopy_cover
from ..solution.transpiration import transpiration
from ..solution.groundwater_inflow import groundwater_inflow
from ..solution.harvest_index import harvest_index

if os.getenv("DEVELOPMENT"):
    from ..solution.growing_degree_day import growing_degree_day
    from ..solution.drainage import drainage
    from ..solution.root_zone_water import root_zone_water
    from ..solution.rainfall_partition import rainfall_partition
    from ..solution.check_groundwater_table import check_groundwater_table
    from ..solution.soil_evaporation import soil_evaporation
    from ..solution.root_development import root_development
    from ..solution.infiltration import infiltration
    from ..solution.HIref_current_day import HIref_current_day
    from ..solution.biomass_accumulation import biomass_accumulation
else:
    from ..solution.solution_growing_degree_day import growing_degree_day
    from ..solution.solution_drainage import drainage
    from ..solution.solution_root_zone_water import root_zone_water
    from ..solution.solution_rainfall_partition import rainfall_partition
    from ..solution.solution_check_groundwater_table import check_groundwater_table
    from ..solution.solution_soil_evaporation import soil_evaporation
    from ..solution.solution_root_development import root_development
    from ..solution.solution_infiltration import infiltration
    from ..solution.solution_HIref_current_day import HIref_current_day
    from ..solution.solution_biomass_accumulation import biomass_accumulation


def solution_single_time_step(
    init_cond, param_struct, clock_struct, weather_step, outputs
):
    """
    Function to perform AquaCrop-OS solution for a single time step



    *Arguments:*\n

    `init_cond` : `InitCondClass` :  containing current model paramaters

    `clock_struct` : `ClockStructClass` :  model time paramaters

    `weather_step`: `np.array` :  containing P,ET,Tmax,Tmin for current day

    `outputs` : `OutputClass` :  object to store outputs

    *Returns:*

    `NewCond` : `InitCondClass` :  containing updated model paramaters

    `outputs` : `OutputClass` :  object to store outputs



    """

    # Unpack structures
    Soil = param_struct.Soil
    CO2 = param_struct.CO2
    if param_struct.WaterTable == 1:
        Groundwater = param_struct.zGW[clock_struct.time_step_counter]
    else:
        Groundwater = 0

    P = weather_step[2]
    Tmax = weather_step[1]
    Tmin = weather_step[0]
    Et0 = weather_step[3]

    # Store initial conditions in structure for updating %%
    NewCond = init_cond

    # Check if growing season is active on current time step %%
    if clock_struct.season_counter >= 0:
        # Check if in growing season
        CurrentDate = clock_struct.step_start_time
        planting_date = clock_struct.planting_dates[clock_struct.season_counter]
        harvest_date = clock_struct.harvest_dates[clock_struct.season_counter]

        if (
            (planting_date <= CurrentDate)
            and (harvest_date >= CurrentDate)
            and (NewCond.CropMature == False)
            and (NewCond.CropDead == False)
        ):
            GrowingSeason = True
        else:
            GrowingSeason = False

        # Assign crop, irrigation management, and field management structures
        Crop_ = param_struct.Seasonal_Crop_List[clock_struct.season_counter]
        Crop_Name = param_struct.CropChoices[clock_struct.season_counter]
        IrrMngt = param_struct.IrrMngt

        if GrowingSeason == True:
            FieldMngt = param_struct.FieldMngt
        else:
            FieldMngt = param_struct.FallowFieldMngt

    else:
        # Not yet reached start of first growing season
        GrowingSeason = False
        # Assign crop, irrigation management, and field management structures
        # Assign first crop as filler crop
        Crop_ = param_struct.Fallow_Crop
        Crop_Name = "fallow"

        Crop_.Aer = 5
        Crop_.Zmin = 0.3
        IrrMngt = param_struct.FallowIrrMngt
        FieldMngt = param_struct.FallowFieldMngt

    # Increment time counters %%
    if GrowingSeason == True:
        # Calendar days after planting
        NewCond.DAP = NewCond.DAP + 1
        # Growing degree days after planting

        GDD = growing_degree_day(Crop_.GDDmethod, Crop_.Tupp, Crop_.Tbase, Tmax, Tmin)

        ## Update cumulative GDD counter ##
        NewCond.GDD = GDD
        NewCond.GDDcum = NewCond.GDDcum + GDD

        NewCond.GrowingSeason = True
    else:
        NewCond.GrowingSeason = False

        # Calendar days after planting
        NewCond.DAP = 0
        # Growing degree days after planting
        GDD = 0.3
        NewCond.GDDcum = 0

    # save current timestep counter
    NewCond.time_step_counter = clock_struct.time_step_counter
    NewCond.P = weather_step[2]
    NewCond.Tmax = weather_step[1]
    NewCond.Tmin = weather_step[0]
    NewCond.Et0 = weather_step[3]

    class_args = {
        key: value
        for key, value in Crop_.__dict__.items()
        if not key.startswith("__") and not callable(key)
    }
    Crop = CropStructNT(**class_args)

    # Run simulations %%
    # 1. Check for groundwater table
    (NewCond.th_fc_Adj, _) = check_groundwater_table(
        Soil.Profile,
        NewCond.zGW,
        NewCond.th,
        NewCond.th_fc_Adj,
        param_struct.WaterTable,
        Groundwater,
    )

    # 2. Root development
    NewCond.Zroot = root_development(
        Crop,
        Soil.Profile,
        NewCond.DAP,
        NewCond.Zroot,
        NewCond.DelayedCDs,
        NewCond.GDDcum,
        NewCond.DelayedGDDs,
        NewCond.TrRatio,
        NewCond.th,
        NewCond.CC,
        NewCond.CC_NS,
        NewCond.Germination,
        NewCond.rCor,
        NewCond.Tpot,
        NewCond.zGW,
        GDD,
        GrowingSeason,
        param_struct.WaterTable,
    )

    # 3. Pre-irrigation
    NewCond, PreIrr = pre_irrigation(
        Soil.Profile, Crop, NewCond, GrowingSeason, IrrMngt
    )

    # 4. Drainage

    NewCond.th, DeepPerc, FluxOut = drainage(
        Soil.Profile,
        NewCond.th,
        NewCond.th_fc_Adj,
    )

    # 5. Surface runoff
    Runoff, Infl, NewCond.DaySubmerged = rainfall_partition(
        P,
        NewCond.th,
        NewCond.DaySubmerged,
        FieldMngt.SRinhb,
        FieldMngt.Bunds,
        FieldMngt.zBund,
        FieldMngt.CNadjPct,
        Soil.CN,
        Soil.AdjCN,
        Soil.zCN,
        Soil.nComp,
        Soil.Profile,
    )

    # 6. Irrigation
    NewCond.Depletion, NewCond.TAW, NewCond.IrrCum, Irr = irrigation(
        IrrMngt.IrrMethod,
        IrrMngt.SMT,
        IrrMngt.AppEff,
        IrrMngt.MaxIrr,
        IrrMngt.IrrInterval,
        IrrMngt.Schedule,
        IrrMngt.depth,
        IrrMngt.MaxIrrSeason,
        NewCond.GrowthStage,
        NewCond.IrrCum,
        NewCond.Epot,
        NewCond.Tpot,
        NewCond.Zroot,
        NewCond.th,
        NewCond.DAP,
        NewCond.time_step_counter,
        Crop,
        Soil.Profile,
        Soil.zTop,
        GrowingSeason,
        P,
        Runoff,
    )

    # 7. Infiltration
    (
        NewCond.th,
        NewCond.SurfaceStorage,
        DeepPerc,
        RunoffTot,
        Infl,
        FluxOut,
    ) = infiltration(
        Soil.Profile,
        NewCond.SurfaceStorage,
        NewCond.th_fc_Adj,
        NewCond.th,
        Infl,
        Irr,
        IrrMngt.AppEff,
        FieldMngt.Bunds,
        FieldMngt.zBund,
        FluxOut,
        DeepPerc,
        Runoff,
        GrowingSeason,
    )
    # 8. Capillary Rise
    NewCond, CR = capillary_rise(
        Soil.Profile,
        Soil.nLayer,
        Soil.fshape_cr,
        NewCond,
        FluxOut,
        param_struct.WaterTable,
    )

    # 9. Check germination
    NewCond = germination(
        NewCond,
        Soil.zGerm,
        Soil.Profile,
        Crop.GermThr,
        Crop.PlantMethod,
        GDD,
        GrowingSeason,
    )

    # 10. Update growth stage
    NewCond = growth_stage(Crop, NewCond, GrowingSeason)

    # 11. Canopy cover development
    NewCond = canopy_cover(
        Crop, Soil.Profile, Soil.zTop, NewCond, GDD, Et0, GrowingSeason
    )

    # 12. Soil evaporation
    (
        NewCond.Epot,
        NewCond.th,
        NewCond.Stage2,
        NewCond.Wstage2,
        NewCond.Wsurf,
        NewCond.SurfaceStorage,
        NewCond.EvapZ,
        Es,
        EsPot,
    ) = soil_evaporation(
        clock_struct.evap_time_steps,
        clock_struct.sim_off_season,
        clock_struct.time_step_counter,
        Soil.Profile,
        Soil.EvapZmin,
        Soil.EvapZmax,
        Soil.REW,
        Soil.Kex,
        Soil.fwcc,
        Soil.fWrelExp,
        Soil.fevap,
        Crop.CalendarType,
        Crop.Senescence,
        IrrMngt.IrrMethod,
        IrrMngt.WetSurf,
        FieldMngt.Mulches,
        FieldMngt.fMulch,
        FieldMngt.MulchPct,
        NewCond.DAP,
        NewCond.Wsurf,
        NewCond.EvapZ,
        NewCond.Stage2,
        NewCond.th,
        NewCond.DelayedCDs,
        NewCond.GDDcum,
        NewCond.DelayedGDDs,
        NewCond.CCxW,
        NewCond.CCadj,
        NewCond.CCxAct,
        NewCond.CC,
        NewCond.PrematSenes,
        NewCond.SurfaceStorage,
        NewCond.Wstage2,
        NewCond.Epot,
        Et0,
        Infl,
        P,
        Irr,
        GrowingSeason,
    )

    # 13. Crop transpiration
    Tr, TrPot_NS, TrPot, NewCond, IrrNet = transpiration(
        Soil.Profile,
        Soil.nComp,
        Soil.zTop,
        Crop,
        IrrMngt.IrrMethod,
        IrrMngt.NetIrrSMT,
        NewCond,
        Et0,
        CO2,
        GrowingSeason,
        GDD,
    )

    # 14. Groundwater inflow
    NewCond, GwIn = groundwater_inflow(Soil.Profile, NewCond)

    # 15. Reference harvest index
    (NewCond.HIref, NewCond.YieldForm, NewCond.PctLagPhase,) = HIref_current_day(
        NewCond.HIref,
        NewCond.DAP,
        NewCond.DelayedCDs,
        NewCond.YieldForm,
        NewCond.PctLagPhase,
        NewCond.CCprev,
        Crop,
        GrowingSeason,
    )

    # 16. Biomass accumulation
    (NewCond.B, NewCond.B_NS) = biomass_accumulation(
        Crop,
        NewCond.DAP,
        NewCond.DelayedCDs,
        NewCond.HIref,
        NewCond.PctLagPhase,
        NewCond.B,
        NewCond.B_NS,
        Tr,
        TrPot_NS,
        Et0,
        GrowingSeason,
    )

    # 17. Harvest index
    NewCond = harvest_index(
        Soil.Profile, Soil.zTop, Crop, NewCond, Et0, Tmax, Tmin, GrowingSeason
    )

    # 18. Crop yield
    if GrowingSeason == True:
        # Calculate crop yield (tonne/ha)
        NewCond.Y = (NewCond.B / 100) * NewCond.HIadj
        # print( clock_struct.time_step_counter,(NewCond.B/100),NewCond.HIadj)
        # Check if crop has reached maturity
        if ((Crop.CalendarType == 1) and (NewCond.DAP >= Crop.Maturity)) or (
            (Crop.CalendarType == 2) and (NewCond.GDDcum >= Crop.Maturity)
        ):
            # Crop has reached maturity
            NewCond.CropMature = True

    elif GrowingSeason == False:
        # Crop yield is zero outside of growing season
        NewCond.Y = 0

    # 19. Root zone water
    _TAW = TAWClass()
    _Dr = DrClass()
    # thRZ = thRZClass()

    Wr, _Dr.Zt, _Dr.Rz, _TAW.Zt, _TAW.Rz, _, _, _, _, _, _ = root_zone_water(
        Soil.Profile,
        float(NewCond.Zroot),
        NewCond.th,
        Soil.zTop,
        float(Crop.Zmin),
        Crop.Aer,
    )

    # Wr, _Dr, _TAW, _thRZ = root_zone_water(
    #     Soil.Profile, NewCond.Zroot, NewCond.th, Soil.zTop, float(Crop.Zmin), Crop.Aer
    # )

    # 20. Update net irrigation to add any pre irrigation
    IrrNet = IrrNet + PreIrr
    NewCond.IrrNetCum = NewCond.IrrNetCum + PreIrr

    # Update model outputs %%
    row_day = clock_struct.time_step_counter
    row_gs = clock_struct.season_counter

    # Irrigation
    if GrowingSeason == True:
        if IrrMngt.IrrMethod == 4:
            # Net irrigation
            IrrDay = IrrNet
            IrrTot = NewCond.IrrNetCum
        else:
            # Irrigation
            IrrDay = Irr
            IrrTot = NewCond.IrrCum

    else:
        IrrDay = 0
        IrrTot = 0

        NewCond.Depletion = _Dr.Rz
        NewCond.TAW = _TAW.Rz

    # Water contents
    outputs.water_storage[row_day, :3] = np.array(
        [clock_struct.time_step_counter, GrowingSeason, NewCond.DAP]
    )
    outputs.water_storage[row_day, 3:] = NewCond.th

    # Water fluxes
    outputs.water_flux[row_day, :] = [
        clock_struct.time_step_counter,
        clock_struct.season_counter,
        NewCond.DAP,
        Wr,
        NewCond.zGW,
        NewCond.SurfaceStorage,
        IrrDay,
        Infl,
        Runoff,
        DeepPerc,
        CR,
        GwIn,
        Es,
        EsPot,
        Tr,
        P,
    ]

    # Crop growth
    outputs.crop_growth[row_day, :] = [
        clock_struct.time_step_counter,
        clock_struct.season_counter,
        NewCond.DAP,
        GDD,
        NewCond.GDDcum,
        NewCond.Zroot,
        NewCond.CC,
        NewCond.CC_NS,
        NewCond.B,
        NewCond.B_NS,
        NewCond.HI,
        NewCond.HIadj,
        NewCond.Y,
    ]

    # Final output (if at end of growing season)
    if clock_struct.season_counter > -1:
        if (
            (NewCond.CropMature == True)
            or (NewCond.CropDead == True)
            or (
                clock_struct.harvest_dates[clock_struct.season_counter]
                == clock_struct.step_end_time
            )
        ) and (NewCond.HarvestFlag == False):

            # Store final outputs
            outputs.final_stats.loc[clock_struct.season_counter] = [
                clock_struct.season_counter,
                Crop_Name,
                clock_struct.step_end_time,
                clock_struct.time_step_counter,
                NewCond.Y,
                IrrTot,
            ]

            # Set harvest flag
            NewCond.HarvestFlag = True

    return NewCond, param_struct, outputs
