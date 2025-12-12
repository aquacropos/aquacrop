"""
Pure cutting/grazing transform applied within a timestep.

Keeps soil water state unchanged, reduces canopy/biomass, and optionally
resets regrowth counters.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from aquacrop.entities.initParamVariables import InitialCondition
    from aquacrop.entities.cuttingManagement import CutMngtStruct


def apply_cutting(
    new_cond: "InitialCondition",
    cut_mngt: "CutMngtStruct",
    is_cut_day: bool,
    crop=None,
) -> Tuple["InitialCondition", float]:
    """
    Apply a cut to the crop state.

    Parameters
    ----------
    new_cond : InitialCondition
        Current crop/soil state for the timestep.
    cut_mngt : CutMngtStruct
        Cutting management settings and schedule.
    is_cut_day : bool
        Whether a cut should be applied on this timestep.

    Returns
    -------
    new_cond : InitialCondition
        Updated state.
    removed_biomass : float
        Removed above-ground biomass (g/m2).
    """
    if not is_cut_day:
        return new_cond, 0.0

    remove_fraction = float(cut_mngt.remove_fraction)
    residual_cc = float(cut_mngt.residual_cc)

    removed_biomass = new_cond.biomass * remove_fraction
    removed_biomass_ns = new_cond.biomass_ns * remove_fraction

    new_cond.biomass = new_cond.biomass - removed_biomass
    new_cond.biomass_ns = new_cond.biomass_ns - removed_biomass_ns

    # Simplest canopy rule: set to residual canopy cover
    new_cond.canopy_cover = residual_cc
    new_cond.canopy_cover_ns = residual_cc

    if getattr(cut_mngt, "reset_regrowth", False):
        # Reset phenology and delay counters so development restarts.
        # For perennial pasture regrowth, keep state at/after emergence so
        # residual canopy is preserved in the next day's canopy update.
        if crop is not None:
            if getattr(crop, "CalendarType", 2) == 1:
                new_cond.dap = int(getattr(crop, "EmergenceCD", 0) or 0)
                new_cond.gdd_cum = 0
            else:
                new_cond.dap = 0
                new_cond.gdd_cum = float(getattr(crop, "Emergence", 0) or 0)
        else:
            new_cond.dap = 0
            new_cond.gdd_cum = 0
        new_cond.delayed_cds = 0
        new_cond.delayed_gdds = 0
        new_cond.age_days = 0
        new_cond.age_days_ns = 0
        new_cond.t_early_sen = 0
        new_cond.premat_senes = False

        # Clear maturity/death flags
        new_cond.crop_mature = False
        new_cond.crop_dead = False
        new_cond.harvest_flag = False
        new_cond.yield_form = False

        # Reset canopy maxima so regrowth isn't treated as senescence
        new_cond.ccx_act = residual_cc
        new_cond.ccx_act_ns = residual_cc
        new_cond.ccx_w = residual_cc
        new_cond.ccx_w_ns = residual_cc
        new_cond.ccx_early_sen = 0

        # Start regrowth from the residual canopy level
        new_cond.cc0_adj = residual_cc

    if getattr(cut_mngt, "export_as_yield", False):
        # DryYield is in tonne/ha; biomass is g/m2 (100 g/m2 = 1 t/ha)
        new_cond.DryYield = new_cond.DryYield + (removed_biomass / 100.0)

    return new_cond, removed_biomass
