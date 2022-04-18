

class GroundWater:
    """
    Ground Water Class stores information on water table params

    **Attributes:**\n


    `WaterTable` : `str` :  Water table considered (Y or N)

    `Method` : `str` :  Water table input data ('Constant' or 'Variable')

    `dates` : `list` : water table observation dates

    `values` : `list` : water table observation depths

    """

    def __init__(self, WaterTable="N", Method="Constant", dates=[], values=[]):

        self.WaterTable = WaterTable
        self.Method = Method
        self.dates = dates
        self.values = values



GwClass = GroundWater