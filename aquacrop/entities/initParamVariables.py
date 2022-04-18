import numpy as np
from numba import float64, int64, boolean, types


InitCond_spec = [
    ("AgeDays", float64),
    ("AgeDays_NS", float64),
    ("AerDays", float64),
    ("AerDaysComp", float64[:]),
    ("IrrCum", float64),
    ("DelayedGDDs", float64),
    ("DelayedCDs", float64),
    ("PctLagPhase", float64),
    ("tEarlySen", float64),
    ("GDDcum", float64),
    ("DaySubmerged", float64),
    ("IrrNetCum", float64),
    ("DAP", int64),
    ("Epot", float64),
    ("Tpot", float64),
    ("PreAdj", boolean),
    ("CropMature", boolean),
    ("CropDead", boolean),
    ("Germination", boolean),
    ("PrematSenes", boolean),
    ("HarvestFlag", boolean),
    ("GrowingSeason", boolean),
    ("YieldForm", boolean),
    ("Stage2", boolean),
    ("WTinSoil", boolean),
    ("Stage", float64),
    ("Fpre", float64),
    ("Fpost", float64),
    ("fpost_dwn", float64),
    ("fpost_upp", float64),
    ("HIcor_Asum", float64),
    ("HIcor_Bsum", float64),
    ("Fpol", float64),
    ("sCor1", float64),
    ("sCor2", float64),
    ("HIref", float64),
    ("GrowthStage", float64),
    ("TrRatio", float64),
    ("rCor", float64),
    ("CC", float64),
    ("CCadj", float64),
    ("CC_NS", float64),
    ("CCadj_NS", float64),
    ("B", float64),
    ("B_NS", float64),
    ("HI", float64),
    ("HIadj", float64),
    ("CCxAct", float64),
    ("CCxAct_NS", float64),
    ("CCxW", float64),
    ("CCxW_NS", float64),
    ("CCxEarlySen", float64),
    ("CCprev", float64),
    ("ProtectedSeed", int64),
    ("Y", float64),
    ("Zroot", float64),
    ("CC0adj", float64),
    ("SurfaceStorage", float64),
    ("zGW", float64),
    ("th_fc_Adj", float64[:]),
    ("th", float64[:]),
    ("thini", float64[:]),
    ("time_step_counter", int64),
    ("P", float64),
    ("Tmax", float64),
    ("Tmin", float64),
    ("Et0", float64),
    ("GDD", float64),
    ("Wsurf", float64),
    ("EvapZ", float64),
    ("Wstage2", float64),
    ("Depletion", float64),
    ("TAW", float64),
]



class InitialCondition:
    """
    The InitCond Class contains all Paramaters and variables used in the simulation

    updated each timestep with the name NewCond


    """

    def __init__(self, num_comp):
        # counters
        self.AgeDays = 0
        self.AgeDays_NS = 0
        self.AerDays = 0
        self.AerDaysComp = np.zeros(num_comp)
        self.IrrCum = 0
        self.DelayedGDDs = 0
        self.DelayedCDs = 0
        self.PctLagPhase = 0
        self.tEarlySen = 0
        self.GDDcum = 0
        self.DaySubmerged = 0
        self.IrrNetCum = 0
        self.DAP = 0
        self.Epot = 0
        self.Tpot = 0

        # States
        self.PreAdj = False
        self.CropMature = False
        self.CropDead = False
        self.Germination = False
        self.PrematSenes = False
        self.HarvestFlag = False
        self.GrowingSeason = False
        self.YieldForm = False
        self.Stage2 = False

        self.WTinSoil = False

        # HI
        self.Stage = 1
        self.Fpre = 1
        self.Fpost = 1
        self.fpost_dwn = 1
        self.fpost_upp = 1

        self.HIcor_Asum = 0
        self.HIcor_Bsum = 0
        self.Fpol = 0
        self.sCor1 = 0
        self.sCor2 = 0
        self.HIref = 0.0

        # GS
        self.GrowthStage = 0

        # Transpiration
        self.TrRatio = 1

        # crop growth
        self.rCor = 1

        self.CC = 0
        self.CCadj = 0
        self.CC_NS = 0
        self.CCadj_NS = 0
        self.B = 0
        self.B_NS = 0
        self.HI = 0
        self.HIadj = 0
        self.CCxAct = 0
        self.CCxAct_NS = 0
        self.CCxW = 0
        self.CCxW_NS = 0
        self.CCxEarlySen = 0
        self.CCprev = 0
        self.ProtectedSeed = 0
        self.Y = 0

        self.Zroot = 0.
        self.CC0adj = 0
        self.SurfaceStorage = 0
        self.zGW = -999

        self.th_fc_Adj = np.zeros(num_comp)
        self.th = np.zeros(num_comp)
        self.thini = np.zeros(num_comp)

        self.time_step_counter = 0

        self.P = 0
        self.Tmax = 0
        self.Tmin = 0
        self.Et0 = 0
        self.GDD = 0

        self.Wsurf = 0
        self.EvapZ = 0
        self.Wstage2 = 0

        self.Depletion = 0
        self.TAW = 0


InitCondClass = InitialCondition