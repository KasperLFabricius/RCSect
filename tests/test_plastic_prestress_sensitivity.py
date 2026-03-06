from core.geometry import CrossSection
from core.materials import Concrete, MildSteel, PrestressedSteel
from core.solver_plastic import PlasticSolver


def _build_solver(include_prestress: bool) -> PlasticSolver:
    section = CrossSection(
        concrete_outline=[
            {"id": "o1", "x": -0.25, "y": -0.35},
            {"id": "o2", "x": 0.25, "y": -0.35},
            {"id": "o3", "x": 0.25, "y": 0.35},
            {"id": "o4", "x": -0.25, "y": 0.35},
        ],
        concrete_voids=[],
        rebar_mild=[
            {"id": "S1", "x": -0.2, "y": -0.3, "area": 120.0},
            {"id": "S2", "x": 0.2, "y": -0.3, "area": 120.0},
            {"id": "S3", "x": -0.2, "y": 0.3, "area": 120.0},
            {"id": "S4", "x": 0.2, "y": 0.3, "area": 120.0},
        ],
        rebar_prestressed=(
            [
                {"id": "P1", "x": -0.18, "y": -0.28, "area": 900.0, "eps0": 0.008},
                {"id": "P2", "x": 0.18, "y": -0.28, "area": 900.0, "eps0": 0.008},
            ]
            if include_prestress
            else []
        ),
    )

    prestressed_steel = None
    if include_prestress:
        prestressed_steel = PrestressedSteel(
            f_p01k=1500.0,
            f_pk=1700.0,
            e_uk=0.035,
            gamma_s=1.2,
            E_p=195000.0,
            initial_strain=0.0,
        )

    return PlasticSolver(
        cross_section=section,
        concrete=Concrete(f_ck=40.0),
        mild_steel=MildSteel(f_yk=500.0),
        prestressed_steel=prestressed_steel,
    )


def test_plastic_capacity_changes_when_prestressed_reinforcement_is_removed():
    with_prestress = _build_solver(include_prestress=True).solve(angle_v_deg=5.0, P_target=150.0)
    without_prestress = _build_solver(include_prestress=False).solve(angle_v_deg=5.0, P_target=150.0)

    assert abs(with_prestress["Mx"] - without_prestress["Mx"]) > 0.5
