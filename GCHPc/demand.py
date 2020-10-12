from enum import Enum
import numpy as np

class ComodityType(Enum):
    ELECTRICITY = 1
    HEAT = 2
    STEAM = 3

comodity_type_label = {ComodityType.ELECTRICITY:"Electricity", ComodityType.HEAT:"Heat", ComodityType.STEAM:"Steam"}


class Demand(object):
    def set_properties(self, **kwargs):
        if 't_supply' in kwargs: self.t_supply = float(kwargs['t_supply'])
        if 't_return' in kwargs: self.t_return = float(kwargs['t_return'])

    def __init__(self, comodity_type: ComodityType, curve: np.ndarray, **kwargs):
        assert type(comodity_type) == ComodityType
        assert type(curve) == np.ndarray

        self.comodity_type = comodity_type
        self.curve = curve

        if kwargs is not None: self.set_properties(**kwargs)