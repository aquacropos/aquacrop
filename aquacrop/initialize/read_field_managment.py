from ..entities.fieldManagement import FieldMngtStruct


def read_field_management(ParamStruct, FieldMngt, FallowFieldMngt):
    """
    turn field management classes into jit classes

    *Arguments:*\n

    `ParamStruct` : `ParamStruct` :  Contains model crop and soil paramaters

    `FieldMngt` : `FieldMngt` :  irr mngt params object

    `FallowFieldMngt` : `FieldMngt` :  irr mngt params object

    *Returns:*

    `ParamStruct` : `ParamStruct` :  updated with field management info


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
