# figures for the README, plots of the real logs go to figures/lab (not in git)
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from cbdbudget.budget import EA, TARGET, TREF, cumulative, equivalent_time
from cbdbudget.logio import check_log, read_log, run_info
from cbdbudget.sensitivity import RUN_A, RUN_B, crossings, sweep

fig_dir = Path(__file__).parent.parent / "figures"
data_dir = Path(__file__).parent.parent / "data"
(fig_dir / "lab").mkdir(parents=True, exist_ok=True)

# error of left and trapezoid on a 60 -> 80 C ramp in 40 min
exact = equivalent_time([0, 40], [60, 80], "linear_T")
dts = [40, 20, 10, 8, 5, 4, 2, 1, 0.5, 0.25]
left, trap = [], []
for dt in dts:
    t = np.arange(0, 40 + dt / 2, dt)
    T = 60 + t / 2
    left.append(exact - equivalent_time(t, T, "left"))
    trap.append(equivalent_time(t, T, "trapezoid") - exact)
plt.loglog(dts, left, "o-", label="left (too low)")
plt.loglog(dts, trap, "o-", label="trapezoid (too high)")
plt.xlabel("time between readings (min)")
plt.ylabel("error (eq-min)")
plt.title("ramp 60 -> 80 C in 40 min")
plt.legend()
plt.savefig(fig_dir / "ramp_error.png", dpi=200)
plt.close()

# runs A and B vs Ea
Ea = np.linspace(20, 150, 131)
x = crossings(RUN_A, RUN_B)[0]
plt.plot(Ea, sweep(RUN_A, Ea), label="A: ramp to 75 C, hold 45 min")
plt.plot(Ea, sweep(RUN_B, Ea), label="B: ramp to 80 C, hold 25 min")
plt.plot(x, equivalent_time(*RUN_A, "linear_T", x), "ko")
plt.axvline(EA, color="gray", ls="--")
plt.xlabel("Ea (kJ/mol)")
plt.ylabel("eq-min at 75 C")
plt.title(f"A = B at {x:.1f} kJ/mol")
plt.legend()
plt.savefig(fig_dir / "ea_sweep.png", dpi=200)
plt.close()

# lab logs
paths = sorted(data_dir.glob("*.csv"))
for p in paths:
    date, sample, dopant = run_info(p)
    t, T, clock = read_log(p)
    bad = [i for i, _ in check_log(t, T)]
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.plot(t, T, ".-")
    ax1.plot(t[bad], T[bad], "rx")
    ax1.axhline(TREF, color="gray", ls="--")
    ax1.set_ylabel("T (C)")
    ax1.set_title(f"{date} {sample}")
    ax2.plot(t, cumulative(t, T))
    ax2.axhline(TARGET, color="gray", ls="--")
    ax2.set_ylabel("eq-min")
    ax2.set_xlabel(f"min after {clock[0]}")
    fig.savefig(fig_dir / "lab" / f"{p.stem}.png", dpi=200)
    plt.close(fig)

if paths:
    for p in paths:
        t, T, _ = read_log(p)
        plt.plot(Ea, sweep((t, T), Ea), label=p.stem)
    plt.axvline(EA, color="gray", ls="--")
    plt.xlabel("Ea (kJ/mol)")
    plt.ylabel("eq-min at 75 C")
    plt.legend()
    plt.savefig(fig_dir / "lab" / "ea_sweep_lab.png", dpi=200)
    plt.close()
