"""Reproducible benchmark fixture for a PCROSS-style prestressed T-beam example.

The source PDFs referenced in the task are not present in the repository, so this
fixture encodes a deterministic T-beam benchmark with the requested topology:
- 8-point T outline
- 28 mild bars
- 2 prestressing bars
- load cases for P=1000 and 2000 kN over requested angle sets

Material mapping keeps this project's modern EC2-oriented models:
- Concrete -> Concrete(f_ck=40 MPa)
- Mild reinforcement -> MildSteel(f_yk=500 MPa)
- Prestressing steel -> PrestressedSteel idealized bilinear EC2 design model
"""

from __future__ import annotations

from dataclasses import dataclass

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel, PrestressedSteel
from core.solver_plastic import PlasticSolver


def _rect_bar_grid(x_values, y_values, area):
    bars = []
    idx = 1
    for y in y_values:
        for x in x_values:
            bars.append({"id": f"S{idx}", "x": x, "y": y, "area": area})
            idx += 1
    return bars


def build_pcross_tbeam_solver(prestress_eps0: float = 0.0075) -> PlasticSolver:
    # 8-point T-section polygon (counter-clockwise), dimensions in meters.
    outline = [
        {"id": 1, "x": -0.45, "y": 0.45},
        {"id": 2, "x": 0.45, "y": 0.45},
        {"id": 3, "x": 0.45, "y": 0.25},
        {"id": 4, "x": 0.15, "y": 0.25},
        {"id": 5, "x": 0.15, "y": -0.65},
        {"id": 6, "x": -0.15, "y": -0.65},
        {"id": 7, "x": -0.15, "y": 0.25},
        {"id": 8, "x": -0.45, "y": 0.25},
    ]

    # 28 mild bars arranged in four layers.
    x7 = [-0.35, -0.23, -0.11, 0.0, 0.11, 0.23, 0.35]
    y4 = [0.36, 0.12, -0.12, -0.52]
    mild_bars = _rect_bar_grid(x7, y4, area=245.0)

    pre_bars = [
        {"id": "P1", "x": -0.08, "y": -0.58, "area": 980.0, "eps0": prestress_eps0},
        {"id": "P2", "x": 0.08, "y": -0.58, "area": 980.0, "eps0": prestress_eps0},
    ]

    cs = CrossSection(outline, [], mild_bars, pre_bars)
    return PlasticSolver(
        cross_section=cs,
        concrete=Concrete(f_ck=40.0, gamma_c=1.45, alpha_cc=1.0),
        mild_steel=MildSteel(f_yk=500.0, gamma_s=1.15),
        prestressed_steel=PrestressedSteel(
            f_p01k=1500.0,
            f_pk=1700.0,
            e_uk=0.035,
            gamma_s=1.15,
            E_p=195000.0,
            initial_strain=0.0,
        ),
    )


@dataclass(frozen=True)
class LoadCase:
    P_target: float
    angles_deg: tuple[float, ...]


LOAD_CASE_3 = LoadCase(P_target=1000.0, angles_deg=tuple(float(v) for v in range(2, 50, 3)))
LOAD_CASE_4 = LoadCase(P_target=2000.0, angles_deg=tuple(float(v) for v in range(5, 76, 5)))
