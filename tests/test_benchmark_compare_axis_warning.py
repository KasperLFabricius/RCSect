import numpy as np

from tests.benchmark_compare import (
    AXIS_TOL,
    BenchmarkSweepSpec,
    estimate_warning_level,
    run_benchmark_sweeps,
)
from tests.pcross_benchmark_fixture import EMBEDDED_BENCHMARK_CASES


class _DummySolver:
    def solve_angle_sweep(self, angles_deg, p_target):
        out = []
        for angle in angles_deg:
            out.append(
                {
                    "angle_v_deg": float(angle),
                    "Mx": 1e-10,
                    "My": 25.0,
                    "candidate_count": 1,
                    "selection_source": "dummy",
                }
            )
        return out


def test_axis_reference_rows_mark_sign_and_quadrant_not_applicable():
    solver = _DummySolver()
    refs = {(999, 0.0): {"Mx": 0.0, "My": 20.0}}
    df = run_benchmark_sweeps(
        solver,
        [BenchmarkSweepSpec(load_case=999, p_target=0.0, angles_deg=(0.0,))],
        reference_rows=refs,
    )

    row = df.iloc[0]
    assert np.isnan(row["sign_agreement_Mx"])
    assert bool(row["sign_agreement_My"])
    assert np.isnan(row["quadrant_agreement"])


def test_axis_tolerance_treats_tiny_reference_component_as_not_applicable():
    solver = _DummySolver()
    refs = {(998, 0.0): {"Mx": AXIS_TOL * 0.5, "My": 20.0}}
    df = run_benchmark_sweeps(
        solver,
        [BenchmarkSweepSpec(load_case=998, p_target=0.0, angles_deg=(0.0,))],
        reference_rows=refs,
    )
    row = df.iloc[0]
    assert np.isnan(row["sign_agreement_Mx"])
    assert np.isnan(row["quadrant_agreement"])


def test_warning_estimator_supports_w1_w2_and_none():
    assert estimate_warning_level(60.0, total_compression_force=150.0) == "W1"
    assert estimate_warning_level(90.0, total_compression_force=150.0) == "W2"
    assert estimate_warning_level(40.0, total_compression_force=150.0) is None


def test_annular_warning_parity_estimator_matches_embedded_w1_w2_rows():
    section0 = EMBEDDED_BENCHMARK_CASES["section0"]
    sectioniv = EMBEDDED_BENCHMARK_CASES["sectioniv"]

    for case in [section0, sectioniv]:
        df = run_benchmark_sweeps(
            case.solver_builder(),
            [BenchmarkSweepSpec(load_case=case.load_case, p_target=case.load.P_target, angles_deg=case.load.angles_deg)],
            reference_rows=case.reference_rows,
        )
        refs = df[df["warning_ref"].notna()]
        assert refs["warning_est_match"].all()
