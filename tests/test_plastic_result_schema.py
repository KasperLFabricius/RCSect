import math

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel, PrestressedSteel
from core.solver_plastic import PlasticSolver
from ui.results import prepare_plastic_results_tables


def _build_cross_section(include_prestress: bool) -> CrossSection:
    rebar_pre = []
    if include_prestress:
        rebar_pre = [
            {"id": "P1", "x": -0.12, "y": -0.10, "area": 140.0, "eps0": 0.0015},
            {"id": "P2", "x": 0.12, "y": 0.10, "area": 140.0},
        ]
    return CrossSection(
        concrete_outline=[
            {"id": "o1", "x": -0.2, "y": -0.3},
            {"id": "o2", "x": 0.2, "y": -0.3},
            {"id": "o3", "x": 0.2, "y": 0.3},
            {"id": "o4", "x": -0.2, "y": 0.3},
        ],
        concrete_voids=[],
        rebar_mild=[
            {"id": "S1", "x": -0.15, "y": -0.25, "area": 200.0},
            {"id": "S2", "x": 0.15, "y": -0.25, "area": 200.0},
            {"id": "S3", "x": 0.15, "y": 0.25, "area": 200.0},
            {"id": "S4", "x": -0.15, "y": 0.25, "area": 200.0},
        ],
        rebar_prestressed=rebar_pre,
    )


def _build_solver(include_prestress: bool) -> PlasticSolver:
    prestressed_steel = (
        PrestressedSteel(
            f_p01k=1500.0,
            f_pk=1700.0,
            e_uk=0.035,
            gamma_s=1.2,
            E_p=195000.0,
            initial_strain=0.001,
        )
        if include_prestress
        else None
    )
    return PlasticSolver(
        cross_section=_build_cross_section(include_prestress=include_prestress),
        concrete=Concrete(f_ck=30.0),
        mild_steel=MildSteel(f_yk=500.0),
        prestressed_steel=prestressed_steel,
    )


def _solve_one_case(include_prestress: bool) -> dict:
    solver = _build_solver(include_prestress=include_prestress)
    return solver.solve(angle_v_deg=25.0, P_target=200.0)


def test_solver_result_schema_with_prestressed_bars():
    result = _solve_one_case(include_prestress=True)

    expected_keys = {
        "na_intersect_x",
        "na_intersect_y",
        "strain_concrete",
        "strain_mild",
        "strain_prestressed",
        "compress_force",
        "lever_L",
        "lever_DX",
        "lever_DY",
        "warning",
        "pivot",
        "candidate_count",
        "selected_candidate_index",
        "selection_source",
    }
    assert expected_keys.issubset(result.keys())
    assert result["strain_prestressed"] is not None
    assert math.isfinite(float(result["strain_prestressed"]))


def test_solver_result_schema_without_prestressed_bars():
    result = _solve_one_case(include_prestress=False)

    expected_keys = {
        "na_intersect_x",
        "na_intersect_y",
        "strain_concrete",
        "strain_mild",
        "strain_prestressed",
        "compress_force",
        "lever_L",
        "lever_DX",
        "lever_DY",
        "warning",
        "pivot",
        "candidate_count",
        "selected_candidate_index",
        "selection_source",
    }
    assert expected_keys.issubset(result.keys())
    assert result["strain_prestressed"] is None


def test_prepare_plastic_results_tables_adds_schema_and_export_columns():
    plastic_rows = [
        {
            "Mx": 100.0,
            "My": 40.0,
            "V": 25.0,
            "y_na": 0.12,
            "kappa": 0.003,
            "na_intersect_x": 0.15,
            "na_intersect_y": -0.32,
            "strain_concrete": 3.5,
            "strain_mild": 8.0,
            "strain_prestressed": None,
            "compress_force": 1230.0,
            "lever_L": 0.22,
            "lever_DX": 0.16,
            "lever_DY": 0.15,
            "warning": None,
            "pivot": "concrete_controls",
        }
    ]

    df_display, export_df = prepare_plastic_results_tables(plastic_rows, target_P=200.0)

    assert "U (deg)" in df_display.columns
    assert "R (m)" in df_display.columns
    assert df_display.attrs == {}
    assert export_df.attrs == {}
    assert math.isclose(df_display.loc[0, "U (deg)"], math.degrees(math.atan2(100.0, 40.0)))
    assert math.isclose(df_display.loc[0, "R (m)"], math.sqrt(100.0**2 + 40.0**2) / 200.0)
    expected_export_cols = {
        "Mx_kNm",
        "My_kNm",
        "V_deg",
        "y_na_m",
        "kappa_1_per_m",
        "na_intersect_x_m",
        "na_intersect_y_m",
        "strain_concrete_permille",
        "strain_mild_permille",
        "strain_prestressed_permille",
        "compress_force_kN",
        "lever_L_m",
        "lever_DX_m",
        "lever_DY_m",
        "warning",
        "pivot",
        "candidate_count",
        "selected_candidate_index",
        "selection_source",
    }
    assert expected_export_cols.issubset(export_df.columns)
    assert export_df.loc[0, "strain_prestressed_permille"] is None
