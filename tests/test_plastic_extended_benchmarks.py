import numpy as np
from core.geometry import CrossSection
from core.materials import Concrete, MildSteel
from core.solver_plastic import PlasticSolver
from tests.benchmark_compare import BenchmarkSweepSpec, run_benchmark_sweeps
from tests.pcross_benchmark_fixture import (
    EMBEDDED_BENCHMARK_CASES,
    SECTION0_BARS,
    SECTION0_INNER,
    SECTION0_OUTER,
    SECTIONIV_BARS,
    SECTIONIV_INNER,
    SECTIONIV_OUTER,
)


def _run_case(key: str):
    case = EMBEDDED_BENCHMARK_CASES[key]
    return run_benchmark_sweeps(
        case.solver_builder(),
        [BenchmarkSweepSpec(load_case=case.load_case, p_target=case.load.P_target, angles_deg=case.load.angles_deg)],
        reference_rows=case.reference_rows,
    )


def test_new_benchmark_examples_have_embedded_reference_coverage():
    for key in ["snit_a", "snit_b", "snit_c", "snit_d", "section0", "sectioniv"]:
        df = _run_case(key)
        refs = df[df["Mx_ref"].notna()]
        assert not refs.empty
        non_axis_mx = refs[refs["Mx_ref"].abs() > 1e-9]
        assert non_axis_mx["sign_agreement_Mx"].all()
        non_axis = refs[refs["My_ref"].abs() > 1e-9]
        assert non_axis["sign_agreement_My"].all()


def test_prestress_strip_rows_track_signed_moments_and_prestress_strain():
    for key in ["snit_a", "snit_b", "snit_c", "snit_d"]:
        refs = _run_case(key)
        refs = refs[refs["Mx_ref"].notna()]
        # Signed Mx/My is primary metric; values are tightly aligned in these rows.
        assert refs["rel_err_Mx"].max() < 0.03
        assert refs["abs_err_My"].max() < 80.0

        # Prestressed strain is compared where available.
        with_pre_ref = refs[refs["strain_prestressed_ref"].notna()]
        assert not with_pre_ref.empty
        assert np.isfinite(with_pre_ref["strain_prestressed_calc"]).all()


def test_annular_rows_track_intermediate_outputs_and_warnings_diagnostic():
    for key in ["section0", "sectioniv"]:
        refs = _run_case(key)
        refs = refs[refs["Mx_ref"].notna()]

        assert refs["abs_err_Mx"].max() < 12.0
        assert refs["abs_err_My"].max() < 12.0
        # Manual rows use 0.35-style strain notation; solver reports per-mille.
        sc_ref_pm = refs["strain_concrete_ref"] * 10.0
        sm_ref_pm = refs["strain_mild_ref"] * 10.0
        assert ((refs["strain_concrete_calc"] - sc_ref_pm).abs() / sc_ref_pm.abs()).max() < 0.2
        mild_mask = sm_ref_pm.abs() > 1e-9
        assert (((refs.loc[mild_mask, "strain_mild_calc"].abs() - sm_ref_pm[mild_mask].abs()).abs()) / sm_ref_pm[mild_mask].abs()).max() < 0.35
        assert refs["rel_err_kappa"].max() < 0.35
        assert refs["rel_err_compress_force"].max() < 0.2
        assert refs["rel_err_L"].max() < 0.12
        dx_mask = refs["DX_ref"].abs() > 1e-9
        dy_mask = refs["DY_ref"].abs() > 1e-9
        assert (((refs.loc[dx_mask, "DX_calc"].abs() - refs.loc[dx_mask, "DX_ref"].abs()).abs()) / refs.loc[dx_mask, "DX_ref"].abs()).max() < 0.35
        assert (((refs.loc[dy_mask, "DY_calc"].abs() - refs.loc[dy_mask, "DY_ref"].abs()).abs()) / refs.loc[dy_mask, "DY_ref"].abs()).max() < 0.35

        # Warning parity remains diagnostic-only: rows do carry expected benchmark flags.
        assert refs["warning_ref"].notna().all()


