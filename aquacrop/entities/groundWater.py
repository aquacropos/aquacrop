

class GroundWater:
    """
    Ground Water Class stores information on water table params

    **Attributes:**\n


    `water_table` : `str` :  Water table considered (yield_ or N)

    `method` : `str` :  Water table input data ('Constant' or 'Variable')

    `dates` : `list` : water table observation dates

    `values` : `list` : water table observation depths

    """

    def __init__(self, water_table="N", method="Constant", dates=[], values=[]):

        self.water_table = water_table
        self.method = method
        self.dates = dates
        self.values = values
