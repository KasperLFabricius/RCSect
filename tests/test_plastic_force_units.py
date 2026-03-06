import numpy as np

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel, PrestressedSteel
from core.solver_plastic import PlasticSolver, _bar_force_kN


def _simple_section(with_mild: bool, with_pre: bool) -> CrossSection:
    mild = [{"id": "S1", "x": 0.0, "y": -0.02, "area": 1000.0}] if with_mild else []
    pre = [{"id": "P1", "x": 0.0, "y": -0.03, "area": 1000.0, "eps0": 0.0}] if with_pre else []
    return CrossSection(
        concrete_outline=[
            {"id": 1, "x": -0.1, "y": -0.1},
            {"id": 2, "x": 0.1, "y": -0.1},
            {"id": 3, "x": 0.1, "y": 0.1},
            {"id": 4, "x": -0.1, "y": 0.1},
        ],
        concrete_voids=[],
        rebar_mild=mild,
        rebar_prestressed=pre,
    )


def test_mild_bar_force_conversion_is_kN_basis():
    sigma_mpa = 100.0
    area_mm2 = 1000.0
    force = _bar_force_kN(sigma_mpa, area_mm2)
    assert np.isclose(force, 100.0, rtol=0.0, atol=1e-12)

    # Compression uses negative stress sign in material convention.
    assert np.isclose(_bar_force_kN(-sigma_mpa, area_mm2), -100.0, rtol=0.0, atol=1e-12)


def test_prestressed_bar_force_conversion_is_same_kN_basis_as_mild():
    sigma_mpa = 100.0
    area_mm2 = 1000.0
    assert np.isclose(_bar_force_kN(sigma_mpa, area_mm2), 100.0, rtol=0.0, atol=1e-12)


def test_mixed_internal_force_assembly_catches_1000x_scaling_errors():
    y_na = 0.01
    kappa = 0.005

    no_steel = PlasticSolver(
        _simple_section(with_mild=False, with_pre=False),
        Concrete(f_ck=30.0),
        MildSteel(f_yk=500.0),
        prestressed_steel=None,
    )
    no_steel._prepare_rotated_state(0.0)
    base = no_steel._calculate_detailed_internal_forces(y_na=y_na, kappa=kappa)

    with_steel = PlasticSolver(
        _simple_section(with_mild=True, with_pre=True),
        Concrete(f_ck=30.0),
        MildSteel(f_yk=500.0),
        prestressed_steel=PrestressedSteel(f_p01k=1500.0, f_pk=1700.0, e_uk=0.035),
    )
    with_steel._prepare_rotated_state(0.0)
    mixed = with_steel._calculate_detailed_internal_forces(y_na=y_na, kappa=kappa)

    mild_y = with_steel.rebar_mild_rot[0]["y"]
    pre_y = with_steel.rebar_pre_rot[0]["y"]
    mild_sigma = with_steel.mild_steel.stress(kappa * (y_na - mild_y))
    pre_sigma = with_steel.prestressed_steel.stress(kappa * (y_na - pre_y))
    expected_delta = _bar_force_kN(mild_sigma, 1000.0) + _bar_force_kN(pre_sigma, 1000.0)

    observed_delta = mixed["N_tot"] - base["N_tot"]
    assert np.isclose(observed_delta, expected_delta, rtol=0.0, atol=1e-9)

    # Guardrail against accidental N->MN conversion (1e-6): expected should be O(10-100) kN.
    assert abs(observed_delta) > 10.0
