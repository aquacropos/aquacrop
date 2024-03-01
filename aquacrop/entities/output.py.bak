import pandas as pd
import numpy as np


class Output:
    """
    Class to hold output data

    During Simulation these are numpy arrays and are converted to pandas dataframes
    at the end of the simulation

    Atributes:
    
        water_flux (pandas.DataFrame, numpy.array): Daily water flux changes

        water_storage (pandas.DataFrame, numpy array): daily water content of each soil compartment

        crop_growth (pandas.DataFrame, numpy array): daily crop growth variables

        final_stats (pandas.DataFrame, numpy array): final stats at end of each season

    """

    def __init__(self, time_span, initial_th):

        self.water_storage = np.zeros((len(time_span), 3 + len(initial_th)))
        self.water_flux = np.zeros((len(time_span), 16))
        self.crop_growth = np.zeros((len(time_span), 15))
        self.final_stats = pd.DataFrame(
            columns=[
                "Season",
                "crop Type",
                "Harvest Date (YYYY/MM/DD)",
                "Harvest Date (Step)",
                "Dry yield (tonne/ha)",
                "Fresh yield (tonne/ha)",
                "Yield potential (tonne/ha)",
                "Seasonal irrigation (mm)",
            ]
        )