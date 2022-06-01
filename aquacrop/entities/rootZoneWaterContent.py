from numba import float64, types
import typing



thRZ_spec = [
    ("Act", float64),
    ("S", float64),
    ("FC", float64),
    ("WP", float64),
    ("Dry", float64),
    ("Aer", float64),
]



class RootZoneWater(object):
    """
    TODO: This class is not used
    
    root zone water content

    **Attributes:**\n



    `Act` : `float` : .

    `S` : `float` : .

    `FC` : `float` : .

    `WP` : `float` : .

    `Dry` : `float` : .

    `Aer` : `float` : .



    """

    def __init__(self):
        self.Act = 0.0
        self.S = 0.0
        self.FC = 0.0
        self.WP = 0.0
        self.Dry = 0.0
        self.Aer = 0.0

thRZNT = typing.NamedTuple("thRZNT", thRZ_spec)
thRZNT_type_sig= types.NamedTuple(tuple(dict(thRZ_spec).values()),thRZNT)
