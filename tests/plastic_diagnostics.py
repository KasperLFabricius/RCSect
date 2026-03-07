"""Row-by-row diagnostic decomposition utilities for plastic benchmark mismatches."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from tests.pcross_benchmark_fixture import (
    BENCHMARK_MAPPINGS,
    EMBEDDED_BENCHMARK_CASES,
    LOAD_CASE_3,
    LOAD_CASE_4,
    MANUAL_ROWS,
    MANUAL_ROW_DIAGNOSTICS,
    TYPE6_PRESTRESS_MAPPINGS,
    build_pcross_tbeam_solver,
    build_strip_snit_a,
    build_strip_snit_b,
    build_strip_snit_c,
    build_strip_snit_d,
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


def diagnose_benchmark_row(load_case: int, angle_deg: float, mapping: str | None = None) -> dict:
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004, mapping=mapping)
    p_target = _case_target(load_case)

    solved = solver.solve(float(angle_deg), p_target)
    ref_mm = MANUAL_ROWS[(load_case, float(angle_deg))]
    ref_diag = MANUAL_ROW_DIAGNOSTICS[(load_case, float(angle_deg))]

    out = {
        "mapping": mapping or "default",
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


def diagnose_manual_rows(mapping: str | None = None) -> pd.DataFrame:
    rows = [diagnose_benchmark_row(lc, angle, mapping=mapping) for lc, angle in DIAGNOSTIC_ROWS]
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


def _grouped_discrepancy_summary(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "group": "force/strain/curvature level",
                "mean_rel": float(
                    df[
                        [
                            "rel_strain_concrete",
                            "rel_strain_mild",
                            "rel_strain_prestressed",
                            "rel_kappa",
                            "rel_compress_force",
                        ]
                    ].mean().mean()
                ),
            },
            {
                "group": "moment/transformation level",
                "mean_rel": float(df[["rel_Mx", "rel_My", "rel_lever_L", "rel_lever_DX", "rel_lever_DY"]].mean().mean()),
            },
        ]
    )


def run_contribution_study() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    signed = []
    for name, mapping in BENCHMARK_MAPPINGS.items():
        df = diagnose_manual_rows(mapping=name)
        rows.append(
            {
                "mapping": name,
                "gamma_c": mapping.gamma_c,
                "gamma_s": mapping.gamma_s,
                "gamma_p": mapping.gamma_p,
                "gamma_E": mapping.gamma_E,
                "gamma_u": mapping.gamma_u,
                "max_rel_err_Mx": float(df["rel_Mx"].max()),
                "max_rel_err_My": float(df["rel_My"].max()),
                "mean_rel_force_strain_curvature": float(
                    df[["rel_strain_concrete", "rel_strain_mild", "rel_strain_prestressed", "rel_kappa", "rel_compress_force"]]
                    .mean()
                    .mean()
                ),
                "mean_rel_moment_transform": float(df[["rel_Mx", "rel_My", "rel_lever_L", "rel_lever_DX", "rel_lever_DY"]].mean().mean()),
                "dominant_mismatch": classify_dominant_mismatch(df),
            }
        )
        for _, r in df.iterrows():
            signed.append(
                {
                    "mapping": name,
                    "load_case": int(r["load_case"]),
                    "V_deg": float(r["V_deg"]),
                    "dMx": float(r["dMx"]),
                    "dMy": float(r["dMy"]),
                }
            )

    return pd.DataFrame(rows), pd.DataFrame(signed)



def run_type6_prestress_mapping_study() -> pd.DataFrame:
    """Benchmark-only type-6 mapping sensitivity study on Snit A-D."""
    from tests.benchmark_compare import BenchmarkSweepSpec, run_benchmark_sweeps

    families = [
        ("snit_a", 101, EMBEDDED_BENCHMARK_CASES["snit_a"].load, build_strip_snit_a),
        ("snit_b", 102, EMBEDDED_BENCHMARK_CASES["snit_b"].load, build_strip_snit_b),
        ("snit_c", 103, EMBEDDED_BENCHMARK_CASES["snit_c"].load, build_strip_snit_c),
        ("snit_d", 104, EMBEDDED_BENCHMARK_CASES["snit_d"].load, build_strip_snit_d),
    ]

    rows = []
    for mapping_name in TYPE6_PRESTRESS_MAPPINGS:
        for family, load_case, load, builder in families:
            df = run_benchmark_sweeps(
                builder(type6_mapping=mapping_name),
                [BenchmarkSweepSpec(load_case=load_case, p_target=load.P_target, angles_deg=load.angles_deg)],
                reference_rows=EMBEDDED_BENCHMARK_CASES[family].reference_rows,
            )
            refs = df[df["Mx_ref"].notna()]
            rows.append(
                {
                    "mapping": mapping_name,
                    "family": family,
                    "max_rel_err_Mx": float(refs["rel_err_Mx"].max()),
                    "max_rel_err_My": float(refs["rel_err_My"].max()),
                    "max_rel_err_strain_prestressed": float(refs["rel_err_strain_prestressed"].max()),
                    "max_rel_err_compress_force": float(refs["rel_err_compress_force"].max()),
                    "max_rel_err_kappa": float(refs["rel_err_kappa"].max()),
                }
            )

    out = pd.DataFrame(rows).sort_values(["family", "mapping"]).reset_index(drop=True)
    baseline = out[out["mapping"] == "baseline"].set_index("family")
    refined = out[out["mapping"] == "refined"].set_index("family")
    if not baseline.empty and not refined.empty:
        deltas = (
            refined[[
                "max_rel_err_Mx",
                "max_rel_err_My",
                "max_rel_err_strain_prestressed",
                "max_rel_err_compress_force",
                "max_rel_err_kappa",
            ]]
            - baseline[[
                "max_rel_err_Mx",
                "max_rel_err_My",
                "max_rel_err_strain_prestressed",
                "max_rel_err_compress_force",
                "max_rel_err_kappa",
            ]]
        )
        out = out.merge(
            deltas.add_prefix("delta_refined_minus_baseline_").reset_index(),
            on="family",
            how="left",
        )
    return out


def _safe_rel_err(calc: float | None, ref: float | None) -> float:
    if calc is None or ref is None:
        return np.nan
    if not np.isfinite(calc) or not np.isfinite(ref):
        return np.nan
    return abs(float(calc) - float(ref)) / max(abs(float(ref)), 1e-12)


def _sign_agreement(calc: float | None, ref: float | None, tol: float = 1e-9) -> float:
    if calc is None or ref is None:
        return np.nan
    if not np.isfinite(calc) or not np.isfinite(ref):
        return np.nan
    if abs(float(ref)) <= tol:
        return np.nan
    return float(np.sign(float(calc)) == np.sign(float(ref)))


def _lever_from_centroids(c_comp: dict | None, c_tens: dict | None) -> tuple[float, float, float]:
    if not c_comp or not c_tens:
        return (np.nan, np.nan, np.nan)
    if c_comp.get("x") is None or c_comp.get("y") is None or c_tens.get("x") is None or c_tens.get("y") is None:
        return (np.nan, np.nan, np.nan)
    dx = float(c_comp["x"] - c_tens["x"])
    dy = float(c_comp["y"] - c_tens["y"])
    return (float(np.sqrt(dx * dx + dy * dy)), dx, dy)


def _row_semantic_candidates(row: dict) -> dict[str, float]:
    dbg = row.get("debug_force_components") or {}
    mild = [float(v) for v in (dbg.get("mild_strains_total_permille") or [])]
    prest = [float(v) for v in (dbg.get("prestressed_strains_total_permille") or [])]
    prest_inc = [float(v) for v in (dbg.get("prestressed_strains_incremental_permille") or [])]
    prest_se = [float(v) for v in (dbg.get("prestressed_strains_stress_equivalent_permille") or [])]
    prest_bars = dbg.get("prestressed_bar_details") or []

    def _max_abs(vals: list[float]) -> float:
        if not vals:
            return np.nan
        return float(max(vals, key=lambda v: abs(v)))

    out: dict[str, float] = {}

    out["strain_mild:max_tension"] = float(max(mild)) if mild else np.nan
    out["strain_mild:max_compression"] = float(min(mild)) if mild else np.nan
    out["strain_mild:governing_abs_signed"] = _max_abs(mild)

    out["strain_prestressed:max_tension"] = float(max(prest)) if prest else np.nan
    out["strain_prestressed:max_compression"] = float(min(prest)) if prest else np.nan
    out["strain_prestressed:governing_abs_signed"] = _max_abs(prest)
    out["strain_prestressed:incremental_max_tension"] = float(max(prest_inc)) if prest_inc else np.nan
    out["strain_prestressed:incremental_max_compression"] = float(min(prest_inc)) if prest_inc else np.nan
    out["strain_prestressed:incremental_governing_abs_signed"] = _max_abs(prest_inc)
    out["strain_prestressed:stress_equivalent_max_tension"] = float(max(prest_se)) if prest_se else np.nan
    out["strain_prestressed:stress_equivalent_max_compression"] = float(min(prest_se)) if prest_se else np.nan
    out["strain_prestressed:stress_equivalent_governing_abs_signed"] = _max_abs(prest_se)

    if prest_bars:
        by_abs_inc = max(prest_bars, key=lambda b: abs(float(b.get("strain_incremental", 0.0))))
        out["strain_prestressed:governing_incremental_bar_total_strain"] = float(by_abs_inc.get("strain_total", np.nan)) * 1000.0
        out["strain_prestressed:governing_incremental_bar_incremental_strain"] = float(by_abs_inc.get("strain_incremental", np.nan)) * 1000.0

        tensile = [b for b in prest_bars if float(b.get("strain_incremental", 0.0)) >= 0.0]
        compressive = [b for b in prest_bars if float(b.get("strain_incremental", 0.0)) < 0.0]
        out["strain_prestressed:tensile_side_total"] = (
            float(max(float(b.get("strain_total", np.nan)) for b in tensile)) * 1000.0 if tensile else np.nan
        )
        out["strain_prestressed:compressive_side_total"] = (
            float(min(float(b.get("strain_total", np.nan)) for b in compressive)) * 1000.0 if compressive else np.nan
        )
    else:
        out["strain_prestressed:governing_incremental_bar_total_strain"] = np.nan
        out["strain_prestressed:governing_incremental_bar_incremental_strain"] = np.nan
        out["strain_prestressed:tensile_side_total"] = np.nan
        out["strain_prestressed:compressive_side_total"] = np.nan

    conc = float(dbg.get("concrete_compression", np.nan))
    comp_mild = float(dbg.get("compression_mild", np.nan))
    comp_pre = float(dbg.get("compression_prestress", np.nan))
    total_comp = float(dbg.get("total_compression", np.nan))

    out["compress_force:concrete_only"] = conc
    out["compress_force:concrete_plus_comp_rebar"] = conc + comp_mild
    out["compress_force:concrete_plus_all_comp_steel"] = conc + comp_mild + comp_pre
    out["compress_force:total_compression_abs"] = total_comp

    l_tot, dx_tot, dy_tot = _lever_from_centroids(dbg.get("centroid_compression"), dbg.get("centroid_tension"))
    l_conc, dx_conc, dy_conc = _lever_from_centroids(dbg.get("centroid_concrete_compression"), dbg.get("centroid_tension"))

    out["lever:total_comp_to_tension:L"] = l_tot
    out["lever:total_comp_to_tension:DX"] = dx_tot
    out["lever:total_comp_to_tension:DY"] = dy_tot
    out["lever:total_comp_to_tension:DY_negated"] = -dy_tot if np.isfinite(dy_tot) else np.nan

    out["lever:concrete_comp_to_tension:L"] = l_conc
    out["lever:concrete_comp_to_tension:DX"] = dx_conc
    out["lever:concrete_comp_to_tension:DY"] = dy_conc
    out["lever:concrete_comp_to_tension:DY_negated"] = -dy_conc if np.isfinite(dy_conc) else np.nan

    m = np.sqrt(float(row.get("Mx", np.nan)) ** 2 + float(row.get("My", np.nan)) ** 2)
    out["lever:moment_over_total_compression:L"] = float(m / total_comp) if np.isfinite(m) and np.isfinite(total_comp) and total_comp > 1e-12 else np.nan

    mx = float(row.get("Mx", np.nan))
    my = float(row.get("My", np.nan))
    c_force = float(row.get("compress_force", np.nan))
    out["lever:moment_over_compression:DY_from_Mx"] = (
        float(mx / c_force) if np.isfinite(mx) and np.isfinite(c_force) and abs(c_force) > 1e-12 else np.nan
    )
    out["lever:moment_over_compression:DY_from_Mx_negated"] = (
        -float(mx / c_force) if np.isfinite(mx) and np.isfinite(c_force) and abs(c_force) > 1e-12 else np.nan
    )
    out["lever:moment_over_compression:DY_from_My"] = (
        float(my / c_force) if np.isfinite(my) and np.isfinite(c_force) and abs(c_force) > 1e-12 else np.nan
    )
    out["lever:moment_over_compression:DY_from_My_negated"] = (
        -float(my / c_force) if np.isfinite(my) and np.isfinite(c_force) and abs(c_force) > 1e-12 else np.nan
    )

    angle_deg = float(row.get("angle_v_deg", np.nan))
    if np.isfinite(angle_deg) and np.isfinite(dy_tot):
        theta = np.deg2rad(angle_deg)
        out["lever:total_comp_to_tension:DY_local"] = float(-dx_tot * np.sin(theta) + dy_tot * np.cos(theta))
        out["lever:total_comp_to_tension:DY_local_negated"] = -out["lever:total_comp_to_tension:DY_local"]
    else:
        out["lever:total_comp_to_tension:DY_local"] = np.nan
        out["lever:total_comp_to_tension:DY_local_negated"] = np.nan

    if np.isfinite(angle_deg) and np.isfinite(dy_conc):
        theta = np.deg2rad(angle_deg)
        out["lever:concrete_comp_to_tension:DY_local"] = float(-dx_conc * np.sin(theta) + dy_conc * np.cos(theta))
        out["lever:concrete_comp_to_tension:DY_local_negated"] = -out["lever:concrete_comp_to_tension:DY_local"]
    else:
        out["lever:concrete_comp_to_tension:DY_local"] = np.nan
        out["lever:concrete_comp_to_tension:DY_local_negated"] = np.nan

    return out


def run_output_semantics_study() -> tuple[pd.DataFrame, pd.DataFrame]:
    from tests.benchmark_compare import BenchmarkSweepSpec

    case_rows = []
    for key in ["tbeam", "snit_a", "snit_b", "snit_c", "snit_d", "section0", "sectioniv"]:
        if key == "tbeam":
            solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
            specs = [
                BenchmarkSweepSpec(load_case=3, p_target=LOAD_CASE_3.P_target, angles_deg=LOAD_CASE_3.angles_deg),
                BenchmarkSweepSpec(load_case=4, p_target=LOAD_CASE_4.P_target, angles_deg=LOAD_CASE_4.angles_deg),
            ]
            refs = MANUAL_ROW_DIAGNOSTICS
            family = "tbeam"
        else:
            case = EMBEDDED_BENCHMARK_CASES[key]
            solver = case.solver_builder()
            specs = [BenchmarkSweepSpec(load_case=case.load_case, p_target=case.load.P_target, angles_deg=case.load.angles_deg)]
            refs = case.reference_rows
            family = "snit" if key.startswith("snit") else "annular"

        for spec in specs:
            solved = solver.solve_angle_sweep(spec.angles_deg, spec.p_target)
            by_angle = {float(r["angle_v_deg"]): r for r in solved}
            for angle in spec.angles_deg:
                a = float(angle)
                row = by_angle[a]
                ref = refs.get((spec.load_case, a), None)
                if ref is None:
                    continue
                candidates = _row_semantic_candidates(row)
                base = {"fixture": key, "fixture_family": family, "load_case": spec.load_case, "V_deg": a}
                # output refs resolve L/DX/DY keys for non-manual fixtures
                ref_map = {
                    "strain_mild": ref.get("strain_mild"),
                    "strain_prestressed": ref.get("strain_prestressed"),
                    "compress_force": ref.get("compress_force"),
                    "lever_L": ref.get("lever_L", ref.get("L")),
                    "lever_DX": ref.get("lever_DX", ref.get("DX")),
                    "lever_DY": ref.get("lever_DY", ref.get("DY")),
                }
                candidate_filters = {
                    "strain_mild": lambda n: n.startswith("strain_mild:"),
                    "strain_prestressed": lambda n: n.startswith("strain_prestressed:"),
                    "compress_force": lambda n: n.startswith("compress_force:"),
                    "lever_L": lambda n: n.startswith("lever:") and n.endswith(":L"),
                    "lever_DX": lambda n: n.startswith("lever:") and n.endswith(":DX"),
                    "lever_DY": lambda n: n.startswith("lever:") and (":DY" in n),
                }
                for output, rval in ref_map.items():
                    if rval is None or not np.isfinite(float(rval)):
                        continue
                    rval_u = float(rval) * 10.0 if output.startswith("strain_") and abs(float(rval)) <= 1.0 else float(rval)
                    filt = candidate_filters[output]
                    for cname, cval in candidates.items():
                        if not filt(cname):
                            continue
                        case_rows.append({
                            **base,
                            "output": output,
                            "candidate": cname,
                            "ref": rval_u,
                            "calc": float(cval) if np.isfinite(cval) else np.nan,
                            "signed_error": (float(cval) - rval_u) if np.isfinite(cval) else np.nan,
                            "rel_error": _safe_rel_err(cval, rval_u),
                            "sign_agreement": _sign_agreement(cval, rval_u),
                        })

    detail = pd.DataFrame(case_rows)
    summary = (
        detail.groupby(["fixture_family", "output", "candidate"], dropna=False)
        .agg(
            count=("rel_error", "count"),
            max_rel_error=("rel_error", "max"),
            median_rel_error=("rel_error", "median"),
            median_signed_error=("signed_error", "median"),
            sign_agreement_rate=("sign_agreement", "mean"),
        )
        .reset_index()
        .sort_values(["fixture_family", "output", "max_rel_error", "median_rel_error"])
        .reset_index(drop=True)
    )
    return detail, summary


def choose_semantic_winners(summary: pd.DataFrame) -> dict[str, str]:
    winners: dict[str, str] = {}
    for output in ["strain_mild", "strain_prestressed", "compress_force", "lever_L", "lever_DX", "lever_DY"]:
        sub = summary[summary["output"] == output]
        if sub.empty:
            continue
        best_by_family = (
            sub.sort_values(["fixture_family", "max_rel_error", "median_rel_error"])
            .groupby("fixture_family", as_index=False)
            .first()
        )
        counts = best_by_family["candidate"].value_counts()
        if counts.empty:
            continue
        cand = counts.index[0]
        robust = True
        if output in {"strain_prestressed", "lever_DY"}:
            cand_rows = sub[sub["candidate"] == cand]
            robust = (
                cand_rows["max_rel_error"].notna().any()
                and float(cand_rows["max_rel_error"].max()) <= 0.25
                and float(cand_rows["median_rel_error"].median()) <= 0.15
            )
        if int(counts.iloc[0]) >= 2 and robust:
            winners[output] = str(cand)
    return winners


def choose_semantic_winners_by_family(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family in ["tbeam", "snit", "annular"]:
        fam = summary[summary["fixture_family"] == family]
        for output in ["strain_prestressed", "lever_DY"]:
            sub = fam[fam["output"] == output]
            if sub.empty:
                continue
            best = sub.sort_values(["max_rel_error", "median_rel_error"]).iloc[0]
            rows.append(
                {
                    "fixture_family": family,
                    "output": output,
                    "candidate": str(best["candidate"]),
                    "max_rel_error": float(best["max_rel_error"]),
                    "median_rel_error": float(best["median_rel_error"]),
                    "median_signed_error": float(best["median_signed_error"]),
                    "sign_agreement_rate": float(best["sign_agreement_rate"]),
                }
            )
    return pd.DataFrame(rows).sort_values(["output", "fixture_family"]).reset_index(drop=True)

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
    grouped = _grouped_discrepancy_summary(df)
    md = "# Plastic Row Diagnostics\n\n"
    md += "Six embedded manual rows with signed and intermediate-quantity decomposition.\n\n"
    headers = list(sub.columns)
    md += "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for _, r in sub.iterrows():
        vals = ["" if (isinstance(r[h], float) and not math.isfinite(r[h])) else str(r[h]) for h in headers]
        md += "| " + " | ".join(vals) + " |\n"

    md += "\n## Grouped discrepancy summary\n\n"
    md += "| group | mean_rel |\n| --- | --- |\n"
    for _, r in grouped.iterrows():
        md += f"| {r['group']} | {r['mean_rel']} |\n"

    md += "\nConclusion: " + conclusion + "\n"
    return md
