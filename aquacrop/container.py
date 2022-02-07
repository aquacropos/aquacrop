
##############
# defining structref data structure
# see link below for details and commented code
# from https://numba.pydata.org/numba-doc/dev/extending/high-level.html#implementing-mutable-structures
##############



# # Cell
# InitCond_spec = [
#     ("AgeDays", float64),
#     ("AgeDays_NS", float64),
#     ("AerDays", float64),
#     ("AerDaysComp", float64[:]),
#     ("IrrCum", float64),
#     ("DelayedGDDs", float64),
#     ("DelayedCDs", float64),
#     ("PctLagPhase", float64),
#     ("tEarlySen", float64),
#     ("GDDcum", float64),
#     ("DaySubmerged", float64),
#     ("IrrNetCum", float64),
#     ("DAP", int64),
#     ("Epot", float64),
#     ("Tpot", float64),
#     ("PreAdj", boolean),
#     ("CropMature", boolean),
#     ("CropDead", boolean),
#     ("Germination", boolean),
#     ("PrematSenes", boolean),
#     ("HarvestFlag", boolean),
#     ("GrowingSeason", boolean),
#     ("YieldForm", boolean),
#     ("Stage2", boolean),
#     ("WTinSoil", boolean),
#     ("Stage", float64),
#     ("Fpre", float64),
#     ("Fpost", float64),
#     ("fpost_dwn", float64),
#     ("fpost_upp", float64),
#     ("HIcor_Asum", float64),
#     ("HIcor_Bsum", float64),
#     ("Fpol", float64),
#     ("sCor1", float64),
#     ("sCor2", float64),
#     ("HIref", float64),
#     ("GrowthStage", float64),
#     ("TrRatio", float64),
#     ("rCor", float64),
#     ("CC", float64),
#     ("CCadj", float64),
#     ("CC_NS", float64),
#     ("CCadj_NS", float64),
#     ("B", float64),
#     ("B_NS", float64),
#     ("HI", float64),
#     ("HIadj", float64),
#     ("CCxAct", float64),
#     ("CCxAct_NS", float64),
#     ("CCxW", float64),
#     ("CCxW_NS", float64),
#     ("CCxEarlySen", float64),
#     ("CCprev", float64),
#     ("ProtectedSeed", int64),
#     ("Y", float64),
#     ("Zroot", float64),
#     ("CC0adj", float64),
#     ("SurfaceStorage", float64),
#     ("zGW", float64),
#     ("th_fc_Adj", float64[:]),
#     ("th", float64[:]),
#     ("thini", float64[:]),
#     ("TimeStepCounter", int64),
#     ("P", float64),
#     ("Tmax", float64),
#     ("Tmin", float64),
#     ("Et0", float64),
#     ("GDD", float64),
#     ("Wsurf", float64),
#     ("EvapZ", float64),
#     ("Wstage2", float64),
#     ("Depletion", float64),
#     ("TAW", float64),
# ]



# # tuple(dict(InitCond_spec).keys())

# @structref.register
# class InitCondStructType(types.StructRef):
#     def preprocess_fields(self, fields):
#         return tuple((name, types.unliteral(typ)) for name, typ in fields)


