from numba import float64
import pandas as pd
from os.path import dirname, abspath

acfp: str = dirname(dirname(abspath(__file__)))

spec = [
    ("ref_concentration", float64),
    ("Cur rentConc", float64),
]


class CO2(object):

    """

    Attributes:

        ref_concentration (float): reference CO2 concentration

        current_concentration (float): current CO2 concentration

    """

    def __init__(self, co2_data=None, constant_conc=False):
        self.ref_concentration = 369.41
        self.current_concentration = 0.0
        self.constant_conc = constant_conc
        if co2_data is not None:
            self.co2_data = co2_data
        else:
            self.co2_data = pd.read_csv(
                    f"{acfp}/data/MaunaLoaCO2.txt",
                    header=1,
                    delim_whitespace=True,
                    names=["year", "ppm"],
    )
        self.co2_data_processed = None



