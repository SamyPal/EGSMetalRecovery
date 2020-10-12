from GCHPc.units import *
from math import exp

class Brine:
    def convert_gpl_to_wtp(self, concentration: float, estimate: float = 0, thresshold = 0.0001, itter: int = 100):
        self.tds = concentration / 1000
        i = 0

#        while abs(estimate - self.tds) > thresshold or i > itter: #GTH seems to give an infintie loop
        while abs(estimate - self.tds) > thresshold and i < itter:
            estimate = self.tds
            self.density =self.set_density()
            self.tds = concentration / self.density
            i += 1

    def set_cp(self):
        """Batzle and Wang, 1992. Geophysics 57, p. 1396 - 1408
        temperature in °C, TDS as kg/kg
        result in J/kg.K"""

        temperature = self.temperature +  273.15  # Should be in K
        tds =  self.tds * 1000  # Should be in g/kg

        self.cp = (5328 - 97.6 * tds + 0.404 * tds ** 2) \
                  + (-6.913 + 0.7351 * tds - 0.00315 * tds ** 2) * temperature \
                  + (0.0096 - 0.001927 * tds + 8.23 * 10 ** -6 * tds ** 2) * temperature ** 2 \
                  + (2.5 * 10 ** -6 + 1.666 * 10 ** -6 * tds - 7.125 * 10 ** -9 * tds ** 2) * temperature ** 3
        self.cp = round(self.cp,0)

        return self.cp


    def set_density(self):
        """Batzle and Wang, 1992. Geophysics 57, p. 1396 - 1408
        For NaCl brine
        pressure in MPa, temperature in °C, TDS as kg/kg
        result in kg/m3
        check: http://www.crewes.org/ResearchLinks/ExplorerPrograms/FlProp/FluidProp.htm"""

        def _density_water_(self):
            """
            Batzle and Wang, 1992. Geophysics 57, p. 1396 - 1408
            pressure in MPa, temperature in °C
            result in kg/m3"""
            return 1000 + 0.001 * (-80 * self.temperature - 3.3 * self.temperature ** 2 \
                   + 0.00175 * self.temperature ** 3 + 489 * self.pressure - 2 * self.temperature * self.pressure \
                   + 0.016 * self.temperature ** 2 * self.pressure - 0.000013 * self.temperature ** 3 * self.pressure \
                   - 0.333 * self.pressure ** 2 - 0.002 * self.temperature * self.pressure ** 2)

        if self.pressure_unit != PressureUnits.megapascal:
            self.pressure =  PressureUnits.convertPressure(self.pressure, self.pressure_unit, PressureUnits.megapascal)
            self.pressure_unit = PressureUnits.megapascal

        self.density = _density_water_(self) + 1000 * self.tds * (0.668 + 0.44 * self.tds \
                       + 10 ** -6 * (300 * self.pressure - 2400 * self.pressure * self.tds \
                       + self.temperature * (80 + 3 * self.temperature - 3300 * self.tds - 13 * self.pressure + 47 * self.pressure * self.tds)))
        self.density = round(self.density,0)

        return self.density


    def set_viscosity(self):
        '''Batzle and Wang, 1992. Geophysics 57, p. 1396 - 1408
        For brine up to 250°C
        temperature in °C, TDS as kg/kg
        result in Pa.s
        conversion used: 0,001 Pa.s is 1 cP
        check: http://www.crewes.org/ResearchLinks/ExplorerPrograms/FlProp/FluidProp.htm'''

        self.viscosity = 0.0001 + 0.000333 * self.tds + (0.00165 + 0.0919 * self.tds ** 3) \
                         * exp(-(0.42 * (self.tds ** 0.8 - 0.17) ** 2 + 0.045) * self.temperature ** 0.8)
        self.viscosity = round(self.viscosity,6)

        return self.viscosity


    def update_properties(self):
        self.set_density
        self.set_cp()
        self.set_viscosity()


    def __init__(self, name: str = 'none', tds: float = .01, temperature: float = 25.,pressure: float = 1., pressure_unit = PressureUnits.bar):
        """
        Class define thermaodynamic properties of a (NaCl) brine
        :param name: indentifier for the boine (string)
        :param temperature: temperature of the brine in °C (float)
        :param tds: total dissolved salts in kg/kg (float)
        """

        self.name = name
        self.tds = tds
        self.temperature = temperature

        if pressure_unit != PressureUnits.bar:
            pressure = convert_pressure(pressure, PressureUnits.bar, PressureUnits.megapascal)

        self.pressure = pressure
        self.pressure_unit = PressureUnits.megapascal

        self.set_density()
        self.set_cp()
        self.set_viscosity()


if __name__ == '__main__':
    brine = Brine(tds=.05, temperature=168., pressure=5.7)
    print(brine.__dict__)

    brine.convert_gpl_to_wtp(29.)
    print(brine.tds)
    print(brine.density)