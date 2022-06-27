from ..entities.fieldManagement import FieldMngtStruct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.fieldManagement import FieldMngt, FieldMngtStruct
    from aquacrop.entities.paramStruct import ParamStruct

def read_field_management(
    ParamStruct: "ParamStruct",
    FieldMngt: "FieldMngt",
    FallowFieldMngt: "FieldMngt") -> "ParamStruct":

    """
    store field management variables as FieldMngtStruct object

    Arguments:

        ParamStruct (ParamStruct):  Contains model crop and soil paramaters

        FieldMngt (FieldMngt):  field mngt params

        FallowFieldMngt (FieldMngt): fallow field mngt params

    Returns:

        ParamStruct (ParamStruct):  updated ParamStruct with field management info


    """

    field_mngt_struct = FieldMngtStruct()
    for a, v in FieldMngt.__dict__.items():
        if hasattr(field_mngt_struct, a):
            field_mngt_struct.__setattr__(a, v)

    fallow_field_mngt_struct = FieldMngtStruct()
    for a, v in FallowFieldMngt.__dict__.items():
        if hasattr(fallow_field_mngt_struct, a):
            fallow_field_mngt_struct.__setattr__(a, v)

    ParamStruct.FieldMngt = field_mngt_struct
    ParamStruct.FallowFieldMngt = fallow_field_mngt_struct

    return ParamStruct
