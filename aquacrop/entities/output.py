class Output:
    """
    Class to hold output data

    **Atributes**:\n

    `water_storage` : `numpy` : Water storage in soil. TODO: it is numpy or pandas?

    `water_flux` : `pandas.DataFrame` : Water flux

    `crop_growth` : `pandas.DataFrame` : crop growth

    `final_stats` : `pandas.DataFrame` : final stats

    """

    def __init__(self):

        self.water_storage = []
        self.water_flux = []
        self.crop_growth = []
        self.final_stats = []


OutputClass = Output
