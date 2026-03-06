"""Reusable plastic benchmark comparison utilities for tests and reporting."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from tests.pcross_benchmark_fixture import MANUAL_ROWS

TINY_REF = 1e-12


@dataclass(frozen=True)
class BenchmarkSweepSpec:
    load_case: int
    p_target: float
    angles_deg: tuple[float, ...]


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


def _trend_sign(values: list[float]) -> list[int]:
    out: list[int] = []
    for a, b in zip(values, values[1:]):
        d = float(b) - float(a)
        out.append(1 if d > 0 else (-1 if d < 0 else 0))
    return out


def _safe_sign_agreement(calc: float, ref: float | None) -> bool | float:
    if ref is None or not np.isfinite(ref):
        return np.nan
    return bool(np.sign(calc) == np.sign(ref))


def run_benchmark_sweeps(solver, sweep_specs: list[BenchmarkSweepSpec], reference_rows: dict[tuple[int, float], dict] | None = None) -> pd.DataFrame:
    """Run solver sweeps and return one normalized DataFrame row per angle."""
    refs = MANUAL_ROWS if reference_rows is None else reference_rows
    rows: list[dict] = []
    for spec in sweep_specs:
        solved = solver.solve_angle_sweep(spec.angles_deg, spec.p_target)
        by_angle = {float(row["angle_v_deg"]): row for row in solved}

        for angle in spec.angles_deg:
            a = float(angle)
            row = by_angle[a]
            ref = refs.get((spec.load_case, a), None)
            ref_mx = float(ref["Mx"]) if ref else np.nan
            ref_my = float(ref["My"]) if ref else np.nan
            calc_mx = float(row["Mx"])
            calc_my = float(row["My"])
            calc_abs_mx = abs(calc_mx)
            calc_abs_my = abs(calc_my)
            ref_abs_mx = abs(ref_mx) if ref else np.nan
            ref_abs_my = abs(ref_my) if ref else np.nan

            quadrant_calc = _quadrant(calc_mx, calc_my)
            quadrant_expected = _quadrant(ref_mx, ref_my) if ref else np.nan

            rows.append(
                {
                    "load_case": spec.load_case,
                    "P_target": spec.p_target,
                    "V_deg": a,
                    "Mx_ref": ref_mx,
                    "My_ref": ref_my,
                    "Mx_calc": calc_mx,
                    "My_calc": calc_my,
                    "Mx_calc_abs": calc_abs_mx,
                    "My_calc_abs": calc_abs_my,
                    "Mx_ref_abs": ref_abs_mx,
                    "My_ref_abs": ref_abs_my,
                    "sign_agreement_Mx": _safe_sign_agreement(calc_mx, ref_mx),
                    "sign_agreement_My": _safe_sign_agreement(calc_my, ref_my),
                    "quadrant_calc": quadrant_calc,
                    "quadrant_expected": quadrant_expected,
                    "quadrant_agreement": (quadrant_calc == quadrant_expected) if ref else np.nan,
                    "candidate_count": int(row.get("candidate_count", 1)),
                    "selected_candidate_index": row.get("selected_candidate_index"),
                    "pivot": row.get("pivot"),
                    "selected_branch": row.get("selection_source"),
                    "residual_abs": float(row.get("residual_abs", np.nan)),
                    "strain_concrete_calc": float(row.get("strain_concrete", np.nan)),
                    "strain_mild_calc": float(row.get("strain_mild", np.nan)),
                    "strain_prestressed_calc": float(row.get("strain_prestressed", np.nan)) if row.get("strain_prestressed") is not None else np.nan,
                    "kappa_calc": float(row.get("kappa", np.nan)),
                    "compress_force_calc": float(row.get("compress_force", np.nan)),
                    "L_calc": float(row.get("lever_L", np.nan)),
                    "DX_calc": float(row.get("lever_DX", np.nan)),
                    "DY_calc": float(row.get("lever_DY", np.nan)),
                    "warning_calc": row.get("warning"),
                    "strain_concrete_ref": float(ref.get("strain_concrete", np.nan)) if ref else np.nan,
                    "strain_mild_ref": float(ref.get("strain_mild", np.nan)) if ref else np.nan,
                    "strain_prestressed_ref": float(ref.get("strain_prestressed", np.nan)) if ref and ref.get("strain_prestressed") is not None else np.nan,
                    "kappa_ref": float(ref.get("kappa", np.nan)) if ref else np.nan,
                    "compress_force_ref": float(ref.get("compress_force", np.nan)) if ref else np.nan,
                    "L_ref": float(ref.get("L", np.nan)) if ref else np.nan,
                    "DX_ref": float(ref.get("DX", np.nan)) if ref else np.nan,
                    "DY_ref": float(ref.get("DY", np.nan)) if ref else np.nan,
                    "warning_ref": (ref.get("warning") if ref else None),
                    "note_ref": (ref.get("note") if ref else None),
                }
            )

    df = pd.DataFrame(rows).sort_values(["load_case", "V_deg"]).reset_index(drop=True)

    has_ref = df["Mx_ref"].notna() & df["My_ref"].notna()
    df["abs_err_Mx"] = np.where(has_ref, np.abs(df["Mx_calc"] - df["Mx_ref"]), np.nan)
    df["abs_err_My"] = np.where(has_ref, np.abs(df["My_calc"] - df["My_ref"]), np.nan)
    for key in ["strain_concrete", "strain_mild", "strain_prestressed", "kappa", "compress_force", "L", "DX", "DY"]:
        ref_col = f"{key}_ref"
        calc_col = f"{key}_calc"
        if ref_col in df.columns and calc_col in df.columns:
            df[f"abs_err_{key}"] = np.where(df[ref_col].notna(), np.abs(df[calc_col] - df[ref_col]), np.nan)
            mask = df[ref_col].notna() & (np.abs(df[ref_col]) > 1e-9)
            df[f"rel_err_{key}"] = np.where(mask, df[f"abs_err_{key}"] / np.maximum(np.abs(df[ref_col]), TINY_REF), np.nan)
    df["warning_match"] = np.where(df["warning_ref"].notna(), df["warning_ref"] == df["warning_calc"], np.nan)
    mx_rel_mask = has_ref & (np.abs(df["Mx_ref"]) > 1e-9)
    my_rel_mask = has_ref & (np.abs(df["My_ref"]) > 1e-9)
    df["rel_err_Mx"] = np.where(mx_rel_mask, df["abs_err_Mx"] / np.maximum(np.abs(df["Mx_ref"]), TINY_REF), np.nan)
    df["rel_err_My"] = np.where(my_rel_mask, df["abs_err_My"] / np.maximum(np.abs(df["My_ref"]), TINY_REF), np.nan)

    # Secondary diagnostic-only magnitude errors.
    df["abs_mag_err_Mx"] = np.where(has_ref, np.abs(df["Mx_calc_abs"] - df["Mx_ref_abs"]), np.nan)
    df["abs_mag_err_My"] = np.where(has_ref, np.abs(df["My_calc_abs"] - df["My_ref_abs"]), np.nan)

    for lc in sorted(df["load_case"].unique()):
        mask = df["load_case"] == lc
        mx_trend = _trend_sign(df.loc[mask, "Mx_calc"].tolist())
        my_trend = _trend_sign(df.loc[mask, "My_calc"].tolist())
        mx_abs_trend = _trend_sign(df.loc[mask, "Mx_calc_abs"].tolist())
        my_abs_trend = _trend_sign(df.loc[mask, "My_calc_abs"].tolist())
        df.loc[mask, "trend_sign_Mx"] = [np.nan] + mx_trend
        df.loc[mask, "trend_sign_My"] = [np.nan] + my_trend
        df.loc[mask, "trend_sign_Mx_abs"] = [np.nan] + mx_abs_trend
        df.loc[mask, "trend_sign_My_abs"] = [np.nan] + my_abs_trend

    return df


def summarize_benchmark(df: pd.DataFrame) -> pd.DataFrame:
    """Compact per-load-case summary for human review."""
    summaries: list[dict] = []
    for lc, group in df.groupby("load_case"):
        with_ref = group[group["Mx_ref"].notna()]
        summaries.append(
            {
                "load_case": lc,
                "angles_checked": int(group.shape[0]),
                "angles_with_reference": int(with_ref.shape[0]),
                "max_abs_err_Mx": float(with_ref["abs_err_Mx"].max()) if not with_ref.empty else np.nan,
                "max_abs_err_My": float(with_ref["abs_err_My"].max()) if not with_ref.empty else np.nan,
                "max_rel_err_Mx": float(with_ref["rel_err_Mx"].max()) if not with_ref.empty else np.nan,
                "max_rel_err_My": float(with_ref["rel_err_My"].max()) if not with_ref.empty else np.nan,
                "all_quadrant_ok": bool(with_ref["quadrant_agreement"].all()) if not with_ref.empty else np.nan,
                "all_sign_ok_Mx": bool(with_ref["sign_agreement_Mx"].all()) if not with_ref.empty else np.nan,
                "all_sign_ok_My": bool(with_ref["sign_agreement_My"].all()) if not with_ref.empty else np.nan,
                "max_candidate_count": int(group["candidate_count"].max()),
            }
        )
    return pd.DataFrame(summaries).sort_values("load_case").reset_index(drop=True)
