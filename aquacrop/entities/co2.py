from numba import float64


spec = [
    ("ref_concentration", float64),
    ("Cur rentConc", float64),
]


class CO2(object):

    """

    **Attributes:**\n


    `ref_concentration` : `float` : reference CO2 concentration

    `current_concentration` : `float` : current CO2 concentration

    """

    def __init__(self):
        self.ref_concentration = 369.41
        self.current_concentration = 0.0


