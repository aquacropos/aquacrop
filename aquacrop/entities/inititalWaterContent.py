from numba import float64, int64, boolean, types

class InitialWaterContent:
    """
    Initial water content Class defines water content at start of sim

    Attributes:

        wc_type (str):  Type of value ('Prop' = 'WP'/'FC'/'SAT'; 'Num' = XXX m3/m3; 'Pct' = % taw))

        method (str):  method ('Depth' = Interpolate depth points; 'Layer' = Constant value for each soil layer)

        depth_layer (list): location in soil profile (soil layer or depth)

        value (list): value at each location given in depth_layer

    """

    def __init__(self, wc_type="Prop", method="Layer", depth_layer=[1], value=["FC"]):

        self.wc_type = wc_type
        self.method = method
        self.depth_layer = depth_layer
        self.value = value
