import HTPE.components as compo
import numpy as np
from math import exp

def _get_e_electrical(**kwargs) -> float:
    a = .5

    if 're' in kwargs:
        a = .065 * float(kwargs['re']) ** -12.

    if 'concentration' in kwargs:
        a = 0.15 * exp(2.7 * float(kwargs['concentration']))

    a = np.random.normal(a, 0.0356)

    if a > 1.: a= 1.
    return a


def _get_e_recovery(metal: str, **kwargs) -> float:
    a = .85

    if 'flow_rate' in kwargs:
        a = 1 - exp(-80./float(kwargs['flow_rate']))

    return np.random.normal(0.85, 0.03)


def get_recovery(flow_rate: float ,metal: str, concentration: float, E0min: float = .3419, voltage: float = 12.,**kwargs) -> {}:
    '''
    Returns a dictionay giving the recovery factor for the given ion, the amount of metal recovered over the given period of time in gram,
    the current supplied (A) and the power consumption for the given period of time (kWh)
    :param flow_rate: flow rate in l/s (float)
    :param metal: the ion to be recovered (string)
    :param concentration: the concentration of the ion in solution (in g/l)
    :param E0min: the minimal reduction potential of metals that can be recovered (V) - default = 0.3419 V (Cu2+ + 2 e- <-> Cu)
    :param voltage: teh voltage of the cell (V) - default = 12.V
    :param kwargs:
        'fullload' can be used to provide the operative period of the metal extraction(hours), if not supplied time is set to 1 second
    :return: dictionary
        result['re'] recovery efficiency - fraction of the metal concentration in the brine
        result['M'] g of metal recovered
        result['I'] power (kW)
        result['E'] energy consumption (kWh)
    '''

    result = {}
    result['re'] = 0.   # recovery efficiency - fraction of the metal concentration in the brine
    result['M'] = 0.    # g of metal recovered
    result['P'] = 0.    # electrical current (A)
    result['E'] = 0.    # energy consumption (kWh)

    time = 1.    #second
    if 'fullload' in kwargs:
        time = float(kwargs['fullload']) * 3600.

    properties = compo.get_properties(metal)

    if properties['E0'] >= E0min:
        result['re'] = _get_e_recovery(metal=metal, flow_rate=flow_rate)

        m = flow_rate * concentration * result['re']    # g/s
        I = m * 96485 * abs(properties['z'])/(properties['m'] * _get_e_electrical(concentration=concentration))    # C/s = A
        P = I * voltage / 1000   #12 V DC device - power in kW

        result['M'] = m * time          # g
        result['P'] = P                 # kW
        result['E'] = P * time / 3600   # kWh

    return result


if __name__  == '__main__':
    #metal_list = {'cu': 'Cu2+', 'au': 'Au+', 'as': 'As3-', 'sb': 'Sb3-'}

    metal_list = {'cu': 'Cu2+'}
    concs = [1., .1]
   # concs = [.690, .345, .165]
   # concs = [.690, .345, .165, 8., .04, .4, .02]

    for c in concs:
        for i in range(0, 49):
            result = get_recovery(flow_rate=40., metal='Cu2+', concentration=c, fullload=6100., voltage=.5)
            #print(f'Cin = {c} -> re: {result["re"]} -  m: {result["M"]/1000} kg - P: {result["P"]} kW - E: {result["E"]} kWh => {result["E"]*1000 / result["M"]} kWh/kg')
            print(c,result["M"]/1000,result["re"],result["E"]*1000 / result["M"])
