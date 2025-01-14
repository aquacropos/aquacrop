import pandas as pd
import numpy as np

from .modelConstants import ModelConstants


class Soil:
    """
    The Soil Class contains Paramaters and variables of the soil used in the simulation

    More float attributes are specified in the initialisation of the class

    Attributes:

        profile (pandas.DataFrame): holds soil profile information

        Profile (SoilProfile): jit class object holdsing soil profile information

        Hydrology (pandas.DataFrame): holds soil layer hydrology informaiton

        Comp (pandas.DataFrame): holds soil compartment information


    """

    def __init__(
        self,
        soil_type,
        dz=[0.1] * 12,
        adj_rew=1,
        rew=9.0,
        calc_cn=0,
        cn=61.0,
        z_res=ModelConstants.NO_VALUE,
        evap_z_surf=0.04,
        evap_z_min=0.15,
        evap_z_max=0.30,
        kex=1.1,
        f_evap=4,
        f_wrel_exp=0.4,
        fwcc=50,
        z_cn=0.3,
        z_germ=0.3,
        adj_cn=1,
        fshape_cr=16,
        z_top=0.1,
    ):

        self.Name = soil_type

        self.zSoil = sum(dz)  # Total thickness of soil profile (m)
        self.nComp = len(dz)  # Total number of soil compartments
        self.nLayer = 0  # Total number of soil layers
        self.adj_rew = adj_rew  # Adjust default value for readily evaporable water (0 = No, 1 = Yes)
        self.rew = rew  # Readily evaporable water (mm) (only used if adjusting from default value)
        self.calc_cn = calc_cn  # adjust Curve number based on Ksat
        self.cn = cn  # Curve number  (0 = No, 1 = Yes)
        self.z_res = z_res  # Depth of restrictive soil layer (set to negative value if not present)

        # Assign default program properties (should not be changed without expert knowledge)
        self.evap_z_surf = (
            evap_z_surf  # Thickness of soil surface skin evaporation layer (m)
        )
        self.evap_z_min = (
            evap_z_min  # Minimum thickness of full soil surface evaporation layer (m)
        )
        self.evap_z_max = (
            evap_z_max  # Maximum thickness of full soil surface evaporation layer (m)
        )
        self.kex = kex  # Maximum soil evaporation coefficient
        self.f_evap = (
            f_evap  # Shape factor describing reduction in soil evaporation in stage 2.
        )
        self.f_wrel_exp = f_wrel_exp  # Proportional value of Wrel at which soil evaporation layer expands
        self.fwcc = fwcc  # Maximum coefficient for soil evaporation reduction due to sheltering effect of withered canopy
        self.z_cn = z_cn  # Thickness of soil surface (m) used to calculate water content to adjust curve number
        self.z_germ = z_germ  # Thickness of soil surface (m) used to calculate water content for germination
        self.adj_cn = (
            adj_cn  # Adjust curve number for antecedent moisture content (0: No, 1: Yes)
        )
        self.fshape_cr = fshape_cr  # Capillary rise shape factor
        self.z_top = max(
            z_top, dz[0]
        )  # Thickness of soil surface layer for water stress comparisons (m)

        if soil_type == "custom":
            self.create_df(dz)

        elif soil_type == "Clay":
            self.cn = 77
            self.calc_cn = 0
            self.rew = 14
            self.create_df(dz)
            self.add_layer(sum(dz), 0.39, 0.54, 0.55, 35, 100)

        elif soil_type == "ClayLoam":
            self.cn = 72
            self.calc_cn = 0
            self.rew = 11
            self.create_df(dz)
            self.add_layer(sum(dz), 0.23, 0.39, 0.5, 125, 100)

        elif soil_type == 'Default':
            self.cn = 61
            self.calc_cn = 0
            self.rew = 9
            self.create_df(dz)
            self.add_layer(sum(dz), 0.1, 0.3, 0.5, 500, 100)

        elif soil_type == "Loam":
            self.cn = 61
            self.calc_cn = 0
            self.rew = 9
            self.create_df(dz)
            self.add_layer(sum(dz), 0.15, 0.31, 0.46, 500, 100)

        elif soil_type == "LoamySand":
            self.cn = 46
            self.calc_cn = 0
            self.rew = 5
            self.create_df(dz)
            self.add_layer(sum(dz), 0.08, 0.16, 0.38, 2200, 100)

        elif soil_type == "Sand":
            self.cn = 46
            self.calc_cn = 0
            self.rew = 4
            self.create_df(dz)
            self.add_layer(sum(dz), 0.06, 0.13, 0.36, 3000, 100)

        elif soil_type == "SandyClay":
            self.cn = 77
            self.calc_cn = 0
            self.rew = 10
            self.create_df(dz)
            self.add_layer(sum(dz), 0.27, 0.39, 0.5, 35, 100)

        elif soil_type == "SandyClayLoam":
            self.cn = 72
            self.calc_cn = 0
            self.rew = 9
            self.create_df(dz)
            self.add_layer(sum(dz), 0.20, 0.32, 0.47, 225, 100)

        elif soil_type == "SandyLoam":
            self.cn = 46
            self.calc_cn = 0
            self.rew = 7
            self.create_df(dz)
            self.add_layer(sum(dz), 0.10, 0.22, 0.41, 1200, 100)

        elif soil_type == "Silt":
            self.cn = 61
            self.calc_cn = 0
            self.rew = 11
            self.create_df(dz)
            self.add_layer(sum(dz), 0.09, 0.33, 0.43, 500, 100)

        elif soil_type == "SiltClayLoam":
            self.cn = 72
            self.calc_cn = 0
            self.rew = 13
            self.create_df(dz)
            self.add_layer(sum(dz), 0.23, 0.44, 0.52, 150, 100)

        elif soil_type == "SiltLoam":
            self.cn = 61
            self.calc_cn = 0
            self.rew = 11
            self.create_df(dz)
            self.add_layer(sum(dz), 0.13, 0.33, 0.46, 575, 100)

        elif soil_type == "SiltClay":
            self.cn = 72
            self.calc_cn = 0
            self.rew = 14
            self.create_df(dz)
            self.add_layer(sum(dz), 0.32, 0.50, 0.54, 100, 100)

        elif soil_type == "Paddy":
            self.cn = 77
            self.calc_cn = 0
            self.rew = 10
            self.create_df(dz)
            self.add_layer(0.5, 0.32, 0.50, 0.54, 15, 100)
            self.add_layer(1.5, 0.39, 0.54, 0.55, 2, 100)

        elif soil_type == "ac_TunisLocal":
            self.cn = 72
            self.calc_cn = 0
            self.rew = 11
            dz = [0.1] * 6 + [0.15] * 5 + [0.2]
            self.create_df(dz)
            self.add_layer(0.3, 0.24, 0.40, 0.50, 155, 100)
            self.add_layer(1.7, 0.11, 0.33, 0.46, 500, 100)
 
        else:
            print("wrong soil type")
            assert 1 == 2

    def __repr__(self):
        for key in self.__dict__:
            if key != "profile":
                print(f"{key}: {getattr(self,key)}")

        return " "

    def create_df(self, dz):

        self.profile = pd.DataFrame(
            np.empty((len(dz), 4)), columns=["Comp", "Layer", "dz", "dzsum"]
        )
        self.profile.dz = dz
        self.profile.dzsum = np.cumsum(self.profile.dz).round(2)
        self.profile.Comp = np.arange(len(dz))
        self.profile.Layer = np.nan

        self.profile["zBot"] = self.profile.dzsum
        self.profile["z_top"] = self.profile["zBot"] - self.profile.dz
        self.profile["zMid"] = (self.profile["z_top"] + self.profile["zBot"]) / 2

    def calculate_soil_hydraulic_properties(self, Sand, Clay, OrgMat, DF=1):

        """
        Function to calculate soil hydraulic properties, given textural inputs.
        Calculations use pedotransfer function equations described in Saxton and Rawls (2006)


        """

        # do calculations

        # Water content at permanent wilting point
        Pred_thWP = (
            -(0.024 * Sand)
            + (0.487 * Clay)
            + (0.006 * OrgMat)
            + (0.005 * Sand * OrgMat)
            - (0.013 * Clay * OrgMat)
            + (0.068 * Sand * Clay)
            + 0.031
        )

        th_wp = Pred_thWP + (0.14 * Pred_thWP) - 0.02

        # Water content at field capacity and saturation
        Pred_thFC = (
            -(0.251 * Sand)
            + (0.195 * Clay)
            + (0.011 * OrgMat)
            + (0.006 * Sand * OrgMat)
            - (0.027 * Clay * OrgMat)
            + (0.452 * Sand * Clay)
            + 0.299
        )

        PredAdj_thFC = Pred_thFC + (
            (1.283 * (np.power(Pred_thFC, 2))) - (0.374 * Pred_thFC) - 0.015
        )

        Pred_thS33 = (
            (0.278 * Sand)
            + (0.034 * Clay)
            + (0.022 * OrgMat)
            - (0.018 * Sand * OrgMat)
            - (0.027 * Clay * OrgMat)
            - (0.584 * Sand * Clay)
            + 0.078
        )

        PredAdj_thS33 = Pred_thS33 + ((0.636 * Pred_thS33) - 0.107)
        Pred_thS = (PredAdj_thFC + PredAdj_thS33) + ((-0.097 * Sand) + 0.043)

        pN = (1 - Pred_thS) * 2.65
        pDF = pN * DF
        PorosComp = (1 - (pDF / 2.65)) - (1 - (pN / 2.65))
        PorosCompOM = 1 - (pDF / 2.65)

        DensAdj_thFC = PredAdj_thFC + (0.2 * PorosComp)
        DensAdj_thS = PorosCompOM

        th_fc = DensAdj_thFC
        th_s = DensAdj_thS

        # Saturated hydraulic conductivity (mm/day)
        lmbda = 1 / ((np.log(1500) - np.log(33)) / (np.log(th_fc) - np.log(th_wp)))
        Ksat = (1930 * (th_s - th_fc) ** (3 - lmbda)) * 24

        # Water content at air dry
        th_dry = th_wp / 2

        # round values
        th_dry = round(10_000 * th_dry) / 10_000
        th_wp = round(1000 * th_wp) / 1000
        th_fc = round(1000 * th_fc) / 1000
        th_s = round(1000 * th_s) / 1000
        Ksat = round(10 * Ksat) / 10

        return th_wp, th_fc, th_s, Ksat

    def add_layer_from_texture(self, thickness, Sand, Clay, OrgMat, penetrability):

        th_wp, th_fc, th_s, Ksat = self.calculate_soil_hydraulic_properties(
            Sand / 100, Clay / 100, OrgMat
        )

        self.add_layer(thickness, th_wp, th_fc, th_s, Ksat, penetrability)

    def add_layer(self, thickness, thWP, thFC, thS, Ksat, penetrability):

        self.nLayer += 1

        num_layers = len(self.profile.dropna().Layer.unique())

        new_layer = num_layers + 1

        if new_layer == 1:
            self.profile.loc[
                (round(thickness, 2) >= round(self.profile.dzsum, 2)), "Layer"
            ] = new_layer
        else:
            last = self.profile[self.profile.Layer == new_layer - 1].dzsum.values[-1]
            self.profile.loc[
                (thickness + last >= self.profile.dzsum) & (self.profile.Layer.isna()),
                "Layer",
            ] = new_layer

        self.profile.loc[
            self.profile.Layer == new_layer, "th_dry"
        ] = self.profile.Layer.map({new_layer: thWP / 2})
        self.profile.loc[
            self.profile.Layer == new_layer, "th_wp"
        ] = self.profile.Layer.map({new_layer: thWP})
        self.profile.loc[
            self.profile.Layer == new_layer, "th_fc"
        ] = self.profile.Layer.map({new_layer: thFC})
        self.profile.loc[
            self.profile.Layer == new_layer, "th_s"
        ] = self.profile.Layer.map({new_layer: thS})
        self.profile.loc[
            self.profile.Layer == new_layer, "Ksat"
        ] = self.profile.Layer.map({new_layer: Ksat})
        self.profile.loc[
            self.profile.Layer == new_layer, "penetrability"
        ] = self.profile.Layer.map({new_layer: penetrability})

        # Calculate drainage characteristic (tau)
        # Calculations use equation given by Raes et al. 2012
        tau = round(0.0866 * (Ksat**0.35), 2)
        if tau > 1:
            tau = 1
        elif tau < 0:
            tau = 0

        self.profile.loc[
            self.profile.Layer == new_layer, "tau"
        ] = self.profile.Layer.map({new_layer: tau})

    def fill_nan(
        self,
    ):

        self.profile = self.profile.ffill()

        self.profile.dz = self.profile.dz.round(2)

        self.profile.dzsum = self.profile.dz.cumsum().round(2)

        self.zSoil = round(self.profile.dz.sum(), 2)

        self.nComp = len(self.profile)

        self.profile.Layer = self.profile.Layer.astype(int)

    def add_capillary_rise_params(
        self,
    ):
        # Calculate capillary rise parameters for all soil layers
        # Only do calculation if water table is present. Calculations use equations
        # described in Raes et al. (2012)
        prof = self.profile

        hydf = prof.groupby("Layer").mean().drop(["dz", "dzsum"], axis=1)

        hydf["aCR"] = 0
        hydf["bCR"] = 0

        for layer in hydf.index.unique():
            layer = int(layer)

            soil = hydf.loc[layer]

            thwp = soil.th_wp
            thfc = soil.th_fc
            ths = soil.th_s
            Ksat = soil.Ksat

            # usually just initialise here (both 0), but temporarily hard-coding for sandy-loam for testing
            aCR =  0
            bCR =  0

            # Define aCR and bCR calculations for each Soil Class 
            aCR_sandy=-0.3112 - Ksat/100000
            bCR_sandy=-1.4936 + 0.2416*np.log(Ksat)

            aCR_loamy=-0.4986 + 9*Ksat/100000
            bCR_loamy=-2.1320 + 0.4778*np.log(Ksat)

            aCR_sandy_clayey=-0.5677 - 4*Ksat/100000
            bCR_sandy_clayey=-3.7189 + 0.5922*np.log(Ksat)

            aCR_silty_clayey=-0.6366 + 8*Ksat/10000
            bCR_silty_clayey=-1.9165 + 0.7063*np.log(Ksat)

            # NEW (V7) aCR bCR calculations logic
            # Assign aCR/bCR based on soil class definition from FAO
            if ths <= 0.55:
                if thwp >= 0.20:
                    if (ths >= 0.49) and (thfc >= 0.40):
                        aCR=aCR_silty_clayey
                        bCR=bCR_silty_clayey
                    else:
                        aCR=aCR_sandy_clayey
                        bCR=bCR_sandy_clayey
                else:
                    if thfc < 0.23:
                        aCR=aCR_sandy
                        bCR=bCR_sandy
                    else:
                        if (thwp > 0.16) and (Ksat < 100):
                            aCR=aCR_sandy_clayey
                            bCR=bCR_sandy_clayey
                        else:
                            if (thwp < 0.06) and (thfc < 0.28) and (Ksat > 750):
                                aCR=aCR_sandy
                                bCR=bCR_sandy
                            else:
                                aCR=aCR_loamy
                                bCR=bCR_loamy
            else:
                aCR=aCR_silty_clayey
                bCR=bCR_silty_clayey






            # OLD (V6) aCR bCR calculation logic
            # if (
            #     (thwp >= 0.04)
            #     and (thwp <= 0.15)
            #     and (thfc >= 0.09)
            #     and (thfc <= 0.28)
            #     and (ths >= 0.32)
            #     and (ths <= 0.51)
            # ):

            #     # Sandy soil class
            #     if (Ksat >= 200) and (Ksat <= 2000):
            #         aCR = -0.3112 - (Ksat * (1e-5))
            #         bCR = -1.4936 + (0.2416 * np.log(Ksat))
            #     elif Ksat < 200:
            #         aCR = -0.3112 - (200 * (1e-5))
            #         bCR = -1.4936 + (0.2416 * np.log(200))
            #     elif Ksat > 2000:
            #         aCR = -0.3112 - (2000 * (1e-5))
            #         bCR = -1.4936 + (0.2416 * np.log(2000))

            # elif (
            #     (thwp >= 0.06)
            #     and (thwp <= 0.20)
            #     and (thfc >= 0.23)
            #     and (thfc <= 0.42)
            #     and (ths >= 0.42)
            #     and (ths <= 0.55)
            # ):

            #     # Loamy soil class
            #     if (Ksat >= 100) and (Ksat <= 750):
            #         aCR = -0.4986 + (9 * (1e-5) * Ksat)
            #         bCR = -2.132 + (0.4778 * np.log(Ksat))
            #     elif Ksat < 100:
            #         aCR = -0.4986 + (9 * (1e-5) * 100)
            #         bCR = -2.132 + (0.4778 * np.log(100))
            #     elif Ksat > 750:
            #         aCR = -0.4986 + (9 * (1e-5) * 750)
            #         bCR = -2.132 + (0.4778 * np.log(750))

            # elif (
            #     (thwp >= 0.16)
            #     and (thwp <= 0.34)
            #     and (thfc >= 0.25)
            #     and (thfc <= 0.45)
            #     and (ths >= 0.40)
            #     and (ths <= 0.53)
            # ):

            #     # Sandy clayey soil class
            #     if (Ksat >= 5) and (Ksat <= 150):
            #         aCR = -0.5677 - (4 * (1e-5) * Ksat)
            #         bCR = -3.7189 + (0.5922 * np.log(Ksat))
            #     elif Ksat < 5:
            #         aCR = -0.5677 - (4 * (1e-5) * 5)
            #         bCR = -3.7189 + (0.5922 * np.log(5))
            #     elif Ksat > 150:
            #         aCR = -0.5677 - (4 * (1e-5) * 150)
            #         bCR = -3.7189 + (0.5922 * np.log(150))

            # elif (
            #     (thwp >= 0.20)
            #     and (thwp <= 0.42)
            #     and (thfc >= 0.40)
            #     and (thfc <= 0.58)
            #     and (ths >= 0.49)
            #     and (ths <= 0.58)
            # ):

            #     # Silty clayey soil class
            #     if (Ksat >= 1) and (Ksat <= 150):
            #         aCR = -0.6366 + (8 * (1e-4) * Ksat)
            #         bCR = -1.9165 + (0.7063 * np.log(Ksat))
            #     elif Ksat < 1:
            #         aCR = -0.6366 + (8 * (1e-4) * 1)
            #         bCR = -1.9165 + (0.7063 * np.log(1))
            #     elif Ksat > 150:
            #         aCR = -0.6366 + (8 * (1e-4) * 150)
            #         bCR = -1.9165 + (0.7063 * np.log(150))

            assert aCR != 0
            assert bCR != 0

            prof.loc[prof.Layer == layer, "aCR"] = prof.Layer.map({layer: aCR})
            prof.loc[prof.Layer == layer, "bCR"] = prof.Layer.map({layer: bCR})

        self.profile = prof
