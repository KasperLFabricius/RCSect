"""Exact PCROSS manual T-beam benchmark fixture used by solver regression tests.

Manual input represented here:
- 8-point concrete T outline
- 28 mild bars (491 mm² each)
- 2 prestressing bars (1016 mm² each)
- LC3/LC4 angle sweeps

Material mapping to this project's current EC2-oriented models:
- baseline post-PR32 mapping retained for contribution studies (gamma_c=1.50, gamma_s/p=1.15)
- benchmark-manual design factors for LC3/LC4 are modeled with gamma_c=1.90, gamma_s=1.50, gamma_p=1.50
- benchmark-only mappings can additionally apply gamma_E (steel modulus factor) and gamma_u
  (rupture-limit factor) without changing app-wide defaults
- manual prestress initial strain 0.40% -> per-bar eps0 = 0.004
"""

from __future__ import annotations

from dataclasses import dataclass

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel, PrestressedSteel
from core.solver_plastic import PlasticSolver


CONCRETE_OUTLINE = [
    {"id": 1, "x": -0.600, "y": 0.35},
    {"id": 2, "x": 0.600, "y": 0.35},
    {"id": 3, "x": 0.600, "y": 0.15},
    {"id": 4, "x": 0.150, "y": 0.15},
    {"id": 5, "x": 0.150, "y": -0.65},
    {"id": 6, "x": -0.150, "y": -0.65},
    {"id": 7, "x": -0.150, "y": 0.15},
    {"id": 8, "x": -0.600, "y": 0.15},
]

MILD_BAR_AREA = 491.0
MILD_BAR_POINTS = [
    (-0.55, 0.30), (-0.50, 0.30), (-0.30, 0.30), (-0.10, 0.30), (0.10, 0.30), (0.30, 0.30), (0.50, 0.30), (0.55, 0.30),
    (-0.55, 0.25), (0.55, 0.25),
    (-0.55, 0.20), (-0.50, 0.20), (-0.30, 0.20), (-0.10, 0.20), (0.10, 0.20), (0.30, 0.20), (0.50, 0.20), (0.55, 0.20),
    (-0.10, -0.07), (0.10, -0.07),
    (-0.10, -0.35), (0.10, -0.35),
    (-0.10, -0.55), (0.10, -0.55),
    (-0.10, -0.60), (-0.03, -0.60), (0.03, -0.60), (0.10, -0.60),
]

PRE_BAR_AREA = 1016.0
PRE_BAR_POINTS = [(0.0, -0.38), (0.0, -0.54)]


@dataclass(frozen=True)
class BenchmarkMaterialMapping:
    name: str
    gamma_c: float
    gamma_s: float
    gamma_p: float
    gamma_E: float = 1.0
    gamma_u: float = 1.0


BENCHMARK_MAPPINGS: dict[str, BenchmarkMaterialMapping] = {
    # Case A: post-PR32 baseline retained for diagnostics.
    "case_a_baseline": BenchmarkMaterialMapping(
        name="case_a_baseline", gamma_c=1.50, gamma_s=1.15, gamma_p=1.15, gamma_E=1.0, gamma_u=1.0
    ),
    # Case B: manual benchmark strength factors (benchmark-only calibration; not app defaults).
    "case_b_manual_strength": BenchmarkMaterialMapping(
        name="case_b_manual_strength", gamma_c=1.90, gamma_s=1.50, gamma_p=1.50, gamma_E=1.0, gamma_u=1.0
    ),
    # Case C: manual strength + modulus partial factor FE.
    "case_c_manual_strength_plus_fe": BenchmarkMaterialMapping(
        name="case_c_manual_strength_plus_fe", gamma_c=1.90, gamma_s=1.50, gamma_p=1.50, gamma_E=1.50, gamma_u=1.0
    ),
    # Case D: manual strength + FE + FU benchmark mapping.
    "case_d_manual_strength_plus_fe_fu": BenchmarkMaterialMapping(
        name="case_d_manual_strength_plus_fe_fu", gamma_c=1.90, gamma_s=1.50, gamma_p=1.50, gamma_E=1.50, gamma_u=1.50
    ),
}

DEFAULT_BENCHMARK_MAPPING = "case_d_manual_strength_plus_fe_fu"


def _build_mild_bars():
    return [
        {"id": f"S{i+1}", "x": x, "y": y, "area": MILD_BAR_AREA}
        for i, (x, y) in enumerate(MILD_BAR_POINTS)
    ]


def _build_prestress_bars(eps0: float):
    return [
        {"id": f"P{i+1}", "x": x, "y": y, "area": PRE_BAR_AREA, "eps0": eps0}
        for i, (x, y) in enumerate(PRE_BAR_POINTS)
    ]


def resolve_benchmark_mapping(mapping: str | BenchmarkMaterialMapping | None) -> BenchmarkMaterialMapping:
    if mapping is None:
        return BENCHMARK_MAPPINGS[DEFAULT_BENCHMARK_MAPPING]
    if isinstance(mapping, BenchmarkMaterialMapping):
        return mapping
    if mapping not in BENCHMARK_MAPPINGS:
        raise ValueError(f"Unknown benchmark mapping '{mapping}'")
    return BENCHMARK_MAPPINGS[mapping]


