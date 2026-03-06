import pytest

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel, PrestressedSteel
from core.solver_plastic import PlasticSolver


def _build_solver(pre_bars, default_eps0=0.0):
    cs = CrossSection(
        concrete_outline=[
            {"id": 1, "x": -0.5, "y": -0.5},
            {"id": 2, "x": 0.5, "y": -0.5},
            {"id": 3, "x": 0.5, "y": 0.5},
            {"id": 4, "x": -0.5, "y": 0.5},
        ],
        concrete_voids=[],
        rebar_mild=[],
        rebar_prestressed=pre_bars,
    )
    solver = PlasticSolver(
        cross_section=cs,
        concrete=Concrete(f_ck=30.0),
        mild_steel=MildSteel(f_yk=500.0),
        prestressed_steel=PrestressedSteel(
            f_p01k=1500.0,
            f_pk=1700.0,
            e_uk=0.035,
            gamma_s=1.2,
            E_p=195000.0,
            initial_strain=default_eps0,
        ),
    )
    solver.poly_rot, solver.rebar_mild_rot, solver.rebar_pre_rot = cs.get_rotated_system(0.0)
    solver.prestrain_default = default_eps0
    return solver


def _bar_force_from_total_strain(total_strain, area_mm2, E_p=195000.0):
    return total_strain * E_p * area_mm2 * 1e-6


def test_prestressed_bar_eps0_override_changes_response_per_bar():
    bars = [
        {"id": 1, "x": 0.0, "y": 0.0, "area": 100.0, "eps0": 0.0},
        {"id": 2, "x": 0.0, "y": 0.0, "area": 100.0, "eps0": 0.002},
    ]
    solver = _build_solver(bars, default_eps0=0.001)

    y_na = 1.0
    kappa = 0.001
    geometric_strain = kappa * (y_na - 0.0)

    res = solver._calculate_detailed_internal_forces(y_na=y_na, kappa=kappa)
    expected = _bar_force_from_total_strain(geometric_strain + 0.0, 100.0) + _bar_force_from_total_strain(
        geometric_strain + 0.002, 100.0
    )

    assert res["N_tot"] == pytest.approx(expected)
    assert _bar_force_from_total_strain(geometric_strain + 0.002, 100.0) > _bar_force_from_total_strain(
        geometric_strain + 0.0, 100.0
    )


def test_prestressed_bar_uses_material_default_eps0_when_missing_on_bar():
    bars = [{"id": 1, "x": 0.0, "y": 0.0, "area": 100.0}]
    solver = _build_solver(bars, default_eps0=0.0015)

    y_na = 1.0
    kappa = 0.001
    geometric_strain = kappa * (y_na - 0.0)

    res = solver._calculate_detailed_internal_forces(y_na=y_na, kappa=kappa)
    expected = _bar_force_from_total_strain(geometric_strain + 0.0015, 100.0)

    assert res["N_tot"] == pytest.approx(expected)


def test_prestressed_bar_uses_geometric_strain_when_no_default_and_no_bar_eps0():
    bars = [{"id": 1, "x": 0.0, "y": 0.0, "area": 100.0}]
    solver = _build_solver(bars, default_eps0=0.0)

    y_na = 1.0
    kappa = 0.001
    geometric_strain = kappa * (y_na - 0.0)

    res = solver._calculate_detailed_internal_forces(y_na=y_na, kappa=kappa)
    expected = _bar_force_from_total_strain(geometric_strain, 100.0)

    assert res["N_tot"] == pytest.approx(expected)
