import numpy as np

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel, ConcreteType1, MildSteelType1, PrestressedSteelType1
from core.solver_plastic import PlasticSolver
from tests.benchmark_compare import BenchmarkSweepSpec, run_benchmark_sweeps
from tests.pcross_benchmark_fixture import (
    BENCHMARK_MAPPINGS,
    DEFAULT_BENCHMARK_MAPPING,
    LOAD_CASE_3,
    LOAD_CASE_4,
    MANUAL_ROWS,
    build_pcross_tbeam_solver,
    EMBEDDED_BENCHMARK_CASES,
)


def _detailed_benchmark_df(mapping=DEFAULT_BENCHMARK_MAPPING):
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004, mapping=mapping)
    specs = [
        BenchmarkSweepSpec(load_case=3, p_target=LOAD_CASE_3.P_target, angles_deg=LOAD_CASE_3.angles_deg),
        BenchmarkSweepSpec(load_case=4, p_target=LOAD_CASE_4.P_target, angles_deg=LOAD_CASE_4.angles_deg),
    ]
    return run_benchmark_sweeps(solver, specs)






def test_fixture_builders_use_legacy_family_material_classes():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004, mapping=DEFAULT_BENCHMARK_MAPPING)
    assert isinstance(solver.concrete, ConcreteType1)
    assert isinstance(solver.mild_steel, MildSteelType1)
    assert isinstance(solver.prestressed_steel, PrestressedSteelType1)

def test_manual_benchmark_mapping_factors_are_applied_in_fixture():
    mapping = BENCHMARK_MAPPINGS[DEFAULT_BENCHMARK_MAPPING]
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004, mapping=DEFAULT_BENCHMARK_MAPPING)

    assert np.isclose(solver.concrete.gamma_c, 1.90)
    assert np.isclose(solver.mild_steel.gamma_s, 1.50)
    assert np.isclose(solver.prestressed_steel.gamma_s, 1.50)
    assert np.isclose(solver.mild_steel.gamma_E, mapping.gamma_E)
    assert np.isclose(solver.prestressed_steel.gamma_E, mapping.gamma_E)
    assert np.isclose(solver.mild_steel.gamma_u, mapping.gamma_u)
    assert np.isclose(solver.prestressed_steel.gamma_u, mapping.gamma_u)
def test_external_axial_force_materially_changes_plastic_solution_exact_fixture():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    res_p1000 = solver.solve(angle_v_deg=10.0, P_target=1000.0)
    res_p2000 = solver.solve(angle_v_deg=10.0, P_target=2000.0)

    assert not np.isclose(res_p1000["Mx"], res_p2000["Mx"], rtol=0.01, atol=10.0)
    # Depending on branch selection, My can move less than Mx for this fixture.
    assert abs(res_p1000["My"] - res_p2000["My"]) > 0.1
    assert not np.isclose(res_p1000["y_na"], res_p2000["y_na"], rtol=0.01, atol=0.005)
    assert np.isclose(res_p1000["N_calc"], 1000.0, rtol=1e-6, atol=1e-4)
    assert np.isclose(res_p2000["N_calc"], 2000.0, rtol=1e-6, atol=1e-4)


def test_prestress_eps0_materially_changes_response_exact_fixture():
    with_prestress = build_pcross_tbeam_solver(prestress_eps0=0.004).solve(angle_v_deg=2.0, P_target=1000.0)
    without_prestress = build_pcross_tbeam_solver(prestress_eps0=0.0).solve(angle_v_deg=2.0, P_target=1000.0)

    assert abs(with_prestress["Mx"] - without_prestress["Mx"]) > 0.5
    assert abs(with_prestress["My"] - without_prestress["My"]) > 0.2
    assert abs(with_prestress["y_na"] - without_prestress["y_na"]) > 3e-4


def test_benchmark_sequences_have_expected_sign_quadrant_and_trend_behavior():
    df = _detailed_benchmark_df()
    refs = df[df["Mx_ref"].notna()].copy()

    assert refs["sign_agreement_Mx"].all()
    assert refs["sign_agreement_My"].all()
    assert refs["quadrant_agreement"].all()

    lc3 = df[df["load_case"] == 3].reset_index(drop=True)
    lc4 = df[df["load_case"] == 4].reset_index(drop=True)

    # Signed and magnitude trends are both useful sequence diagnostics.
    assert (lc3["trend_sign_Mx"].dropna() >= 0).all()
    assert (lc4["trend_sign_Mx"].dropna() >= 0).all()
    assert (lc3["trend_sign_My"].dropna() <= 0).all()
    assert (lc4["trend_sign_My"].dropna() <= 0).all()
    assert (lc3["trend_sign_Mx_abs"].dropna() >= 0).all()
    assert (lc4["trend_sign_Mx_abs"].dropna() >= 0).all()
    assert (lc3["trend_sign_My_abs"].dropna() <= 0).all()
    assert (lc4["trend_sign_My_abs"].dropna() <= 0).all()


