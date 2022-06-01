import pandas as pd
import numpy as np


class Output:
    """
    Class to hold output data

    **Atributes**:\n

    `water_storage` : `numpy` : Water storage in soil. TODO: it is numpy or pandas?

    TODO: water_flux and crop_growth are numpy arrays during simulation. I think it should be clearer
    `water_flux` : `pandas.DataFrame` : Water flux

    `crop_growth` : `pandas.DataFrame` : crop growth

    `final_stats` : `pandas.DataFrame` : final stats

    """

    def __init__(self, time_span, initial_th):

        self.water_storage = np.zeros((len(time_span), 3 + len(initial_th)))
        self.water_flux = np.zeros((len(time_span), 16))
        self.crop_growth = np.zeros((len(time_span), 13))
        self.final_stats = pd.DataFrame(
            columns=[
                "Season",
                "crop Type",
                "Harvest Date (YYYY/MM/DD)",
                "Harvest Date (Step)",
                "Yield (tonne/ha)",
                "Seasonal irrigation (mm)",
            ]
        )