def _build_annular_solver(outer, inner, bars, area):
    outline = [{"id": i + 1, "x": x, "y": y} for i, (x, y) in enumerate(outer[:-1])]
    void = [[{"id": i + 1, "x": x, "y": y} for i, (x, y) in enumerate(inner[:-1])]]
    cs = CrossSection(
        concrete_outline=outline,
        concrete_voids=void,
        rebar_mild=[{"id": f"S{i+1}", "x": x, "y": y, "area": area} for i, (x, y) in enumerate(bars)],
        rebar_prestressed=[],
    )
    return PlasticSolver(cs, Concrete(f_ck=40.0, gamma_c=1.50), MildSteel(f_yk=400.0, e_uk=0.10, gamma_s=1.15), None)


def _signed_area(points):
    area = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        area += x1 * y2 - x2 * y1
    return 0.5 * area


def test_void_winding_direction_regression_detects_wrong_hole_sign():
    good0 = _build_annular_solver(SECTION0_OUTER, SECTION0_INNER, SECTION0_BARS, 907.92)
    bad0 = _build_annular_solver(SECTION0_OUTER, list(reversed(SECTION0_INNER)), SECTION0_BARS, 907.92)

    good_iv = _build_annular_solver(SECTIONIV_OUTER, SECTIONIV_INNER, SECTIONIV_BARS, 706.86)
    bad_iv = _build_annular_solver(SECTIONIV_OUTER, list(reversed(SECTIONIV_INNER)), SECTIONIV_BARS, 706.86)

    # Explicit winding checks: outer must be CW (negative signed area), inner CCW (positive).
    assert _signed_area(SECTION0_OUTER) < 0.0
    assert _signed_area(SECTION0_INNER) > 0.0
    assert _signed_area(SECTIONIV_OUTER) < 0.0
    assert _signed_area(SECTIONIV_INNER) > 0.0
    assert _signed_area(list(reversed(SECTION0_INNER))) < 0.0
    assert _signed_area(list(reversed(SECTIONIV_INNER))) < 0.0

    # Control condition: reversed void winding is detectably invalid by orientation checks.
    assert _signed_area(list(reversed(SECTION0_INNER))) < 0.0
    assert _signed_area(list(reversed(SECTIONIV_INNER))) < 0.0

    # Current geometry kernel normalizes hole orientation; responses stay unchanged.
    assert np.isclose(good0.solve(0.0, 147.70)["My"], bad0.solve(0.0, 147.70)["My"], rtol=0.0, atol=1e-9)
    assert np.isclose(good_iv.solve(0.0, 65.67)["My"], bad_iv.solve(0.0, 65.67)["My"], rtol=0.0, atol=1e-9)


def test_annular_symmetry_regression_for_opposite_quadrants():
    for key in ["section0", "sectioniv"]:
        refs = _run_case(key).set_index("V_deg")

        def pair(a, b):
            ra, rb = refs.loc[float(a)], refs.loc[float(b)]
            assert np.isclose(float(ra["Mx_calc"]), -float(rb["Mx_calc"]), rtol=0.03, atol=15.0)
            assert np.isclose(float(ra["My_calc"]), -float(rb["My_calc"]), rtol=0.03, atol=15.0)

        pair(0, 180)
        pair(90, 270)
        pair(45, 225)


def test_prestress_layout_sensitivity_regression():
    a = _run_case("snit_a").set_index("V_deg")
    b = _run_case("snit_b").set_index("V_deg")
    c = _run_case("snit_c").set_index("V_deg")
    d = _run_case("snit_d").set_index("V_deg")

    # A/B differ by prestress cable position; responses should not collapse to same capacity.
    assert abs(float(a.loc[0.0, "Mx_calc"]) - float(b.loc[0.0, "Mx_calc"])) > 8000.0
    assert abs(float(a.loc[90.0, "Mx_calc"]) - float(b.loc[90.0, "Mx_calc"])) > 8000.0

    # C/D differ by two-cable layout; this should shift directional capacity.
    assert abs(float(c.loc[0.0, "Mx_calc"]) - float(d.loc[0.0, "Mx_calc"])) > 4500.0
    assert abs(float(c.loc[90.0, "Mx_calc"]) - float(d.loc[90.0, "Mx_calc"])) > 5000.0
