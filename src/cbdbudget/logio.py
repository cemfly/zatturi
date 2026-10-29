import csv
from pathlib import Path

import numpy as np


def run_info(path):
    # 2026-08-19_CdS-5_Na3.csv -> date, sample, dopant
    p = Path(path).stem.split("_")
    return p[0], p[1], p[2] if len(p) > 2 else "-"


def clock_to_min(s):
    # 15:52 or 15.52
    h, m = s.strip().replace(".", ":").split(":")
    return int(h) * 60 + int(m)


def read_log(path):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    clock = [r["saat"].strip() for r in rows]
    t = np.array([clock_to_min(c) for c in clock], dtype=float)
    T = np.array([float(r["T_C"]) for r in rows])
    return t - t[0], T, clock


def check_log(t, T, heat_max=1.5, cool_min=-0.5):
    # only marks rows, nothing is removed
    flags = []
    for i in range(len(T)):
        if T[i] < 10 or T[i] > 100:
            flags.append((i, f"T = {T[i]} out of range"))
        if i == 0:
            continue
        dt = t[i] - t[i - 1]
        if dt <= 0:
            flags.append((i, "time not increasing"))
            continue
        rate = (T[i] - T[i - 1]) / dt
        if rate > heat_max or rate < cool_min:
            flags.append((i, f"{rate:+.2f} C/min"))
    return flags
