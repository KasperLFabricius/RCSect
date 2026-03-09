"""Reusable plastic benchmark comparison utilities for tests and reporting."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from tests.pcross_benchmark_fixture import MANUAL_ROWS

TINY_REF = 1e-12
AXIS_TOL = 1e-6


@dataclass(frozen=True)
class BenchmarkSweepSpec:
    load_case: int
    p_target: float
    angles_deg: tuple[float, ...]


def _quadrant(mx: float, my: float, tol: float = AXIS_TOL) -> str:
    if abs(mx) <= tol or abs(my) <= tol:
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


def _safe_sign_agreement(calc: float, ref: float | None, axis_tol: float = AXIS_TOL) -> bool | float:
    if ref is None or not np.isfinite(ref):
        return np.nan
    if abs(ref) <= axis_tol:
        return np.nan
    return bool(np.sign(calc) == np.sign(ref))


def estimate_warning_level(
    compression_rebar_force: float,
    full_design_concrete_force: float | None = None,
    total_compression_force: float | None = None,
) -> str | None:
    """Diagnostic warning estimate aligned with benchmark W1/W2 intent.

    Primary estimate uses currently solved internal forces:
    concrete_design_force_est ~= total_compression - compression_rebar_force.
    Fallback uses full_design_concrete_force if total compression is unavailable.
    """
    if not np.isfinite(compression_rebar_force):
        return None

    concrete_force_est = np.nan
    if total_compression_force is not None and np.isfinite(total_compression_force):
        concrete_force_est = float(total_compression_force) - float(compression_rebar_force)

    if np.isfinite(concrete_force_est) and concrete_force_est > 0.0:
        if compression_rebar_force > concrete_force_est:
            return "W2"
        if compression_rebar_force > 0.5 * concrete_force_est:
            return "W1"
        return None

    if full_design_concrete_force is None or not np.isfinite(full_design_concrete_force):
        return None
    if compression_rebar_force > full_design_concrete_force:
        return "W2"
    if compression_rebar_force > 0.5 * full_design_concrete_force:
        return "W1"
    return None


def _ref_to_solver_units(key: str, value: float) -> float:
    if key in {"strain_concrete", "strain_mild", "strain_prestressed"} and abs(value) <= 1.0:
        return value * 10.0
    return value




def _row_force_debug(row: dict, key: str, default=np.nan):
    debug = row.get("debug_force_components")
    if isinstance(debug, dict):
        return debug.get(key, default)
    return default


def _semantic_outputs(row: dict, profile: str = "reported") -> dict[str, float]:
    """Return benchmark comparison outputs under an explicit semantic profile."""
    reported = {
        "strain_mild": row.get("strain_mild", np.nan),
        "strain_prestressed": row.get("strain_prestressed", np.nan),
        "compress_force": row.get("compress_force", np.nan),
        "L": row.get("lever_L", np.nan),
        "DX": row.get("lever_DX", np.nan),
        "DY": row.get("lever_DY", np.nan),
    }
    if profile == "reported":
        return reported

    c_tens = _row_force_debug(row, "centroid_tension", {}) or {}
    c_comp = _row_force_debug(row, "centroid_compression", {}) or {}
    c_conc = _row_force_debug(row, "centroid_concrete_compression", {}) or {}

    dx_tot = np.nan
    dy_tot = np.nan
    if c_tens.get("x") is not None and c_tens.get("y") is not None and c_comp.get("x") is not None and c_comp.get("y") is not None:
        dx_tot = float(c_comp["x"] - c_tens["x"])
        dy_tot = float(c_comp["y"] - c_tens["y"])

    dx_conc = np.nan
    dy_conc = np.nan
    if c_tens.get("x") is not None and c_tens.get("y") is not None and c_conc.get("x") is not None and c_conc.get("y") is not None:
        dx_conc = float(c_conc["x"] - c_tens["x"])
        dy_conc = float(c_conc["y"] - c_tens["y"])


    if profile == "legacy_force_tension_centroid":
        sc = row.get("debug_strain_candidates", {}) or {}
        c = row.get("debug_resultant_centroids", {}) or {}
        dx = dy = l = np.nan
        if c.get("compress_zone_centroid_x") is not None and c.get("tension_zone_centroid_x") is not None and c.get("compress_zone_centroid_y") is not None and c.get("tension_zone_centroid_y") is not None:
            dx = float(c["tension_zone_centroid_x"] - c["compress_zone_centroid_x"])
            dy = float(c["tension_zone_centroid_y"] - c["compress_zone_centroid_y"])
            l = float(np.hypot(dx, dy))
        return {
            "strain_mild": sc.get("strain_mild_governing_force_bar_reported_legacy_permille", reported["strain_mild"]),
            "strain_prestressed": sc.get("strain_prestressed_governing_force_bar_reported_legacy_permille", reported["strain_prestressed"]),
            "compress_force": reported["compress_force"],
            "L": l if np.isfinite(l) else reported["L"],
            "DX": dx if np.isfinite(dx) else reported["DX"],
            "DY": dy if np.isfinite(dy) else reported["DY"],
        }

    if profile == "semantic_aligned":
        # Conservative semantic alignment profile based on study winners that
        # were consistent across fixture families. For ambiguous outputs
        # (notably prestress strain and DY), keep reported semantics unchanged.
        return {
            "strain_mild": reported["strain_mild"],
            "strain_prestressed": reported["strain_prestressed"],
            "compress_force": _row_force_debug(row, "total_compression", reported["compress_force"]),
            "L": float(np.sqrt(dx_tot**2 + dy_tot**2)) if np.isfinite(dx_tot) and np.isfinite(dy_tot) else reported["L"],
            "DX": float(dx_tot) if np.isfinite(dx_tot) else reported["DX"],
            "DY": float(dy_tot) if np.isfinite(dy_tot) else reported["DY"],
        }

    raise ValueError(f"Unknown semantic profile: {profile}")

def run_benchmark_sweeps(
    solver,
    sweep_specs: list[BenchmarkSweepSpec],
    reference_rows: dict[tuple[int, float], dict] | None = None,
    semantic_profile: str = "reported",
) -> pd.DataFrame:
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
            quadrant_agreement = np.nan
            if ref and abs(ref_mx) > AXIS_TOL and abs(ref_my) > AXIS_TOL:
                quadrant_agreement = quadrant_calc == quadrant_expected

            warning_calc_est = estimate_warning_level(
                compression_rebar_force=float(row.get("compression_rebar_force", np.nan)),
                full_design_concrete_force=float(row.get("full_design_concrete_force", np.nan)),
                total_compression_force=float(row.get("compress_force", np.nan)),
            )

            sem = _semantic_outputs(row, profile=semantic_profile)

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
                    "quadrant_agreement": quadrant_agreement,
                    "candidate_count": int(row.get("candidate_count", 1)),
                    "selected_candidate_index": row.get("selected_candidate_index"),
                    "pivot": row.get("pivot"),
                    "selected_branch": row.get("selection_source"),
                    "semantic_profile": semantic_profile,
                    "residual_abs": float(row.get("residual_abs", np.nan)),
                    "strain_concrete_calc": float(row.get("strain_concrete", np.nan)),
                    "strain_mild_calc": float(sem.get("strain_mild", np.nan)) if sem.get("strain_mild") is not None else np.nan,
                    "strain_prestressed_calc": float(sem.get("strain_prestressed", np.nan)) if sem.get("strain_prestressed") is not None else np.nan,
                    "kappa_calc": float(row.get("kappa", np.nan)),
                    "compress_force_calc": float(sem.get("compress_force", np.nan)) if sem.get("compress_force") is not None else np.nan,
                    "compression_rebar_force_calc": float(row.get("compression_rebar_force", np.nan)),
                    "full_design_concrete_force_calc": float(row.get("full_design_concrete_force", np.nan)),
                    "L_calc": float(sem.get("L", np.nan)) if sem.get("L") is not None else np.nan,
                    "DX_calc": float(sem.get("DX", np.nan)) if sem.get("DX") is not None else np.nan,
                    "DY_calc": float(sem.get("DY", np.nan)) if sem.get("DY") is not None else np.nan,
                    "warning_calc": row.get("warning"),
                    "warning_calc_est": warning_calc_est,
                    "y_na_calc": float(row.get("y_na", np.nan)),
                    "strain_concrete_ref": float(ref.get("strain_concrete", np.nan)) if ref else np.nan,
                    "strain_mild_ref": float(ref.get("strain_mild", np.nan)) if ref else np.nan,
                    "strain_prestressed_ref": float(ref.get("strain_prestressed", np.nan)) if ref and ref.get("strain_prestressed") is not None else np.nan,
                    "kappa_ref": float(ref.get("kappa", np.nan)) if ref else np.nan,
                    "compress_force_ref": float(ref.get("compress_force", np.nan)) if ref else np.nan,
                    "L_ref": float(ref.get("L", np.nan)) if ref else np.nan,
                    "DX_ref": float(ref.get("DX", np.nan)) if ref else np.nan,
                    "DY_ref": float(ref.get("DY", np.nan)) if ref else np.nan,
                    "U_ref": float(ref.get("U", np.nan)) if ref else np.nan,
                    "y_na_ref": float(ref.get("U", np.nan)) if ref else np.nan,
                    "R_ref": float(ref.get("R", np.nan)) if ref else np.nan,
                    "warning_ref": (ref.get("warning") if ref else None),
                    "note_ref": (ref.get("note") if ref else None),
                }
            )

    df = pd.DataFrame(rows).sort_values(["load_case", "V_deg"]).reset_index(drop=True)

    has_ref = df["Mx_ref"].notna() & df["My_ref"].notna()
    df["abs_err_Mx"] = np.where(has_ref, np.abs(df["Mx_calc"] - df["Mx_ref"]), np.nan)
    df["abs_err_My"] = np.where(has_ref, np.abs(df["My_calc"] - df["My_ref"]), np.nan)
    for key in ["strain_concrete", "strain_mild", "strain_prestressed", "kappa", "compress_force", "L", "DX", "DY", "y_na"]:
        ref_col = f"{key}_ref"
        calc_col = f"{key}_calc"
        if ref_col in df.columns and calc_col in df.columns:
            scaled_ref = df[ref_col].map(lambda v: _ref_to_solver_units(key, float(v)) if np.isfinite(v) else np.nan)
            df[f"abs_err_{key}"] = np.where(scaled_ref.notna(), np.abs(df[calc_col] - scaled_ref), np.nan)
            mask = scaled_ref.notna() & (np.abs(scaled_ref) > 1e-9)
            df[f"rel_err_{key}"] = np.where(mask, df[f"abs_err_{key}"] / np.maximum(np.abs(scaled_ref), TINY_REF), np.nan)
    df["warning_match"] = np.where(df["warning_ref"].notna(), df["warning_ref"] == df["warning_calc"], np.nan)
    df["warning_est_match"] = np.where(df["warning_ref"].notna(), df["warning_ref"] == df["warning_calc_est"], np.nan)
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
                "warning_match_rate": float(with_ref["warning_est_match"].mean()) if "warning_est_match" in with_ref.columns else np.nan,
            }
        )
    return pd.DataFrame(summaries).sort_values("load_case").reset_index(drop=True)
