import os
import numpy as np


from ..entities.totalAvailableWater import TAW
from ..entities.moistureDepletion import Dr
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

    `init_cond` : `InitialCondition` :  containing current model paramaters

    `clock_struct` : `ClockStruct` :  model time paramaters

    `weather_step`: `np.array` :  containing precipitation,ET,temp_max,temp_min for current day

    `outputs` : `Output` :  object to store outputs

    *Returns:*

    `NewCond` : `InitialCondition` :  containing updated model paramaters

    `outputs` : `Output` :  object to store outputs



    """

    # Unpack structures
    Soil = param_struct.Soil
    CO2 = param_struct.CO2
    if param_struct.water_table == 1:
        Groundwater = param_struct.z_gw[clock_struct.time_step_counter]
    else:
        Groundwater = 0

    precipitation = weather_step[2]
    temp_max = weather_step[1]
    temp_min = weather_step[0]
    et0 = weather_step[3]

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
            and (NewCond.crop_mature is False)
            and (NewCond.crop_dead is False)
        ):
            growing_season = True
        else:
            growing_season = False

        # Assign crop, irrigation management, and field management structures
        Crop_ = param_struct.Seasonal_Crop_List[clock_struct.season_counter]
        Crop_Name = param_struct.CropChoices[clock_struct.season_counter]
        IrrMngt = param_struct.IrrMngt

        if growing_season is True:
            FieldMngt = param_struct.FieldMngt
        else:
            FieldMngt = param_struct.FallowFieldMngt

    else:
        # Not yet reached start of first growing season
        growing_season = False
        # Assign crop, irrigation management, and field management structures
        # Assign first crop as filler crop
        Crop_ = param_struct.Fallow_Crop
        Crop_Name = "fallow"

        Crop_.Aer = 5
        Crop_.Zmin = 0.3
        IrrMngt = param_struct.FallowIrrMngt
        FieldMngt = param_struct.FallowFieldMngt

    # Increment time counters %%
    if growing_season is True:
        # Calendar days after planting
        NewCond.dap = NewCond.dap + 1
        # Growing degree days after planting

        gdd = growing_degree_day(
            Crop_.GDDmethod, Crop_.Tupp, Crop_.Tbase, temp_max, temp_min
        )

        # Update cumulative gdd counter
        NewCond.gdd = gdd
        NewCond.gdd_cum = NewCond.gdd_cum + gdd

        NewCond.growing_season = True
    else:
        NewCond.growing_season = False

        # Calendar days after planting
        NewCond.dap = 0
        # Growing degree days after planting
        gdd = 0.3
        NewCond.gdd_cum = 0

    # save current timestep counter
    NewCond.time_step_counter = clock_struct.time_step_counter
    NewCond.precipitation = weather_step[2]
    NewCond.temp_max = weather_step[1]
    NewCond.temp_min = weather_step[0]
    NewCond.et0 = weather_step[3]

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
        NewCond.z_gw,
        NewCond.th,
        NewCond.th_fc_Adj,
        param_struct.water_table,
        Groundwater,
    )

    # 2. Root development
    NewCond.z_root = root_development(
        Crop,
        Soil.Profile,
        NewCond.dap,
        NewCond.z_root,
        NewCond.delayed_cds,
        NewCond.gdd_cum,
        NewCond.delayed_gdds,
        NewCond.tr_ratio,
        NewCond.th,
        NewCond.canopy_cover,
        NewCond.canopy_cover_ns,
        NewCond.germination,
        NewCond.r_cor,
        NewCond.t_pot,
        NewCond.z_gw,
        gdd,
        growing_season,
        param_struct.water_table,
    )

    # 3. Pre-irrigation
    NewCond, PreIrr = pre_irrigation(
        Soil.Profile, Crop, NewCond, growing_season, IrrMngt
    )

    # 4. Drainage

    NewCond.th, DeepPerc, FluxOut = drainage(
        Soil.Profile,
        NewCond.th,
        NewCond.th_fc_Adj,
    )

    # 5. Surface runoff
    Runoff, Infl, NewCond.day_submerged = rainfall_partition(
        precipitation,
        NewCond.th,
        NewCond.day_submerged,
        FieldMngt.sr_inhb,
        FieldMngt.bunds,
        FieldMngt.z_bund,
        FieldMngt.curve_number_adj_pct,
        Soil.cn,
        Soil.adj_cn,
        Soil.z_cn,
        Soil.nComp,
        Soil.Profile,
    )

    # 6. Irrigation
    NewCond.depletion, NewCond.taw, NewCond.irr_cum, Irr = irrigation(
        IrrMngt.irrigation_method,
        IrrMngt.SMT,
        IrrMngt.AppEff,
        IrrMngt.MaxIrr,
        IrrMngt.IrrInterval,
        IrrMngt.Schedule,
        IrrMngt.depth,
        IrrMngt.MaxIrrSeason,
        NewCond.growth_stage,
        NewCond.irr_cum,
        NewCond.e_pot,
        NewCond.t_pot,
        NewCond.z_root,
        NewCond.th,
        NewCond.dap,
        NewCond.time_step_counter,
        Crop,
        Soil.Profile,
        Soil.z_top,
        growing_season,
        precipitation,
        Runoff,
    )

    # 7. Infiltration
    (
        NewCond.th,
        NewCond.surface_storage,
        DeepPerc,
        Runoff,
        Infl,
        FluxOut,
    ) = infiltration(
        Soil.Profile,
        NewCond.surface_storage,
        NewCond.th_fc_Adj,
        NewCond.th,
        Infl,
        Irr,
        IrrMngt.AppEff,
        FieldMngt.bunds,
        FieldMngt.z_bund,
        FluxOut,
        DeepPerc,
        Runoff,
        growing_season,
    )
    # 8. Capillary Rise
    NewCond, CR = capillary_rise(
        Soil.Profile,
        Soil.nLayer,
        Soil.fshape_cr,
        NewCond,
        FluxOut,
        param_struct.water_table,
    )

    # 9. Check germination
    NewCond = germination(
        NewCond,
        Soil.z_germ,
        Soil.Profile,
        Crop.GermThr,
        Crop.PlantMethod,
        gdd,
        growing_season,
    )

    # 10. Update growth stage
    NewCond = growth_stage(Crop, NewCond, growing_season)

    # 11. Canopy cover development
    NewCond = canopy_cover(
        Crop, Soil.Profile, Soil.z_top, NewCond, gdd, et0, growing_season
    )

    # 12. Soil evaporation
    (
        NewCond.e_pot,
        NewCond.th,
        NewCond.stage2,
        NewCond.w_stage_2,
        NewCond.w_surf,
        NewCond.surface_storage,
        NewCond.evap_z,
        Es,
        EsPot,
    ) = soil_evaporation(
        clock_struct.evap_time_steps,
        clock_struct.sim_off_season,
        clock_struct.time_step_counter,
        Soil.Profile,
        Soil.evap_z_min,
        Soil.evap_z_max,
        Soil.rew,
        Soil.kex,
        Soil.fwcc,
        Soil.f_wrel_exp,
        Soil.f_evap,
        Crop.CalendarType,
        Crop.Senescence,
        IrrMngt.irrigation_method,
        IrrMngt.WetSurf,
        FieldMngt.mulches,
        FieldMngt.f_mulch,
        FieldMngt.mulch_pct,
        NewCond.dap,
        NewCond.w_surf,
        NewCond.evap_z,
        NewCond.stage2,
        NewCond.th,
        NewCond.delayed_cds,
        NewCond.gdd_cum,
        NewCond.delayed_gdds,
        NewCond.ccx_w,
        NewCond.canopy_cover_adj,
        NewCond.ccx_act,
        NewCond.canopy_cover,
        NewCond.premat_senes,
        NewCond.surface_storage,
        NewCond.w_stage_2,
        NewCond.e_pot,
        et0,
        Infl,
        precipitation,
        Irr,
        growing_season,
    )

    # 13. Crop transpiration
    Tr, TrPot_NS, TrPot, NewCond, IrrNet = transpiration(
        Soil.Profile,
        Soil.nComp,
        Soil.z_top,
        Crop,
        IrrMngt.irrigation_method,
        IrrMngt.NetIrrSMT,
        NewCond,
        et0,
        CO2,
        growing_season,
        gdd,
    )

    # 14. Groundwater inflow
    NewCond, GwIn = groundwater_inflow(Soil.Profile, NewCond)

    # 15. Reference harvest index
    (NewCond.hi_ref, NewCond.yield_form, NewCond.pct_lag_phase,) = HIref_current_day(
        NewCond.hi_ref,
        NewCond.dap,
        NewCond.delayed_cds,
        NewCond.yield_form,
        NewCond.pct_lag_phase,
        NewCond.cc_prev,
        Crop,
        growing_season,
    )

    # 16. Biomass accumulation
    (NewCond.biomass, NewCond.biomass_ns) = biomass_accumulation(
        Crop,
        NewCond.dap,
        NewCond.delayed_cds,
        NewCond.hi_ref,
        NewCond.pct_lag_phase,
        NewCond.biomass,
        NewCond.biomass_ns,
        Tr,
        TrPot_NS,
        et0,
        growing_season,
    )

    # 17. Harvest index
    NewCond = harvest_index(
        Soil.Profile, Soil.z_top, Crop, NewCond, et0, temp_max, temp_min, growing_season
    )

    # 18. Crop yield_
    if growing_season is True:
        # Calculate crop yield_ (tonne/ha)
        NewCond.yield_ = (NewCond.biomass / 100) * NewCond.harvest_index_adj
        # print( clock_struct.time_step_counter,(NewCond.biomass/100),NewCond.harvest_index_adj)
        # Check if crop has reached maturity
        if ((Crop.CalendarType == 1) and (NewCond.dap >= Crop.Maturity)) or (
            (Crop.CalendarType == 2) and (NewCond.gdd_cum >= Crop.Maturity)
        ):
            # Crop has reached maturity
            NewCond.crop_mature = True

    elif growing_season is False:
        # Crop yield_ is zero outside of growing season
        NewCond.yield_ = 0

    # 19. Root zone water
    _TAW = TAW()
    _water_root_depletion = Dr()
    # thRZ = RootZoneWater()

    Wr, _water_root_depletion.Zt, _water_root_depletion.Rz, _TAW.Zt, _TAW.Rz, _, _, _, _, _, _ = root_zone_water(
        Soil.Profile,
        float(NewCond.z_root),
        NewCond.th,
        Soil.z_top,
        float(Crop.Zmin),
        Crop.Aer,
    )

    # 20. Update net irrigation to add any pre irrigation
    IrrNet = IrrNet + PreIrr
    NewCond.irr_net_cum = NewCond.irr_net_cum + PreIrr

    # Update model outputs %%
    row_day = clock_struct.time_step_counter
    row_gs = clock_struct.season_counter

    # Irrigation
    if growing_season is True:
        if IrrMngt.irrigation_method == 4:
            # Net irrigation
            IrrDay = IrrNet
            IrrTot = NewCond.irr_net_cum
        else:
            # Irrigation
            IrrDay = Irr
            IrrTot = NewCond.irr_cum

    else:
        IrrDay = 0
        IrrTot = 0

        NewCond.depletion = _water_root_depletion.Rz
        NewCond.taw = _TAW.Rz

    # Water contents
    outputs.water_storage[row_day, :3] = np.array(
        [clock_struct.time_step_counter, growing_season, NewCond.dap]
    )
    outputs.water_storage[row_day, 3:] = NewCond.th

    # Water fluxes
    outputs.water_flux[row_day, :] = [
        clock_struct.time_step_counter,
        clock_struct.season_counter,
        NewCond.dap,
        Wr,
        NewCond.z_gw,
        NewCond.surface_storage,
        IrrDay,
        Infl,
        Runoff,
        DeepPerc,
        CR,
        GwIn,
        Es,
        EsPot,
        Tr,
        TrPot,
    ]

    # Crop growth
    outputs.crop_growth[row_day, :] = [
        clock_struct.time_step_counter,
        clock_struct.season_counter,
        NewCond.dap,
        gdd,
        NewCond.gdd_cum,
        NewCond.z_root,
        NewCond.canopy_cover,
        NewCond.canopy_cover_ns,
        NewCond.biomass,
        NewCond.biomass_ns,
        NewCond.harvest_index,
        NewCond.harvest_index_adj,
        NewCond.yield_,
    ]

    # Final output (if at end of growing season)
    if clock_struct.season_counter > -1:
        if (
            (NewCond.crop_mature is True)
            or (NewCond.crop_dead is True)
            or (
                clock_struct.harvest_dates[clock_struct.season_counter]
                == clock_struct.step_end_time
            )
        ) and (NewCond.harvest_flag is False):

            # Store final outputs
            outputs.final_stats.loc[row_gs] = [
                clock_struct.season_counter,
                Crop_Name,
                clock_struct.step_end_time,
                clock_struct.time_step_counter,
                NewCond.yield_,
                IrrTot,
            ]

            # Set harvest flag
            NewCond.harvest_flag = True

    return NewCond, param_struct, outputs
