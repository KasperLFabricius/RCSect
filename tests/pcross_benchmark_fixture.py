"""Embedded PCROSS benchmark fixtures used by solver regression tests.

Contains the existing T-beam benchmark plus six additional fixtures:
- Snit A/B/C/D prestressed strip sections
- Section0 / SectionIV voided annular sections
"""

from __future__ import annotations

from dataclasses import dataclass

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel, PrestressedSteel
from core.solver_plastic import PlasticSolver


# ----------------------------- Existing T-beam fixture -----------------------------
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
    "case_a_baseline": BenchmarkMaterialMapping(
        name="case_a_baseline", gamma_c=1.50, gamma_s=1.15, gamma_p=1.15, gamma_E=1.0, gamma_u=1.0
    ),
    "case_b_manual_strength": BenchmarkMaterialMapping(
        name="case_b_manual_strength", gamma_c=1.90, gamma_s=1.50, gamma_p=1.50, gamma_E=1.0, gamma_u=1.0
    ),
    "case_c_manual_strength_plus_fe": BenchmarkMaterialMapping(
        name="case_c_manual_strength_plus_fe", gamma_c=1.90, gamma_s=1.50, gamma_p=1.50, gamma_E=1.50, gamma_u=1.0
    ),
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

MANUAL_ROW_DIAGNOSTICS = {
    (3, 2.0): {"U": 0.2391, "R": 1.4066, "strain_concrete": 3.500, "strain_mild": 5.024, "strain_prestressed": 8.553, "kappa": 0.006404, "compress_force": 3933.8, "lever_L": 0.7441, "lever_DX": 0.6110, "lever_DY": 0.4245},
    (3, 5.0): {"U": 0.2229, "R": 1.7226, "strain_concrete": 3.500, "strain_mild": 7.820, "strain_prestressed": 10.612, "kappa": 0.005805, "compress_force": 3775.6, "lever_L": 0.8590, "lever_DX": 0.7476, "lever_DY": 0.4222},
    (3, 8.0): {"U": 0.2076, "R": 1.9920, "strain_concrete": 3.500, "strain_mild": 10.324, "strain_prestressed": 12.465, "kappa": 0.005229, "compress_force": 3638.1, "lever_L": 0.9478, "lever_DX": 0.8627, "lever_DY": 0.4323},
    (4, 5.0): {"U": 0.0953, "R": 0.9802, "strain_concrete": 3.500, "strain_mild": 2.929, "strain_prestressed": 6.998, "kappa": 0.007745, "compress_force": 4986.2, "lever_L": 0.5444, "lever_DX": 0.5244, "lever_DY": 0.4561},
    (4, 10.0): {"U": 0.0657, "R": 1.6327, "strain_concrete": 3.500, "strain_mild": 9.144, "strain_prestressed": 11.161, "kappa": 0.006482, "compress_force": 4506.2, "lever_L": 0.7358, "lever_DX": 0.6762, "lever_DY": 0.4505},
    (4, 15.0): {"U": 0.0301, "R": 2.6422, "strain_concrete": 3.500, "strain_mild": 16.551, "strain_prestressed": 16.003, "kappa": 0.005153, "compress_force": 4126.7, "lever_L": 0.8462, "lever_DX": 0.7810, "lever_DY": 0.4440},
}


# ----------------------------- New fixtures -----------------------------

@dataclass(frozen=True)
class EmbeddedBenchmarkCase:
    key: str
    load_case: int
    load: LoadCase
    solver_builder: callable
    reference_rows: dict[tuple[int, float], dict]


def _cw_strip_outline():
    pts = [(-0.660, -0.550), (-0.660, 0.550), (0.660, 0.550), (0.660, -0.550)]
    return [{"id": i + 1, "x": x, "y": y} for i, (x, y) in enumerate(pts)]


def _build_mild_pair():
    pts = [(0.000, 0.492, 1447.65), (0.000, -0.496, 1447.65)]
    return [{"id": f"S{i+1}", "x": x, "y": y, "area": a} for i, (x, y, a) in enumerate(pts)]




@dataclass(frozen=True)
class Type6PrestressMapping:
    name: str
    gamma_E: float
    gamma_u: float


