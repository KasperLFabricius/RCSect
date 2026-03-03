from __future__ import annotations


def gpa_to_mpa(E_gpa: float) -> float:
    return 1000.0 * float(E_gpa)


def mpa_to_kn_m2(s_mpa: float) -> float:
    return 1000.0 * float(s_mpa)


def kn_m2_to_mpa(s_kn_m2: float) -> float:
    return float(s_kn_m2) / 1000.0


def strain_to_permille(strain: float) -> float:
    return 1000.0 * float(strain)


def permille_to_strain(permille: float) -> float:
    return float(permille) / 1000.0


def fmt_mpa(value: float, precision: int = 2) -> str:
    return f"{float(value):.{precision}f} MPa"


def fmt_gpa(value: float, precision: int = 2) -> str:
    return f"{float(value):.{precision}f} GPa"


def fmt_mm2(value: float, precision: int = 1) -> str:
    return f"{float(value):.{precision}f} mm²"


def fmt_permille(value: float, precision: int = 1) -> str:
    return f"{float(value):.{precision}f} ‰"
