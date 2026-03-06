"""Row-by-row diagnostic decomposition utilities for plastic benchmark mismatches."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from tests.pcross_benchmark_fixture import (
    LOAD_CASE_3,
    LOAD_CASE_4,
    MANUAL_ROWS,
    MANUAL_ROW_DIAGNOSTICS,
    build_pcross_tbeam_solver,
)

DIAGNOSTIC_ROWS: tuple[tuple[int, float], ...] = (
    (3, 2.0),
    (3, 5.0),
    (3, 8.0),
    (4, 5.0),
    (4, 10.0),
    (4, 15.0),
)


def _case_target(load_case: int) -> float:
    if load_case == 3:
        return LOAD_CASE_3.P_target
    if load_case == 4:
        return LOAD_CASE_4.P_target
    raise ValueError(f"Unsupported load_case={load_case}")


def _safe_rel(diff: float, ref: float | None) -> float:
    if ref is None or not np.isfinite(ref):
        return np.nan
    return abs(diff) / max(abs(ref), 1e-12)


def _add_pair(row: dict, key: str, ref_val: float | None, calc_val: float | None) -> None:
    row[f"{key}_ref"] = ref_val
    row[f"{key}_calc"] = calc_val
    if ref_val is None or calc_val is None or not np.isfinite(ref_val) or not np.isfinite(calc_val):
        row[f"d{key}"] = np.nan
        row[f"rel_{key}"] = np.nan
        return
    d = float(calc_val) - float(ref_val)
    row[f"d{key}"] = d
    row[f"rel_{key}"] = _safe_rel(d, ref_val)


def diagnose_benchmark_row(load_case: int, angle_deg: float) -> dict:
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    p_target = _case_target(load_case)

    solved = solver.solve(float(angle_deg), p_target)
    ref_mm = MANUAL_ROWS[(load_case, float(angle_deg))]
    ref_diag = MANUAL_ROW_DIAGNOSTICS[(load_case, float(angle_deg))]

    out = {
        "load_case": load_case,
        "P_target": p_target,
        "V_deg": float(angle_deg),
        "pivot": solved.get("pivot"),
        "candidate_count": solved.get("candidate_count"),
        "selected_candidate_index": solved.get("selected_candidate_index"),
        "selection_source": solved.get("selection_source"),
        "Mx_local": solved.get("Mx_local"),
        "My_local": solved.get("My_local"),
        "N_internal_signed": solved.get("N_internal_signed"),
        "N_calc": solved.get("N_calc"),
        "R_unavailable_reason": (
            "manual R semantic is ambiguous against current solver outputs; "
            "report omitted from strict numeric comparisons"
        ),
    }

    _add_pair(out, "Mx", ref_mm["Mx"], solved.get("Mx"))
    _add_pair(out, "My", ref_mm["My"], solved.get("My"))
    _add_pair(out, "y_na", ref_diag["U"], solved.get("y_na"))
    _add_pair(out, "strain_concrete", ref_diag["strain_concrete"], solved.get("strain_concrete"))
    _add_pair(out, "strain_mild", ref_diag["strain_mild"], solved.get("strain_mild"))
    _add_pair(out, "strain_prestressed", ref_diag["strain_prestressed"], solved.get("strain_prestressed"))
    _add_pair(out, "kappa", ref_diag["kappa"], solved.get("kappa"))
    _add_pair(out, "compress_force", ref_diag["compress_force"], solved.get("compress_force"))
    _add_pair(out, "lever_L", ref_diag["lever_L"], solved.get("lever_L"))
    _add_pair(out, "lever_DX", ref_diag["lever_DX"], solved.get("lever_DX"))
    _add_pair(out, "lever_DY", ref_diag["lever_DY"], solved.get("lever_DY"))

    mx_ref, my_ref = ref_mm["Mx"], ref_mm["My"]
    mx_calc, my_calc = solved.get("Mx"), solved.get("My")
    out["sign_agreement_Mx"] = bool(np.sign(mx_ref) == np.sign(mx_calc))
    out["sign_agreement_My"] = bool(np.sign(my_ref) == np.sign(my_calc))
    out["quadrant_ref"] = _quadrant(mx_ref, my_ref)
    out["quadrant_calc"] = _quadrant(mx_calc, my_calc)
    out["quadrant_agreement"] = out["quadrant_ref"] == out["quadrant_calc"]

    return out


def _quadrant(mx: float, my: float) -> str:
    if mx == 0.0 or my == 0.0:
        return "axis"
    if mx > 0.0 and my > 0.0:
        return "I"
    if mx < 0.0 and my > 0.0:
        return "II"
    if mx < 0.0 and my < 0.0:
        return "III"
    return "IV"


def diagnose_manual_rows() -> pd.DataFrame:
    rows = [diagnose_benchmark_row(lc, angle) for lc, angle in DIAGNOSTIC_ROWS]
    return pd.DataFrame(rows).sort_values(["load_case", "V_deg"]).reset_index(drop=True)


def classify_dominant_mismatch(df: pd.DataFrame) -> str:
    """Classify dominant mismatch layer using transparent grouped indicators."""
    moment_rel = float(df[["rel_Mx", "rel_My"]].mean().mean())
    equilibrium_rel = float(df[["rel_kappa", "rel_compress_force"]].mean().mean())
    strain_rel = float(df[["rel_strain_concrete", "rel_strain_mild", "rel_strain_prestressed"]].mean().mean())
    lever_rel = float(df[["rel_lever_L", "rel_lever_DX", "rel_lever_DY"]].mean().mean())

    if moment_rel > 1.5 * max(equilibrium_rel, strain_rel) and lever_rel < moment_rel:
        return "largest mismatch appears concentrated in moment transformation / lever-arm projection"
    if equilibrium_rel >= moment_rel or strain_rel >= moment_rel:
        return "largest mismatch appears already present in constitutive/equilibrium response"
    return "mismatch is mixed across equilibrium and transformation layers"


def diagnostics_markdown(df: pd.DataFrame) -> str:
    cols = [
        "load_case",
        "V_deg",
        "Mx_ref",
        "Mx_calc",
        "rel_Mx",
        "My_ref",
        "My_calc",
        "rel_My",
        "kappa_ref",
        "kappa_calc",
        "rel_kappa",
        "compress_force_ref",
        "compress_force_calc",
        "rel_compress_force",
        "lever_DX_ref",
        "lever_DX_calc",
        "rel_lever_DX",
        "sign_agreement_Mx",
        "sign_agreement_My",
        "quadrant_agreement",
        "candidate_count",
        "pivot",
        "selection_source",
    ]
    sub = df[cols]
    conclusion = classify_dominant_mismatch(df)
    md = "# Plastic Row Diagnostics\n\n"
    md += "Six embedded manual rows with signed and intermediate-quantity decomposition.\n\n"
    headers = list(sub.columns)
    md += "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for _, r in sub.iterrows():
        vals = ["" if (isinstance(r[h], float) and not math.isfinite(r[h])) else str(r[h]) for h in headers]
        md += "| " + " | ".join(vals) + " |\n"
    md += "\nConclusion: " + conclusion + "\n"
    return md
