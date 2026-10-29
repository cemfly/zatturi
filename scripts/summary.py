# budget of every log in data/ and the pairs that swap order between 60 and 110 kJ/mol
from pathlib import Path

from cbdbudget.budget import equivalent_time
from cbdbudget.logio import check_log, read_log, run_info
from cbdbudget.sensitivity import ranking_flips

runs = {}
for p in sorted((Path(__file__).parent.parent / "data").glob("*.csv")):
    date, sample, dopant = run_info(p)
    t, T, clock = read_log(p)
    trap = equivalent_time(t, T)
    lin = equivalent_time(t, T, "linear_T")
    flags = [clock[i] for i, _ in check_log(t, T)]
    print(f"{date} {sample} {dopant}  Tmax {T.max():.1f}  trap {trap:.1f}  linear_T {lin:.1f}  flags {flags}")
    runs[sample] = (t, T)

for a, b, Ea in ranking_flips(runs):
    print(f"{a} and {b} swap at {Ea:.1f} kJ/mol")
