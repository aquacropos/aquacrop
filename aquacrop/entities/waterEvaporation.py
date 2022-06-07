


from numba import float64, int64, boolean, types




spec = [
    ("Act", float64),
    ("Sat", float64),
    ("Fc", float64),
    ("Wp", float64),
    ("Dry", float64),
]



class WaterEvaporation(object):
    """
    TODO: THIS CLASS IS NOT USED
    
    stores soil water contents in the evaporation layer

    **Attributes:**\n


    `Sat` : `float` :  Water storage in evaporation layer at saturation (mm)

    `Fc` : `float` :  Water storage in evaporation layer at Field Capacity (mm)

    `Wp` : `float`:  Water storage in evaporation layer at Wilting Point (mm)

    `Dry` : `float` : Water storage in evaporation layer at air dry (mm)

    `Act` : `float` : Actual Water storage in evaporation layer (mm)

    """

    def __init__(self):
        self.Sat = 0.0
        self.Fc = 0.0
        self.Wp = 0.0
        self.Dry = 0.0
        self.Act = 0.0

