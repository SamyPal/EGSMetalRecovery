from enum import Enum
from GCHPc.curve_calculator import calculate, read_curve
from GCHPc.brine_properties import Brine
from GCHPc.orc_m01 import BinaryType, ORC
from GCHPc.heat_exchanger_m01 import HeatXType, HeatX
from GCHPc.demand import Demand, ComodityType
from GCHPc.units import PressureUnits
import numpy as np
import matplotlib.pyplot as plt

'''
----------------------------------- GEOTHERMAL CHP PLANT MODEL -----------------------------------
Model for a low temperature geothermal CHP plant based on 1410166_ENE_EFRO910_kostenmodel.docx
The orc model is valid up to temperature of 150°C. It is based on:
    - Walraven, B. Laenen and W. D'haeseleer, 2015. Economic system optimization of air-cooled organic Rankine cycles 
      powered by low-temperature geothermal heat sources. Energy 80: 104-113
    - Walraven, D., Laenen, B., D’haeseleer, W., 2015. Minimizing the levelized cost of electricity production from
      low-temperature geothermal heat sources with ORCs: Water or air cooled? Applied Energy, 142C: 144-153
'''


class GCHPpType(Enum):
    heat_only = 0
    parallel = 1
    series = 2
    preheat_parallel = 3
    hb4 = 4
    parallel_serries = 5


def sum_demands_by_t_cutoff(demands: {}, t_cutoff: float, t_pinch: float = 0.) -> {}:
    '''
    Devides the heat demands in two groups - a high temperature and a low temperature group - based on t_cutoff
    :param demands: a dictionary of heat demands (Demand)
    :param t_cutoff: dividing temperature in °C (float)
    :param t_pinch: pinch temperature of the low-temperature group heat exhanger in °C (float)
    :return: dictionary containing:
             ht_demand: demand curve equal to the sum of the demands with a supply temperature larger then t_cutoff
             ht_t_supply: the maximal supply temperature of the demands with a supply temperature larger then t_cutoff
             ht_t_return: the minimal return temperature of the demands with a supply temperature larger then t_cutoff
             lt_demand: demand curve equal to the sum of the demands with a supply temperature less or equal then t_cutoff
             lt_t_supply: the maximal supply temperature of the demands with a supply temperature less or equal then t_cutoff
             lt_t_return: the minimal return temperature of the demands with a supply temperature less or equal then t_cutoff
    '''
    assert demands != {}, 'no heat demands set'

    key = list(demands.keys())[0]
    ht_demand = np.zeros_like(demands[key].curve)
    ht_t_supply = demands[key].t_supply
    ht_t_return = demands[key].t_return
    lt_demand = np.zeros_like(demands[key].curve)
    lt_t_supply = 0.
    lt_t_return = ht_t_return
    t_cutoff = t_cutoff + t_pinch

    for key in demands:
        if demands[key].t_supply > t_cutoff:
            ht_demand = ht_demand + demands[key].curve
            if ht_t_return > demands[key].t_return: ht_t_return = demands[key].t_return
            if ht_t_supply < demands[key].t_supply: ht_t_supply = demands[key].t_supply
        else:
            lt_demand = lt_demand + demands[key].curve
            if lt_t_return > demands[key].t_return: lt_t_return = demands[key].t_return
            if lt_t_supply < demands[key].t_supply: lt_t_supply = demands[key].t_supply

    return {'ht_demand': ht_demand, 'ht_t_supply': ht_t_supply, 'ht_t_return': ht_t_return, \
            'lt_demand': lt_demand, 'lt_t_supply': lt_t_supply, 'lt_t_return': lt_t_return}


