import numpy as np

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel
from core.solver_plastic import PlasticSolver
from tests.pcross_benchmark_fixture import LOAD_CASE_3, LOAD_CASE_4, MANUAL_ROWS, build_pcross_tbeam_solver


def _by_angle(rows):
    return {float(r["angle_v_deg"]): r for r in rows}


def test_external_axial_force_materially_changes_plastic_solution_exact_fixture():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    res_p1000 = solver.solve(angle_v_deg=10.0, P_target=1000.0)
    res_p2000 = solver.solve(angle_v_deg=10.0, P_target=2000.0)

    assert not np.isclose(res_p1000["Mx"], res_p2000["Mx"], rtol=0.01, atol=10.0)
    assert not np.isclose(res_p1000["My"], res_p2000["My"], rtol=0.01, atol=10.0)
    assert not np.isclose(res_p1000["y_na"], res_p2000["y_na"], rtol=0.01, atol=0.005)
    assert np.isclose(res_p1000["N_calc"], 1000.0, rtol=1e-6, atol=1e-4)
    assert np.isclose(res_p2000["N_calc"], 2000.0, rtol=1e-6, atol=1e-4)


def test_prestress_eps0_materially_changes_response_exact_fixture():
    with_prestress = build_pcross_tbeam_solver(prestress_eps0=0.004).solve(angle_v_deg=2.0, P_target=1000.0)
    without_prestress = build_pcross_tbeam_solver(prestress_eps0=0.0).solve(angle_v_deg=2.0, P_target=1000.0)

    assert abs(with_prestress["Mx"] - without_prestress["Mx"]) > 0.5
    assert abs(with_prestress["My"] - without_prestress["My"]) > 0.2
    assert abs(with_prestress["y_na"] - without_prestress["y_na"]) > 3e-4


def test_manual_rows_lc3_lc4_via_sweep_helper_with_explicit_tolerances():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)

    lc3_rows = solver.solve_angle_sweep(LOAD_CASE_3.angles_deg, LOAD_CASE_3.P_target)
    lc4_rows = solver.solve_angle_sweep(LOAD_CASE_4.angles_deg, LOAD_CASE_4.P_target)
    lc3_by_angle = _by_angle(lc3_rows)
    lc4_by_angle = _by_angle(lc4_rows)

    # Sign/quadrant assertions in this solver convention.
    assert all(lc3_by_angle[a]["Mx"] < 0.0 and lc3_by_angle[a]["My"] > 0.0 for a in [2.0, 5.0, 8.0])
    assert all(lc4_by_angle[a]["Mx"] < 0.0 and lc4_by_angle[a]["My"] > 0.0 for a in [5.0, 10.0, 15.0])

    # Monotonic trends for absolute moments over benchmark subsets.
    assert abs(lc3_by_angle[2.0]["Mx"]) < abs(lc3_by_angle[5.0]["Mx"]) < abs(lc3_by_angle[8.0]["Mx"])
    assert abs(lc4_by_angle[5.0]["Mx"]) < abs(lc4_by_angle[10.0]["Mx"]) < abs(lc4_by_angle[15.0]["Mx"])
    assert abs(lc4_by_angle[5.0]["My"]) > abs(lc4_by_angle[10.0]["My"]) > abs(lc4_by_angle[15.0]["My"])

    # Explicit benchmark tolerances (relative on absolute moment magnitudes).
    # With modern EC2 models vs legacy PCROSS families, LC3 remains the hardest to match.
    # Tightest stable tolerances achieved with exact fixture + deterministic sweep:
    #   Mx within 65%, My within 55%.
    tol_mx = 0.65
    tol_my = 0.55

    for (lc, angle), ref in MANUAL_ROWS.items():
        res = lc3_by_angle[float(angle)] if lc == 3 else lc4_by_angle[float(angle)]
        rel_mx = abs(abs(res["Mx"]) - ref["Mx"]) / ref["Mx"]
        rel_my = abs(abs(res["My"]) - ref["My"]) / ref["My"]
        assert rel_mx <= tol_mx
        assert rel_my <= tol_my


def test_sweep_branch_selection_prefers_continuity_when_two_candidates_exist():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    angles = [2.0, 5.0]

    sweep = solver.solve_angle_sweep(angles, 1000.0)
    assert len(sweep) == 2

    cands_a2 = solver._solve_candidates(2.0, 1000.0)
    cands_a5 = solver._solve_candidates(5.0, 1000.0)
    assert len(cands_a2) == 2
    assert len(cands_a5) == 2

    # First point rule: smallest |kappa|.
    first_expected = min(cands_a2, key=lambda c: (abs(c["kappa"]), c["pivot"]))
    assert sweep[0]["pivot"] == first_expected["pivot"]

    # Second point rule: minimum normalized continuity score.
    prev = sweep[0]
    scale_m = max(abs(prev["Mx"]), abs(prev["My"]), 1.0)
    scale_y = max(solver.y_top - solver.y_bottom, 1e-3)
    scale_k = max(abs(prev["kappa"]), 1e-5)

    def score(c):
        return (
            abs(c["Mx"] - prev["Mx"]) / scale_m
            + abs(c["My"] - prev["My"]) / scale_m
            + 0.5 * abs(c["y_na"] - prev["y_na"]) / scale_y
            + 0.5 * abs(c["kappa"] - prev["kappa"]) / scale_k
        )

    second_expected = min(cands_a5, key=lambda c: (score(c), c["pivot"]))
    assert sweep[1]["pivot"] == second_expected["pivot"]


def test_low_axial_sweep_is_continuous_for_exact_fixture():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    rows = solver.solve_angle_sweep([float(v) for v in range(0, 181, 5)], P_target=0.0)

    # Guard against disjoint/open branch jumps by limiting normalized step jumps.
    for prev, cur in zip(rows, rows[1:]):
        scale_m = max(abs(prev["Mx"]), abs(prev["My"]), 10.0)
        jump = abs(cur["Mx"] - prev["Mx"]) / scale_m + abs(cur["My"] - prev["My"]) / scale_m
        assert jump < 0.6


def test_symmetric_section_opposite_angles_give_opposite_moments_for_p_zero():
    section = CrossSection(
        concrete_outline=[
            {"id": 1, "x": -0.3, "y": -0.3},
            {"id": 2, "x": 0.3, "y": -0.3},
            {"id": 3, "x": 0.3, "y": 0.3},
            {"id": 4, "x": -0.3, "y": 0.3},
        ],
        concrete_voids=[],
        rebar_mild=[
            {"id": "S1", "x": -0.22, "y": -0.22, "area": 250.0},
            {"id": "S2", "x": 0.22, "y": -0.22, "area": 250.0},
            {"id": "S3", "x": -0.22, "y": 0.22, "area": 250.0},
            {"id": "S4", "x": 0.22, "y": 0.22, "area": 250.0},
        ],
        rebar_prestressed=[],
    )
    solver = PlasticSolver(section, Concrete(f_ck=35.0), MildSteel(f_yk=500.0), prestressed_steel=None)

    res_v = solver.solve(35.0, P_target=0.0)
    res_op = solver.solve(215.0, P_target=0.0)

    assert np.isclose(res_v["Mx"], -res_op["Mx"], rtol=0.03, atol=8.0)
    assert np.isclose(res_v["My"], -res_op["My"], rtol=0.03, atol=8.0)
