class CurveSet(object):
    def __init__(self, day, week, month):
        self.__day = day
        self.__week = week
        self.__month = month

    @property
    def day(self):
        return self.__day

    @property
    def week(self):
        return self.__week

    @property
    def month(self):
        return self.__month


# A - Dag, 5 d. op 7 (kantoren, scholen, diensten)
def get_profile_A():
    day = [2.8, 2.9, 3.1, 3.2, 4.8, 8.1, 7.4, 6.4, 5.5, 5.1, 4.5, 4.5, 4.2, 4.1, 4.1, 3.9, 3.5, 3.7, 4.2, 3.5, 2.5, 2.6, 2.6, 2.8]
    week = [17.4, 17.6, 17.4, 17.6, 16.1, 7.2, 6.8]
    month = [15.2, 13.8, 12.2, 9.2, 5.3, 3.2, 2.1, 2.1, 3.8, 7.2, 11.6, 14.4]
    return CurveSet(day, week, month)


# B - Dag, 6 d. op 7 (handelszaken, kultuur)
def get_profile_B():
    day = [3.4, 3.2, 3.2, 3.0, 3.2, 3.3, 3.3, 3.5, 5.7, 7.3, 6.4, 6.4, 6.0, 5.6, 5.1, 4.6, 4.7, 5.1, 4.3, 2.9, 2.4, 2.4, 2.4, 2.7]
    week = [18.2, 16.2, 15.1, 15.3, 15.1, 13.4, 6.7]
    month = [15.3, 13.9, 12.2, 9.2, 5.3, 3.2, 2.0, 2.0, 3.7, 7.1, 11.6, 14.5]
    return CurveSet(day, week, month)


# C - Dag, 7 d. op 7 (sportcentra)
def get_profile_C():
    day = [3.4, 3.5, 3.4, 3.5, 3.7, 3.9, 4.2, 4.7, 4.7, 4.7, 4.7, 4.6, 4.5, 4.4, 4.4, 4.4, 4.4, 4.5, 4.7, 4.5, 4.2, 4.3, 3.4, 3.4]
    week = [14.4, 15.1, 14.9, 14.9, 14.7, 13.3, 12.7]
    month = [14.0, 12.8, 11.5, 9.0, 5.9, 4.2, 3.2, 3.2, 4.6, 7.4, 11.0, 13.3]
    return CurveSet(day, week, month)


# D - Continu, 7 d. op 7 (zorg, horeca)
def get_profile_D():
    day = [3.4, 3.5, 3.6, 3.8, 4.7, 6.5, 6.1, 5.6, 5.2, 4.9, 4.5, 4.3, 4.1, 4.0, 4.0, 3.9, 3.6, 3.8, 4.0, 3.6, 3.1, 3.2, 3.2, 3.4]
    week = [16.9, 16.4, 15.0, 14.8, 14.8, 10.9, 11.2]
    month = [13.5, 12.4, 11.2, 9.0, 6.1, 4.5, 3.6, 3.6, 4.9, 7.5, 10.8, 12.9]
    return CurveSet(day, week, month)


# E - Dag, 5 d. op 7 (KMO, wasserijen, enz…, zeer regelmatig verbruik)
def get_profile_E():
    day = [1.0, 1.0, 1.0, 1.0, 3.9, 8.4, 8.1, 7.9, 7.8, 7.5, 7.4, 7.3, 7.2, 7.0, 6.7, 6.5, 3.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    week = [18.5, 18.5, 18.5, 18.5, 18.5, 3.8, 3.8]
    month = [9.4, 9.1, 8.8, 9.0, 8.2, 7.7, 6.3, 6.2, 6.6, 8.6, 9.7, 10.4]
    return CurveSet(day, week, month)


# F - Dag, 7 d. op 7 (collectieve huisvesting)
def get_profile_F():
    day = [2.2, 2.4, 2.5, 2.8, 4.1, 4.9, 5.0, 5.0, 5.1, 5.0, 4.8, 4.5, 4.4, 4.3, 4.2, 4.2, 4.3, 4.6, 4.8, 4.8, 4.9, 4.8, 4.3, 2.2]
    week = [13.5, 13.5, 13.5, 13.5, 13.5, 16.3, 16.3]
    month = [15.7, 14.2, 12.4, 9.2, 5.1, 2.9, 1.7, 1.6, 3.4, 7.1, 11.8, 14.9]
    return CurveSet(day, week, month)


# G - Specifiek profiel voor de Brusselse hotels
def get_profile_G():
    day = [3.4, 3.5, 3.6, 3.8, 4.7, 6.5, 6.1, 5.6, 5.2, 4.9, 4.5, 4.3, 4.1, 4.0, 4.0, 3.9, 3.6, 3.8, 4.0, 3.6, 3.1, 3.2, 3.2, 3.4]
    week = [16.9, 16.4, 15.0, 14.8, 14.8, 10.9, 11.2]
    month = [13.8, 14.5, 13.0, 8.9, 6.5, 4.9, 3.7, 4.3, 4.2, 5.5, 10.1, 10.6]
    return CurveSet(day, week, month)

# H - Industrie (productie 6 dagen op 7 - volcontinue
def get_profile_H():
    day = [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]
    week = [1., 1., 1., 1., 1., 0.67, 0.33]
    month = [3.6, 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 3.1]
    return CurveSet(day, week, month)
