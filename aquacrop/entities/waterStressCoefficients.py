from numba import float64, int64, boolean, types
import typing


Ksw_spec = [
    ("Exp", float64),
    ("Sto", float64),
    ("Sen", float64),
    ("Pol", float64),
    ("StoLin", float64),
]



class Ksw(object):

    """
    water stress coefficients

    **Attributes:**\n


    `Exp` : `float` : .

    `Sto` : `float` : .

    `Sen` : `float` : .

    `Pol` : `float` : .

    `StoLin` : `float` : .



    """

    def __init__(self):
        self.Exp = 1.0
        self.Sto = 1.0
        self.Sen = 1.0
        self.Pol = 1.0
        self.StoLin = 1.0



KswClass = Ksw
KswNT = typing.NamedTuple("KswNT", Ksw_spec)
KswNT_type_sig= types.NamedTuple(tuple(dict(Ksw_spec).values()),KswNT)