def calculate_ht_mass_flow(gchpp, cutoff: float = .6, t_pinch: float = 1.) -> {}:
    '''
    Calculates the brine mass flow r over the high temperature heat exchanger for a parallel CHP configuration and the
    corresponding heat delivered
    :param gchpp: an instance of GCHPp
    :param cutoff: value used to define what fraction of the maximal thermal power demand should be covered by geothermal energy
                   - value between 0 and 1 - (float)
    :param t_pinch: pinch temperature of the high temperature / parallel heat exchanger in °C (float)
    :return: dictionary containing:
             ht_supply: geothermal heat supplied in MW x time step of the time curve (np.ndarray)
             ht_flow: brine mass flow rate over the high temperature heat exchanger in kg/s (np.ndarray)
             ht_power: the maximal thermal power of the high temperature / parallel heat supply in MW (float)
    '''
    assert hasattr(gchpp,'ht_demand'), "ht_demand for gchpp has not been set"
    assert hasattr(gchpp,'brine'), "brine for gchpp has not been set"

    ht_supply = np.copy(gchpp.ht_demand.curve) * 1000000    # power_max supplied by the source is calculated in Watt; heat demand is in MW x timestep of array

    gchpp.brine.temperature = gchpp.t_bi
    gchpp.brine.set_cp()

    power_max = min((gchpp.t_bi - gchpp.ht_demand.t_return - t_pinch) * gchpp.brine.cp * gchpp.m_bi, \
                ht_supply.max() * cutoff)

    ht_supply[ht_supply > power_max] = power_max
    div = gchpp.brine.cp * (gchpp.t_bi - gchpp.ht_demand.t_return - t_pinch)
    ht_flow = np.around(ht_supply / div, 2)

    return {'ht_supply': ht_supply / 1000000, 'ht_flow': ht_flow, 'ht_power': power_max / 1000000}


def calculate_lt_supply(gchpp, cuttoff: float = .6, t_pinch: float = 0.) -> {}:
    '''

    :param gchpp: an instance of GCHPp
    :param cuttoff: value used to define what fraction of the maximal thermal power demand should be covered by geothermal energy
                   - value between 0 and 1 - (float)
    :param t_pinch: pinch temperature of the low temperature / series heat exchanger in °C (float)
    :return: dictionary containing:
             lt_supply: geothermal heat supplied in MW x time step of the time curve (np.ndarray)
             lt_power: the maximal thermal power of the low temperature / series heat supply in MW (float)
    '''
    lt_supply = np.copy(gchpp.lt_demand.curve) * 1000000

    gchpp.brine.temperature = gchpp.lt_demand.t_supply
    gchpp.brine.set_cp()

    t_o = max(gchpp.lt_demand.t_return, gchpp.t_bo)
    t_i = min(gchpp.t_th_o)

    power_max = min((t_i - t_o - t_pinch) * gchpp.brine.cp * gchpp.m_bi, \
                lt_supply.max() * cuttoff)

    lt_supply[lt_supply > power_max] = power_max

    return {'lt_supply': lt_supply / 1000000, 'lt_power': power_max / 1000000}


def calculate_orc_mass_flow(gchpp, flow_range = [.6,1.2]) -> np.ndarray:
    '''
    Calculates the brine flow rate towards the orc over
    :param gchpp: an instance of the class GCHPp
    :param flow_range: maximal and minimal deviation of the optimal (design) flow rate towards the orc - fraction (list)
    :return: array containing the flow rate towards he orc over the year - flow rate in kg/s (np.ndarray)
    '''
    if gchpp.type != GCHPpType.heat_only:
        assert hasattr(gchpp,'m_ht'), "ht mass flow has not been set"
    else:
        orc_flow = np.zeros_like(gchpp.m_ht)

    orc_flow = np.full_like(gchpp.m_ht, gchpp.m_bi)
    orc_flow = np.round(orc_flow - gchpp.m_ht,2)
    '''
    As a first assumption, the average residual flow rate is used to assess the annual power output of the orc.
    Ideally, the flow rate that results in the highest annual power output should be used.
    '''
    flow_min = round(np.average(orc_flow) * flow_range[0],2)
    flow_max = round(np.average(orc_flow) * flow_range[1],2)

    orc_flow[orc_flow > flow_max] = flow_max
    orc_flow[orc_flow < flow_min] = 0

    return orc_flow


