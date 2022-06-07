
from numba import float64, int64, boolean, types

spec = [
    ("Rz", float64),
    ("Zt", float64),
]



class Dr:

    """

    **Attributes:**\n

    `Rz` : `float` : .

    `Zt` : `float` : .


    """

    def __init__(self):
        self.Rz = 0.0
        self.Zt = 0.0