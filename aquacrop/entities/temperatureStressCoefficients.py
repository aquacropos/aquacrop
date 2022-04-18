from numba import float64, int64, boolean, types
import typing



Kst_spec = [
    ("PolH", float64),
    ("PolC", float64),
]



class Kst(object):

    """
    temperature stress coefficients

    **Attributes:**\n


    `PolH` : `float` : heat stress

    `PolC` : `float` : cold stress


    """

    def __init__(self):
        self.PolH = 1.0
        self.PolC = 1.0

KstClass =Kst
KstNT = typing.NamedTuple("KstNT", Kst_spec)
KstNT_type_sig= types.NamedTuple(tuple(dict(Kst_spec).values()),KstNT)
