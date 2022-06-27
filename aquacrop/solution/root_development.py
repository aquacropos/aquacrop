import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.soilProfile import SoilProfileNT_typ_sig
    from ..entities.crop import CropStructNT_type_sig

except:
    from entities.soilProfile import SoilProfileNT_typ_sig
    from entities.crop import CropStructNT_type_sig
    
# temporary name for compiled module
cc = CC("solution_root_development")

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.soilProfile import SoilProfileNT
    from aquacrop.entities.crop import CropStructNT
    from numpy import ndarray


@cc.export("root_development", (CropStructNT_type_sig,SoilProfileNT_typ_sig,f8,f8,f8,f8,f8,f8,f8[:],f8,f8,b1,f8,f8,f8,f8,b1,i8))
def root_development(
    Crop: "CropStructNT",
    prof: "SoilProfileNT",
    NewCond_DAP: float,
    NewCond_Zroot: float,
    NewCond_DelayedCDs: float,
    NewCond_GDDcum: float,
    NewCond_DelayedGDDs: float,
    NewCond_TrRatio: float,
    NewCond_th: "ndarray",
    NewCond_CC: float,
    NewCond_CC_NS: float,
    NewCond_Germination: bool,
    NewCond_rCor: float,
    NewCond_Tpot: float,
    NewCond_zGW: float,
    gdd: float,
    growing_season: bool,
    water_table_presence: int,
    ) -> float:
    """
    Function to calculate root zone expansion

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=46" target="_blank">Reference Manual: root developement equations</a> (pg. 37-41)


    Arguments:

        Crop (CropStructNT): crop params

        prof (SoilProfileNT): soilv profile paramaters

        NewCond_DAP (float): days after planting

        NewCond_Zroot (float): root depth

        NewCond_DelayedCDs (float): delayed calendar days

        NewCond_GDDcum (float): cumulative growing degree days

        NewCond_TrRatio (float): transpiration ratio

        NewCond_CC (float): canopy cover

        NewCond_CC_NS (float): canopy cover no-stress

        NewCond_Germination (float): germination flag

        NewCond_rCor (float): 

        NewCond_DAP (float): days after planting

        NewCond_Tpot (float): potential transpiration

        NewCond_zGW (float): groundwater depth

        gdd (float): Growing degree days on current day

        growing_season (bool): is growing season (True or Flase)

        water_table_presence (int): water table present (True=1 or Flase=0)


    Returns:

        NewCond_Zroot (float): updated rooting depth


    """
    # Store initial conditions for updating
    # NewCond = InitCond

    # save initial zroot
    Zroot_init = float(NewCond_Zroot) * 1.0
    Soil_nLayer = np.unique(prof.Layer).shape[0]

    # Calculate root expansion (if in growing season)
    if growing_season == True:
        # If today is first day of season, root depth is equal to minimum depth
        if NewCond_DAP == 1:
            NewCond_Zroot = float(Crop.Zmin) * 1.0
            Zroot_init = float(Crop.Zmin) * 1.0

        # Adjust time for any delayed development
        if Crop.CalendarType == 1:
            tAdj = NewCond_DAP - NewCond_DelayedCDs
        elif Crop.CalendarType == 2:
            tAdj = NewCond_GDDcum - NewCond_DelayedGDDs

        # Calculate root expansion #
        Zini = Crop.Zmin * (Crop.PctZmin / 100)
        t0 = round((Crop.Emergence / 2))
        tmax = Crop.MaxRooting
        if Crop.CalendarType == 1:
            tOld = tAdj - 1
        elif Crop.CalendarType == 2:
            tOld = tAdj - gdd

        # Potential root depth on previous day
        if tOld >= tmax:
            ZrOld = Crop.Zmax
        elif tOld <= t0:
            ZrOld = Zini
        else:
            X = (tOld - t0) / (tmax - t0)
            ZrOld = Zini + (Crop.Zmax - Zini) * np.power(X, 1 / Crop.fshape_r)

        if ZrOld < Crop.Zmin:
            ZrOld = Crop.Zmin

        # Potential root depth on current day
        if tAdj >= tmax:
            Zr = Crop.Zmax
        elif tAdj <= t0:
            Zr = Zini
        else:
            X = (tAdj - t0) / (tmax - t0)
            Zr = Zini + (Crop.Zmax - Zini) * np.power(X, 1 / Crop.fshape_r)

        if Zr < Crop.Zmin:
            Zr = Crop.Zmin

        # Store Zr as potential value
        ZrPot = Zr

        # Determine rate of change
        dZr = Zr - ZrOld

        # Adjust expansion rate for presence of restrictive soil horizons
        if Zr > Crop.Zmin:
            layeri = 1
            l_idx = np.argwhere(prof.Layer == layeri).flatten()
            Zsoil = prof.dz[l_idx].sum()
            while (round(Zsoil, 2) <= Crop.Zmin) and (layeri < Soil_nLayer):
                layeri = layeri + 1
                l_idx = np.argwhere(prof.Layer == layeri).flatten()
                Zsoil = Zsoil + prof.dz[l_idx].sum()

            soil_layer_dz = prof.dz[l_idx].sum()
            layer_comp = l_idx[0]
            # soil_layer = prof.Layer[layeri]
            ZrAdj = Crop.Zmin
            ZrRemain = Zr - Crop.Zmin
            deltaZ = Zsoil - Crop.Zmin
            EndProf = False
            while EndProf == False:
                ZrTest = ZrAdj + (ZrRemain * (prof.Penetrability[layer_comp] / 100))
                if (
                    (layeri == Soil_nLayer)
                    or (prof.Penetrability[layer_comp] == 0)
                    or (ZrTest <= Zsoil)
                ):
                    ZrOUT = ZrTest
                    EndProf = True
                else:
                    ZrAdj = Zsoil
                    ZrRemain = ZrRemain - (deltaZ / (prof.Penetrability[layer_comp] / 100))
                    layeri = layeri + 1
                    l_idx = np.argwhere(prof.Layer == layeri).flatten()
                    layer_comp = l_idx[0]
                    soil_layer_dz = prof.dz[l_idx].sum()
                    Zsoil = Zsoil + soil_layer_dz
                    deltaZ = soil_layer_dz

            # Correct Zr and dZr for effects of restrictive horizons
            Zr = ZrOUT
            dZr = Zr - ZrOld

        # Adjust rate of expansion for any stomatal water stress
        if NewCond_TrRatio < 0.9999:
            if Crop.fshape_ex >= 0:
                dZr = dZr * NewCond_TrRatio
            else:
                fAdj = (np.exp(NewCond_TrRatio * Crop.fshape_ex) - 1) / (np.exp(Crop.fshape_ex) - 1)
                dZr = dZr * fAdj

        # print(NewCond.dap,NewCond.th)

        # Adjust rate of root expansion for dry soil at expansion front
        if dZr > 0.001:
            # Define water stress threshold for inhibition of root expansion
            pZexp = Crop.p_up[1] + ((1 - Crop.p_up[1]) / 2)
            # Define potential new root depth
            ZiTmp = float(Zroot_init + dZr)
            # Find compartment that root zone will expand in to
            # compi_index = prof.dzsum[prof.dzsum>=ZiTmp].index[0] # have changed to index
            idx = np.argwhere(prof.dzsum >= ZiTmp).flatten()[0]
            prof = prof
            # Get taw in compartment
            layeri = prof.Layer[idx]
            TAWprof = prof.th_fc[idx] - prof.th_wp[idx]
            # Define stress threshold
            thThr = prof.th_fc[idx] - (pZexp * TAWprof)
            # Check for stress conditions
            if NewCond_th[idx] < thThr:
                # Root expansion limited by water content at expansion front
                if NewCond_th[idx] <= prof.th_wp[idx]:

                    # Expansion fully inhibited
                    dZr = 0
                else:
                    # Expansion partially inhibited
                    Wrel = (prof.th_fc[idx] - NewCond_th[idx]) / TAWprof
                    Drel = 1 - ((1 - Wrel) / (1 - pZexp))
                    Ks = 1 - (
                        (np.exp(Drel * Crop.fshape_w[1]) - 1) / (np.exp(Crop.fshape_w[1]) - 1)
                    )
                    dZr = dZr * Ks

        # Adjust for early senescence
        if (NewCond_CC <= 0) and (NewCond_CC_NS > 0.5):
            dZr = 0

        # Adjust root expansion for failure to germinate (roots cannot expand
        # if crop has not germinated)
        if NewCond_Germination == False:
            dZr = 0

        # Get new rooting depth
        NewCond_Zroot = float(Zroot_init + dZr)

        # Adjust root density if deepening is restricted due to dry subsoil
        # and/or restrictive layers
        if NewCond_Zroot < ZrPot:
            NewCond_rCor = (
                2 * (ZrPot / NewCond_Zroot) * ((Crop.SxTop + Crop.SxBot) / 2) - Crop.SxTop
            ) / Crop.SxBot

            if NewCond_Tpot > 0:
                NewCond_rCor = NewCond_rCor * NewCond_TrRatio
                if NewCond_rCor < 1:
                    NewCond_rCor = 1

        else:
            NewCond_rCor = 1

        # Limit rooting depth if groundwater table is present (roots cannot
        # develop below the water table)
        if (water_table_presence == 1) and (NewCond_zGW > 0):
            if NewCond_Zroot > NewCond_zGW:
                NewCond_Zroot = float(NewCond_zGW)
                if NewCond_Zroot < Crop.Zmin:
                    NewCond_Zroot = float(Crop.Zmin)

    else:
        # No root system outside of the growing season
        NewCond_Zroot = 0

    return NewCond_Zroot

if __name__ == "__main__":
    cc.compile()
