
from numba import float64, int64, boolean, types

spec = [
    ("Rz", float64),
    ("Zt", float64),
]



class Dr:
    """
    Depletion class to hold the rootzone and topsoil depletion

    Attributes:

    Rz (float): Root zone soil-water depletion

    Zt (float): Top soil depletion


    """

    def __init__(self):
        self.Rz = 0.0
        self.Zt = 0.0