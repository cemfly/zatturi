from itertools import combinations

import numpy as np
from scipy.optimize import brentq

from .budget import equivalent_time

# made up runs: ramp to 75 and hold 45 min, ramp to 80 and hold 25 min
RUN_A = ([0, 90, 135], [25, 75, 75])
RUN_B = ([0, 90, 115], [25, 80, 80])


def sweep(run, Ea_list, rule="linear_T", Tmin=None):
    t, T = run
    return np.array([equivalent_time(t, T, rule, Ea, Tmin) for Ea in Ea_list])


def crossings(run1, run2, lo=5, hi=200, n=100, rule="linear_T"):
    # Ea values where the two runs get the same budget
    f = lambda Ea: equivalent_time(*run1, rule, Ea) - equivalent_time(*run2, rule, Ea)
    x = np.linspace(lo, hi, n)
    y = [f(Ea) for Ea in x]
    return [brentq(f, x[i], x[i + 1]) for i in range(n - 1) if y[i] * y[i + 1] < 0]


def ranking_flips(runs, lo=60, hi=110, rule="trapezoid"):
    # runs = {name: (t, T)}
    flips = []
    for a, b in combinations(runs, 2):
        for Ea in crossings(runs[a], runs[b], lo, hi, 51, rule):
            flips.append((a, b, Ea))
    return flips