TYPE6_PRESTRESS_MAPPINGS: dict[str, Type6PrestressMapping] = {
    "baseline": Type6PrestressMapping(name="baseline", gamma_E=0.97, gamma_u=1.12),
    "refined": Type6PrestressMapping(name="refined", gamma_E=1.02, gamma_u=1.05),
}

DEFAULT_TYPE6_PRESTRESS_MAPPING = "baseline"


def resolve_type6_mapping(mapping: str | Type6PrestressMapping | None) -> Type6PrestressMapping:
    if mapping is None:
        return TYPE6_PRESTRESS_MAPPINGS[DEFAULT_TYPE6_PRESTRESS_MAPPING]
    if isinstance(mapping, Type6PrestressMapping):
        return mapping
    if mapping not in TYPE6_PRESTRESS_MAPPINGS:
        raise ValueError(f"Unknown type-6 mapping '{mapping}'")
    return TYPE6_PRESTRESS_MAPPINGS[mapping]

def _build_pre_bars(points):
    return [{"id": f"P{i+1}", "x": x, "y": y, "area": a, "eps0": 0.0059} for i, (x, y, a) in enumerate(points)]


def _build_strip_solver(pre_points, p_target, type6_mapping: str | Type6PrestressMapping | None = None):
    mapping = resolve_type6_mapping(type6_mapping)
    cs = CrossSection(
        concrete_outline=_cw_strip_outline(),
        concrete_voids=[],
        rebar_mild=_build_mild_pair(),
        rebar_prestressed=_build_pre_bars(pre_points),
    )
    solver = PlasticSolver(
        cross_section=cs,
        concrete=Concrete(f_ck=43.8, gamma_c=1.53),
        mild_steel=MildSteel(
            f_yk=550.0,
            f_yk_t=550.0,
            f_yk_c=550.0,
            e_uk=0.025,
            f_uk=550.0,
            include_hardening=True,
            gamma_s=1.12,
            gamma_u=mapping.gamma_u,
            gamma_E=mapping.gamma_E,
        ),
        prestressed_steel=PrestressedSteel(
            f_p01k=1550.0,
            f_pk=1770.0,
            e_uk=0.035,
            E_p=200000.0,
            gamma_s=1.12,
            gamma_u=mapping.gamma_u,
            gamma_E=mapping.gamma_E,
            initial_strain=0.0,
        ),
    )
    return solver


def build_strip_snit_a(type6_mapping: str | Type6PrestressMapping | None = None) -> PlasticSolver:
    return _build_strip_solver([(0.000, 0.430, 8928.00)], p_target=6016.0, type6_mapping=type6_mapping)


def build_strip_snit_b(type6_mapping: str | Type6PrestressMapping | None = None) -> PlasticSolver:
    return _build_strip_solver([(0.000, -0.411, 8928.00)], p_target=7207.0, type6_mapping=type6_mapping)


def build_strip_snit_c(type6_mapping: str | Type6PrestressMapping | None = None) -> PlasticSolver:
    return _build_strip_solver([(0.000, -0.411, 6696.00), (0.000, 0.078, 2232.00)], p_target=7229.5, type6_mapping=type6_mapping)


def build_strip_snit_d(type6_mapping: str | Type6PrestressMapping | None = None) -> PlasticSolver:
    return _build_strip_solver([(0.000, 0.108, 6696.00), (0.000, 0.377, 2232.00)], p_target=7229.5, type6_mapping=type6_mapping)


def _ring(points):
    return [{"id": i + 1, "x": x, "y": y} for i, (x, y) in enumerate(points[:-1])]


