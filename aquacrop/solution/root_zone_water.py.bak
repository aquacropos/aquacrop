import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.soilProfile import SoilProfileNT_typ_sig
except:
    from entities.soilProfile import SoilProfileNT_typ_sig
    

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.soilProfile import SoilProfileNT
    from numpy import ndarray




# temporary name for compiled module
cc = CC("solution_root_zone_water")
@njit
@cc.export("root_zone_water", (SoilProfileNT_typ_sig,f8,f8[:],f8,f8,f8))
def root_zone_water(
    prof: "SoilProfileNT_typ_sig",
    InitCond_Zroot: float,
    InitCond_th: "ndarray",
    Soil_zTop: float,
    Crop_Zmin: float,
    Crop_Aer: float,
) -> Tuple[float, float, float, float, float, float, float, float, float, float, float]:
    """
    Function to calculate actual and total available water in the rootzone at current time step


    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=14" target="_blank">Reference Manual: root-zone water calculations</a> (pg. 5-8)


    Arguments:

        prof (SoilProfile): jit class Object containing soil paramaters

        InitCond_Zroot (float): Initial rooting depth

        InitCond_th (np.array): Initial water content

        Soil_zTop (float): Top soil depth

        Crop_Zmin (float): crop minimum rooting depth

        Crop_Aer (int): number of aeration stress days

    Returns:

        WrAct (float):  Actual rootzone water content

        Dr_Zt (float):  topsoil depletion

        Dr_Rz (float):  rootzone depletion

        TAW_Zt (float):  topsoil total available water

        TAW_Rz (float):  rootzone total available water

        thRZ_Act (float):  Actual rootzone water content

        thRZ_S (float):  rootzone water content at saturation

        thRZ_FC (float):  rootzone water content at field capacity

        thRZ_WP (float):  rootzone water content at wilting point

        thRZ_Dry (float):  rootzone water content at air dry

        thRZ_Aer (float):  rootzone water content at aeration stress threshold 


    """

    ## Calculate root zone water content and available water ##
    # Compartments covered by the root zone
    rootdepth = round(np.maximum(InitCond_Zroot, Crop_Zmin), 2)
    comp_sto = np.argwhere(prof.dzsum >= rootdepth).flatten()[0]

    # Initialise counters
    WrAct = 0
    WrS = 0
    WrFC = 0
    WrWP = 0
    WrDry = 0
    WrAer = 0
    for ii in range(comp_sto + 1):
        # Fraction of compartment covered by root zone
        if prof.dzsum[ii] > rootdepth:
            factor = 1 - ((prof.dzsum[ii] - rootdepth) / prof.dz[ii])
        else:
            factor = 1

        # Actual water storage in root zone (mm)
        WrAct = WrAct + round(factor * 1000 * InitCond_th[ii] * prof.dz[ii], 2)
        # Water storage in root zone at saturation (mm)
        WrS = WrS + round(factor * 1000 * prof.th_s[ii] * prof.dz[ii], 2)
        # Water storage in root zone at field capacity (mm)
        WrFC = WrFC + round(factor * 1000 * prof.th_fc[ii] * prof.dz[ii], 2)
        # Water storage in root zone at permanent wilting point (mm)
        WrWP = WrWP + round(factor * 1000 * prof.th_wp[ii] * prof.dz[ii], 2)
        # Water storage in root zone at air dry (mm)
        WrDry = WrDry + round(factor * 1000 * prof.th_dry[ii] * prof.dz[ii], 2)
        # Water storage in root zone at aeration stress threshold (mm)
        WrAer = WrAer + round(factor * 1000 * (prof.th_s[ii] - (Crop_Aer / 100)) * prof.dz[ii], 2)

    if WrAct < 0:
        WrAct = 0

    # define total available water, depletion, root zone water content
    # taw = TAW()
    # Dr = Dr()
    # thRZ = RootZoneWater()

    # Calculate total available water (m3/m3)
    TAW_Rz = max(WrFC - WrWP, 0.0)
    # Calculate soil water depletion (mm)
    Dr_Rz = min(WrFC - WrAct, TAW_Rz)

    # Actual root zone water content (m3/m3)
    thRZ_Act = WrAct / (rootdepth * 1000)
    # Root zone water content at saturation (m3/m3)
    thRZ_S = WrS / (rootdepth * 1000)
    # Root zone water content at field capacity (m3/m3)
    thRZ_FC = WrFC / (rootdepth * 1000)
    # Root zone water content at permanent wilting point (m3/m3)
    thRZ_WP = WrWP / (rootdepth * 1000)
    # Root zone water content at air dry (m3/m3)
    thRZ_Dry = WrDry / (rootdepth * 1000)
    # Root zone water content at aeration stress threshold (m3/m3)
    thRZ_Aer = WrAer / (rootdepth * 1000)

    # print('inside')

    # thRZ = thRZNT(
    # Act=thRZ_Act,
    # S=thRZ_S,
    # FC=thRZ_FC,
    # WP=thRZ_WP,
    # Dry=thRZ_Dry,
    # Aer=thRZ_Aer,
    # )
    # print(thRZ)


    ## Calculate top soil water content and available water ##
    if rootdepth > Soil_zTop:
        # Determine compartments covered by the top soil
        ztopdepth = round(Soil_zTop, 2)
        comp_sto = np.sum(prof.dzsum <= ztopdepth)
        # Initialise counters
        WrAct_Zt = 0
        WrFC_Zt = 0
        WrWP_Zt = 0
        # Calculate water storage in top soil
        assert comp_sto > 0

        for ii in range(comp_sto):

            # Fraction of compartment covered by root zone
            if prof.dzsum[ii] > ztopdepth:
                factor = 1 - ((prof.dzsum[ii] - ztopdepth) / prof.dz[ii])
            else:
                factor = 1

            # Actual water storage in top soil (mm)
            WrAct_Zt = WrAct_Zt + (factor * 1000 * InitCond_th[ii] * prof.dz[ii])
            # Water storage in top soil at field capacity (mm)
            WrFC_Zt = WrFC_Zt + (factor * 1000 * prof.th_fc[ii] * prof.dz[ii])
            # Water storage in top soil at permanent wilting point (mm)
            WrWP_Zt = WrWP_Zt + (factor * 1000 * prof.th_wp[ii] * prof.dz[ii])

        # Ensure available water in top soil is not less than zero
        if WrAct_Zt < 0:
            WrAct_Zt = 0

        # Calculate total available water in top soil (m3/m3)
        TAW_Zt = max(WrFC_Zt - WrWP_Zt, 0)
        # Calculate depletion in top soil (mm)
        Dr_Zt = min(WrFC_Zt - WrAct_Zt, TAW_Zt)
    else:
        # Set top soil depletions and taw to root zone values
        Dr_Zt = Dr_Rz
        TAW_Zt = TAW_Rz


    return (
        WrAct,
        Dr_Zt,
        Dr_Rz,
        TAW_Zt,
        TAW_Rz,
        thRZ_Act,
        thRZ_S,
        thRZ_FC,
        thRZ_WP,
        thRZ_Dry,
        thRZ_Aer,
    )

if __name__ == "__main__":
    cc.compile()
