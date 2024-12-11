
class FieldMngt:
    """
    Field Management Class containing mulches and bunds parameters

    Attributes:

        mulches (bool):  Soil surface covered by mulches (yield_ or N)

        bunds (bool):  Surface bunds present (yield_ or N)

        curve_number_adj (bool): Field conditions affect curve number (yield_ or N)

        sr_inhb (bool): Management practices fully inhibit surface runoff (yield_ or N)

        mulch_pct (float):  Area of soil surface covered by mulches (%)

        f_mulch (float): Soil evaporation adjustment factor due to effect of mulches

        z_bund (float): Bund height, user specifies in (m) but immediately converted to (mm) on initialisation for coherent calculations

        bund_water (float): Initial water height in surface bunds (mm)

        curve_number_adj_pct (float): Percentage change in curve number (positive or negative)

    """

    def __init__(
        self,
        mulches=False,
        bunds=False,
        curve_number_adj=False,
        sr_inhb=False,
        mulch_pct=50,
        f_mulch=0.5,
        z_bund=0,
        bund_water=0,
        curve_number_adj_pct=0,
    ):

        self.mulches = mulches  #  Soil surface covered by mulches (yield_ or N)
        self.bunds = bunds  #  Surface bunds present (yield_ or N)
        self.curve_number_adj = curve_number_adj  # Field conditions affect curve number (yield_ or N)
        self.sr_inhb = sr_inhb  # Management practices fully inhibit surface runoff (yield_ or N)

        self.mulch_pct = mulch_pct  #  Area of soil surface covered by mulches (%)
        self.f_mulch = f_mulch  # Soil evaporation adjustment factor due to effect of mulches
        self.z_bund = z_bund * 1000 # Bund height, user-specified as (m), here immediately converted to (mm)
        self.bund_water = bund_water  # Initial water height in surface bunds (mm)
        self.curve_number_adj_pct = curve_number_adj_pct  # Percentage change in curve number (positive or negative)




class FieldMngtStruct:

    """


    """

    def __init__(self):
        self.mulches = False
        self.bunds = False
        self.curve_number_adj = False
        self.sr_inhb = False

        self.mulch_pct = 0.0
        self.f_mulch = 0.0
        self.z_bund = 0.0
        self.bund_water = 0.0
        self.curve_number_adj_pct = 0.0