# class InitCondStruct(structref.StructRefProxy):
#     def __new__(cls,
#                 AgeDays,
#                 AgeDays_NS,
#                 AerDays,
#                 AerDaysComp,
#                 IrrCum,
#                 DelayedGDDs,
#                 DelayedCDs,
#                 PctLagPhase,
#                 tEarlySen,
#                 GDDcum,
#                 DaySubmerged,
#                 IrrNetCum,
#                 DAP,
#                 Epot,
#                 Tpot,
#                 PreAdj,
#                 CropMature,
#                 CropDead,
#                 Germination,
#                 PrematSenes,
#                 HarvestFlag,
#                 GrowingSeason,
#                 YieldForm,
#                 Stage2,
#                 WTinSoil,
#                 Stage,
#                 Fpre,
#                 Fpost,
#                 fpost_dwn,
#                 fpost_upp,
#                 HIcor_Asum,
#                 HIcor_Bsum,
#                 Fpol,
#                 sCor1,
#                 sCor2,
#                 HIref,
#                 GrowthStage,
#                 TrRatio,
#                 rCor,
#                 CC,
#                 CCadj,
#                 CC_NS,
#                 CCadj_NS,
#                 B,
#                 B_NS,
#                 HI,
#                 HIadj,
#                 CCxAct,
#                 CCxAct_NS,
#                 CCxW,
#                 CCxW_NS,
#                 CCxEarlySen,
#                 CCprev,
#                 ProtectedSeed,
#                 Y,
#                 Zroot,
#                 CC0adj,
#                 SurfaceStorage,
#                 zGW,
#                 th_fc_Adj,
#                 th,
#                 thini,
#                 TimeStepCounter,
#                 P,
#                 Tmax,
#                 Tmin,
#                 Et0,
#                 GDD,
#                 Wsurf,
#                 EvapZ,
#                 Wstage2,
#                 Depletion,
#                 TAW,
# ):
#         return structref.StructRefProxy.__new__(cls, 
#                 AgeDays,
#                 AgeDays_NS,
#                 AerDays,
#                 AerDaysComp,
#                 IrrCum,
#                 DelayedGDDs,
#                 DelayedCDs,
#                 PctLagPhase,
#                 tEarlySen,
#                 GDDcum,
#                 DaySubmerged,
#                 IrrNetCum,
#                 DAP,
#                 Epot,
#                 Tpot,
#                 PreAdj,
#                 CropMature,
#                 CropDead,
#                 Germination,
#                 PrematSenes,
#                 HarvestFlag,
#                 GrowingSeason,
#                 YieldForm,
#                 Stage2,
#                 WTinSoil,
#                 Stage,
#                 Fpre,
#                 Fpost,
#                 fpost_dwn,
#                 fpost_upp,
#                 HIcor_Asum,
#                 HIcor_Bsum,
#                 Fpol,
#                 sCor1,
#                 sCor2,
#                 HIref,
#                 GrowthStage,
#                 TrRatio,
#                 rCor,
#                 CC,
#                 CCadj,
#                 CC_NS,
#                 CCadj_NS,
#                 B,
#                 B_NS,
#                 HI,
#                 HIadj,
#                 CCxAct,
#                 CCxAct_NS,
#                 CCxW,
#                 CCxW_NS,
#                 CCxEarlySen,
#                 CCprev,
#                 ProtectedSeed,
#                 Y,
#                 Zroot,
#                 CC0adj,
#                 SurfaceStorage,
#                 zGW,
#                 th_fc_Adj,
#                 th,
#                 thini,
#                 TimeStepCounter,
#                 P,
#                 Tmax,
#                 Tmin,
#                 Et0,
#                 GDD,
#                 Wsurf,
#                 EvapZ,
#                 Wstage2,
#                 Depletion,
#                 TAW,

#         )

    
#     @property
#     def AgeDays(self):
#         return MyStruct_get_AgeDays(self)

#     @property
#     def AgeDays_NS(self):
#         return MyStruct_get_AgeDays_NS(self)

#     @property
#     def AerDays(self):
#         return MyStruct_get_AerDays(self)

#     @property
#     def AerDaysComp(self):
#         return MyStruct_get_AerDaysComp(self)

#     @property
#     def IrrCum(self):
#         return MyStruct_get_IrrCum(self)

#     @property
#     def DelayedGDDs(self):
#         return MyStruct_get_DelayedGDDs(self)

#     @property
#     def DelayedCDs(self):
#         return MyStruct_get_DelayedCDs(self)

#     @property
#     def PctLagPhase(self):
#         return MyStruct_get_PctLagPhase(self)

#     @property
#     def tEarlySen(self):
#         return MyStruct_get_tEarlySen(self)

#     @property
#     def GDDcum(self):
#         return MyStruct_get_GDDcum(self)

#     @property
#     def DaySubmerged(self):
#         return MyStruct_get_DaySubmerged(self)

