import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq, least_squares

from .budget import TARGET, credit

TAU = 31     # min, from the 29.07 ramp
THETA = 6    # min, dead time after changing the set


def remaining_at_plateau(B, T, target=TARGET):
    # bath already sitting at T, B eq-min collected so far
    return max(0, (target - B) / credit(T))


def bath_T(t, T0, Tinf, tau=TAU, theta=THETA):
    return np.where(t < theta, T0, Tinf - (Tinf - T0) * np.exp(-(t - theta) / tau))


def model_budget(t, T0, Tinf, tau=TAU, theta=THETA, B0=0):
    B = B0 + min(t, theta) * credit(T0)
    if t > theta:
        B += quad(lambda s: credit(bath_T(s, T0, Tinf, tau, theta)), theta, t)[0]
    return B


def stop_time(T0, Tinf, tau=TAU, theta=THETA, B0=0, target=TARGET):
    # minutes until the model bath reaches the target (heating only)
    if B0 >= target:
        return 0
    return brentq(lambda t: model_budget(t, T0, Tinf, tau, theta, B0) - target, 0, 600)


def fit_bath(ramps):
    # ramps = [(t, T), ...] starting at the set change, same tau and theta, one Tinf per ramp
    def res(p):
        return np.concatenate([bath_T(t, T[0], p[2 + i], p[0], p[1]) - T for i, (t, T) in enumerate(ramps)])

    p = least_squares(res, [30, 5] + [T[-1] for t, T in ramps]).x
    return p[0], p[1], p[2:]
