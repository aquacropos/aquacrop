import numpy as np

from ..entities.modelConstants import ModelConstants


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
        self.HIfinal = 0.0

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
        self.YieldPot = 0
        self.harvest_index = 0
        self.harvest_index_adj = 0
        self.ccx_act = 0
        self.ccx_act_ns = 0
        self.ccx_w = 0
        self.ccx_w_ns = 0
        self.ccx_early_sen = 0
        self.cc_prev = 0
        self.protected_seed = 0
        self.DryYield = 0
        self.FreshYield = 0

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
        self.sumET0EarlySen = 0
        self.gdd = 0

        self.w_surf = 0
        self.evap_z = 0
        self.w_stage_2 = 0

        self.depletion = 0
        self.taw = 0
