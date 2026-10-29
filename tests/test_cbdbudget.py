import numpy as np
import pytest
from scipy.integrate import quad

from cbdbudget.budget import credit, equivalent_time
from cbdbudget.logio import check_log, clock_to_min, read_log, run_info
from cbdbudget.sensitivity import RUN_A, RUN_B, crossings, ranking_flips, sweep
from cbdbudget.stoptime import bath_T, fit_bath, model_budget, remaining_at_plateau, stop_time


def test_credit():
    assert credit(75) == 1
    # printed table next to the bath
    for T, c in {66: 0.46, 70: 0.66, 74: 0.92, 76: 1.09, 80: 1.51}.items():
        assert round(credit(T), 2) == c


def test_rules():
    t = np.arange(0, 61, 5)
    for rule in ["left", "right", "trapezoid", "linear_T"]:
        assert equivalent_time(t, 75 + 0 * t, rule) == pytest.approx(60)
    # 60 -> 80 C in 40 min, dT/dt = 0.5
    t = np.array([0, 10, 20, 30, 40])
    T = 60 + t / 2
    exact = equivalent_time(t, T, "linear_T")
    assert exact == pytest.approx(2 * quad(credit, 60, 80)[0])
    assert equivalent_time(t, T) == pytest.approx(29.7035, abs=1e-4)
    assert equivalent_time(t, T, "left") < exact < equivalent_time(t, T)


def test_tmin():
    # 40 -> 60 C in 20 min, only the half above 50 C counts
    assert equivalent_time([0, 20], [40, 60], "trapezoid", Ea=0, Tmin=50) == pytest.approx(10)
    assert equivalent_time([0, 20], [40, 60], "linear_T", Tmin=50) == pytest.approx(quad(credit, 50, 60)[0])
    assert equivalent_time([0, 20], [60, 40], "linear_T", Tmin=50) == pytest.approx(quad(credit, 50, 60)[0])


def test_log(tmp_path):
    assert run_info("2026-08-19_CdS-5_Na3.csv") == ("2026-08-19", "CdS-5", "Na3")
    assert run_info("data/2026-08-03_CdS-3.csv")[2] == "-"
    assert clock_to_min("15:52") == clock_to_min("15.52") == 952
    p = tmp_path / "log.csv"
    p.write_text("saat,T_C\n15.40,60.0\n15:52,62.5\n16.05,64.0\n")
    t, T, clock = read_log(p)
    assert list(t) == [0, 12, 25]
    assert list(T) == [60, 62.5, 64]


def test_check_log():
    flags = check_log([0, 5, 10, 20, 21, 22], [70, 72, 68, 69, 72, 73])
    assert [i for i, _ in flags] == [2, 4]
    assert "-0.80" in flags[0][1] and "+3.00" in flags[1][1]
    assert check_log([0, 5, 5, 10], [60, 61, 62, 63])[0][0] == 2
    assert check_log([0, 5], [60, 150])[0][0] == 1


def test_stop_time():
    assert remaining_at_plateau(53.4, 75.9) == pytest.approx(6.13, abs=0.01)
    assert remaining_at_plateau(70, 75.9) == 0
    assert stop_time(60, 76, theta=0) == pytest.approx(83.53, abs=0.01)
    assert stop_time(60, 76) == pytest.approx(87.88, abs=0.01)
    assert stop_time(70, 76, B0=61) == 0
    t = np.arange(0, 90.001, 0.05)
    assert model_budget(90, 60, 76) == pytest.approx(equivalent_time(t, bath_T(t, 60, 76), "linear_T"), rel=1e-5)


def test_fit_bath():
    rng = np.random.default_rng(2026)
    t = np.arange(0, 150.0)
    ramps = [(t, bath_T(t, T0, Tinf) + rng.normal(0, 0.2, t.size)) for T0, Tinf in [(24, 74.6), (22, 79)]]
    tau, theta, Tinf = fit_bath(ramps)
    assert tau == pytest.approx(31, rel=0.1)
    assert theta == pytest.approx(6, rel=0.1)
    assert Tinf == pytest.approx([74.6, 79], abs=0.3)


def test_sensitivity():
    assert sweep(RUN_A, [83.7, 40]) == pytest.approx([65.192, 81.971], abs=1e-3)
    assert sweep(RUN_A, [83.7, 40], Tmin=50) == pytest.approx([63.433, 73.002], abs=1e-3)
    assert sweep(RUN_B, [83.7]) == pytest.approx([66.125], abs=1e-3)
    assert crossings(RUN_A, RUN_B) == pytest.approx([79.635], abs=1e-3)
    runs = {"A": RUN_A, "B": RUN_B, "C": ([0, 60], [75, 75])}
    assert [(a, b) for a, b, _ in ranking_flips(runs, rule="linear_T")] == [("A", "B")]