#     @property
#     def IrrNetCum(self):
#         return MyStruct_get_IrrNetCum(self)

#     @property
#     def DAP(self):
#         return MyStruct_get_DAP(self)

#     @property
#     def Epot(self):
#         return MyStruct_get_Epot(self)

#     @property
#     def Tpot(self):
#         return MyStruct_get_Tpot(self)

#     @property
#     def PreAdj(self):
#         return MyStruct_get_PreAdj(self)

#     @property
#     def CropMature(self):
#         return MyStruct_get_CropMature(self)

#     @property
#     def CropDead(self):
#         return MyStruct_get_CropDead(self)
        
#     @property
#     def Germination(self):
#         return MyStruct_get_Germination(self)

#     @property
#     def PrematSenes(self):
#         return MyStruct_get_PrematSenes(self)

#     @property
#     def HarvestFlag(self):
#         return MyStruct_get_HarvestFlag(self)

#     @property
#     def GrowingSeason(self):
#         return MyStruct_get_GrowingSeason(self)
        
#     @property
#     def YieldForm(self):
#         return MyStruct_get_YieldForm(self)

#     @property
#     def Stage2(self):
#         return MyStruct_get_Stage2(self)

#     @property
#     def WTinSoil(self):
#         return MyStruct_get_WTinSoil(self)

#     @property
#     def Stage(self):
#         return MyStruct_get_Stage(self)
        
#     @property
#     def Fpre(self):
#         return MyStruct_get_Fpre(self)

#     @property
#     def Fpost(self):
#         return MyStruct_get_Fpost(self)

#     @property
#     def fpost_dwn(self):
#         return MyStruct_get_fpost_dwn(self)

#     @property
#     def fpost_upp(self):
#         return MyStruct_get_fpost_upp(self)
        
#     @property
#     def HIcor_Asum(self):
#         return MyStruct_get_HIcor_Asum(self)

#     @property
#     def HIcor_Bsum(self):
#         return MyStruct_get_HIcor_Bsum(self)

#     @property
#     def Fpol(self):
#         return MyStruct_get_Fpol(self)

#     @property
#     def sCor1(self):
#         return MyStruct_get_sCor1(self)
        
#     @property
#     def sCor2(self):
#         return MyStruct_get_sCor2(self)
#     @property
#     def HIref(self):
#         return MyStruct_get_HIref(self)

#     @property
#     def GrowthStage(self):
#         return MyStruct_get_GrowthStage(self)
        
#     @property
#     def TrRatio(self):
#         return MyStruct_get_TrRatio(self)

#     @property
#     def rCor(self):
#         return MyStruct_get_rCor(self)

#     @property
#     def CC(self):
#         return MyStruct_get_CC(self)

#     @property
#     def CCadj(self):
#         return MyStruct_get_CCadj(self)

#     @property
#     def CC_NS(self):
#         return MyStruct_get_CC_NS(self)

#     @property
#     def B(self):
#         return MyStruct_get_B(self)

#     @property
#     def B_NS(self):
#         return MyStruct_get_B_NS(self)

#     @property
#     def HI(self):
#         return MyStruct_get_HI(self)

#     @property
#     def HIadj(self):
#         return MyStruct_get_HIadj(self)

#     @property
#     def CCxAct(self):
#         return MyStruct_get_CCxAct(self)

#     @property
#     def CCxAct_NS(self):
#         return MyStruct_get_CCxAct_NS(self)

#     @property
#     def CCxW(self):
#         return MyStruct_get_CCxW(self)

#     @property
#     def CCxEarlySen(self):
#         return MyStruct_get_CCxEarlySen(self)

#     @property
#     def CCprev(self):
#         return MyStruct_get_CCprev(self)

#     @property
#     def ProtectedSeed(self):
#         return MyStruct_get_ProtectedSeed(self)

#     @property
#     def Y(self):
#         return MyStruct_get_Y(self)

#     @property
#     def Zroot(self):
#         return MyStruct_get_Zroot(self)