SECTION0_OUTER = [(0.375,0.000),(0.369,-0.065),(0.352,-0.128),(0.325,-0.188),(0.287,-0.241),(0.241,-0.287),(0.188,-0.325),(0.128,-0.352),(0.065,-0.369),(0.000,-0.375),(-0.065,-0.369),(-0.128,-0.352),(-0.188,-0.325),(-0.241,-0.287),(-0.287,-0.241),(-0.325,-0.188),(-0.352,-0.128),(-0.369,-0.065),(-0.375,0.000),(-0.369,0.065),(-0.352,0.128),(-0.325,0.188),(-0.287,0.241),(-0.241,0.287),(-0.188,0.325),(-0.128,0.352),(-0.065,0.369),(0.000,0.375),(0.065,0.369),(0.128,0.352),(0.188,0.325),(0.241,0.287),(0.287,0.241),(0.325,0.188),(0.352,0.128),(0.369,0.065),(0.375,0.000)]
SECTION0_INNER = [(0.265,0.000),(0.261,0.046),(0.249,0.091),(0.229,0.133),(0.203,0.170),(0.170,0.203),(0.133,0.229),(0.091,0.249),(0.046,0.261),(0.000,0.265),(-0.046,0.261),(-0.091,0.249),(-0.133,0.229),(-0.170,0.203),(-0.203,0.170),(-0.229,0.133),(-0.249,0.091),(-0.261,0.046),(-0.265,0.000),(-0.261,-0.046),(-0.249,-0.091),(-0.229,-0.133),(-0.203,-0.170),(-0.170,-0.203),(-0.133,-0.229),(-0.091,-0.249),(-0.046,-0.261),(0.000,-0.265),(0.046,-0.261),(0.091,-0.249),(0.133,-0.229),(0.170,-0.203),(0.203,-0.170),(0.229,-0.133),(0.249,-0.091),(0.261,-0.046),(0.265,0.000)]
SECTION0_BARS = [(0.340,0.000),(0.319,0.116),(0.260,0.219),(0.170,0.294),(0.059,0.335),(-0.059,0.335),(-0.170,0.294),(-0.260,0.219),(-0.319,0.116),(-0.340,0.000),(-0.319,-0.116),(-0.260,-0.219),(-0.170,-0.294),(-0.059,-0.335),(0.059,-0.335),(0.170,-0.294),(0.260,-0.219),(0.319,-0.116)]

SECTIONIV_OUTER = [(0.285,0.000),(0.281,-0.049),(0.268,-0.097),(0.247,-0.142),(0.218,-0.183),(0.183,-0.218),(0.142,-0.247),(0.097,-0.268),(0.049,-0.281),(0.000,-0.285),(-0.049,-0.281),(-0.097,-0.268),(-0.142,-0.247),(-0.183,-0.218),(-0.218,-0.183),(-0.247,-0.142),(-0.268,-0.097),(-0.281,-0.049),(-0.285,0.000),(-0.281,0.049),(-0.268,0.097),(-0.247,0.142),(-0.218,0.183),(-0.183,0.218),(-0.142,0.247),(-0.097,0.268),(-0.049,0.281),(0.000,0.285),(0.049,0.281),(0.097,0.268),(0.142,0.247),(0.183,0.218),(0.218,0.183),(0.247,0.142),(0.268,0.097),(0.281,0.049),(0.285,0.000)]
SECTIONIV_INNER = [(0.189,0.000),(0.186,0.033),(0.178,0.065),(0.164,0.095),(0.145,0.121),(0.121,0.145),(0.095,0.164),(0.065,0.178),(0.033,0.186),(0.000,0.189),(-0.033,0.186),(-0.065,0.178),(-0.095,0.164),(-0.121,0.145),(-0.145,0.121),(-0.164,0.095),(-0.178,0.065),(-0.186,0.033),(-0.189,0.000),(-0.186,-0.033),(-0.178,-0.065),(-0.164,-0.095),(-0.145,-0.121),(-0.121,-0.145),(-0.095,-0.164),(-0.065,-0.178),(-0.033,-0.186),(0.000,-0.189),(0.033,-0.186),(0.065,-0.178),(0.095,-0.164),(0.121,-0.145),(0.145,-0.121),(0.164,-0.095),(0.178,-0.065),(0.186,-0.033),(0.189,0.000)]
SECTIONIV_BARS = [(0.252,0.000),(0.237,0.086),(0.193,0.162),(0.126,0.218),(0.044,0.248),(-0.044,0.248),(-0.126,0.218),(-0.193,0.162),(-0.237,0.086),(-0.252,0.000),(-0.237,-0.086),(-0.193,-0.162),(-0.126,-0.218),(-0.044,-0.248),(0.044,-0.248),(0.126,-0.218),(0.193,-0.162),(0.237,-0.086)]


