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

        current_concentration (float): current CO2 concentration (initialize if constant_conc=True)

        constant_conc (bool): use constant conc every season

        co2_data (DataFrame): CO2 timeseries (2 columns: 'year' and 'ppm')

    """

    def __init__(
        self,
        ref_concentration=369.41,
        current_concentration=0.,
        constant_conc=False,
        co2_data=None,
    ):
        self.ref_concentration = ref_concentration
        self.current_concentration = current_concentration
        self.constant_conc = constant_conc
        if co2_data is not None:
            self.co2_data = co2_data
        else:
            self.co2_data = pd.read_csv(
                f"{acfp}/data/MaunaLoaCO2.txt",
                header=1,
                sep=r'\s+',
                names=["year", "ppm"],
            )
        self.co2_data_processed = None