#     @property
#     def CC0adj(self):
#         return MyStruct_get_CC0adj(self)

#     @property
#     def SurfaceStorage(self):
#         return MyStruct_get_SurfaceStorage(self)

#     @property
#     def zGW(self):
#         return MyStruct_get_zGW(self)

#     @property
#     def th_fc_Adj(self):
#         return MyStruct_get_th_fc_Adj(self)

#     @property
#     def th(self):
#         return MyStruct_get_th(self)

#     @property
#     def thini(self):
#         return MyStruct_get_thini(self)

#     @property
#     def TimeStepCounter(self):
#         return MyStruct_get_TimeStepCounter(self)

#     @property
#     def P(self):
#         return MyStruct_get_P(self)

#     @property
#     def Tmax(self):
#         return MyStruct_get_Tmax(self)

#     @property
#     def Tmin(self):
#         return MyStruct_get_Tmin(self)

#     @property
#     def Et0(self):
#         return MyStruct_get_Et0(self)

#     @property
#     def GDD(self):
#         return MyStruct_get_GDD(self)

#     @property
#     def Wsurf(self):
#         return MyStruct_get_Wsurf(self)

#     @property
#     def EvapZ(self):
#         return MyStruct_get_EvapZ(self)

#     @property
#     def Wstage2(self):
#         return MyStruct_get_Wstage2(self)

#     @property
#     def Depletion(self):
#         return MyStruct_get_Depletion(self)

#     @property
#     def TAW(self):
#         return MyStruct_get_TAW(self)



# @njit
# def MyStruct_get_AgeDays(self):
#     return self.AgeDays

# @njit
# def MyStruct_get_AgeDays_NS(self):
#     return self.AgeDays_NS

# @njit
# def MyStruct_get_AerDays(self):
#     return self.AerDays

# @njit
# def MyStruct_get_AerDaysComp(self):
#     return self.AerDaysComp

# @njit
# def MyStruct_get_IrrCum(self):
#     return self.IrrCum

# @njit
# def MyStruct_get_DelayedGDDs(self):
#     return self.DelayedGDDs

# @njit
# def MyStruct_get_DelayedCDs(self):
#     return self.DelayedCDs

# @njit
# def MyStruct_get_PctLagPhase(self):
#     return self.PctLagPhase

# @njit
# def MyStruct_get_tEarlySen(self):
#     return self.f1

# @njit
# def MyStruct_get_GDDcum(self):
#     return self.GDDcum

# @njit
# def MyStruct_get_DaySubmerged(self):
#     return self.DaySubmerged

# @njit
# def MyStruct_get_IrrNetCum(self):
#     return self.IrrNetCum

# @njit
# def MyStruct_get_DAP(self):
#     return self.DAP

# @njit
# def MyStruct_get_Epot(self):
#     return self.Epot

# @njit
# def MyStruct_get_Tpot(self):
#     return self.Tpot

# @njit
# def MyStruct_get_PreAdj(self):
#     return self.PreAdj

# @njit
# def MyStruct_get_CropMature(self):
#     return self.CropMature

# @njit
# def MyStruct_get_CropDead(self):
#     return self.CropDead

# @njit
# def MyStruct_get_Germination(self):
#     return self.Germination

# @njit
# def MyStruct_get_PrematSenes(self):
#     return self.PrematSenes

# @njit
# def MyStruct_get_HarvestFlag(self):
#     return self.HarvestFlag

# @njit
# def MyStruct_get_GrowingSeason(self):
#     return self.GrowingSeason

# @njit
# def MyStruct_get_YieldForm(self):
#     return self.YieldForm

# @njit
# def MyStruct_get_Stage2(self):
#     return self.Stage2

# @njit
# def MyStruct_get_WTinSoil(self):
#     return self.WTinSoil

# @njit
# def MyStruct_get_Stage(self):
#     return self.Stage

# @njit
# def MyStruct_get_Fpre(self):
#     return self.Fpre

# @njit
# def MyStruct_get_Fpost(self):
#     return self.Fpost