def _build_annular_solver(outer, inner, bars, bar_area):
    cs = CrossSection(
        concrete_outline=_ring(outer),
        concrete_voids=[_ring(inner)],
        rebar_mild=[{"id": f"S{i+1}", "x": x, "y": y, "area": bar_area} for i, (x, y) in enumerate(bars)],
        rebar_prestressed=[],
    )
    return PlasticSolver(
        cross_section=cs,
        concrete=Concrete(f_ck=40.0, gamma_c=1.50),
        mild_steel=MildSteel(
            f_yk=400.0,
            f_yk_t=400.0,
            f_yk_c=400.0,
            e_uk=0.10,
            f_uk=400.0,
            include_hardening=True,
            gamma_s=1.15,
            gamma_u=1.15,
            gamma_E=1.0,
        ),
        prestressed_steel=None,
    )


def build_annular_section0() -> PlasticSolver:
    return _build_annular_solver(SECTION0_OUTER, SECTION0_INNER, SECTION0_BARS, 907.92)


def build_annular_sectioniv() -> PlasticSolver:
    return _build_annular_solver(SECTIONIV_OUTER, SECTIONIV_INNER, SECTIONIV_BARS, 706.86)


# New load cases
LOAD_CASE_SNIT_A = LoadCase(P_target=6016.0, angles_deg=(0.0, 90.0, 180.0, 270.0, 360.0))
LOAD_CASE_SNIT_B = LoadCase(P_target=7207.0, angles_deg=(0.0, 90.0, 180.0, 270.0, 360.0))
LOAD_CASE_SNIT_C = LoadCase(P_target=7229.5, angles_deg=(0.0, 90.0, 180.0, 270.0, 360.0))
LOAD_CASE_SNIT_D = LoadCase(P_target=7229.5, angles_deg=(0.0, 90.0, 180.0, 270.0, 360.0))
LOAD_CASE_SECTION0 = LoadCase(P_target=147.70, angles_deg=tuple(float(v) for v in range(0, 361, 45)))
LOAD_CASE_SECTIONIV = LoadCase(P_target=65.67, angles_deg=tuple(float(v) for v in range(0, 361, 45)))


def _ref(load_case, angle, **vals):
    return (load_case, float(angle)), vals


