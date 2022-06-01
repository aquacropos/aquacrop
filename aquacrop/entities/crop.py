"""
Crop class module
"""
import numpy as np
from numba import float64, int64, types
import typing

try:
    from .crops.crop_params import crop_params
except:
    from crops.crop_params import crop_params


class Crop:
    """
    The Crop Class contains Paramaters and variables of the crop used in the simulation


    **Attributes**:\n

    `c_name`: `str`: crop name ('custom' or one of built in defaults e.g. 'Maize')

    `planting_date` : `str` : Planting Date (mm/dd)

    `harvest_date` : `str` : Latest Harvest Date (mm/dd)

    `CropType` : `int` : Crop Type (1 = Leafy vegetable, 2 = Root/tuber, 3 = Fruit/grain)

    `PlantMethod` : `int` : Planting method (0 = Transplanted, 1 =  Sown)

    `CalendarType` : `int` : Calendar Type (1 = Calendar days, 2 = Growing degree days)

    `SwitchGDD` : `int` : Convert calendar to gdd mode if inputs are given in calendar days (0 = No; 1 = Yes)



    `IrrMngt`: `dict` :  dictionary containting irrigation management information

    `IrrSchd` : `pandas.DataFrame` :  pandas DataFrame containing the Irrigation Schedule if predefined

    `FieldMngt` : `dict` :   Dictionary containing field management variables for the growing season of the crop

     A number of default program properties of type float are also specified during initialisation

    """

    def __init__(self, c_name, planting_date, harvest_date=None, **kwargs):

        self.Name = c_name

        # Assign default program properties (should not be changed without expert knowledge)

        self.fshape_b = 13.8135  # Shape factor describing the reduction in biomass production for insufficient growing degree days
        self.PctZmin = (
            70  # Initial percentage of minimum effective rooting depth
        )
        self.fshape_ex = (
            -6
        )  # Shape factor describing the effects of water stress on root expansion
        self.ETadj = 1  # Adjustment to water stress thresholds depending on daily ET0 (0 = No, 1 = Yes)
        self.Aer = 5  # Vol (%) below saturation at which stress begins to occur due to deficient aeration
        self.LagAer = (
            3  # Number of days lag before aeration stress affects crop growth
        )
        self.beta = 12  # Reduction (%) to p_lo3 when early canopy senescence is triggered
        self.a_Tr = 1  # Exponent parameter for adjustment of Kcx once senescence is triggered
        self.GermThr = 0.2  # Proportion of total water storage needed for crop to germinate
        self.CCmin = 0.05  # Minimum canopy size below which yield_ formation cannot occur
        self.MaxFlowPct = (
            100 / 3
        )  # Proportion of total flowering time (%) at which peak flowering occurs
        self.HIini = 0.01  # Initial harvest index
        self.bsted = 0.000138  # WP co2 adjustment parameter given by Steduto et al. 2007
        self.bface = (
            0.001165  # WP co2 adjustment parameter given by FACE experiments
        )

        if c_name == "custom":

            self.Name = "custom"
            self.planting_date = planting_date  # Planting Date (mm/dd)
            self.harvest_date = harvest_date  # Latest Harvest Date (mm/dd)

        elif c_name in crop_params.keys():
            self.__dict__.update(
                (k, v) for k, v in crop_params[c_name].items()
            )
            self.planting_date = planting_date  # Planting Date (mm/dd)
            self.harvest_date = harvest_date  # Latest Harvest Date (mm/dd)

        else:
            assert (
                c_name in crop_params.keys()
            ), f"Crop name not defined in crop_params dictionary, \
        if defining a custom crop please use crop name 'custom'. Otherwise use one of the \
        pre-defined crops: {crop_params.keys()}"

        # overide any pre-defined paramater with any passed by the user
        allowed_keys = {
            "fshape_b",
            "PctZmin",
            "fshape_ex",
            "ETadj",
            "Aer",
            "LagAer",
            "beta",
            "a_Tr",
            "GermThr",
            "CCmin",
            "MaxFlowPct",
            "HIini",
            "bsted",
            "bface",
            "Name",
            "CropType",
            "PlantMethod",
            "CalendarType",
            "SwitchGDD",
            "planting_date",
            "harvest_date",
            "Emergence",
            "MaxRooting",
            "Senescence",
            "Maturity",
            "HIstart",
            "Flowering",
            "YldForm",
            "GDDmethod",
            "Tbase",
            "Tupp",
            "PolHeatStress",
            "Tmax_up",
            "Tmax_lo",
            "PolColdStress",
            "Tmin_up",
            "Tmin_lo",
            "TrColdStress",
            "GDD_up",
            "GDD_lo",
            "Zmin",
            "Zmax",
            "fshape_r",
            "SxTopQ",
            "SxBotQ",
            "SeedSize",
            "PlantPop",
            "CCx",
            "CDC",
            "CGC",
            "Kcb",
            "fage",
            "WP",
            "WPy",
            "fsink",
            "HI0",
            "dHI_pre",
            "a_HI",
            "b_HI",
            "dHI0",
            "Determinant",
            "exc",
            "p_up1",
            "p_up2",
            "p_up3",
            "p_up4",
            "p_lo1",
            "p_lo2",
            "p_lo3",
            "p_lo4",
            "fshape_w1",
            "fshape_w2",
            "fshape_w3",
            "fshape_w4",
            "CGC_CD",
            "CDC_CD",
            "EmergenceCD",
            "MaxRootingCD",
            "SenescenceCD",
            "MaturityCD",
            "HIstartCD",
            "FloweringCD",
            "YldFormCD",
        }

        self.__dict__.update(
            (k, v) for k, v in kwargs.items() if k in allowed_keys
        )

        self.calculate_additional_params()

    def calculate_additional_params(
        self,
    ):
        '''
        Calculate additional parameters for all self types in mix
        '''

        # Fractional canopy cover size at emergence
        self.CC0 = self.PlantPop * self.SeedSize * 1e-8
        # Root extraction terms
        SxTopQ = self.SxTopQ
        SxBotQ = self.SxBotQ
        S1 = self.SxTopQ
        S2 = self.SxBotQ
        if S1 == S2:
            SxTop = S1
            SxBot = S2
        else:
            if SxTopQ < SxBotQ:
                S1 = SxBotQ
                S2 = SxTopQ

            xx = 3 * (S2 / (S1 - S2))
            if xx < 0.5:
                SS1 = (4 / 3.5) * S1
                SS2 = 0
            else:
                SS1 = (xx + 3.5) * (S1 / (xx + 3))
                SS2 = (xx - 0.5) * (S2 / xx)

            if SxTopQ > SxBotQ:
                SxTop = SS1
                SxBot = SS2
            else:
                SxTop = SS2
                SxBot = SS1

        self.SxTop = SxTop
        self.SxBot = SxBot

        # Water stress thresholds
        self.p_up = np.array([self.p_up1, self.p_up2, self.p_up3, self.p_up4])

        self.p_lo = np.array([self.p_lo1, self.p_lo2, self.p_lo3, self.p_lo4])

        self.fshape_w = np.array(
            [self.fshape_w1, self.fshape_w2, self.fshape_w3, self.fshape_w4]
        )


