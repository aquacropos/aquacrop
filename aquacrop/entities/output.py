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

        self.water_storage = np.zeros((len(time_span)-1, 3 + len(initial_th)))
        self.water_flux = np.zeros((len(time_span)-1, 16))
        self.crop_growth = np.zeros((len(time_span)-1, 20))
        
        self.ET_color = np.zeros((len(time_span)-1, 6))
        self.S_color = np.zeros((len(time_span)-1, 6))
        
        self.final_stats = pd.DataFrame(
            columns=[
                "Season",
                "crop Type",
                'Planting Date (YYYY/MM/DD)',
                'Anthesis Date (YYYY/MM/DD)',
                "Harvest Date (YYYY/MM/DD)",
                "Harvest Date (Step)",
                "Dry yield (tonne/ha)",
                "Fresh yield (tonne/ha)",
                "Yield potential (tonne/ha)",
                "Seasonal irrigation (mm)",
                'GDD cummulative',
                'Initial Soil Water (mm)',
                'Precipitation (mm)',
                'Irrigation (mm)',
                'Capillary rise (mm)',
                'GW inflow (mm)',
                'Final Soil Water (mm)',
                'Evaporation (mm)',
                'Transpiration (mm)',
                'Runoff (mm)',
                'Percolation (mm)',
            ])
            
        self.final_watercolor = pd.DataFrame(
            columns=[
                "Season",
                'ET green (mm)',
                'ET blue irr (mm)',
                'ET blue cr (mm)',
                'Storage green (mm)',
                'Storage blue irr (mm)',
                'Storage blue cr (mm)'
            ]
        )