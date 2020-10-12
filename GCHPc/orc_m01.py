from enum import Enum
import numpy as np
from GCHPc.brine_properties import Brine

class BinaryType(Enum):
    ocr_acc = 0 #ACC cooled orc
    orc_wct = 1 #orc with wet cooling tower
    orc_dwc = 2 #orc with direct wate cooling

class ORC():
    def n_cycle(self, Thi: float) -> float:
        '''
        Returns the cycle efficiency of the orc
        :param Th_i: brine input temperature in °C (float)
        :return: cycle efficiency in % (float)
        '''
        if self.type == BinaryType.ocr_acc:
            self.n = round(-0.0005182 * Thi ** 2 + 0.2307 * Thi - 10.71, 2)
        else:
            self.n = round(0.08434 * Thi - 0.4457, 2)
        return self.n

    def corr_t0(self,Thi: float, t0: float = 10.3) -> float:
        return ((Thi - t0) / (Thi - 10.3)) * ((556.6 + Thi) / (546.3 + Thi + t0))

    def get_t_bo(self, t_bi: float) -> float:
        '''
        Calculates the brine output temperature of the orc

        :param t_bi: brine inlet temperature in °C (float)
        :return: brine outlet temperature in °C (float)
        '''
        if self.type == BinaryType.ocr_acc:
            self.t_bo = round(0.0317 * t_bi + 60.9,1)
        else:
            self.t_bo = round(0.1211 * t_bi + 44.138,1)
        return self.t_bo

    def get_dp_brine(self, Th_i: float, m_brine: float) -> float:
        return 2

    def calculate_output(self, flow_rate: np.ndarray, brine: Brine) -> np.ndarray:
        '''
        Calculates the net electrical output of the orc based on the supplied flow rate(s) and brine properties
        :param flow_rate: brine mass flow rate in kg/s (float)
        :param brine: brine properties (Brine)
        :return: electrical output in MWh (x time step of array)
        In case just one element is supplied by the flow_rate array, the returned value is in MW.
        '''
        assert flow_rate is not None, "flow rate not set"
        assert brine is not None, "brine not set"

        if self.t_bi == 0:
            self.t_bi = brine.temperature
        brine.set_cp()
        f = (self.t_bi - self.t_bo) * brine.cp * self.n / 100
        orc_output = flow_rate * f

        return orc_output / 1000000

    def __init__(self, name: str, type=BinaryType.ocr_acc, **kwargs):
        '''
        Initiates Class ORC

        :param name: name of the orc installation (str)
        :param type: orc type (BinaryType)
        :param kwargs: 't_bi' -> brine input temperature in °C (float)
                       'm_brine -> brine flow rate towards the orc in kg/s (float)
        '''
        self.name = name
        self.type = type
        self.t_bi = 0

        if 't_bi' in kwargs:
            self.t_bi = float(kwargs['t_bi'])
            self.t_bo = self.get_t_bo(float(kwargs['t_bi']))
            self.n = self.n_cycle(float(kwargs['t_bi']))

        if 't_bi' in kwargs and 'm_brine' in kwargs:
            self.m_brine = float(kwargs['m_brine'])
            self.dP_brine = self.get_dp_brine(Th_i=float(kwargs['Thi']), m_brine=float(kwargs['m_brine']))

if __name__ == '__main__':
    t_in = [108.,165.,122.,165.,140.,152., 180.,]
    orc_type = [BinaryType.ocr_acc, BinaryType.orc_wct, BinaryType.orc_dwc, BinaryType.orc_wct, BinaryType.orc_wct, BinaryType.ocr_acc, BinaryType.ocr_acc]
    n_acc = []
    n = []
    orc = ORC(name='none')
    i = 0

    for val in t_in:
        n_acc.append(orc.n_cycle(Thi=val))

    print (n_acc)

    for i in range(len(t_in)):
        orc.type = orc_type[i]
        n.append(orc.n_cycle(Thi=t_in[i]))

    print(n)

    t0 = [16.8, 15, 5, 23.9, 13, 23, 17.5]
    n_corr = []

    for i in range(6):
        corr = orc.corr_t0(Thi=t_in[i], t0=t0[i])
        n_corr.append(n[i] * corr)

    print(n_corr)