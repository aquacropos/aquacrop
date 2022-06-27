import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.soilProfile import SoilProfileNT_typ_sig
except:
    from entities.soilProfile import SoilProfileNT_typ_sig
    
# temporary name for compiled module
cc = CC("solution_rainfall_partition")


from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.soilProfile import SoilProfileNT
    from numpy import ndarray


@cc.export("rainfall_partition", (f8,f8[:],i8,f8,b1,f8,f8,f8,f8,f8,f8,SoilProfileNT_typ_sig))
def rainfall_partition(
    precipitation: float,
    InitCond_th: "ndarray",
    NewCond_DaySubmerged: int,
    FieldMngt_SRinhb: float,
    FieldMngt_Bunds: bool,
    FieldMngt_zBund: float,
    FieldMngt_CNadjPct: float,
    Soil_CN: float,
    Soil_AdjCN: float,
    Soil_zCN: float,
    Soil_nComp: int,
    prof: "SoilProfileNT",
) -> Tuple[float, float, float]:
    """
    Function to partition rainfall into surface runoff and infiltration using the curve number approach


    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=57" target="_blank">Reference Manual: rainfall partition calculations</a> (pg. 48-51)


    Arguments:

        precipitation (float): Percipitation on current day

        InitCond_th (numpy.array): InitCond object containing model paramaters

        NewCond_DaySubmerged (int): number of days submerged

        FieldMngt_SRinhb (float): field management params

        FieldMngt_Bunds (bool): field management params

        FieldMngt_zBund (float): bund height

        FieldMngt_CNadjPct (float): curve number adjustment percent

        Soil_CN (float): curve number

        Soil_AdjCN (float): adjusted curve number

        Soil_zCN (float` :

        Soil_nComp (float): number of compartments

        prof (SoilProfile): Soil object

    Returns:

        Runoff (float): Total Suface Runoff

        Infl (float): Total Infiltration

        NewCond_DaySubmerged (float): number of days submerged


    """

    # can probs make this faster by doing a if precipitation=0 loop

    ## Store initial conditions for updating ##
    # NewCond = InitCond

    ## Calculate runoff ##
    if (FieldMngt_SRinhb == False) and ((FieldMngt_Bunds == False) or (FieldMngt_zBund < 0.001)):
        # Surface runoff is not inhibited and no soil bunds are on field
        # Reset submerged days
        NewCond_DaySubmerged = 0
        # Adjust curve number for field management practices
        cn = Soil_CN * (1 + (FieldMngt_CNadjPct / 100))
        if Soil_AdjCN == 1:  # Adjust cn for antecedent moisture
            # Calculate upper and lowe curve number bounds
            CNbot = round(
                1.4 * (np.exp(-14 * np.log(10)))
                + (0.507 * cn)
                - (0.00374 * cn ** 2)
                + (0.0000867 * cn ** 3)
            )
            CNtop = round(
                5.6 * (np.exp(-14 * np.log(10)))
                + (2.33 * cn)
                - (0.0209 * cn ** 2)
                + (0.000076 * cn ** 3)
            )
            # Check which compartment cover depth of top soil used to adjust
            # curve number
            comp_sto_array = prof.dzsum[prof.dzsum >= Soil_zCN]
            if comp_sto_array.shape[0] == 0:
                comp_sto = int(Soil_nComp)
            else:
                comp_sto = int(Soil_nComp - comp_sto_array.shape[0])

            comp_sto+=1
            
            # Calculate weighting factors by compartment
            xx = 0
            wrel = np.zeros(comp_sto)
            for ii in range(comp_sto):
                if prof.dzsum[ii] > Soil_zCN:
                    prof.dzsum[ii] = Soil_zCN

                wx = 1.016 * (1 - np.exp(-4.16 * (prof.dzsum[ii] / Soil_zCN)))
                wrel[ii] = wx - xx
                if wrel[ii] < 0:
                    wrel[ii] = 0
                elif wrel[ii] > 1:
                    wrel[ii] = 1

                xx = wx

            # Calculate relative wetness of top soil
            wet_top = 0
            # prof = prof

            for ii in range(comp_sto):
                th = max(prof.th_wp[ii], InitCond_th[ii])
                wet_top = wet_top + (
                    wrel[ii] * ((th - prof.th_wp[ii]) / (prof.th_fc[ii] - prof.th_wp[ii]))
                )

            # Calculate adjusted curve number
            if wet_top > 1:
                wet_top = 1
            elif wet_top < 0:
                wet_top = 0

            cn = round(CNbot + (CNtop - CNbot) * wet_top)

        # Partition rainfall into runoff and infiltration (mm)
        S = (25400 / cn) - 254
        term = precipitation - ((5 / 100) * S)
        if term <= 0:
            Runoff = 0
            Infl = precipitation
        else:
            Runoff = (term ** 2) / (precipitation + (1 - (5 / 100)) * S)
            Infl = precipitation - Runoff

    else:
        # bunds on field, therefore no surface runoff
        Runoff = 0
        Infl = precipitation

    return Runoff, Infl, NewCond_DaySubmerged

if __name__ == "__main__":
    cc.compile()