NEW_BENCHMARK_ROWS = dict([
    _ref(101, 0, U=-35.5, R=1.32, Mx=-4595.6, My=6448.4, strain_concrete=0.35, strain_mild=0.00, strain_prestressed=-0.58, kappa=0.5266e-02, compress_force=6016.0, note="P=0 IN TENSION ZONE"),
    _ref(101, 90, U=90.0, R=0.45, Mx=2714.6, My=0.0, strain_concrete=0.35, strain_mild=-0.55, strain_prestressed=-0.34, kappa=0.8621e-02, compress_force=6728.8, L=0.847, DX=0.000, DY=0.847),
    _ref(101, 180, U=-144.5, R=1.32, Mx=-4595.6, My=-6448.4, strain_concrete=0.35, strain_mild=0.00, strain_prestressed=-0.58, kappa=0.5266e-02, compress_force=6016.0, note="P=0 IN TENSION ZONE"),
    _ref(102, 0, U=33.2, R=1.08, Mx=4272.2, My=6528.4, strain_concrete=0.35, strain_mild=0.02, strain_prestressed=-0.57, kappa=0.5024e-02, compress_force=7205.8, note="P=0 IN TENSION ZONE"),
    _ref(102, 90, U=90.0, R=1.57, Mx=11308.3, My=0.0, strain_concrete=0.35, strain_mild=-0.21, strain_prestressed=-0.75, kappa=0.5391e-02, compress_force=20276.0, L=0.705, DX=0.000, DY=0.705),
    _ref(102, 180, U=146.8, R=1.08, Mx=4272.2, My=-6528.4, strain_concrete=0.35, strain_mild=0.02, strain_prestressed=-0.57, kappa=0.5024e-02, compress_force=7205.8, note="P=0 IN TENSION ZONE"),
    _ref(103, 0, U=24.7, R=0.99, Mx=2999.7, My=6529.8, strain_concrete=0.35, strain_mild=0.02, strain_prestressed=-0.57, kappa=0.5020e-02, compress_force=7229.5, note="P=0 IN TENSION ZONE"),
    _ref(103, 90, U=90.0, R=1.36, Mx=9869.1, My=0.0, strain_concrete=0.35, strain_mild=-0.24, strain_prestressed=-0.77, kappa=0.5596e-02, compress_force=17268.4, L=0.746, DX=0.000, DY=0.746),
    _ref(103, 180, U=155.3, R=0.99, Mx=2999.7, My=-6529.8, strain_concrete=0.35, strain_mild=0.02, strain_prestressed=-0.57, kappa=0.5020e-02, compress_force=7229.5, note="P=0 IN TENSION ZONE"),
    _ref(103, 270, U=270.0, R=0.58, Mx=-4223.3, My=0.0, strain_concrete=0.35, strain_mild=-0.39, strain_prestressed=-0.68, kappa=0.7069e-02, compress_force=11039.8, L=0.484, DX=0.000, DY=-0.484),
    _ref(103, 360, U=384.7, R=0.99, Mx=2999.7, My=6529.8, strain_concrete=0.35, strain_mild=0.02, strain_prestressed=-0.57, kappa=0.5020e-02, compress_force=7229.5, note="P=0 IN TENSION ZONE"),
    _ref(104, 0, U=-15.6, R=0.94, Mx=-1822.9, My=6529.8, strain_concrete=0.35, strain_mild=0.02, strain_prestressed=-0.57, kappa=0.5020e-02, compress_force=7229.5, note="P=0 IN TENSION ZONE"),
    _ref(104, 90, U=90.0, R=0.64, Mx=4627.3, My=0.0, strain_concrete=0.35, strain_mild=-0.34, strain_prestressed=-0.53, kappa=0.6568e-02, compress_force=7942.2, L=1.034, DX=0.000, DY=1.034),
    _ref(104, 180, U=-164.4, R=0.94, Mx=-1822.9, My=-6529.8, strain_concrete=0.35, strain_mild=0.02, strain_prestressed=-0.57, kappa=0.5020e-02, compress_force=7229.5, note="P=0 IN TENSION ZONE"),
    _ref(201, 0, U=0.0, R=10.62, Mx=0.0, My=1568.3, strain_concrete=0.35, strain_mild=-0.73, kappa=0.1515e-01, compress_force=3456.7, L=0.461, DX=-0.461, DY=0.000, warning="W1"),
    _ref(201, 45, U=45.4, R=10.62, Mx=1115.7, My=1101.6, strain_concrete=0.35, strain_mild=-0.72, kappa=0.1506e-01, compress_force=3440.8, L=0.463, DX=-0.330, DY=0.326, warning="W1"),
    _ref(201, 90, U=90.0, R=10.60, Mx=1566.2, My=0.0, strain_concrete=0.35, strain_mild=-0.71, kappa=0.1494e-01, compress_force=3438.5, L=0.463, DX=0.000, DY=0.463, warning="W1"),
    _ref(201, 135, U=134.6, R=10.62, Mx=1115.7, My=-1101.6, strain_concrete=0.35, strain_mild=-0.72, kappa=0.1506e-01, compress_force=3440.8, L=0.463, DX=0.330, DY=0.326, warning="W1"),
    _ref(201, 180, U=180.0, R=10.62, Mx=0.0, My=-1568.3, strain_concrete=0.35, strain_mild=-0.73, kappa=0.1515e-01, compress_force=3456.7, L=0.461, DX=0.461, DY=0.000, warning="W1"),
    _ref(201, 225, U=225.4, R=10.62, Mx=-1115.7, My=-1101.6, strain_concrete=0.35, strain_mild=-0.72, kappa=0.1506e-01, compress_force=3440.8, L=0.463, DX=0.330, DY=-0.326, warning="W1"),
    _ref(201, 270, U=270.0, R=10.60, Mx=-1566.2, My=0.0, strain_concrete=0.35, strain_mild=-0.71, kappa=0.1494e-01, compress_force=3438.5, L=0.463, DX=0.000, DY=-0.463, warning="W1"),
    _ref(201, 315, U=314.6, R=10.62, Mx=-1115.7, My=1101.6, strain_concrete=0.35, strain_mild=-0.72, kappa=0.1506e-01, compress_force=3440.8, L=0.463, DX=-0.330, DY=-0.326, warning="W1"),
    _ref(201, 360, U=360.0, R=10.62, Mx=0.0, My=1568.3, strain_concrete=0.35, strain_mild=-0.73, kappa=0.1515e-01, compress_force=3456.7, L=0.461, DX=-0.461, DY=0.000, warning="W1"),
    _ref(202, 0, U=0.0, R=13.31, Mx=0.0, My=874.3, strain_concrete=0.35, strain_mild=-0.64, kappa=0.1851e-01, compress_force=2551.3, L=0.346, DX=-0.346, DY=0.000, warning="W2"),
    _ref(202, 45, U=44.9, R=13.31, Mx=617.0, My=619.2, strain_concrete=0.35, strain_mild=-0.64, kappa=0.1844e-01, compress_force=2541.7, L=0.348, DX=-0.245, DY=0.246, warning="W2"),
    _ref(202, 90, U=90.0, R=13.33, Mx=875.7, My=0.0, strain_concrete=0.35, strain_mild=-0.62, kappa=0.1810e-01, compress_force=2529.5, L=0.350, DX=0.000, DY=0.350, warning="W2"),
    _ref(202, 135, U=135.1, R=13.31, Mx=617.0, My=-619.2, strain_concrete=0.35, strain_mild=-0.64, kappa=0.1844e-01, compress_force=2541.7, L=0.348, DX=0.245, DY=0.246, warning="W2"),
    _ref(202, 180, U=180.0, R=13.31, Mx=0.0, My=-874.3, strain_concrete=0.35, strain_mild=-0.64, kappa=0.1851e-01, compress_force=2551.3, L=0.346, DX=0.346, DY=0.000, warning="W2"),
    _ref(202, 225, U=-135.1, R=13.31, Mx=-617.0, My=-619.2, strain_concrete=0.35, strain_mild=-0.64, kappa=0.1844e-01, compress_force=2541.7, L=0.348, DX=0.245, DY=-0.246, warning="W2"),
    _ref(202, 270, U=270.0, R=13.33, Mx=-875.7, My=0.0, strain_concrete=0.35, strain_mild=-0.62, kappa=0.1810e-01, compress_force=2529.5, L=0.350, DX=0.000, DY=-0.350, warning="W2"),
    _ref(202, 315, U=315.1, R=13.31, Mx=-617.0, My=619.2, strain_concrete=0.35, strain_mild=-0.64, kappa=0.1844e-01, compress_force=2541.7, L=0.348, DX=-0.245, DY=-0.246, warning="W2"),
    _ref(202, 360, U=360.0, R=13.31, Mx=0.0, My=874.3, strain_concrete=0.35, strain_mild=-0.64, kappa=0.1851e-01, compress_force=2551.3, L=0.346, DX=-0.346, DY=0.000, warning="W2"),
])