#     def flowerfun(self,xx):
#         assert self.CropType == 3
#         return (0.00558*(xx**0.63))-(0.000969*xx)-0.00383


crop_spec = [
    ("fshape_b", float64),
    ("PctZmin", float64),
    ("fshape_ex", float64),
    ("ETadj", float64),
    ("Aer", float64),
    ("LagAer", int64),
    ("beta", float64),
    ("a_Tr", float64),
    ("GermThr", float64),
    ("CCmin", float64),
    ("MaxFlowPct", float64),
    ("HIini", float64),
    ("bsted", float64),
    ("bface", float64),
    ("CropType", int64),
    ("PlantMethod", int64),
    ("CalendarType", int64),
    ("SwitchGDD", int64),
    ("EmergenceCD", int64),
    ("Canopy10PctCD", int64),
    ("MaxRootingCD", int64),
    ("SenescenceCD", int64),
    ("MaturityCD", int64),
    ("MaxCanopyCD", int64),
    ("CanopyDevEndCD", int64),
    ("HIstartCD", int64),
    ("HIendCD", int64),
    ("YldFormCD", int64),
    ("Emergence", float64),
    ("MaxRooting", float64),
    ("Senescence", float64),
    ("Maturity", float64),
    ("HIstart", float64),
    ("Flowering", float64),
    ("YldForm", float64),
    ("HIend", float64),
    ("CanopyDevEnd", float64),
    ("MaxCanopy", float64),
    ("GDDmethod", int64),
    ("Tbase", float64),
    ("Tupp", float64),
    ("PolHeatStress", int64),
    ("Tmax_up", float64),
    ("Tmax_lo", float64),
    ("PolColdStress", int64),
    ("Tmin_up", float64),
    ("Tmin_lo", float64),
    ("TrColdStress", int64),
    ("GDD_up", float64),
    ("GDD_lo", float64),
    ("Zmin", float64),
    ("Zmax", float64),
    ("fshape_r", float64),
    ("SxTopQ", float64),
    ("SxBotQ", float64),
    ("SxTop", float64),
    ("SxBot", float64),
    ("SeedSize", float64),
    ("PlantPop", int64),
    ("CCx", float64),
    ("CDC", float64),
    ("CGC", float64),
    ("CDC_CD", float64),
    ("CGC_CD", float64),
    ("Kcb", float64),
    ("fage", float64),
    ("WP", float64),
    ("WPy", float64),
    ("fsink", float64),
    ("HI0", float64),
    ("dHI_pre", float64),
    ("a_HI", float64),
    ("b_HI", float64),
    ("dHI0", float64),
    ("Determinant", int64),
    ("exc", float64),
    ("p_up", float64[:]),
    ("p_lo", float64[:]),
    ("fshape_w", float64[:]),
    ("Canopy10Pct", int64),
    ("CC0", float64),
    ("HIGC", float64),
    ("tLinSwitch", int64),
    ("dHILinear", float64),
    ("fCO2", float64),
    ("FloweringCD", int64),
    ("FloweringEnd", float64),
]


