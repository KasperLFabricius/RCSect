import math
import pathlib
import sys

from shapely.geometry import Polygon

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core.geometry import CrossSection
from core.solver_elastic import (
    ElasticSolver,
    _max_concrete_stress_on_boundary,
    integrate_concrete_zone,
)


def _make_rectangular_section():
    outline = [
        {"id": "p1", "x": -0.2, "y": -0.3},
        {"id": "p2", "x": 0.2, "y": -0.3},
        {"id": "p3", "x": 0.2, "y": 0.3},
        {"id": "p4", "x": -0.2, "y": 0.3},
    ]
    rebars = [
        {"id": "B1", "x": -0.15, "y": -0.25, "area": 200.0},
        {"id": "B2", "x": 0.15, "y": -0.25, "area": 200.0},
        {"id": "B3", "x": 0.15, "y": 0.25, "area": 200.0},
        {"id": "B4", "x": -0.15, "y": 0.25, "area": 200.0},
    ]
    return CrossSection(outline, [], rebars, [])


def test_boundary_max_concrete_stress_exceeds_quadrature_peak_when_vertex_controls():
    concrete = Polygon([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
    eps0 = 0.0
    kx = 0.0
    ky = 100.0
    ec_eff = 1.0

    _, _, _, max_qp = integrate_concrete_zone(concrete, eps0, kx, ky, ec_eff)
    max_boundary = _max_concrete_stress_on_boundary(concrete, eps0, kx, ky, ec_eff)

    assert math.isclose(max_boundary, 100.0, rel_tol=0.0, abs_tol=1e-12)
    assert max_boundary > max_qp


def test_combined_loads_exposes_long_and_rst1_na_intersections():
    section = _make_rectangular_section()
    solver = ElasticSolver(section, E_c=32000.0, E_s=200000.0)

    result = solver.solve_combined_loads(
        P_l=1200.0,
        Mx_l=30.0,
        My_l=20.0,
        n_l=8.0,
        P_s=300.0,
        Mx_s=10.0,
        My_s=5.0,
        n_s=6.0,
    )

    assert "na_LONG" in result
    assert "na_RST1" in result

    for key in ("na_LONG", "na_RST1"):
        assert "x_intercept" in result[key]
        assert "y_intercept" in result[key]
        assert result[key]["x_intercept"] is not None
        assert result[key]["y_intercept"] is not None
        assert math.isfinite(result[key]["x_intercept"])
        assert math.isfinite(result[key]["y_intercept"])
