import numpy as np
from numba import float64, int64, boolean

from ..entities.modelConstants import ModelConstants

InitCond_spec = [
    ("age_days", float64),
    ("age_days_ns", float64),
    ("aer_days", float64),
    ("aer_days_comp", float64[:]),
    ("irr_cum", float64),
    ("delayed_gdds", float64),
    ("delayed_cds", float64),
    ("pct_lag_phase", float64),
    ("t_early_sen", float64),
    ("gdd_cum", float64),
    ("day_submerged", float64),
    ("irr_net_cum", float64),
    ("dap", int64),
    ("e_pot", float64),
    ("t_pot", float64),
    ("pre_adj", boolean),
    ("crop_mature", boolean),
    ("crop_dead", boolean),
    ("germination", boolean),
    ("premat_senes", boolean),
    ("harvest_flag", boolean),
    ("growing_season", boolean),
    ("yield_form", boolean),
    ("stage2", boolean),
    ("wt_in_soil", boolean),
    ("stage", float64),
    ("f_pre", float64),
    ("f_post", float64),
    ("fpost_dwn", float64),
    ("fpost_upp", float64),
    ("h1_cor_asum", float64),
    ("h1_cor_bsum", float64),
    ("f_pol", float64),
    ("s_cor1", float64),
    ("s_cor2", float64),
    ("hi_ref", float64),
    ("growth_stage", float64),
    ("tr_ratio", float64),
    ("r_cor", float64),
    ("canopy_cover", float64),
    ("canopy_cover_adj", float64),
    ("canopy_cover_ns", float64),
    ("canopy_cover_adj_ns", float64),
    ("biomass", float64),
    ("biomass_ns", float64),
    ("harvest_index", float64),
    ("harvest_index_adj", float64),
    ("ccx_act", float64),
    ("ccx_act_ns", float64),
    ("ccx_w", float64),
    ("ccx_w_ns", float64),
    ("ccx_early_sen", float64),
    ("cc_prev", float64),
    ("protected_seed", int64),
    ("yield_", float64),
    ("z_root", float64),
    ("cc0_adj", float64),
    ("surface_storage", float64),
    ("z_gw", float64),
    ("th_fc_Adj", float64[:]),
    ("th", float64[:]),
    ("thini", float64[:]),
    ("time_step_counter", int64),
    ("precipitation", float64),
    ("temp_max", float64),
    ("temp_min", float64),
    ("et0", float64),
    ("gdd", float64),
    ("w_surf", float64),
    ("evap_z", float64),
    ("w_stage_2", float64),
    ("depletion", float64),
    ("taw", float64),
]


class InitialCondition:
    """
    The InitCond Class contains all Paramaters and variables used in the simulation

    updated each timestep with the name NewCond


    """

    def __init__(self, num_comp):
        # counters
        self.age_days = 0
        self.age_days_ns = 0
        self.aer_days = 0
        self.aer_days_comp = np.zeros(num_comp)
        self.irr_cum = 0
        self.delayed_gdds = 0
        self.delayed_cds = 0
        self.pct_lag_phase = 0
        self.t_early_sen = 0
        self.gdd_cum = 0
        self.day_submerged = 0
        self.irr_net_cum = 0
        self.dap = 0
        self.e_pot = 0
        self.t_pot = 0

        # States
        self.pre_adj = False
        self.crop_mature = False
        self.crop_dead = False
        self.germination = False
        self.premat_senes = False
        self.harvest_flag = False
        self.growing_season = False
        self.yield_form = False
        self.stage2 = False

        self.wt_in_soil = False

        # harvest_index
        self.stage = 1
        self.f_pre = 1
        self.f_post = 1
        self.fpost_dwn = 1
        self.fpost_upp = 1

        self.h1_cor_asum = 0
        self.h1_cor_bsum = 0
        self.f_pol = 0
        self.s_cor1 = 0
        self.s_cor2 = 0
        self.hi_ref = 0.0

        # GS
        self.growth_stage = 0

        # Transpiration
        self.tr_ratio = 1

        # crop growth
        self.r_cor = 1

        self.canopy_cover = 0
        self.canopy_cover_adj = 0
        self.canopy_cover_ns = 0
        self.canopy_cover_adj_ns = 0
        self.biomass = 0
        self.biomass_ns = 0
        self.harvest_index = 0
        self.harvest_index_adj = 0
        self.ccx_act = 0
        self.ccx_act_ns = 0
        self.ccx_w = 0
        self.ccx_w_ns = 0
        self.ccx_early_sen = 0
        self.cc_prev = 0
        self.protected_seed = 0
        self.yield_ = 0

        self.z_root = 0.0
        self.cc0_adj = 0
        self.surface_storage = 0
        self.z_gw = ModelConstants.NO_VALUE

        self.th_fc_Adj = np.zeros(num_comp)
        self.th = np.zeros(num_comp)
        self.thini = np.zeros(num_comp)

        self.time_step_counter = 0

        self.precipitation = 0
        self.temp_max = 0
        self.temp_min = 0
        self.et0 = 0
        self.gdd = 0

        self.w_surf = 0
        self.evap_z = 0
        self.w_stage_2 = 0

        self.depletion = 0
        self.taw = 0
