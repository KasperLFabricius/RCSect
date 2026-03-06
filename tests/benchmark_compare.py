"""Reusable plastic benchmark comparison utilities for tests and reporting."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from tests.pcross_benchmark_fixture import MANUAL_ROWS


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


def run_benchmark_sweeps(solver, sweep_specs: list[BenchmarkSweepSpec]) -> pd.DataFrame:
    """Run solver sweeps and return one normalized DataFrame row per angle."""
    rows: list[dict] = []
    for spec in sweep_specs:
        solved = solver.solve_angle_sweep(spec.angles_deg, spec.p_target)
        by_angle = {float(row["angle_v_deg"]): row for row in solved}

        for angle in spec.angles_deg:
            a = float(angle)
            row = by_angle[a]
            ref = MANUAL_ROWS.get((spec.load_case, a), None)
            ref_mx = float(ref["Mx"]) if ref else np.nan
            ref_my = float(ref["My"]) if ref else np.nan
            calc_abs_mx = abs(float(row["Mx"]))
            calc_abs_my = abs(float(row["My"]))

            rows.append(
                {
                    "load_case": spec.load_case,
                    "P_target": spec.p_target,
                    "V_deg": a,
                    "Mx_ref": ref_mx,
                    "My_ref": ref_my,
                    "Mx_calc": float(row["Mx"]),
                    "My_calc": float(row["My"]),
                    "Mx_calc_abs": calc_abs_mx,
                    "My_calc_abs": calc_abs_my,
                    "sign_agreement_Mx": (np.sign(row["Mx"]) == -1),
                    "sign_agreement_My": (np.sign(row["My"]) == 1),
                    "quadrant_calc": _quadrant(float(row["Mx"]), float(row["My"])),
                    "quadrant_expected": "II",
                    "quadrant_agreement": _quadrant(float(row["Mx"]), float(row["My"])) == "II",
                    "candidate_count": int(row.get("candidate_count", 1)),
                    "selected_candidate_index": row.get("selected_candidate_index"),
                    "pivot": row.get("pivot"),
                    "selected_branch": row.get("selection_source"),
                    "residual_abs": float(row.get("residual_abs", np.nan)),
                }
            )

    df = pd.DataFrame(rows).sort_values(["load_case", "V_deg"]).reset_index(drop=True)

    has_ref = df["Mx_ref"].notna() & df["My_ref"].notna()
    df["abs_err_Mx"] = np.where(has_ref, np.abs(df["Mx_calc_abs"] - df["Mx_ref"]), np.nan)
    df["abs_err_My"] = np.where(has_ref, np.abs(df["My_calc_abs"] - df["My_ref"]), np.nan)
    df["rel_err_Mx"] = np.where(has_ref, df["abs_err_Mx"] / df["Mx_ref"], np.nan)
    df["rel_err_My"] = np.where(has_ref, df["abs_err_My"] / df["My_ref"], np.nan)

    for lc in sorted(df["load_case"].unique()):
        mask = df["load_case"] == lc
        mx_trend = _trend_sign(df.loc[mask, "Mx_calc_abs"].tolist())
        my_trend = _trend_sign(df.loc[mask, "My_calc_abs"].tolist())
        df.loc[mask, "trend_sign_Mx_abs"] = [np.nan] + mx_trend
        df.loc[mask, "trend_sign_My_abs"] = [np.nan] + my_trend

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
                "all_quadrant_ok": bool(group["quadrant_agreement"].all()),
                "all_sign_ok_Mx": bool(group["sign_agreement_Mx"].all()),
                "all_sign_ok_My": bool(group["sign_agreement_My"].all()),
                "max_candidate_count": int(group["candidate_count"].max()),
            }
        )
    return pd.DataFrame(summaries).sort_values("load_case").reset_index(drop=True)
