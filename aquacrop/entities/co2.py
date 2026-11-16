import pandas as pd
from os.path import dirname, abspath

acfp: str = dirname(dirname(abspath(__file__)))


class CO2(object):

    """

    Attributes:

        ref_concentration (float): reference CO2 concentration

        current_concentration (float): current CO2 concentration (initialize if constant_conc=True)

        constant_conc (bool): use constant conc every season

        co2_data (DataFrame): CO2 timeseries (2 columns: 'year' and 'ppm')

        scenario (str): SSP pathway for years after the observed record, e.g.
            'ssp585'. Defaults to SSP2-4.5, with a warning for simulations that
            extend past the observed record.

        observed_end (int): last year of the Mauna Loa observations

        default_scenario (bool): True when no scenario was chosen and the
            default pathway fills years after the observed record

    """
    
    _BUILTIN = {
        "ssp119":   "CO2_SSP1-1.9.txt",
        "ssp126":   "CO2_SSP1-2.6.txt",
        "ssp245":   "CO2_SSP2-4.5.txt",
        "ssp370":   "CO2_SSP3-7.0.txt",
        "ssp434":   "CO2_SSP4-3.4.txt",
        "ssp460":   "CO2_SSP4-6.0.txt",
        "ssp534os": "CO2_SSP5-3.4-OS.txt",
        "ssp585":   "CO2_SSP5-8.5.txt",
    }
    _DEFAULT_SCENARIO = "ssp245"

    def __init__(
        self,
        ref_concentration=369.41,
        current_concentration=0.,
        constant_conc=False,
        co2_data=None,
        scenario=None
    ):
        self.ref_concentration = ref_concentration
        self.current_concentration = current_concentration
        self.constant_conc = constant_conc
        
        self.scenario = scenario
        self.observed_end = None
        self.default_scenario = False

        if co2_data is not None:
            self.co2_data = co2_data
        else:
            # Mauna Loa observations, then an SSP pathway for later years
            observed = self._read("MaunaLoaCO2.txt")
            self.observed_end = int(observed["year"].max())
            self.default_scenario = scenario is None
            future = self._read(self._BUILTIN[self._key(scenario or self._DEFAULT_SCENARIO)])
            self.co2_data = pd.concat(
                [observed, future[future["year"] > self.observed_end]], ignore_index=True)

        self.co2_data_processed = None

    @classmethod
    def _key(cls, scenario):
        key = scenario.lower().replace("-", "").replace("_", "").replace(".", "")
        if key not in cls._BUILTIN:
            raise ValueError(
                f"Unknown CO2 scenario '{scenario}'. Options: {sorted(cls._BUILTIN)}")
        return key

    @staticmethod
    def _read(fname):
        return pd.read_csv(
            f"{acfp}/data/co2/{fname}", header=1, sep=r"\s+", names=["year", "ppm"])
