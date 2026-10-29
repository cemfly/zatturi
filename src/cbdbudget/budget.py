import numpy as np
from scipy.integrate import quad

EA = 83.7     # kJ/mol, Ortega-Borges & Lincot give ~85
R = 8.314
TREF = 75     # C
TARGET = 60   # eq-min


def credit(T, Ea=EA):
    # 1 min at T is worth this many min at 75 C
    b = Ea * 1000 / R
    return np.exp(b * (1 / (TREF + 273.15) - 1 / (T + 273.15)))


def segment(t0, t1, T0, T1, rule="trapezoid", Ea=EA, Tmin=None):
    if Tmin is not None:
        if T0 < Tmin and T1 < Tmin:
            return 0
        # cut the segment where it crosses Tmin
        if T0 < Tmin:
            t0, T0 = t0 + (Tmin - T0) / (T1 - T0) * (t1 - t0), Tmin
        elif T1 < Tmin:
            t1, T1 = t0 + (Tmin - T0) / (T1 - T0) * (t1 - t0), Tmin
    dt = t1 - t0
    if rule == "left":
        return credit(T0, Ea) * dt
    if rule == "right":
        return credit(T1, Ea) * dt
    if rule == "trapezoid":
        return (credit(T0, Ea) + credit(T1, Ea)) / 2 * dt
    # linear_T
    return dt * quad(lambda u: credit(T0 + (T1 - T0) * u, Ea), 0, 1)[0]


def cumulative(t, T, rule="trapezoid", Ea=EA, Tmin=None):
    B = [0]
    for i in range(1, len(t)):
        B.append(B[-1] + segment(t[i - 1], t[i], T[i - 1], T[i], rule, Ea, Tmin))
    return np.array(B)


def equivalent_time(t, T, rule="trapezoid", Ea=EA, Tmin=None):
    return cumulative(t, T, rule, Ea, Tmin)[-1]