def calculate_t_hto(gchpp):
    '''
    Calculates the mixing temperature of the brine derived from the output ot the orc and from the high temperature / parallel
    heat exhanger for high temperature heat supply
    :param gchpp: an instance of GCHPp
    :return: an array containing the mixing temperature of the two high temperature branches - orc & HT heat supply - of the CHP plant in °C
    '''
    gchpp.brine.temperature = gchpp.t_bi
    gchpp.brine.set_cp()

    t_orc_o = np.full_like(gchpp.m_ht, gchpp.orc.t_bo)
    gchpp.m_ht = np.full_like(gchpp.m_ht, gchpp.m_bi)
    gchpp.m_ht = gchpp.m_ht - gchpp.m_orc
    t_ht_o = gchpp.t_bi - gchpp.ht_supply * 1000000 / (gchpp.brine.cp * gchpp.m_ht)

    f_orc = gchpp.m_orc / gchpp.m_bi

    return np.around(t_ht_o + (t_orc_o - t_ht_o) * f_orc, 2)


def calculate_t_bo(gchpp):
    '''
    Calculates the return temperature of the brine
    :param gchpp: an instance of GCHPp
    :return: an array containing the brine return temperature the CHP plant in °C
    '''
    if not hasattr(gchpp, 't_th_o'):
        gchpp.t_th_o = calculate_t_hto(gchpp)

    gchpp.brine.temperature = np.average(gchpp.t_th_o)
    gchpp.brine.set_cp()

    t_bo = np.zeros_like(gchpp.m_ht)

    t_bo = gchpp.t_th_o - gchpp.lt_supply * 1000000 /(gchpp.brine.cp * gchpp.m_bi)
    return np.around(t_bo, 2)


class GCHPp():
    def set_properties(self, **kwargs):
        if 't_bi' in kwargs: self.t_bi = float(kwargs['t_bi'])
        if 't_bo' in kwargs: self.t_bo = float(kwargs['t_bo'])
        if 'm_bi' in kwargs: self.m_bi = float(kwargs['m_bi'])
        if 'type' in kwargs: self.type = GCHPpType(kwargs['type'])

    def remove_orc(self):
        self.orc = None

    def set_orc(self, type: BinaryType, Thi: float, name: str = 'ORC01'):
        self.orc = ORC(name=name, type=type, Thi=Thi)

    def add_heat_demand(self, name: str, demand: Demand):
        self.demands[name] = demand

    def remove_heat_demand(self, name: str):
        del self.heat_demands[name]

    def add_hX(self, name: str, hX: HeatX ):
        self.hXs[name] = hX

    def remove_hX(self, name: str):
        del self.hXs[name]

    def set_heat_demand(self, demands: Demand):
        for key, demand in demands:
            if demand['T_supply'] > self.t_bo: HT_supply = HT_supply + demand['curve']


    def __init__(self, name: str, **kwargs):
        self.name = name
        self.t_bo = 35  #°C
        self.demands = {}

        if kwargs is not None: self.set_properties(**kwargs)