# @njit
# def MyStruct_get_fpost_dwn(self):
#     return self.fpost_dwn

# @njit
# def MyStruct_get_fpost_upp(self):
#     return self.fpost_upp

# @njit
# def MyStruct_get_HIcor_Asum(self):
#     return self.HIcor_Asum

# @njit
# def MyStruct_get_HIcor_Bsum(self):
#     return self.HIcor_Bsum

# @njit
# def MyStruct_get_Fpol(self):
#     return self.Fpol

# @njit
# def MyStruct_get_sCor1(self):
#     return self.sCor1

# @njit
# def MyStruct_get_sCor2(self):
#     return self.sCor2

# @njit
# def MyStruct_get_HIref(self):
#     return self.HIref

# @njit
# def MyStruct_get_GS(self):
#     return self.GS

# @njit
# def MyStruct_get_GrowthStage(self):
#     return self.GrowthStage

# @njit
# def MyStruct_get_TrRatio(self):
#     return self.TrRatio

# @njit
# def MyStruct_get_rCor(self):
#     return self.rCor

# @njit
# def MyStruct_get_CC(self):
#     return self.CC

# @njit
# def MyStruct_get_CCadj(self):
#     return self.CCadj

# @njit
# def MyStruct_get_CC_NS(self):
#     return self.CC_NS

# @njit
# def MyStruct_get_B(self):
#     return self.B

# @njit
# def MyStruct_get_CC_NS(self):
#     return self.CC_NS

# @njit
# def MyStruct_get_B(self):
#     return self.B

# @njit
# def MyStruct_get_B_NS(self):
#     return self.B_NS

# @njit
# def MyStruct_get_HI(self):
#     return self.HI

# @njit
# def MyStruct_get_HIadj(self):
#     return self.HIadj

# @njit
# def MyStruct_get_CCxAct(self):
#     return self.CCxAct

# @njit
# def MyStruct_get_CCxAct_NS(self):
#     return self.CCxAct_NS

# @njit
# def MyStruct_get_CCxW(self):
#     return self.CCxW

# @njit
# def MyStruct_get_CCxEarlySen(self):
#     return self.CCxEarlySen

# @njit
# def MyStruct_get_CCprev(self):
#     return self.CCprev

# @njit
# def MyStruct_get_ProtectedSeed(self):
#     return self.ProtectedSeed

# @njit
# def MyStruct_get_Y(self):
#     return self.Y

# @njit
# def MyStruct_get_Zroot(self):
#     return self.Zroot

# @njit
# def MyStruct_get_CC0adj(self):
#     return self.CC0adj

# @njit
# def MyStruct_get_SurfaceStorage(self):
#     return self.SurfaceStorage

# @njit
# def MyStruct_get_zGW(self):
#     return self.zGW

# @njit
# def MyStruct_get_th_fc_Adj(self):
#     return self.th_fc_Adj

# @njit
# def MyStruct_get_th(self):
#     return self.th

# @njit
# def MyStruct_get_thini(self):
#     return self.thini

# @njit
# def MyStruct_get_TimeStepCounter(self):
#     return self.TimeStepCounter

# @njit
# def MyStruct_get_P(self):
#     return self.P

# @njit
# def MyStruct_get_Tmax(self):
#     return self.Tmax

# @njit
# def MyStruct_get_Tmin(self):
#     return self.Tmin

# @njit
# def MyStruct_get_Et0(self):
#     return self.Et0

# @njit
# def MyStruct_get_GDD(self):
#     return self.GDD

# @njit
# def MyStruct_get_Wsurf(self):
#     return self.Wsurf

# @njit
# def MyStruct_get_EvapZ(self):
#     return self.EvapZ

# @njit
# def MyStruct_get_Wstage2(self):
#     return self.Wstage2

# @njit
# def MyStruct_get_Depletion(self):
#     return self.Depletion

# @njit
# def MyStruct_get_TAW(self):
#     return self.TAW


# structref.define_proxy(InitCondStruct, InitCondStructType, list(dict(InitCond_spec).keys()))


