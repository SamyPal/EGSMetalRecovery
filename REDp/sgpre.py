from math import exp
from HTPE.components import get_molar_mass

def _get_active_area(flow_rate: float, velocity: float = 0.03, cell_width: float = 0.0001, cell_height: float = 0.1) -> float:
    '''
    Returns the active membrane ares in m3
    :param flow_rate: in l/s
    :param velocity: in m/s
    :param cell_width: in m
    :param cell_height: in m
    :return: area in m
    '''
    l = flow_rate /(1000 * velocity * cell_width)
    return l * cell_height


def _get_power_density(temperature: float, nacl: float, bivalents: float = 0.0):
    '''
    Returns power density in w/m2
    :param temperature: input tempeature in °C
    :param nacl: M NaCl in the brine
    :param bivalents: M Ca+Mg in the brine
    :return: power density (W/m2)
    '''
    pd = 0.9 * nacl
    pd *= 0.25 * temperature + 7.2
    pd *= 1.3 * bivalents**2 - 2.* bivalents + 1.

    return pd


def _get_dilution_factor() -> float:
    '''
    Brine dilution factor
    :return:
    '''
    return 0.75


def _get_output_temperature(t_in: float, velocity: float = 0.03) -> float:
    '''
    Output temperature in °C
    :param t_in:
    :param velocity:
    :return:
    '''
    return round(t_in * 0.9405 * velocity**0.1845, ndigits=0)


def get_output(flow_rate, concentrations: {}, temperature: float, velocity: float = 0.03):
    results = {}
    results['P'] = 0. # power in kW
    results['d'] = 0. # dilution factor
    results['t_out'] = temperature #output temperature in °C

    area = _get_active_area(flow_rate=flow_rate, velocity=velocity)

    nacl = concentrations['na'] / (1000 * get_molar_mass('Na+'))
    nacl += concentrations['cl'] / (1000 * get_molar_mass('Cl-'))

    biv = concentrations['ca'] / (1000 * get_molar_mass('Ca2+'))
    biv += concentrations['mg'] / (1000 * get_molar_mass('Mg2+'))

    #print(area, nacl, biv)
    results['P'] = area * _get_power_density(temperature=temperature, nacl=nacl, bivalents=biv) / 1000
    results['d'] = _get_dilution_factor()
    results['t_out'] = _get_output_temperature(t_in=temperature, velocity=velocity)

    return results


if __name__ == '__main__':
    composition = {
        'na': 49800.,
        'ca': 1500.,
        'mg': 25.,
        'cl': 98100.
    }

    velocity = [0.005, 0.01, 0.03]

    for v in velocity:
        print(get_output(flow_rate=30., temperature=125.,concentrations=composition, velocity=v))