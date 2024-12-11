"""
Crop class module
"""
import numpy as np
import typing

try:
    from .crops.crop_params import crop_params
except:
    from crops.crop_params import crop_params


class Crop:
    """
    The Crop Class contains paramaters and variables of the crop used in the simulation

    Most Crop attributes can be found in the `crops.crop_params.py` file
    
    A number of default program properties of type float are also specified during initialisation

    ```
    Initialization example:
    
    crop = Crop('Maize', planting_date='05/01')
    ```

    Attributes:

        c_name (str): crop name ('custom' or one of built in defaults e.g. 'Maize')

        planting_date (str): Planting Date (mm/dd)

        harvest_date (str): Latest Harvest Date (mm/dd)


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
        self.ET0dorm = 0 # Duration of dormant crop period (during early senescence) in terms of cumulative reference ET (mm)
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
        self.SwitchGDDType = 'mean' # calculate GDD phenology based on mean of CD phenology across entire simulation period (mean/median)

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
            "ET0dorm",
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
            "SwitchGDDType",
            "planting_date",
            "harvest_date",
            "Emergence",
            "MaxRooting",
            "Senescence",
            "Maturity",
            "HIstart",
            "Flowering",
            "YldForm",
            "YldWC",
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
