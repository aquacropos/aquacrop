import numpy as np
from numba import float64, int64, boolean, types
import typing


SoilProfileNT_spec = [
    ("Comp", int64[:]),
    ("dz", float64[:]),
    ("Layer", int64[:]),
    ("dzsum", float64[:]),
    ("th_fc", float64[:]),
    ("th_s", float64[:]),
    ("th_wp", float64[:]),
    ("Ksat", float64[:]),
    ("Penetrability", float64[:]),
    ("th_dry", float64[:]),
    ("tau", float64[:]),
    ("zBot", float64[:]),
    ("z_top", float64[:]),
    ("zMid", float64[:]),
    ("th_fc_Adj", float64[:]),
    ("aCR", float64[:]),
    ("bCR", float64[:]),
]



class SoilProfile:
    """

    **Attributes:**\n

    `Comp` : `list` :

    `Layer` : `list` :

    `dz` : `list` :

    `dzsum` : `list` :

    `zBot` : `list` :

    `z_top` : `list` :

    `zMid` : `list` :

    """

    def __init__(self, length):

        self.Comp = np.zeros(length, dtype=np.int64)
        self.dz = np.zeros(length, dtype=np.float64)
        self.Layer = np.zeros(length, dtype=np.int64)
        self.dzsum = np.zeros(length, dtype=np.float64)
        self.th_fc = np.zeros(length, dtype=np.float64)
        self.th_s = np.zeros(length, dtype=np.float64)
        self.th_wp = np.zeros(length, dtype=np.float64)
        self.Ksat = np.zeros(length, dtype=np.float64)
        self.Penetrability = np.zeros(length, dtype=np.float64)
        self.th_dry = np.zeros(length, dtype=np.float64)
        self.tau = np.zeros(length, dtype=np.float64)
        self.zBot = np.zeros(length, dtype=np.float64)
        self.z_top = np.zeros(length, dtype=np.float64)
        self.zMid = np.zeros(length, dtype=np.float64)
        self.th_fc_Adj = np.zeros(length, dtype=np.float64)
        self.aCR = np.zeros(length, dtype=np.float64)
        self.bCR = np.zeros(length, dtype=np.float64)

SoilProfileNT = typing.NamedTuple("SoilProfileNT", SoilProfileNT_spec)
SoilProfileNT_typ_sig= types.NamedTuple(tuple(dict(SoilProfileNT_spec).values()),SoilProfileNT)
