import numpy as np
import pandas as pd
from numba import float64, int64, boolean, types


class IrrigationManagement:

    """
    Farmer Class defines irrigation strategy

    **Attributes:**\n


    `Name` : `str` :  name

    `irrigation_method` : `int` :  Irrigation method {0: rainfed, 1: soil moisture targets, 2: set time interval,
                                              3: predifined schedule, 4: net irrigation, 5: constant depth }

    `WetSurf` : `int` : Soil surface wetted by irrigation (%)

    `AppEff` : `int` : Irrigation application efficiency (%)

    `MaxIrr` : `float` : Maximum depth (mm) that can be applied each day

    `SMT` : `list` :  Soil moisture targets (%taw) to maintain in each growth stage (only used if irrigation method is equal to 1)

    `IrrInterval` : `int` : Irrigation interval in days (only used if irrigation method is equal to 2)

    `Schedule` : `pandas.DataFrame` : DataFrame containing dates and depths

    `NetIrrSMT` : `float` : Net irrigation threshold moisture level (% of taw that will be maintained, for irrigation_method=4)

    `Depth` : `float` : constant depth to apply on each day

    """

    def __init__(self, irrigation_method, **kwargs):
        self.irrigation_method = irrigation_method

        self.WetSurf = 100.0
        self.AppEff = 100.0
        self.MaxIrr = 25.0
        self.MaxIrrSeason = 10_000.0
        self.SMT = np.zeros(4)
        self.IrrInterval = 0
        self.Schedule = []
        self.NetIrrSMT = 80.0
        self.depth = 0.0

        if irrigation_method == 1:
            self.SMT = [100] * 4

        if irrigation_method == 2:
            self.IrrInterval = 3

        if irrigation_method == 3:
            # wants a pandas dataframe with Date and Depth, pd.Datetime and float
            """
            dates = pd.DatetimeIndex(['20/10/1979','20/11/1979','20/12/1979'])
            depths = [25,25,25]
            irr=pd.DataFrame([dates,depths]).T
            irr.columns=['Date','Depth']
            """
            self.Schedule = pd.DataFrame(columns=["Date", "Depth"])

        if irrigation_method == 4:
            self.NetIrrSMT = 80

        if irrigation_method == 5:
            self.depth = 0

        allowed_keys = {
            "name",
            "WetSurf",
            "AppEff",
            "MaxIrr",
            "MaxIrrSeason",
            "SMT",
            "IrrInterval",
            "NetIrrSMT",
            "Schedule",
            "depth",
        }

        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)


spec = [
    ("irrigation_method", int64),
    ("WetSurf", float64),
    ("AppEff", float64),
    ("MaxIrr", float64),
    ("MaxIrrSeason", float64),
    ("SMT", float64[:]),
    ("IrrInterval", int64),
    ("Schedule", float64[:]),
    ("NetIrrSMT", float64),
    ("depth", float64),
]



class IrrMngtStruct:

    """


    """

    def __init__(self, sim_len):
        self.irrigation_method = 0

        self.WetSurf = 100.0
        self.AppEff = 100.0
        self.MaxIrr = 25.0
        self.MaxIrrSeason = 10_000
        self.SMT = np.zeros(4)
        self.IrrInterval = 0
        self.Schedule = np.zeros(sim_len)
        self.NetIrrSMT = 80.0
        self.depth = 0.0