def test_benchmark_reference_rows_match_with_explicit_error_tolerances():
    df = _detailed_benchmark_df()
    refs = df[df["Mx_ref"].notna()].copy()

    assert refs.shape[0] == len(MANUAL_ROWS)

    # Signed benchmark agreement: signs and quadrants must match embedded references.
    assert refs["sign_agreement_Mx"].all()
    assert refs["sign_agreement_My"].all()
    assert refs["quadrant_agreement"].all()

    # Keep guards close to the current branch achieved benchmark performance,
    # while allowing limited numerical headroom.
    assert refs["rel_err_Mx"].max() <= 0.10
    assert refs["rel_err_My"].max() <= 0.06

    lc3_refs = refs[refs["load_case"] == 3]
    lc4_refs = refs[refs["load_case"] == 4]

    assert lc3_refs["rel_err_Mx"].max() <= 0.07
    assert lc3_refs["rel_err_My"].max() <= 0.03
    assert lc4_refs["rel_err_Mx"].max() <= 0.08
    assert lc4_refs["rel_err_My"].max() <= 0.04


def test_sweep_has_branch_continuity_and_no_obvious_branch_flips():
    df = _detailed_benchmark_df()

    for load_case, group in df.groupby("load_case"):
        rows = group.sort_values("V_deg").to_dict("records")
        flips = 0
        for prev, cur in zip(rows, rows[1:]):
            scale_m = max(abs(prev["Mx_calc"]), abs(prev["My_calc"]), 10.0)
            jump = abs(cur["Mx_calc"] - prev["Mx_calc"]) / scale_m + abs(cur["My_calc"] - prev["My_calc"]) / scale_m
            assert jump < 0.65
            if prev["pivot"] != cur["pivot"]:
                flips += 1

        # Continuity rule should avoid chatter in these benchmark sweeps.
        assert flips <= 1, f"excessive branch flips in load case {load_case}"


def test_single_angle_matches_sweep_for_unique_candidate_case():
    section = CrossSection(
        concrete_outline=[
            {"id": 1, "x": -0.2, "y": -0.2},
            {"id": 2, "x": 0.2, "y": -0.2},
            {"id": 3, "x": 0.2, "y": 0.2},
            {"id": 4, "x": -0.2, "y": 0.2},
        ],
        concrete_voids=[],
        rebar_mild=[
            {"id": "S1", "x": -0.14, "y": -0.14, "area": 200.0},
            {"id": "S2", "x": 0.14, "y": -0.14, "area": 200.0},
            {"id": "S3", "x": -0.14, "y": 0.14, "area": 200.0},
            {"id": "S4", "x": 0.14, "y": 0.14, "area": 200.0},
        ],
        rebar_prestressed=[],
    )
    solver = PlasticSolver(section, Concrete(f_ck=30.0), MildSteel(f_yk=500.0), prestressed_steel=None)

    angle = 0.0
    p_target = 0.0
    cands = solver._solve_candidates(angle, p_target)
    assert len(cands) == 1

    single = solver.solve(angle, p_target)
    sweep = solver.solve_angle_sweep([angle], p_target)[0]

    assert single["candidate_count"] == 1
    assert sweep["candidate_count"] == 1
    assert np.isclose(single["Mx"], sweep["Mx"], rtol=1e-8, atol=1e-8)
    assert np.isclose(single["My"], sweep["My"], rtol=1e-8, atol=1e-8)
    assert np.isclose(single["y_na"], sweep["y_na"], rtol=1e-8, atol=1e-10)


def test_single_angle_vs_sweep_multicandidate_is_explicit_in_diagnostics():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    angle = 5.0
    p_target = LOAD_CASE_3.P_target

    cands = solver._solve_candidates(angle, p_target)
    assert len(cands) == 2

    single = solver.solve(angle, p_target)
    sweep = solver.solve_angle_sweep([angle], p_target)[0]

    assert single["candidate_count"] == 2
    assert sweep["candidate_count"] == 2
    assert single["selection_source"] == "single_min_abs_kappa"
    assert sweep["selection_source"] == "sweep_seed_min_abs_kappa"
    assert single["selected_candidate_index"] in (0, 1)
    assert sweep["selected_candidate_index"] in (0, 1)


