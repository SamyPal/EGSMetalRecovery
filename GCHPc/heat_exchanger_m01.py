from GCHPc.brine_properties import Brine
import logging
from math import log
from enum import Enum

class HeatXType(Enum):
    hX_plate = 0
    hX_shellAndTube = 1


def DTlm(Thi, Tho, Tci, Tco) -> float:
    '''
    Log temperature difference

    :param Thi: hot/brine input temperature in °C (float)
    :param Tho: hot/brine output temperature in °C (float)
    :param Tci: hx input temperature cold/fresh side in °C (float)
    :param Tco: hx output temperature cold/fresh side in °C  (float)
    :return: DTlm (float)
    '''

    if Thi <= Tco:
        logging.error(f"DTlm Tco {Tco} cannot be heated above Thi {Thi}.  Assume Thi-Tco == 1")
        Tco = Thi - 1
    if Tho <= Tci:
        logging.error(f"DTlm Tho {Tho} cannot be cooled down below Tci {Tci}.  Assume Tho-Tci == 1")
        Tci = Tho - 1
    dT1 = Thi - Tco
    dT2 = Tho - Tci
    assert dT1 > 0 and dT2 > 0
    if (dT1 == dT2):
        return dT1
    DTlm = (dT1 - dT2) / log(dT1 / dT2)
    return DTlm


def ahx(Thi, mhi, Tci, Tco, duty, brine: Brine =None, hx_type=HeatXType.hX_plate, F=1, U=0):
    '''
    Calculates area of the heat exchanger

    :param Thi: brine input temperature in °C (float)
    :param mhi: mass flow brine in kg/s (float)
    :param Tci: hx input temperature cold side in °C (float)
    :param Tco: hx output temperature cold side in °C (float)
    :param duty: heat delivering in Watt (float)
    :param brine: brine (brine)
    :param hx_type: type of heat exchanger (Enum)
    :param F: log mean temperature difference correction factor - equals 1 for cross flow hx (float)
    :param U: heat transfer coefficient in W/m2.K -  if 0 then use 1500 of plate hX or 5500 for s&t hX(float)
    :return: (list) area - area of the heat exchanger in m2, Tho - output temperature hot/brine side in °C
    '''

    if brine is None:
        brine = Brine(name='default', temperature=Thi)

    if U ==0:
        U = 1500 if hx_type == HeatXType.hX_plate else 5500

    Tho = round(Thi - duty / (mhi * brine.cp),2)
    print("Tho as computed by ahx", Tho, "Tci in ahx", Tci)
    return {'area': duty / (U * F * DTlm(Thi, Tho, Tci, Tco)), 't_ho': Tho}

class HeatX():
    def set_ahx(self,**kwargs):
        if kwargs is not None: self.set_property(**kwargs)

        result = ahx(self.t_hi, self.m_hi, self.t_ci, self.t_co, self.duty, self.brine, self.type, self.F, self.U)
        self.ahx = result['area']
        self.t_ho = result['t_ho']

    def set_property(self, **kwargs):
        '''
        Set key properties of the heat exchanger

        :param kwargs:
          t_hi: brine input temperature (°C)
          m_hi: mass flow brine (kg/s)
          t_ci: hx input temperature cold side (°C)
          t_co: hx output temperature cold side (°C)
          duty: heat delivering (W)
          tds: total dissolved solids brine (kg/kg)
          U: heat transfer coefficient (W/m2.K)
          F: log mean temperature difference correction factor (equals 1 for cross flow hX)

        :return: Nothing
        '''
        if 't_hi' in kwargs: self.t_hi = float(kwargs['t_hi'])
        if 'm_hi' in kwargs: self.m_hi = float(kwargs['m_hi'])
        if 't_ci' in kwargs: self.t_ci = float(kwargs['t_ci'])
        if 't_co' in kwargs: self.t_co = float(kwargs['t_co'])
        if 'duty' in kwargs: self.duty = float(kwargs['duty'])
        if 'F' in kwargs:
            self.F = float(kwargs['F'])
        else:
            self.F = 1
        if 'U' in kwargs:
            self.U = float(kwargs['U'])
        elif self.type == HeatXType.hX_plate:
            self.U = 1500
        elif self.type == HeatXType.hX_shellAndTube:
            self.U = 5500
        if 'pressure' in kwargs:
            self.p_i = float(kwargs['pressure'])
        else:
            self.p_i = 1
        if 'tds' in kwargs:
            self.brine = Brine(name='newBrine', tds=float(kwargs['tds']), temperature=float(kwargs['t_hi']), pressure=self.p_i)

    def __init__(self, name: str, type:HeatXType, **kwargs):
        self.name = name
        self.type = type

        if kwargs is not None: self.set_property(**kwargs)

if __name__ == '__main__':
    brine = Brine(name='test', temperature=120, tds = 0.1)
    result = ahx(Thi= 120, mhi= 50, Tci = 60, Tco = 110, duty=5000000, brine = brine)
    newHx = HeatX(name='newHx', type=HeatXType.hX_plate, t_hi = 120, m_hi = 50, t_ci=60, t_co = 110, duty = 5000000, tds = .1)
    newHx.set_ahx()
