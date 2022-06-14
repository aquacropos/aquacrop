import numpy as np

from ..entities.soilProfile import SoilProfile, SoilProfileNT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.paramStruct import ParamStruct


def create_soil_profile(param_struct: "ParamStruct") -> "ParamStruct":
    """
    funciton to create soil profile namedTuple to store soil info.
    Its much faster to access the info when its in a namedTuple
    compared to a dataframe

    Arguments:

        param_struct (ParamStruct):  Contains model crop and soil paramaters

    Returns:

        param_struct (ParamStruct):  updated with soil profile


    """

    profile = SoilProfile(int(param_struct.Soil.profile.shape[0]))

    pdf = param_struct.Soil.profile.astype("float64")

    profile.dz = pdf.dz.values
    profile.dzsum = pdf.dzsum.values
    profile.zBot = pdf.zBot.values
    profile.z_top = pdf.z_top.values
    profile.zMid = pdf.zMid.values

    profile.Comp = np.int64(pdf.Comp.values)
    profile.Layer = np.int64(pdf.Layer.values)
    # profile.Layer_dz = pdf.Layer_dz.values
    profile.th_wp = pdf.th_wp.values
    profile.th_fc = pdf.th_fc.values
    profile.th_s = pdf.th_s.values

    profile.Ksat = pdf.Ksat.values
    profile.Penetrability = pdf.penetrability.values
    profile.th_dry = pdf.th_dry.values
    profile.tau = pdf.tau.values
    profile.th_fc_Adj = pdf.th_fc_Adj.values

    if param_struct.water_table == 1:
        profile.aCR = pdf.aCR.values
        profile.bCR = pdf.bCR.values
    else:
        profile.aCR = pdf.dz.values * 0.0
        profile.bCR = pdf.dz.values * 0.0

    # param_struct.Soil.profile = profile

    param_struct.Soil.Profile = SoilProfileNT(
        dz=profile.dz,
        dzsum=profile.dzsum,
        zBot=profile.zBot,
        z_top=profile.z_top,
        zMid=profile.zMid,
        Comp=profile.Comp,
        Layer=profile.Layer,
        th_wp=profile.th_wp,
        th_fc=profile.th_fc,
        th_s=profile.th_s,
        Ksat=profile.Ksat,
        Penetrability=profile.Penetrability,
        th_dry=profile.th_dry,
        tau=profile.tau,
        th_fc_Adj=profile.th_fc_Adj,
        aCR=profile.aCR,
        bCR=profile.bCR,
    )

    return param_struct