def test_low_axial_sweep_is_continuous_for_exact_fixture():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    rows = solver.solve_angle_sweep([float(v) for v in range(0, 181, 5)], P_target=0.0)

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


def test_candidate_multiplicity_is_visible_for_known_dual_root_case():
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    angle = 2.0
    p_target = LOAD_CASE_3.P_target

    raw = solver._solve_candidates(angle, p_target)
    assert len(raw) == 2

    picked = solver.solve(angle, p_target)
    assert picked["candidate_count"] == 2
    assert picked["selected_candidate_index"] in (0, 1)
    assert picked["pivot"] in {c["pivot"] for c in raw}


def test_extended_fixture_sweeps_have_signed_moment_coverage():
    for key in ["snit_a", "snit_b", "snit_c", "snit_d", "section0", "sectioniv"]:
        case = EMBEDDED_BENCHMARK_CASES[key]
        df = run_benchmark_sweeps(
            case.solver_builder(),
            [BenchmarkSweepSpec(case.load_case, case.load.P_target, case.load.angles_deg)],
            reference_rows=case.reference_rows,
        )
        refs = df[df["Mx_ref"].notna()]
        assert not refs.empty
        assert refs[refs["Mx_ref"].abs() > 1e-9]["sign_agreement_Mx"].all()


def test_compress_force_is_direct_sum_of_compression_partitions():
    case = EMBEDDED_BENCHMARK_CASES["snit_a"]
    result = case.solver_builder().solve(angle_v_deg=90.0, P_target=case.load.P_target)

    comp_total = result["compress_zone_force_total"]
    comp_parts = (
        result["compress_zone_force_concrete"]
        + result["compress_zone_force_mild"]
        + result["compress_zone_force_prestressed"]
    )
    assert np.isclose(comp_total, comp_parts, rtol=0.0, atol=1e-9)
    assert np.isclose(result["compress_force"], comp_total, rtol=0.0, atol=1e-9)


def test_lever_arm_is_centroid_vector_and_not_m_over_compress_override():
    case = EMBEDDED_BENCHMARK_CASES["snit_a"]
    angle = 90.0
    result = case.solver_builder().solve(angle_v_deg=angle, P_target=case.load.P_target)

    c = result["debug_resultant_centroids"]
    dx_local = c["tension_zone_centroid_x"] - c["compress_zone_centroid_x"]
    dy_local = c["tension_zone_centroid_y"] - c["compress_zone_centroid_y"]

    angle_rad = np.radians(case.solver_builder().cs.local_rotation_deg(angle))
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    dx_global = dx_local * cos_a - dy_local * sin_a
    dy_global = dx_local * sin_a + dy_local * cos_a

    # Legacy benchmark sign convention uses negated arm components.
    assert np.isclose(result["lever_DX"], -dx_global, rtol=0.0, atol=1e-9)
    assert np.isclose(result["lever_DY"], -dy_global, rtol=0.0, atol=1e-9)
    assert np.isclose(result["lever_L"], np.hypot(dx_global, dy_global), rtol=0.0, atol=1e-9)

    # Guardrail: benchmark-critical path should not force moment/compress surrogate.
    dy_from_m = result["Mx"] / max(result["compress_force"], 1e-9)
    assert abs(result["lever_DY"] - dy_from_m) > 1e-4


def test_strain_outputs_follow_governing_force_bars_with_total_strain():
    case = EMBEDDED_BENCHMARK_CASES["snit_a"]
    result = case.solver_builder().solve(angle_v_deg=90.0, P_target=case.load.P_target)
    dbg = result["debug_force_components"]
    sc = result["debug_strain_candidates"]

    mild = max(dbg["mild_bar_details"], key=lambda r: abs(r["force_kN"]))
    assert sc["strain_mild_governing_force_bar_id"] == mild["id"]
    assert np.isclose(result["strain_mild"], -mild["strain_total"] * 1000.0, rtol=0.0, atol=1e-9)

    prest = max(dbg["prestressed_bar_details"], key=lambda r: abs(r["force_kN"]))
    assert sc["strain_prestressed_governing_force_bar_id"] == prest["id"]
    assert np.isclose(result["strain_prestressed"], -prest["strain_total"] * 1000.0, rtol=0.0, atol=1e-9)
    assert not np.isclose(result["strain_prestressed"], prest["strain_incremental"] * 1000.0, rtol=0.0, atol=1e-6)
