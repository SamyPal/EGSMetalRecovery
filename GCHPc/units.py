from enum import Enum

class PressureUnits(Enum):
    bar = 1
    pascal = 2
    megapascal = 3

class MassUnits():
    µg = -6
    mg = -3
    g = 0
    kg = 3
    ton = 6

class TemperatureUnits(Enum):
    kelvin = 1
    celcius = 2

def convert_pressure(pressure, unit_in, unit_out):
    if unit_in == PressureUnits.bar and unit_out == PressureUnits.megapascal:
        divider = 10
    elif unit_in == PressureUnits.megapascal and unit_out == PressureUnits.bar:
        divider = .1
    elif unit_in == unit_out:
        divider = 1.

    return pressure / divider

def convert_mass_units(mass: float, unit_in: MassUnits, unit_out: MassUnits) -> float:
    con = 10**(int(unit_in) - int(unit_out))
    return mass * con

if __name__ == '__main__':
    pressure = convert_pressure(100, PressureUnits.bar, PressureUnits.megapascal)
    print(pressure)

    print(convert_mass_units(2.5, MassUnits.g, MassUnits.kg))
