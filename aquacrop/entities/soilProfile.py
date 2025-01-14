import numpy as np
import typing


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
