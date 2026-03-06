import numpy as np

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel
from core.solver_plastic import PlasticSolver
from tests.pcross_benchmark_fixture import LOAD_CASE_3, LOAD_CASE_4, build_pcross_tbeam_solver


def test_external_axial_force_materially_changes_plastic_solution():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.0075)

    res_p0 = solver.solve(angle_v_deg=15.0, P_target=0.0)
    res_p2000 = solver.solve(angle_v_deg=15.0, P_target=2000.0)

    assert not np.isclose(res_p0["Mx"], res_p2000["Mx"], rtol=0.01, atol=20.0)
    assert not np.isclose(res_p0["My"], res_p2000["My"], rtol=0.01, atol=20.0)
    assert not np.isclose(res_p0["y_na"], res_p2000["y_na"], rtol=0.01, atol=0.01)
    assert not np.isclose(res_p0["kappa"], res_p2000["kappa"], rtol=0.05, atol=1e-4)
    assert np.isclose(res_p2000["N_calc"], 2000.0, rtol=1e-6, atol=1e-4)


def test_prestress_initial_strain_materially_changes_response_at_same_external_p():
    with_prestress = build_pcross_tbeam_solver(prestress_eps0=0.0075).solve(angle_v_deg=5.0, P_target=1000.0)
    without_prestress = build_pcross_tbeam_solver(prestress_eps0=0.0).solve(angle_v_deg=5.0, P_target=1000.0)

    # Prestress manifests primarily via equilibrium shift (y_na/kappa) for this case.
    assert abs(with_prestress["y_na"] - without_prestress["y_na"]) > 0.005
    assert abs(with_prestress["kappa"] - without_prestress["kappa"]) > 5e-4


def test_manual_style_benchmark_subset_is_in_expected_physical_regime():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.0075)

    # Manual-style subset requested in task text.
    subset_lc4 = [5.0, 10.0, 15.0]
    subset_lc3 = [2.0, 5.0, 8.0]

    lc4 = [solver.solve(v, LOAD_CASE_4.P_target) for v in subset_lc4]
    lc3 = [solver.solve(v, LOAD_CASE_3.P_target) for v in subset_lc3]

    # Signs/quadrants: all Mx expected sagging-negative in this convention,
    # while My remains positive for small positive V.
    assert all(r["Mx"] < 0.0 for r in lc4)
    assert all(r["My"] > 0.0 for r in lc4)
    assert all(r["Mx"] < 0.0 for r in lc3)
    assert all(r["My"] > 0.0 for r in lc3)

    # Angle trend checks in the expected physical regime.
    # For this section/material mapping, small-angle My softens with angle for LC3.
    assert lc3[0]["My"] > lc3[1]["My"] > lc3[2]["My"]
    # LC4 shows a mild non-monotonicity but remains smooth (no erratic jump).
    assert max(abs(lc4[i + 1]["My"] - lc4[i]["My"]) for i in range(2)) < 30.0

    # Approximate magnitude regime checks (deliberately broad).
    for row in lc4:
        assert 300.0 < abs(row["Mx"]) < 1600.0
        assert 20.0 < abs(row["My"]) < 700.0
    for row in lc3:
        assert 300.0 < abs(row["Mx"]) < 1600.0
        assert 10.0 < abs(row["My"]) < 500.0


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

    v = 35.0
    res_v = solver.solve(v, P_target=0.0)
    res_op = solver.solve(v + 180.0, P_target=0.0)

    assert np.isclose(res_v["Mx"], -res_op["Mx"], rtol=0.03, atol=8.0)
    assert np.isclose(res_v["My"], -res_op["My"], rtol=0.03, atol=8.0)