def build_pcross_tbeam_solver(
    prestress_eps0: float = 0.004,
    mapping: str | BenchmarkMaterialMapping | None = None,
) -> PlasticSolver:
    benchmark_mapping = resolve_benchmark_mapping(mapping)

    cs = CrossSection(
        concrete_outline=CONCRETE_OUTLINE,
        concrete_voids=[],
        rebar_mild=_build_mild_bars(),
        rebar_prestressed=_build_prestress_bars(prestress_eps0),
    )

    return PlasticSolver(
        cross_section=cs,
        # Mapping note: these are benchmark-only factors used to map the embedded
        # manual PCROSS rows. They are not recommendations for app-wide defaults.
        concrete=Concrete(f_ck=18.0, gamma_c=benchmark_mapping.gamma_c),
        mild_steel=MildSteel(
            f_yk=225.0,
            e_uk=0.20,
            gamma_s=benchmark_mapping.gamma_s,
            gamma_E=benchmark_mapping.gamma_E,
            gamma_u=benchmark_mapping.gamma_u,
        ),
        prestressed_steel=PrestressedSteel(
            f_p01k=1500.0,
            f_pk=1700.0,
            e_uk=0.035,
            E_p=195000.0,
            gamma_s=benchmark_mapping.gamma_p,
            gamma_E=benchmark_mapping.gamma_E,
            gamma_u=benchmark_mapping.gamma_u,
            initial_strain=0.0,
        ),
    )


@dataclass(frozen=True)
class LoadCase:
    P_target: float
    angles_deg: tuple[float, ...]


LOAD_CASE_3 = LoadCase(P_target=1000.0, angles_deg=tuple(float(v) for v in range(2, 50, 3)))
LOAD_CASE_4 = LoadCase(P_target=2000.0, angles_deg=tuple(float(v) for v in range(5, 76, 5)))

MANUAL_ROWS = {
    (3, 2.0): {"Mx": 544.3, "My": 921.8},
    (3, 5.0): {"Mx": 619.0, "My": 917.4},
    (3, 8.0): {"Mx": 698.8, "My": 905.8},
    (4, 5.0): {"Mx": 437.0, "My": 894.2},
    (4, 10.0): {"Mx": 561.4, "My": 869.8},
    (4, 15.0): {"Mx": 682.9, "My": 837.7},
}



# Detailed six-row diagnostic reference values embedded from the manual example
# used by this repository. These are NOT new benchmark rows; they annotate the
# existing MANUAL_ROWS entries with intermediate quantities for decomposition.
MANUAL_ROW_DIAGNOSTICS = {
    (3, 2.0): {
        "U": 0.2391,
        "R": 1.4066,
        "strain_concrete": 3.500,
        "strain_mild": 5.024,
        "strain_prestressed": 8.553,
        "kappa": 0.006404,
        "compress_force": 3933.8,
        "lever_L": 0.7441,
        "lever_DX": 0.6110,
        "lever_DY": 0.4245,
    },
    (3, 5.0): {
        "U": 0.2229,
        "R": 1.7226,
        "strain_concrete": 3.500,
        "strain_mild": 7.820,
        "strain_prestressed": 10.612,
        "kappa": 0.005805,
        "compress_force": 3775.6,
        "lever_L": 0.8590,
        "lever_DX": 0.7476,
        "lever_DY": 0.4222,
    },
    (3, 8.0): {
        "U": 0.2076,
        "R": 1.9920,
        "strain_concrete": 3.500,
        "strain_mild": 10.324,
        "strain_prestressed": 12.465,
        "kappa": 0.005229,
        "compress_force": 3638.1,
        "lever_L": 0.9478,
        "lever_DX": 0.8627,
        "lever_DY": 0.4323,
    },
    (4, 5.0): {
        "U": 0.0953,
        "R": 0.9802,
        "strain_concrete": 3.500,
        "strain_mild": 2.929,
        "strain_prestressed": 6.998,
        "kappa": 0.007745,
        "compress_force": 4986.2,
        "lever_L": 0.5444,
        "lever_DX": 0.5244,
        "lever_DY": 0.4561,
    },
    (4, 10.0): {
        "U": 0.0657,
        "R": 1.6327,
        "strain_concrete": 3.500,
        "strain_mild": 9.144,
        "strain_prestressed": 11.161,
        "kappa": 0.006482,
        "compress_force": 4506.2,
        "lever_L": 0.7358,
        "lever_DX": 0.6762,
        "lever_DY": 0.4505,
    },
    (4, 15.0): {
        "U": 0.0301,
        "R": 2.6422,
        "strain_concrete": 3.500,
        "strain_mild": 16.551,
        "strain_prestressed": 16.003,
        "kappa": 0.005153,
        "compress_force": 4126.7,
        "lever_L": 0.8462,
        "lever_DX": 0.7810,
        "lever_DY": 0.4440,
    },
}