EMBEDDED_BENCHMARK_CASES: dict[str, EmbeddedBenchmarkCase] = {
    "tbeam_lc3": EmbeddedBenchmarkCase("tbeam_lc3", 3, LOAD_CASE_3, lambda: build_pcross_tbeam_solver(prestress_eps0=0.004), MANUAL_ROWS),
    "tbeam_lc4": EmbeddedBenchmarkCase("tbeam_lc4", 4, LOAD_CASE_4, lambda: build_pcross_tbeam_solver(prestress_eps0=0.004), MANUAL_ROWS),
    "snit_a": EmbeddedBenchmarkCase("snit_a", 101, LOAD_CASE_SNIT_A, build_strip_snit_a, NEW_BENCHMARK_ROWS),
    "snit_b": EmbeddedBenchmarkCase("snit_b", 102, LOAD_CASE_SNIT_B, build_strip_snit_b, NEW_BENCHMARK_ROWS),
    "snit_c": EmbeddedBenchmarkCase("snit_c", 103, LOAD_CASE_SNIT_C, build_strip_snit_c, NEW_BENCHMARK_ROWS),
    "snit_d": EmbeddedBenchmarkCase("snit_d", 104, LOAD_CASE_SNIT_D, build_strip_snit_d, NEW_BENCHMARK_ROWS),
    "section0": EmbeddedBenchmarkCase("section0", 201, LOAD_CASE_SECTION0, build_annular_section0, NEW_BENCHMARK_ROWS),
    "sectioniv": EmbeddedBenchmarkCase("sectioniv", 202, LOAD_CASE_SECTIONIV, build_annular_sectioniv, NEW_BENCHMARK_ROWS),
}