class CropStruct(object):
    """
    The Crop Class contains Paramaters and variables of the crop used in the simulation


    **Attributes**:\n



    """

    def __init__(
        self,
    ):

        # Assign default program properties (should not be changed without expert knowledge)

        self.fshape_b = 13.8135  # Shape factor describing the reduction in biomass production for insufficient growing degree days
        self.PctZmin = (
            70  # Initial percentage of minimum effective rooting depth
        )
        self.fshape_ex = (
            -6
        )  # Shape factor describing the effects of water stress on root expansion
        self.ETadj = 1  # Adjustment to water stress thresholds depending on daily ET0 (0 = No, 1 = Yes)
        self.Aer = 5  # Vol (%) below saturation at which stress begins to occur due to deficient aeration
        self.LagAer = (
            3  # Number of days lag before aeration stress affects crop growth
        )
        self.beta = 12  # Reduction (%) to p_lo3 when early canopy senescence is triggered
        self.a_Tr = 1  # Exponent parameter for adjustment of Kcx once senescence is triggered
        self.GermThr = 0.2  # Proportion of total water storage needed for crop to germinate
        self.CCmin = 0.05  # Minimum canopy size below which yield_ formation cannot occur
        self.MaxFlowPct = (
            100 / 3
        )  # Proportion of total flowering time (%) at which peak flowering occurs
        self.HIini = 0.01  # Initial harvest index
        self.bsted = 0.000138  # WP co2 adjustment parameter given by Steduto et al. 2007
        self.bface = (
            0.001165  # WP co2 adjustment parameter given by FACE experiments
        )

        # added in Read_Model_Paramaters
        self.CropType = 3  # Crop Type (1 = Leafy vegetable, 2 = Root/tuber, 3 = Fruit/grain)
        self.PlantMethod = 1  # Planting method (0 = Transplanted, 1 =  Sown)
        self.CalendarType = (
            2  # Calendar Type (1 = Calendar days, 2 = Growing degree days)
        )
        self.SwitchGDD = 0  # Convert calendar to gdd mode if inputs are given in calendar days (0 = No; 1 = Yes)

        self.EmergenceCD = 0
        self.Canopy10PctCD = 0
        self.MaxRootingCD = 0
        self.SenescenceCD = 0
        self.MaturityCD = 0
        self.MaxCanopyCD = 0
        self.CanopyDevEndCD = 0
        self.HIstartCD = 0
        self.HIendCD = 0
        self.YldFormCD = 0

        self.Emergence = 80  # Growing degree/Calendar days from sowing to emergence/transplant recovery
        self.MaxRooting = (
            1420  # Growing degree/Calendar days from sowing to maximum rooting
        )
        self.Senescence = (
            1420  # Growing degree/Calendar days from sowing to senescence
        )
        self.Maturity = (
            1670  # Growing degree/Calendar days from sowing to maturity
        )
        self.HIstart = 850  # Growing degree/Calendar days from sowing to start of yield_ formation
        self.Flowering = 190  # Duration of flowering in growing degree/calendar days (-999 for non-fruit/grain crops)
        self.YldForm = (
            775  # Duration of yield_ formation in growing degree/calendar days
        )
        self.HIend = 0
        self.MaxCanopy = 0
        self.CanopyDevEnd = 0
        self.Canopy10Pct = 0

        self.GDDmethod = 2  # Growing degree day calculation method
        self.Tbase = (
            8  # Base temperature (degC) below which growth does not progress
        )
        self.Tupp = 30  # Upper temperature (degC) above which crop development no longer increases
        self.PolHeatStress = (
            1  # Pollination affected by heat stress (0 = No, 1 = Yes)
        )
        self.Tmax_up = 40  # Maximum air temperature (degC) above which pollination begins to fail
        self.Tmax_lo = 45  # Maximum air temperature (degC) at which pollination completely fails
        self.PolColdStress = (
            1  # Pollination affected by cold stress (0 = No, 1 = Yes)
        )
        self.Tmin_up = 10  # Minimum air temperature (degC) below which pollination begins to fail
        self.Tmin_lo = 5  # Minimum air temperature (degC) at which pollination completely fails
        self.TrColdStress = 1  # Transpiration affected by cold temperature stress (0 = No, 1 = Yes)
        self.GDD_up = 12  # Minimum growing degree days (degC/day) required for full crop transpiration potential
        self.GDD_lo = 0  # Growing degree days (degC/day) at which no crop transpiration occurs
        self.Zmin = 0.3  # Minimum effective rooting depth (m)
        self.Zmax = 1.7  # Maximum rooting depth (m)
        self.fshape_r = 1.3  # Shape factor describing root expansion
        self.SxTopQ = 0.0480  # Maximum root water extraction at top of the root zone (m3/m3/day)
        self.SxBotQ = 0.0117  # Maximum root water extraction at the bottom of the root zone (m3/m3/day)

        self.SxTop = 0.0
        self.SxBot = 0.0

        self.SeedSize = 6.5  # Soil surface area (cm2) covered by an individual seedling at 90% emergence
        self.PlantPop = 75_000  # Number of plants per hectare
        self.CCx = 0.96  # Maximum canopy cover (fraction of soil cover)
        self.CDC = (
            0.01  # Canopy decline coefficient (fraction per gdd/calendar day)
        )
        self.CGC = 0.0125  # Canopy growth coefficient (fraction per gdd)
        self.CDC_CD = (
            0.01  # Canopy decline coefficient (fraction per gdd/calendar day)
        )
        self.CGC_CD = 0.0125  # Canopy growth coefficient (fraction per gdd)
        self.Kcb = 1.05  # Crop coefficient when canopy growth is complete but prior to senescence
        self.fage = 0.3  #  Decline of crop coefficient due to ageing (%/day)
        self.WP = 33.7  # Water productivity normalized for ET0 and C02 (g/m2)
        self.WPy = 100  # Adjustment of water productivity in yield_ formation stage (% of WP)
        self.fsink = 0.5  # Crop performance under elevated atmospheric CO2 concentration (%/100)
        self.HI0 = 0.48  # Reference harvest index
        self.dHI_pre = 0  # Possible increase of harvest index due to water stress before flowering (%)
        self.a_HI = 7  # Coefficient describing positive impact on harvest index of restricted vegetative growth during yield_ formation
        self.b_HI = 3  # Coefficient describing negative impact on harvest index of stomatal closure during yield_ formation
        self.dHI0 = 15  # Maximum allowable increase of harvest index above reference value
        self.Determinant = (
            1  # Crop Determinancy (0 = Indeterminant, 1 = Determinant)
        )
        self.exc = 50  # Excess of potential fruits
        self.p_up = np.zeros(
            4
        )  # Upper soil water depletion threshold for water stress effects on affect canopy expansion
        self.p_lo = np.zeros(
            4
        )  # Lower soil water depletion threshold for water stress effects on canopy expansion
        self.fshape_w = np.ones(
            4
        )  # Shape factor describing water stress effects on canopy expansion

        self.CC0 = 0.0

        self.HIGC = 0.0
        self.tLinSwitch = 0
        self.dHILinear = 0.0

        self.fCO2 = 0.0

        self.FloweringCD = 0
        self.FloweringEnd = 0.0


CropStructNT = typing.NamedTuple("CropStructNT", crop_spec)
CropStructNT_type_sig = types.NamedTuple(
    tuple(dict(crop_spec).values()), CropStructNT
)
