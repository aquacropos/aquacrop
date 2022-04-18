
from numba import float64, int64, boolean, types


class FieldMngt:
    """
    Field Management Class

    **Attributes:**\n


    `Mulches` : `bool` :  Soil surface covered by mulches (Y or N)

    `Bunds` : `bool` :  Surface bunds present (Y or N)

    `CNadj` : `bool` : Field conditions affect curve number (Y or N)

    `SRinhb` : `bool` : Management practices fully inhibit surface runoff (Y or N)



    `MulchPct` : `float` :  Area of soil surface covered by mulches (%)

    `fMulch` : `float` : Soil evaporation adjustment factor due to effect of mulches

    `zBund` : `float` : Bund height (m)

    `BundWater` : `float` : Initial water height in surface bunds (mm)

    `CNadjPct` : `float` : Percentage change in curve number (positive or negative)

    """

    def __init__(
        self,
        Mulches=False,
        Bunds=False,
        CNadj=False,
        SRinhb=False,
        MulchPct=50,
        fMulch=0.5,
        zBund=0,
        BundWater=0,
        CNadjPct=0,
    ):

        self.Mulches = Mulches  #  Soil surface covered by mulches (Y or N)
        self.Bunds = Bunds  #  Surface bunds present (Y or N)
        self.CNadj = CNadj  # Field conditions affect curve number (Y or N)
        self.SRinhb = SRinhb  # Management practices fully inhibit surface runoff (Y or N)

        self.MulchPct = MulchPct  #  Area of soil surface covered by mulches (%)
        self.fMulch = fMulch  # Soil evaporation adjustment factor due to effect of mulches
        self.zBund = zBund  # Bund height (m)
        self.BundWater = BundWater  # Initial water height in surface bunds (mm)
        self.CNadjPct = CNadjPct  # Percentage change in curve number (positive or negative)



spec = [
    ("Mulches", boolean),
    ("Bunds", boolean),
    ("CNadj", boolean),
    ("SRinhb", boolean),
    ("MulchPct", float64),
    ("fMulch", float64),
    ("zBund", float64),
    ("BundWater", float64),
    ("CNadjPct", float64),
]




class FieldMngtStruct:

    """


    """

    def __init__(self):
        self.Mulches = False
        self.Bunds = False
        self.CNadj = False
        self.SRinhb = False

        self.MulchPct = 0.0
        self.fMulch = 0.0
        self.zBund = 0.0
        self.BundWater = 0.0
        self.CNadjPct = 0.0

FieldMngtClass = FieldMngt