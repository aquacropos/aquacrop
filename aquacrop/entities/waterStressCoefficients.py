from numba import float64, int64, boolean, types
import typing


Ksw_spec = [
    ("exp", float64),
    ("sto", float64),
    ("sen", float64),
    ("pol", float64),
    ("sto_lin", float64),
]



class Ksw(object):

    """
    water stress coefficients

    **Attributes:**\n


    `exp` : `float` : .

    `sto` : `float` : .

    `sen` : `float` : .

    `pol` : `float` : .

    `sto_lin` : `float` : .



    """

    def __init__(self):
        self.exp = 1.0
        self.sto = 1.0
        self.sen = 1.0
        self.pol = 1.0
        self.sto_lin = 1.0


KswNT = typing.NamedTuple("KswNT", Ksw_spec)
KswNT_type_sig= types.NamedTuple(tuple(dict(Ksw_spec).values()),KswNT)