if __name__ == '__main__':

    flow = np.linspace(start=150. , stop=200., num=5, dtype=float)
    out = []

    for q in flow:
        newCHPp = GCHPp(name='test', m_bi = q, t_bi = 110., t_bo = 35., type=GCHPpType.parallel_serries)
        newCHPp.brine = Brine(name = 'balmatt', tds = .03, temperature = newCHPp.t_bi, pressure = 10., pressure_unit=PressureUnits.bar)
        newCHPp.m_bi = q * newCHPp.brine.density / 3600

        newCHPp.ht_demand = Demand(comodity_type=ComodityType.HEAT, curve=np.array([3.]), t_supply=120, t_return=80)
        newCHPp.lt_demand = Demand(comodity_type=ComodityType.HEAT, curve=np.array([5.]), t_supply=60, t_return=40)

        result = calculate_ht_mass_flow(newCHPp, cutoff=.6)
        print(result)

        newCHPp.ht_supply = result['ht_supply']
        newCHPp.m_ht = result['ht_flow']

        newCHPp.m_orc = calculate_orc_mass_flow(newCHPp)
        newCHPp.orc = ORC(name='orc1', type=BinaryType.ocr_acc, t_bi=newCHPp.t_bi)
        result = newCHPp.orc.calculate_output(flow_rate=newCHPp.m_orc, brine=newCHPp.brine)
        print('Output ORC (MW): ', result)

        out.append(result[0])

        newCHPp.t_th_o = calculate_t_hto(newCHPp)
        print(newCHPp.orc.__dict__)

        result = calculate_lt_supply(newCHPp, cuttoff=1.)
        newCHPp.lt_supply = result['lt_supply']
        print(result)

    print(out)
    plt.plot(flow, out, 'b-')
    plt.xlabel('flow rate (m3/h)')
    plt.ylabel('ORC output (MW)')
    plt.show()

    '''
    curve = calculate(10000, 'H')
    htDemand = Demand(comodity_type = ComodityType.HEAT, curve = curve, t_supply = 95, t_return = 65)
    newCHPp.add_heat_demand(name='HT1', demand=htDemand)

    curve = calculate(5000, 'A')
    htDemand = Demand(comodity_type=ComodityType.HEAT, curve=curve, t_supply=80, t_return=60)
    newCHPp.add_heat_demand(name='HT2', demand=htDemand)

    curve = calculate(17500, 'D')
    htDemand = Demand(comodity_type=ComodityType.HEAT, curve=curve, t_supply=60, t_return=40)
    newCHPp.add_heat_demand(name='LT1', demand=htDemand)

    result = sum_demands_by_t_cutoff(newCHPp.demands,60)

    newCHPp.ht_demand = Demand(comodity_type = ComodityType.HEAT, curve = result['ht_demand'], t_supply = result['ht_t_supply'], t_return = result['ht_t_return'])
    newCHPp.lt_demand = Demand(comodity_type = ComodityType.HEAT, curve = result['lt_demand'], t_supply = result['lt_t_supply'], t_return = result['lt_t_return'])

  #  print('HT_demand', newCHPp.ht_demand.__dict__)
  #  print('LT_demand', newCHPp.lt_demand.__dict__)

    result = calculate_ht_mass_flow(newCHPp, cutoff=.6)
    newCHPp.ht_supply = result['ht_supply']
    newCHPp.m_ht =  result['ht_flow']

    newCHPp.m_orc = calculate_orc_mass_flow(newCHPp)

    newCHPp.orc = ORC(name='orc1', type=BinaryType.ocr_acc, t_bi=newCHPp.t_bi)
  #  print(newCHPp.orc.__dict__)

    result = newCHPp.orc.calculate_output(flow_rate=newCHPp.m_orc, brine=newCHPp.brine)
  #  print(result)

    result = calculate_t_hto(newCHPp)
  #  print(newCHPp.orc.__dict__)
    newCHPp.t_th_o = result

    result = calculate_lt_supply(newCHPp)
    newCHPp.lt_supply = result['lt_supply']

    plt.plot(newCHPp.lt_supply, 'b-')
    plt.show()

    result = calculate_t_bo(newCHPp)
    print('HT heat supply', newCHPp.ht_supply.sum())
    print('LT heat supply', newCHPp.lt_supply.sum())
    print('Total heat supply', newCHPp.ht_supply.sum() + newCHPp.lt_supply.sum())
    print('t_out', np.average(result))

    fig, ax1 = plt.subplots()
    fig.set_size_inches(10, 7.5)
    ax2 = ax1.twinx()

    ax1.plot(result, 'b-', label='calculated')
    ax1.set_xlabel('hours')
    ax1.set_ylabel('t_bo')

    ax2.plot(newCHPp.lt_supply, 'g-', label='HS (MW)')
    ax2.set_ylabel('HS (MW)')
    plt.show()
    '''
