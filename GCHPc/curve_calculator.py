import GCHPc.curve_models as cm
from datetime import date, timedelta
import numpy as np
import matplotlib.pyplot as plt

def read_curve(file_name: str, workspace: str= ".\\GCHPp\\data\\", delimiter: str = "\t", skiprows: int = 0):
    file = file_name if workspace == '' else workspace + file_name
    curve = np.loadtxt(file, delimiter, skiprows)
    if len(curve) != 24 * 365:
        raise Exception(file_name + " should contain 24*365 values")
    return curve

def calculate(value, selection):
    model = get_model(selection)
    d = date(2001, 1, 1)

    hour_result = np.zeros(24 * 365, )

    for i in range(0, 365):
        day = d.isoweekday()
        month = d.month

        dayValue = model.month[month - 1] * model.week[day - 1]

        for j in range(0,24):
            hour_result[i * 24 + j] = dayValue * model.day[j]

        d = d + timedelta(days=1.)

    hour_result = hour_result/hour_result.sum()
    return hour_result * value

def get_model(selection):
    if selection == "A":            # Dag, 5 d. op 7 (kantoren, scholen, diensten)
        return cm.get_profile_A()
    elif selection == "B":          # Dag, 6 d. op 7 (handelszaken, kultuur)
        return cm.get_profile_B()
    elif selection == "C":          # Dag, 7 d. op 7 (sportcentra)
        return cm.get_profile_C()
    elif selection == "D":          # Dag, 6 d. op 7 (handelszaken, kultuur)
        return cm.get_profile_D()
    elif selection == "E":          # Dag, 5 d. op 7 (KMO, wasserijen, enz…, zeer regelmatig verbruik)
        return cm.get_profile_E()
    elif selection == "F":          # Dag, 7 d. op 7 (collectieve huisvesting)
        return cm.get_profile_F()
    elif selection == "G":
        return cm.get_profile_G()
    elif selection == "H":
        return cm.get_profile_H()

    assert False

if __name__ == '__main__':
    curve = calculate(68500,'F')

    print(curve.sum(), curve.max(), curve.min())
    print(curve)
    ws = 'C:\\temp\\'
    file = ws + 'out.txt'
    np.savetxt(file,curve)
    x = np.linspace(1,8760,8760)
    plt.plot(curve, 'b-')
    plt.show()