

class ParamStruct:
    """
    The ParamStruct class contains the bulk of model Paramaters. 
    In general these will not change over the course of the simulation


    Attributes:

        Soil (Soil): Soil object contains data and paramaters related to the soil

        FallowFieldMngt (FieldMngt): Object containing field management variables for the off season (fallow periods)

        NCrops (int): Number of crop types to be simulated

        SpecifiedPlantCalander (str):  Specified crop rotation calendar (yield_ or N)

        CropChoices (list): List of crop type names in each simulated season

        CO2data (pd.Series): CO2 data indexed by year

        CO2 (CO2): object containing reference and current co2 concentration

        water_table (int): Water table present (1=yes, 0=no)

        z_gw (np.array): water_table depth (mm) for each day of simulation

        zGW_dates (np.array): Corresponding dates to the z_gw values

        WTMethod (str): 'Constant' or 'Variable'

        CropList (list): List of Crop Objects which contain paramaters for all the differnet crops used in simulations

        python_crop_list (list): List of Crop Objects, one for each season

        python_fallow_crop (Crop): Crop object for off season

        Seasonal_Crop_List (list): List of CropStructs, one for each season (jit class objects)

        crop_name_list (list): List of crop names, one for each season

        Fallow_Crop (CropStruct): CropStruct object (jit class) for off season

        Fallow_Crop_Name (str): name of fallow crop

        """

    def __init__(self):

        # soil
        self.Soil = 0

        # field management
        self.FallowFieldMngt = 0

        # variables extracted from cropmix.txt
        self.NCrops = 0
        self.SpecifiedPlantCalander = ""
        self.RotationFilename = ""

        # calculated Co2 variables
        self.CO2data = []
        self.CO2 = 0
        self.co2_concentration_adj = None

        # water table
        self.water_table = 0
        self.z_gw = []
        self.zGW_dates = []
        self.WTMethod = ""

        # crops
        self.CropList = []
        self.python_crop_list = []
        self.python_fallow_crop = 0
        self.Seasonal_Crop_List = []
        self.crop_name_list = []
        self.Fallow_Crop = 0
        self.Fallow_Crop_Name = ""