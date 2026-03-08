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



def _nearest_bar_strain(rows: list[dict], which: str = "compression", field: str = "strain_total") -> tuple[float, str | None]:
    if not rows:
        return (np.nan, None)
    if which == "compression":
        chosen = max(rows, key=lambda r: float(r.get("y", -np.inf)))
    else:
        chosen = min(rows, key=lambda r: float(r.get("y", np.inf)))
    return (float(chosen.get(field, np.nan)) * 1000.0, chosen.get("id"))


def _row_output_definition_candidates(row: dict) -> list[dict]:
    dbg = row.get("debug_force_components") or {}
    mild_rows = dbg.get("mild_bar_details") or []
    pre_rows = dbg.get("prestressed_bar_details") or []

    out: list[dict] = []

    def add(output: str, candidate: str, value: float, bar_id=None):
        out.append({"output": output, "candidate": candidate, "value": value, "bar_id": bar_id})

    # --- strain_mild candidates ---
    if mild_rows:
        force_gov = max(mild_rows, key=lambda b: abs(float(b.get("force_kN", 0.0))))
        abs_gov = max(mild_rows, key=lambda b: abs(float(b.get("strain_total", 0.0))))
        tmax = max(mild_rows, key=lambda b: float(b.get("strain_total", -np.inf)))
        cmax = min(mild_rows, key=lambda b: float(b.get("strain_total", np.inf)))
        near_comp_val, near_comp_id = _nearest_bar_strain(mild_rows, "compression", "strain_total")
        near_tens_val, near_tens_id = _nearest_bar_strain(mild_rows, "tension", "strain_total")

        add("strain_mild", "strain_mild:force_governing_total", float(force_gov.get("strain_total", np.nan)) * 1000.0, force_gov.get("id"))
        add("strain_mild", "strain_mild:abs_strain_governing_total", float(abs_gov.get("strain_total", np.nan)) * 1000.0, abs_gov.get("id"))
        add("strain_mild", "strain_mild:max_tensile_total", float(tmax.get("strain_total", np.nan)) * 1000.0, tmax.get("id"))
        add("strain_mild", "strain_mild:max_compressive_total", float(cmax.get("strain_total", np.nan)) * 1000.0, cmax.get("id"))
        add("strain_mild", "strain_mild:nearest_extreme_compression_total", near_comp_val, near_comp_id)
        add("strain_mild", "strain_mild:nearest_extreme_tension_total", near_tens_val, near_tens_id)

    # --- strain_prestressed candidates ---
    if pre_rows:
        force_gov = max(pre_rows, key=lambda b: abs(float(b.get("force_kN", 0.0))))
        inc_force_gov = max(pre_rows, key=lambda b: abs(float(b.get("force_kN", 0.0))))
        abs_gov = max(pre_rows, key=lambda b: abs(float(b.get("strain_total", 0.0))))
        abs_inc_gov = max(pre_rows, key=lambda b: abs(float(b.get("strain_incremental", 0.0))))
        tmax = max(pre_rows, key=lambda b: float(b.get("strain_total", -np.inf)))
        tmax_inc = max(pre_rows, key=lambda b: float(b.get("strain_incremental", -np.inf)))
        cmax = min(pre_rows, key=lambda b: float(b.get("strain_total", np.inf)))
        cmax_inc = min(pre_rows, key=lambda b: float(b.get("strain_incremental", np.inf)))
        near_comp_t, near_comp_id = _nearest_bar_strain(pre_rows, "compression", "strain_total")
        near_tens_t, near_tens_id = _nearest_bar_strain(pre_rows, "tension", "strain_total")

        add("strain_prestressed", "strain_prestressed:force_governing_total", float(force_gov.get("strain_total", np.nan)) * 1000.0, force_gov.get("id"))
        add("strain_prestressed", "strain_prestressed:force_governing_incremental", float(inc_force_gov.get("strain_incremental", np.nan)) * 1000.0, inc_force_gov.get("id"))
        add("strain_prestressed", "strain_prestressed:abs_strain_governing_total", float(abs_gov.get("strain_total", np.nan)) * 1000.0, abs_gov.get("id"))
        add("strain_prestressed", "strain_prestressed:abs_strain_governing_incremental", float(abs_inc_gov.get("strain_incremental", np.nan)) * 1000.0, abs_inc_gov.get("id"))
        add("strain_prestressed", "strain_prestressed:max_tensile_total", float(tmax.get("strain_total", np.nan)) * 1000.0, tmax.get("id"))
        add("strain_prestressed", "strain_prestressed:max_tensile_incremental", float(tmax_inc.get("strain_incremental", np.nan)) * 1000.0, tmax_inc.get("id"))
        add("strain_prestressed", "strain_prestressed:max_compressive_total", float(cmax.get("strain_total", np.nan)) * 1000.0, cmax.get("id"))
        add("strain_prestressed", "strain_prestressed:max_compressive_incremental", float(cmax_inc.get("strain_incremental", np.nan)) * 1000.0, cmax_inc.get("id"))
        add("strain_prestressed", "strain_prestressed:nearest_extreme_compression_total", near_comp_t, near_comp_id)
        add("strain_prestressed", "strain_prestressed:nearest_extreme_tension_total", near_tens_t, near_tens_id)

    # --- compress force candidates ---
    conc = float(dbg.get("concrete_compression", np.nan))
    comp_mild = float(dbg.get("compression_mild", np.nan))
    comp_pre = float(dbg.get("compression_prestress", np.nan))
    total_comp = float(dbg.get("total_compression", np.nan))

    add("compress_force", "compress_force:concrete_only", conc)
    add("compress_force", "compress_force:concrete_plus_comp_mild", conc + comp_mild)
    add("compress_force", "compress_force:concrete_plus_comp_mild_plus_comp_prestress", conc + comp_mild + comp_pre)
    add("compress_force", "compress_force:total_compression_abs", abs(total_comp))
    add("compress_force", "compress_force:full_compression_resultant_abs", abs(total_comp))

    # --- lever candidates ---
    c_comp = dbg.get("centroid_compression") or {}
    c_tens = dbg.get("centroid_tension") or {}
    c_conc = dbg.get("centroid_concrete_compression") or {}

    if c_comp.get("x") is not None and c_tens.get("x") is not None:
        dx = float(c_tens["x"] - c_comp["x"])
        dy = float(c_tens["y"] - c_comp["y"])
        add("lever_DX", "lever:centroid_total:dx", dx)
        add("lever_DY", "lever:centroid_total:dy", dy)
        add("lever_DX", "lever:centroid_total:dx_negated", -dx)
        add("lever_DY", "lever:centroid_total:dy_negated", -dy)
        add("lever_L", "lever:centroid_total:L", float(np.hypot(dx, dy)))

    if c_conc.get("x") is not None and c_tens.get("x") is not None:
        dx = float(c_tens["x"] - c_conc["x"])
        dy = float(c_tens["y"] - c_conc["y"])
        add("lever_DX", "lever:centroid_concrete_to_tension:dx", dx)
        add("lever_DY", "lever:centroid_concrete_to_tension:dy", dy)
        add("lever_DX", "lever:centroid_concrete_to_tension:dx_negated", -dx)
        add("lever_DY", "lever:centroid_concrete_to_tension:dy_negated", -dy)
        add("lever_L", "lever:centroid_concrete_to_tension:L", float(np.hypot(dx, dy)))

    # local->global and direct-global are equivalent transforms; keep explicit names
    add("lever_DX", "lever:reported:DX", float(row.get("lever_DX", np.nan)))
    add("lever_DY", "lever:reported:DY", float(row.get("lever_DY", np.nan)))
    add("lever_L", "lever:reported:L", float(row.get("lever_L", np.nan)))

    cf = float(row.get("compress_force", np.nan))
    if np.isfinite(cf) and abs(cf) > 1e-12:
        add("lever_DY", "lever:moment_over_compress_global:DY_from_Mx", float(row.get("Mx", np.nan)) / cf)
        add("lever_DX", "lever:moment_over_compress_global:DX_from_My", float(row.get("My", np.nan)) / cf)
        add("lever_DY", "lever:moment_over_compress_local:DY_from_Mx_local", float(row.get("Mx_local", np.nan)) / cf)
        add("lever_DX", "lever:moment_over_compress_local:DX_from_My_local", float(row.get("My_local", np.nan)) / cf)
        lx = float(row.get("My_local", np.nan)) / cf if np.isfinite(float(row.get("My_local", np.nan))) else np.nan
        ly = float(row.get("Mx_local", np.nan)) / cf if np.isfinite(float(row.get("Mx_local", np.nan))) else np.nan
        add("lever_L", "lever:moment_over_compress_local:L", float(np.hypot(lx, ly)) if np.isfinite(lx) and np.isfinite(ly) else np.nan)

    return out


def run_output_definition_study() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from tests.benchmark_compare import BenchmarkSweepSpec

    case_rows = []
    for key, case in EMBEDDED_BENCHMARK_CASES.items():
        family = (
            "tbeam" if case.load_case in (3, 4)
            else "snit" if case.load_case in (101, 102, 103, 104)
            else "annular"
        )
        refs = case.reference_rows
        solver = case.solver_builder()
        specs = [BenchmarkSweepSpec(load_case=case.load_case, p_target=case.load.P_target, angles_deg=case.load.angles_deg)]
        for spec in specs:
            solved = solver.solve_angle_sweep(spec.angles_deg, spec.p_target)
            by_angle = {float(r["angle_v_deg"]): r for r in solved}
            for angle in spec.angles_deg:
                a = float(angle)
                row = by_angle[a]
                ref = refs.get((spec.load_case, a), None)
                if ref is None:
                    continue

                ref_map = {
                    "strain_mild": ref.get("strain_mild"),
                    "strain_prestressed": ref.get("strain_prestressed"),
                    "compress_force": ref.get("compress_force"),
                    "lever_L": ref.get("lever_L", ref.get("L")),
                    "lever_DX": ref.get("lever_DX", ref.get("DX")),
                    "lever_DY": ref.get("lever_DY", ref.get("DY")),
                }

                candidates = _row_output_definition_candidates(row)
                for c in candidates:
                    output = c["output"]
                    rval = ref_map.get(output)
                    if rval is None or not np.isfinite(float(rval)):
                        continue
                    rval_u = float(rval) * 10.0 if output.startswith("strain_") and abs(float(rval)) <= 1.0 else float(rval)
                    calc = c["value"]
                    case_rows.append({
                        "fixture": key,
                        "fixture_family": family,
                        "load_case": spec.load_case,
                        "V_deg": a,
                        "output": output,
                        "candidate": c["candidate"],
                        "source_bar_id": c.get("bar_id"),
                        "ref": rval_u,
                        "calc": float(calc) if np.isfinite(calc) else np.nan,
                        "signed_error": (float(calc) - rval_u) if np.isfinite(calc) else np.nan,
                        "rel_error": _safe_rel_err(calc, rval_u),
                        "sign_agreement": _sign_agreement(calc, rval_u),
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
        .sort_values(["output", "fixture_family", "max_rel_error", "median_rel_error"])
        .reset_index(drop=True)
    )

    winner_rows = []
    for output in ["strain_mild", "strain_prestressed", "compress_force", "lever_L", "lever_DX", "lever_DY"]:
        out_sub = summary[summary["output"] == output]
        if out_sub.empty:
            continue
        best = out_sub.sort_values(["fixture_family", "max_rel_error", "median_rel_error"]).groupby("fixture_family", as_index=False).first()
        cand_counts = best["candidate"].value_counts()
        cross = cand_counts.index[0] if (not cand_counts.empty and int(cand_counts.iloc[0]) == 3) else None
        for _, r in best.iterrows():
            winner_rows.append({
                "output": output,
                "fixture_family": r["fixture_family"],
                "best_candidate": r["candidate"],
                "max_rel_error": r["max_rel_error"],
                "median_rel_error": r["median_rel_error"],
                "sign_agreement_rate": r["sign_agreement_rate"],
                "cross_family_winner": cross,
                "cross_family_winner_exists": bool(cross is not None),
            })

    winners = pd.DataFrame(winner_rows).sort_values(["output", "fixture_family"]).reset_index(drop=True)
    return detail, summary, winners



def run_zone_partition_study() -> pd.DataFrame:
    from tests.benchmark_compare import BenchmarkSweepSpec

    rows = []
    for key, case in EMBEDDED_BENCHMARK_CASES.items():
        family = (
            "tbeam" if case.load_case in (3, 4)
            else "snit" if case.load_case in (101, 102, 103, 104)
            else "annular"
        )
        refs = case.reference_rows
        solver = case.solver_builder()
        spec = BenchmarkSweepSpec(load_case=case.load_case, p_target=case.load.P_target, angles_deg=case.load.angles_deg)
        solved = solver.solve_angle_sweep(spec.angles_deg, spec.p_target)
        by_angle = {float(r["angle_v_deg"]): r for r in solved}
        for angle in spec.angles_deg:
            a = float(angle)
            row = by_angle[a]
            ref = refs.get((spec.load_case, a), None)
            if ref is None:
                continue
            dbg = row.get("debug_force_components") or {}
            # force-sign based
            sign_comp = float(dbg.get("concrete_compression", np.nan) + dbg.get("compression_mild", np.nan) + dbg.get("compression_prestress", np.nan))
            # zone-based
            zone_comp = float(row.get("compress_zone_force_total", np.nan))

            dx_sign = float(row.get("debug_resultant_centroids", {}).get("comp_centroid_x", np.nan))
            dy_sign = float(row.get("debug_resultant_centroids", {}).get("comp_centroid_y", np.nan))
            dx_t_sign = float(row.get("debug_resultant_centroids", {}).get("tens_centroid_x", np.nan))
            dy_t_sign = float(row.get("debug_resultant_centroids", {}).get("tens_centroid_y", np.nan))
            dx_sign_val = (dx_t_sign - dx_sign) if np.isfinite(dx_sign) and np.isfinite(dx_t_sign) else np.nan
            dy_sign_val = (dy_t_sign - dy_sign) if np.isfinite(dy_sign) and np.isfinite(dy_t_sign) else np.nan

            dz = row.get("debug_resultant_centroids", {})
            dx_zone_raw = dz.get("tension_zone_centroid_x", np.nan)
            dy_zone_raw = dz.get("tension_zone_centroid_y", np.nan)
            dx_c_zone_raw = dz.get("compress_zone_centroid_x", np.nan)
            dy_c_zone_raw = dz.get("compress_zone_centroid_y", np.nan)
            dx_zone = float(dx_zone_raw) if dx_zone_raw is not None else np.nan
            dy_zone = float(dy_zone_raw) if dy_zone_raw is not None else np.nan
            dx_c_zone = float(dx_c_zone_raw) if dx_c_zone_raw is not None else np.nan
            dy_c_zone = float(dy_c_zone_raw) if dy_c_zone_raw is not None else np.nan
            dx_zone_val = (dx_zone - dx_c_zone) if np.isfinite(dx_zone) and np.isfinite(dx_c_zone) else np.nan
            dy_zone_val = (dy_zone - dy_c_zone) if np.isfinite(dy_zone) and np.isfinite(dy_c_zone) else np.nan

            rows.append({
                "fixture": key,
                "fixture_family": family,
                "load_case": spec.load_case,
                "V_deg": a,
                "compress_force_ref": float(ref.get("compress_force", np.nan)),
                "compress_force_force_sign": sign_comp,
                "compress_force_zone": zone_comp,
                "compress_force_reported": float(row.get("compress_force", np.nan)),
                "compress_force_zone_rel_error": _safe_rel_err(zone_comp, float(ref.get("compress_force", np.nan))),
                "compress_force_force_sign_rel_error": _safe_rel_err(sign_comp, float(ref.get("compress_force", np.nan))),
                "DX_ref": float(ref.get("lever_DX", ref.get("DX", np.nan))),
                "DY_ref": float(ref.get("lever_DY", ref.get("DY", np.nan))),
                "DX_force_sign": dx_sign_val,
                "DY_force_sign": dy_sign_val,
                "DX_zone": dx_zone_val,
                "DY_zone": dy_zone_val,
                "DX_reported": float(row.get("lever_DX", np.nan)),
                "DY_reported": float(row.get("lever_DY", np.nan)),
                "DX_zone_rel_error": _safe_rel_err(dx_zone_val, float(ref.get("lever_DX", ref.get("DX", np.nan)))),
                "DY_zone_rel_error": _safe_rel_err(dy_zone_val, float(ref.get("lever_DY", ref.get("DY", np.nan)))),
                "DX_force_sign_rel_error": _safe_rel_err(dx_sign_val, float(ref.get("lever_DX", ref.get("DX", np.nan)))),
                "DY_force_sign_rel_error": _safe_rel_err(dy_sign_val, float(ref.get("lever_DY", ref.get("DY", np.nan)))),
            })

    return pd.DataFrame(rows).sort_values(["load_case", "V_deg"]).reset_index(drop=True)


def _family_for_load_case(load_case: int) -> str:
    if load_case in (3, 4):
        return "tbeam"
    if load_case in (101, 102, 103, 104):
        return "snit"
    return "annular"


def _iter_pcross_rows_for_definition_studies() -> list[dict]:
    from tests.benchmark_compare import BenchmarkSweepSpec

    rows: list[dict] = []

    # T-beam rows from manual corpus (LC3/LC4).
    tbeam_solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    t_specs = [
        BenchmarkSweepSpec(load_case=3, p_target=LOAD_CASE_3.P_target, angles_deg=LOAD_CASE_3.angles_deg),
        BenchmarkSweepSpec(load_case=4, p_target=LOAD_CASE_4.P_target, angles_deg=LOAD_CASE_4.angles_deg),
    ]
    for spec in t_specs:
        solved = tbeam_solver.solve_angle_sweep(spec.angles_deg, spec.p_target)
        by_angle = {float(r["angle_v_deg"]): r for r in solved}
        for angle in spec.angles_deg:
            a = float(angle)
            ref = MANUAL_ROW_DIAGNOSTICS.get((spec.load_case, a))
            if ref is None:
                continue
            rows.append(
                {
                    "fixture": f"lc{spec.load_case}",
                    "fixture_family": "tbeam",
                    "load_case": spec.load_case,
                    "V_deg": a,
                    "row": by_angle[a],
                    "ref": ref,
                    "local_rotation_deg": float(tbeam_solver.cs.local_rotation_deg(a)),
                }
            )

    # Embedded rows (snit + annular).
    for key, case in EMBEDDED_BENCHMARK_CASES.items():
        family = _family_for_load_case(int(case.load_case))
        solver = case.solver_builder()
        spec = BenchmarkSweepSpec(load_case=case.load_case, p_target=case.load.P_target, angles_deg=case.load.angles_deg)
        solved = solver.solve_angle_sweep(spec.angles_deg, spec.p_target)
        by_angle = {float(r["angle_v_deg"]): r for r in solved}
        for angle in spec.angles_deg:
            a = float(angle)
            ref = case.reference_rows.get((spec.load_case, a), None)
            if ref is None:
                continue
            rows.append(
                {
                    "fixture": key,
                    "fixture_family": family,
                    "load_case": spec.load_case,
                    "V_deg": a,
                    "row": by_angle[a],
                    "ref": ref,
                    "local_rotation_deg": float(solver.cs.local_rotation_deg(a)),
                }
            )
    return rows


def _to_permille_ref(ref_val: float | None) -> float:
    if ref_val is None:
        return np.nan
    fv = float(ref_val)
    return fv * 10.0 if abs(fv) <= 1.0 else fv


def _row_strain_definition_candidates(row: dict) -> list[dict]:
    dbg = row.get("debug_force_components") or {}
    mild_rows = dbg.get("mild_bar_details") or []
    pre_rows = dbg.get("prestressed_bar_details") or []

    out: list[dict] = []

    def add(output: str, candidate: str, value: float, bar_id=None):
        out.append({"output": output, "candidate": candidate, "value": value, "bar_id": bar_id})

    if mild_rows:
        force_gov = max(mild_rows, key=lambda b: abs(float(b.get("force_kN", 0.0))))
        abs_gov = max(mild_rows, key=lambda b: abs(float(b.get("strain_total", 0.0))))
        tmax = max(mild_rows, key=lambda b: float(b.get("strain_total", -np.inf)))
        cmax = min(mild_rows, key=lambda b: float(b.get("strain_total", np.inf)))
        near_comp_val, near_comp_id = _nearest_bar_strain(mild_rows, "compression", "strain_total")
        near_tens_val, near_tens_id = _nearest_bar_strain(mild_rows, "tension", "strain_total")

        mild_total_pm = [float(b.get("strain_total", np.nan)) * 1000.0 for b in mild_rows]
        mild_legacy_pm = [-v for v in mild_total_pm]

        max_legacy_idx = int(np.nanargmax(mild_legacy_pm)) if mild_legacy_pm else -1
        min_legacy_idx = int(np.nanargmin(mild_legacy_pm)) if mild_legacy_pm else -1

        add("strain_mild", "A_force_governing_total_legacy", -float(force_gov.get("strain_total", np.nan)) * 1000.0, force_gov.get("id"))
        add("strain_mild", "B_abs_strain_governing_total_legacy", -float(abs_gov.get("strain_total", np.nan)) * 1000.0, abs_gov.get("id"))
        add("strain_mild", "C_max_tensile_total_internal", float(tmax.get("strain_total", np.nan)) * 1000.0, tmax.get("id"))
        add("strain_mild", "D_max_compressive_total_internal", float(cmax.get("strain_total", np.nan)) * 1000.0, cmax.get("id"))
        add("strain_mild", "E_nearest_extreme_compression_total_internal", near_comp_val, near_comp_id)
        add("strain_mild", "F_nearest_extreme_tension_total_internal", near_tens_val, near_tens_id)
        add(
            "strain_mild",
            "G_max_algebraic_legacy_converted_total",
            float(max(mild_legacy_pm)) if mild_legacy_pm else np.nan,
            mild_rows[max_legacy_idx].get("id") if max_legacy_idx >= 0 else None,
        )
        add(
            "strain_mild",
            "H_min_algebraic_legacy_converted_total",
            float(min(mild_legacy_pm)) if mild_legacy_pm else np.nan,
            mild_rows[min_legacy_idx].get("id") if min_legacy_idx >= 0 else None,
        )

    if pre_rows:
        force_gov = max(pre_rows, key=lambda b: abs(float(b.get("force_kN", 0.0))))
        abs_gov_t = max(pre_rows, key=lambda b: abs(float(b.get("strain_total", 0.0))))
        abs_gov_i = max(pre_rows, key=lambda b: abs(float(b.get("strain_incremental", 0.0))))
        tmax_t = max(pre_rows, key=lambda b: float(b.get("strain_total", -np.inf)))
        cmax_t = min(pre_rows, key=lambda b: float(b.get("strain_total", np.inf)))
        tmax_i = max(pre_rows, key=lambda b: float(b.get("strain_incremental", -np.inf)))
        cmax_i = min(pre_rows, key=lambda b: float(b.get("strain_incremental", np.inf)))
        near_comp_t, near_comp_id = _nearest_bar_strain(pre_rows, "compression", "strain_total")
        near_tens_t, near_tens_id = _nearest_bar_strain(pre_rows, "tension", "strain_total")

        pre_total_pm = [float(b.get("strain_total", np.nan)) * 1000.0 for b in pre_rows]
        pre_legacy_pm = [-v for v in pre_total_pm]
        max_legacy_idx = int(np.nanargmax(pre_legacy_pm)) if pre_legacy_pm else -1
        min_legacy_idx = int(np.nanargmin(pre_legacy_pm)) if pre_legacy_pm else -1

        add("strain_prestressed", "A_force_governing_total_legacy", -float(force_gov.get("strain_total", np.nan)) * 1000.0, force_gov.get("id"))
        add("strain_prestressed", "B_force_governing_incremental_internal", float(force_gov.get("strain_incremental", np.nan)) * 1000.0, force_gov.get("id"))
        add("strain_prestressed", "C_abs_strain_governing_total_legacy", -float(abs_gov_t.get("strain_total", np.nan)) * 1000.0, abs_gov_t.get("id"))
        add("strain_prestressed", "D_abs_strain_governing_incremental_internal", float(abs_gov_i.get("strain_incremental", np.nan)) * 1000.0, abs_gov_i.get("id"))
        add("strain_prestressed", "E_max_tensile_total_internal", float(tmax_t.get("strain_total", np.nan)) * 1000.0, tmax_t.get("id"))
        add("strain_prestressed", "F_max_compressive_total_internal", float(cmax_t.get("strain_total", np.nan)) * 1000.0, cmax_t.get("id"))
        add("strain_prestressed", "G_max_tensile_incremental_internal", float(tmax_i.get("strain_incremental", np.nan)) * 1000.0, tmax_i.get("id"))
        add("strain_prestressed", "H_max_compressive_incremental_internal", float(cmax_i.get("strain_incremental", np.nan)) * 1000.0, cmax_i.get("id"))
        add("strain_prestressed", "I_nearest_extreme_compression_total_internal", near_comp_t, near_comp_id)
        add("strain_prestressed", "J_nearest_extreme_tension_total_internal", near_tens_t, near_tens_id)
        add(
            "strain_prestressed",
            "K_max_algebraic_legacy_converted_total",
            float(max(pre_legacy_pm)) if pre_legacy_pm else np.nan,
            pre_rows[max_legacy_idx].get("id") if max_legacy_idx >= 0 else None,
        )
        add(
            "strain_prestressed",
            "L_min_algebraic_legacy_converted_total",
            float(min(pre_legacy_pm)) if pre_legacy_pm else np.nan,
            pre_rows[min_legacy_idx].get("id") if min_legacy_idx >= 0 else None,
        )

    return out


def run_strain_definition_study() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    for rec in _iter_pcross_rows_for_definition_studies():
        ref_mild = _to_permille_ref(rec["ref"].get("strain_mild"))
        ref_pre = _to_permille_ref(rec["ref"].get("strain_prestressed"))
        for cand in _row_strain_definition_candidates(rec["row"]):
            ref = ref_mild if cand["output"] == "strain_mild" else ref_pre
            if not np.isfinite(ref):
                continue
            calc = float(cand["value"]) if np.isfinite(cand["value"]) else np.nan
            rows.append(
                {
                    "fixture": rec["fixture"],
                    "fixture_family": rec["fixture_family"],
                    "load_case": rec["load_case"],
                    "V_deg": rec["V_deg"],
                    "output": cand["output"],
                    "candidate": cand["candidate"],
                    "source_bar_id": cand.get("bar_id"),
                    "ref": ref,
                    "calc": calc,
                    "signed_error": calc - ref if np.isfinite(calc) else np.nan,
                    "rel_error": _safe_rel_err(calc, ref),
                    "sign_agreement": _sign_agreement(calc, ref),
                }
            )

    detail = pd.DataFrame(rows).sort_values(["output", "fixture_family", "load_case", "V_deg", "candidate"]).reset_index(drop=True)
    summary = (
        detail.groupby(["fixture_family", "output", "candidate"], dropna=False)
        .agg(
            count=("rel_error", "count"),
            max_rel_error=("rel_error", "max"),
            median_rel_error=("rel_error", "median"),
            sign_agreement_rate=("sign_agreement", "mean"),
        )
        .reset_index()
        .sort_values(["output", "fixture_family", "max_rel_error", "median_rel_error"]) 
        .reset_index(drop=True)
    )

    winner_rows = []
    for output in ["strain_mild", "strain_prestressed"]:
        out_sub = summary[summary["output"] == output]
        if out_sub.empty:
            continue
        best = out_sub.sort_values(["fixture_family", "max_rel_error", "median_rel_error"]).groupby("fixture_family", as_index=False).first()
        counts = best["candidate"].value_counts()
        cross = counts.index[0] if (not counts.empty and int(counts.iloc[0]) == 3) else None
        for _, r in best.iterrows():
            winner_rows.append(
                {
                    "output": output,
                    "fixture_family": r["fixture_family"],
                    "best_candidate": r["candidate"],
                    "max_rel_error": r["max_rel_error"],
                    "median_rel_error": r["median_rel_error"],
                    "sign_agreement_rate": r["sign_agreement_rate"],
                    "cross_family_winner": cross,
                    "cross_family_winner_exists": bool(cross is not None),
                }
            )

    winners = pd.DataFrame(winner_rows).sort_values(["output", "fixture_family"]).reset_index(drop=True)
    return detail, summary, winners


def _rotate_to_global(dx_local: float, dy_local: float, angle_deg: float) -> tuple[float, float]:
    a = np.radians(angle_deg)
    c = np.cos(a)
    s = np.sin(a)
    return (dx_local * c - dy_local * s, dx_local * s + dy_local * c)


def _row_dxdy_sign_candidates(row: dict, local_rotation_deg: float) -> list[dict]:
    dbg_cent = row.get("debug_resultant_centroids") or {}
    xc = dbg_cent.get("compress_zone_centroid_x")
    yc = dbg_cent.get("compress_zone_centroid_y")
    xt = dbg_cent.get("tension_zone_centroid_x")
    yt = dbg_cent.get("tension_zone_centroid_y")

    out = []

    def add(candidate: str, dx: float, dy: float):
        out.append({"candidate": candidate, "output": "lever_DX", "value": dx})
        out.append({"candidate": candidate, "output": "lever_DY", "value": dy})
        out.append({"candidate": candidate, "output": "lever_L", "value": float(np.hypot(dx, dy)) if np.isfinite(dx) and np.isfinite(dy) else np.nan})

    finite_centroids = all(v is not None and np.isfinite(float(v)) for v in [xc, yc, xt, yt])
    if finite_centroids:
        xcf, ycf, xtf, ytf = float(xc), float(yc), float(xt), float(yt)
        dx_local_ct = xtf - xcf
        dy_local_ct = ytf - ycf
        dx_local_tc = xcf - xtf
        dy_local_tc = ycf - ytf

        dxg_ct, dyg_ct = _rotate_to_global(dx_local_ct, dy_local_ct, local_rotation_deg)
        dxg_tc, dyg_tc = _rotate_to_global(dx_local_tc, dy_local_tc, local_rotation_deg)

        # A/B/C/D + single-axis flips for explicit sign diagnostics.
        add("A_current_centroid_with_explicit_sign_flip", -dxg_ct, -dyg_ct)
        add("B_centroid_without_explicit_sign_flip", dxg_ct, dyg_ct)
        add("C_flip_DX_only", -dxg_ct, dyg_ct)
        add("D_flip_DY_only", dxg_ct, -dyg_ct)
        add("E_comp_to_tens_local_then_global_no_override", dxg_ct, dyg_ct)
        add("F_tens_to_comp_local_then_global", dxg_tc, dyg_tc)

        # Direct-global build from centroid coordinates.
        xcg, ycg = _rotate_to_global(xcf, ycf, local_rotation_deg)
        xtg, ytg = _rotate_to_global(xtf, ytf, local_rotation_deg)
        dxg_direct = xtg - xcg
        dyg_direct = ytg - ycg
        add("E2_comp_to_tens_direct_global_no_flip", dxg_direct, dyg_direct)
        add("F2_comp_to_tens_direct_global_with_flip", -dxg_direct, -dyg_direct)

    cf = float(row.get("compress_force", np.nan))
    if np.isfinite(cf) and abs(cf) > 1e-12:
        dxg = float(row.get("My", np.nan)) / cf if np.isfinite(float(row.get("My", np.nan))) else np.nan
        dyg = float(row.get("Mx", np.nan)) / cf if np.isfinite(float(row.get("Mx", np.nan))) else np.nan
        add("G_M_over_compress_surrogate_global", dxg, dyg)

        dxl = float(row.get("My_local", np.nan)) / cf if np.isfinite(float(row.get("My_local", np.nan))) else np.nan
        dyl = float(row.get("Mx_local", np.nan)) / cf if np.isfinite(float(row.get("Mx_local", np.nan))) else np.nan
        dxg_l, dyg_l = _rotate_to_global(dxl, dyl, local_rotation_deg) if np.isfinite(dxl) and np.isfinite(dyl) else (np.nan, np.nan)
        add("H_M_over_compress_surrogate_local_then_global", dxg_l, dyg_l)

    return out


def run_dxdy_sign_transformation_study() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    annular_rows = []
    for rec in _iter_pcross_rows_for_definition_studies():
        ref_dx = float(rec["ref"].get("lever_DX", rec["ref"].get("DX", np.nan)))
        ref_dy = float(rec["ref"].get("lever_DY", rec["ref"].get("DY", np.nan)))
        ref_l = float(rec["ref"].get("lever_L", rec["ref"].get("L", np.nan)))
        for cand in _row_dxdy_sign_candidates(rec["row"], rec["local_rotation_deg"]):
            output = cand["output"]
            ref = ref_dx if output == "lever_DX" else ref_dy if output == "lever_DY" else ref_l
            if not np.isfinite(ref):
                continue
            calc = float(cand["value"]) if np.isfinite(cand["value"]) else np.nan
            out_row = {
                "fixture": rec["fixture"],
                "fixture_family": rec["fixture_family"],
                "load_case": rec["load_case"],
                "V_deg": rec["V_deg"],
                "output": output,
                "candidate": cand["candidate"],
                "ref": ref,
                "calc": calc,
                "signed_error": calc - ref if np.isfinite(calc) else np.nan,
                "rel_error": _safe_rel_err(calc, ref),
                "sign_agreement": _sign_agreement(calc, ref),
            }
            rows.append(out_row)
            if rec["fixture_family"] == "annular":
                annular_rows.append(out_row)

    detail = pd.DataFrame(rows).sort_values(["output", "fixture_family", "load_case", "V_deg", "candidate"]).reset_index(drop=True)
    summary = (
        detail.groupby(["fixture_family", "output", "candidate"], dropna=False)
        .agg(
            count=("rel_error", "count"),
            max_rel_error=("rel_error", "max"),
            median_rel_error=("rel_error", "median"),
            sign_agreement_rate=("sign_agreement", "mean"),
        )
        .reset_index()
        .sort_values(["output", "fixture_family", "max_rel_error", "median_rel_error"]) 
        .reset_index(drop=True)
    )

    winner_rows = []
    for output in ["lever_DX", "lever_DY", "lever_L"]:
        out_sub = summary[summary["output"] == output]
        if out_sub.empty:
            continue
        best = out_sub.sort_values(["fixture_family", "max_rel_error", "median_rel_error"]).groupby("fixture_family", as_index=False).first()
        counts = best["candidate"].value_counts()
        cross = counts.index[0] if (not counts.empty and int(counts.iloc[0]) == 3) else None
        for _, r in best.iterrows():
            winner_rows.append(
                {
                    "output": output,
                    "fixture_family": r["fixture_family"],
                    "best_candidate": r["candidate"],
                    "max_rel_error": r["max_rel_error"],
                    "median_rel_error": r["median_rel_error"],
                    "sign_agreement_rate": r["sign_agreement_rate"],
                    "cross_family_winner": cross,
                    "cross_family_winner_exists": bool(cross is not None),
                }
            )

    winners = pd.DataFrame(winner_rows).sort_values(["output", "fixture_family"]).reset_index(drop=True)

    # Explicit annular sign-pattern diagnostics for opposite-angle pairs.
    ann = pd.DataFrame(annular_rows)
    pair_rows = []
    pairs = [(0.0, 180.0), (90.0, 270.0), (45.0, 225.0)]
    if not ann.empty:
        for (fixture, output, cand), grp in ann.groupby(["fixture", "output", "candidate"]):
            by_angle = {float(r["V_deg"]): r for _, r in grp.iterrows()}
            for a, b in pairs:
                if a not in by_angle or b not in by_angle:
                    continue
                ra = by_angle[a]
                rb = by_angle[b]
                ref_opposite = bool(np.sign(float(ra["ref"])) == -np.sign(float(rb["ref"])))
                calc_opposite = bool(np.sign(float(ra["calc"])) == -np.sign(float(rb["calc"])))
                pair_rows.append(
                    {
                        "fixture": fixture,
                        "output": output,
                        "candidate": cand,
                        "pair": f"{int(a)}_vs_{int(b)}",
                        "ref_opposite_sign": ref_opposite,
                        "calc_opposite_sign": calc_opposite,
                        "match_ref_pattern": bool(ref_opposite == calc_opposite),
                    }
                )
    annular_pairs = pd.DataFrame(pair_rows).sort_values(["fixture", "output", "candidate", "pair"]).reset_index(drop=True)
    return detail, summary, winners, annular_pairs


def run_annular_dxdy_sign_focus_study() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Focused annular-only DX/DY sign/transformation discriminator."""
    rows = []
    for key in ["section0", "sectioniv"]:
        case = EMBEDDED_BENCHMARK_CASES[key]
        solver = case.solver_builder()
        solved = solver.solve_angle_sweep(case.load.angles_deg, case.load.P_target)
        by_angle = {float(r["angle_v_deg"]): r for r in solved}
        for angle in case.load.angles_deg:
            a = float(angle)
            row = by_angle[a]
            ref = case.reference_rows.get((case.load_case, a), None)
            if ref is None:
                continue
            ref_dx = float(ref.get("lever_DX", ref.get("DX", np.nan)))
            ref_dy = float(ref.get("lever_DY", ref.get("DY", np.nan)))
            if not (np.isfinite(ref_dx) and np.isfinite(ref_dy)):
                continue

            dz = row.get("debug_resultant_centroids", {})
            xc = dz.get("compress_zone_centroid_x")
            yc = dz.get("compress_zone_centroid_y")
            xt = dz.get("tension_zone_centroid_x")
            yt = dz.get("tension_zone_centroid_y")
            if any(v is None or not np.isfinite(float(v)) for v in [xc, yc, xt, yt]):
                continue

            dx_local = float(xt) - float(xc)
            dy_local = float(yt) - float(yc)
            phi = float(solver.cs.local_rotation_deg(a))
            dx_g, dy_g = _rotate_to_global(dx_local, dy_local, phi)
            dx_g_tc, dy_g_tc = _rotate_to_global(-dx_local, -dy_local, phi)

            candidates = {
                "1_current_branch_flip_both": (-dx_g, -dy_g),
                "2_no_blanket_flip": (dx_g, dy_g),
                "3_flip_DX_only": (-dx_g, dy_g),
                "4_flip_DY_only": (dx_g, -dy_g),
                "5_local_to_global_no_override": (dx_g, dy_g),
                "6_local_to_global_post_flip_DY": (dx_g, -dy_g),
                "6b_local_to_global_tension_to_compression": (dx_g_tc, dy_g_tc),
            }

            qref = _quadrant(ref_dx, ref_dy)
            for cand, (dx, dy) in candidates.items():
                rows.append(
                    {
                        "fixture": key,
                        "fixture_family": "annular",
                        "load_case": int(case.load_case),
                        "V_deg": a,
                        "candidate": cand,
                        "DX_ref": ref_dx,
                        "DY_ref": ref_dy,
                        "DX_calc": dx,
                        "DY_calc": dy,
                        "DX_rel_error": _safe_rel_err(dx, ref_dx),
                        "DY_rel_error": _safe_rel_err(dy, ref_dy),
                        "DX_sign_agreement": _sign_agreement(dx, ref_dx),
                        "DY_sign_agreement": _sign_agreement(dy, ref_dy),
                        "quadrant_ref": qref,
                        "quadrant_calc": _quadrant(dx, dy),
                        "quadrant_agreement": bool(_quadrant(dx, dy) == qref),
                    }
                )

    detail = pd.DataFrame(rows).sort_values(["candidate", "fixture", "V_deg"]).reset_index(drop=True)
    summary = (
        detail.groupby("candidate", dropna=False)
        .agg(
            max_rel_error_DX=("DX_rel_error", "max"),
            max_rel_error_DY=("DY_rel_error", "max"),
            sign_agreement_rate_DX=("DX_sign_agreement", "mean"),
            sign_agreement_rate_DY=("DY_sign_agreement", "mean"),
            quadrant_consistency_rate=("quadrant_agreement", "mean"),
        )
        .reset_index()
        .sort_values(["max_rel_error_DX", "max_rel_error_DY", "quadrant_consistency_rate"], ascending=[True, True, False])
        .reset_index(drop=True)
    )
    return detail, summary


def _tbeam_rows_for_constitutive_audit() -> tuple[list[dict], object]:
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    rows = []
    for lc, load in [(3, LOAD_CASE_3), (4, LOAD_CASE_4)]:
        solved = solver.solve_angle_sweep(load.angles_deg, load.P_target)
        by_angle = {float(r["angle_v_deg"]): r for r in solved}
        for angle in load.angles_deg:
            a = float(angle)
            ref = MANUAL_ROW_DIAGNOSTICS.get((lc, a))
            if ref is None:
                continue
            rows.append({"load_case": lc, "V_deg": a, "row": by_angle[a], "ref": ref})
    return rows, solver


def _mild_state_label(ms, eps: float, sigma: float) -> str:
    if eps >= 0.0:
        if abs(eps) <= ms.eps_yd_t + 1e-12:
            return "tension_elastic"
        if abs(sigma) >= ms.f_yd_t - 1e-6:
            return "tension_post_yield"
        return "tension_transition"
    if abs(eps) <= ms.eps_yd_c + 1e-12:
        return "compression_elastic"
    return "compression_post_yield"


def _prestress_state_label(total_eps: float, stress_mpa: float) -> str:
    e_pct = 100.0 * float(total_eps)
    if e_pct < 0.0:
        return "compression_zero_branch"
    if e_pct < 0.6:
        return "segment_0_0p6"
    if e_pct < 1.0:
        return "segment_0p6_1p0"
    if e_pct < 1.75:
        return "segment_1p0_1p75"
    if e_pct <= 3.5:
        return "segment_1p75_3p5_plateau"
    return "post_residual_zero"


def run_tbeam_constitutive_audit() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    tbeam_rows, base_solver = _tbeam_rows_for_constitutive_audit()
    ms = base_solver.mild_steel
    for rec in tbeam_rows:
        lc = rec["load_case"]
        a = rec["V_deg"]
        row = rec["row"]
        ref = rec["ref"]
        dbg = row.get("debug_force_components") or {}

        mild_ref_pm = _to_permille_ref(ref.get("strain_mild"))
        pre_ref_pm = _to_permille_ref(ref.get("strain_prestressed"))

        for b in dbg.get("mild_bar_details", []):
            eps_t = float(b.get("strain_total", np.nan))
            eps_legacy = -eps_t * 1000.0
            eps_pm = eps_t * 1000.0
            rows.append(
                {
                    "load_case": lc,
                    "V_deg": a,
                    "family": "tbeam",
                    "bar_family": "mild",
                    "bar_id": b.get("id"),
                    "zone_classification": "compression" if eps_t < 0.0 else "tension",
                    "strain_total_permille": eps_pm,
                    "strain_incremental_permille": np.nan,
                    "strain_total_legacy_permille": eps_legacy,
                    "stress_mpa": float(b.get("stress_mpa", np.nan)),
                    "force_kN": float(b.get("force_kN", np.nan)),
                    "state_label": _mild_state_label(ms, eps_t, float(b.get("stress_mpa", np.nan))),
                    "strain_mild_ref_permille": mild_ref_pm,
                    "strain_prestressed_ref_permille": pre_ref_pm,
                    "abs_gap_to_mild_ref_total": abs(eps_pm - mild_ref_pm) if np.isfinite(mild_ref_pm) else np.nan,
                    "abs_gap_to_mild_ref_legacy": abs(eps_legacy - mild_ref_pm) if np.isfinite(mild_ref_pm) else np.nan,
                    "abs_gap_to_prestress_ref_total": np.nan,
                    "abs_gap_to_prestress_ref_legacy": np.nan,
                    "abs_gap_to_prestress_ref_incremental": np.nan,
                    "abs_gap_to_prestress_ref_incremental_legacy": np.nan,
                }
            )

        for b in dbg.get("prestressed_bar_details", []):
            eps_t = float(b.get("strain_total", np.nan))
            eps_i = float(b.get("strain_incremental", np.nan))
            eps_legacy = -eps_t * 1000.0
            eps_i_legacy = -eps_i * 1000.0
            rows.append(
                {
                    "load_case": lc,
                    "V_deg": a,
                    "family": "tbeam",
                    "bar_family": "prestressed",
                    "bar_id": b.get("id"),
                    "zone_classification": "compression" if eps_i < 0.0 else "tension",
                    "strain_total_permille": eps_t * 1000.0,
                    "strain_incremental_permille": eps_i * 1000.0,
                    "strain_total_legacy_permille": eps_legacy,
                    "stress_mpa": float(b.get("stress_mpa", np.nan)),
                    "force_kN": float(b.get("force_kN", np.nan)),
                    "state_label": _prestress_state_label(eps_t, float(b.get("stress_mpa", np.nan))),
                    "strain_mild_ref_permille": mild_ref_pm,
                    "strain_prestressed_ref_permille": pre_ref_pm,
                    "abs_gap_to_mild_ref_total": np.nan,
                    "abs_gap_to_mild_ref_legacy": np.nan,
                    "abs_gap_to_prestress_ref_total": abs((eps_t * 1000.0) - pre_ref_pm) if np.isfinite(pre_ref_pm) else np.nan,
                    "abs_gap_to_prestress_ref_legacy": abs(eps_legacy - pre_ref_pm) if np.isfinite(pre_ref_pm) else np.nan,
                    "abs_gap_to_prestress_ref_incremental": abs((eps_i * 1000.0) - pre_ref_pm) if np.isfinite(pre_ref_pm) else np.nan,
                    "abs_gap_to_prestress_ref_incremental_legacy": abs(eps_i_legacy - pre_ref_pm) if np.isfinite(pre_ref_pm) else np.nan,
                }
            )

    detail = pd.DataFrame(rows).sort_values(["load_case", "V_deg", "bar_family", "bar_id"]).reset_index(drop=True)

    summary_rows = []
    for (lc, a), grp in detail.groupby(["load_case", "V_deg"]):
        mild = grp[grp["bar_family"] == "mild"]
        pre = grp[grp["bar_family"] == "prestressed"]
        summary_rows.append(
            {
                "load_case": int(lc),
                "V_deg": float(a),
                "strain_mild_ref_permille": float(grp["strain_mild_ref_permille"].dropna().iloc[0]) if grp["strain_mild_ref_permille"].notna().any() else np.nan,
                "strain_prestressed_ref_permille": float(grp["strain_prestressed_ref_permille"].dropna().iloc[0]) if grp["strain_prestressed_ref_permille"].notna().any() else np.nan,
                "best_mild_gap_total": float(mild["abs_gap_to_mild_ref_total"].min()) if not mild.empty else np.nan,
                "best_mild_gap_legacy": float(mild["abs_gap_to_mild_ref_legacy"].min()) if not mild.empty else np.nan,
                "best_prestress_gap_total": float(pre["abs_gap_to_prestress_ref_total"].min()) if not pre.empty else np.nan,
                "best_prestress_gap_legacy": float(pre["abs_gap_to_prestress_ref_legacy"].min()) if not pre.empty else np.nan,
                "best_prestress_gap_incremental": float(pre["abs_gap_to_prestress_ref_incremental"].min()) if not pre.empty else np.nan,
                "best_prestress_gap_incremental_legacy": float(pre["abs_gap_to_prestress_ref_incremental_legacy"].min()) if not pre.empty else np.nan,
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(["load_case", "V_deg"]).reset_index(drop=True)
    return detail, summary


def run_tbeam_constitutive_variant_study() -> pd.DataFrame:
    """Narrow benchmark-only constitutive variants for T-beam strain diagnostics."""

    variants = [
        "baseline",
        "mild_perfect_plastic",
        "prestress_soft_post_yield",
        "mild_perfect_plastic_plus_prestress_soft",
    ]

    rows = []
    target_rows = list(DIAGNOSTIC_ROWS)

    for var in variants:
        solver = build_pcross_tbeam_solver(prestress_eps0=0.004)

        if "mild_perfect_plastic" in var:
            ms = solver.mild_steel

            def mild_stress_variant(eps):
                ea = np.asarray(eps, dtype=float)
                s = np.zeros_like(ea)
                mt = ea >= 0.0
                if np.any(mt):
                    et = ea[mt]
                    s[mt] = np.where(et <= ms.eps_yd_t, ms.E_s * et, ms.f_yd_t)
                mc = ea < 0.0
                if np.any(mc):
                    ec = np.abs(ea[mc])
                    s[mc] = np.where(ec <= ms.eps_yd_c, -ms.E_s * ec, -ms.f_yd_c)
                return s

            ms.stress = mild_stress_variant

        if "prestress_soft_post_yield" in var:
            ps = solver.prestressed_steel

            def pre_stress_variant(total_eps):
                eps_arr = np.asarray(total_eps, dtype=float)
                e_pct = 100.0 * eps_arr
                sigma = np.zeros_like(eps_arr, dtype=float)

                m1 = (e_pct >= 0.0) & (e_pct < 0.6)
                sigma[m1] = (2000.0 * e_pct[m1]) / ps.gamma_y

                m2 = (e_pct >= 0.6) & (e_pct < 1.0)
                e = e_pct[m2]
                sigma[m2] = (-2500.0 * e**2 + 5000.0 * e - 900.0) / ps.gamma_y

                m3 = (e_pct >= 1.0) & (e_pct < 1.75)
                sigma[m3] = (0.85 * (60.0 * e_pct[m3] + 1540.0)) / ps.gamma_y

                m4 = (e_pct >= 1.75) & (e_pct <= 3.5)
                sigma[m4] = (0.85 * 1645.0) / ps.gamma_y
                return sigma

            ps.stress = pre_stress_variant

        rel_mx = []
        rel_my = []
        rel_kappa = []
        rel_cf = []
        rel_sm = []
        rel_sp = []
        for lc, ang in target_rows:
            solved = solver.solve(float(ang), _case_target(int(lc)))
            ref_mm = MANUAL_ROWS[(int(lc), float(ang))]
            ref_diag = MANUAL_ROW_DIAGNOSTICS[(int(lc), float(ang))]

            rel_mx.append(_safe_rel_err(float(solved.get("Mx", np.nan)), float(ref_mm["Mx"])))
            rel_my.append(_safe_rel_err(float(solved.get("My", np.nan)), float(ref_mm["My"])))
            rel_kappa.append(_safe_rel_err(float(solved.get("kappa", np.nan)), float(ref_diag["kappa"])))
            rel_cf.append(_safe_rel_err(float(solved.get("compress_force", np.nan)), float(ref_diag["compress_force"])))
            rel_sm.append(_safe_rel_err(float(solved.get("strain_mild", np.nan)), _to_permille_ref(ref_diag["strain_mild"])))
            sp_ref = ref_diag.get("strain_prestressed", None)
            rel_sp.append(_safe_rel_err(float(solved.get("strain_prestressed", np.nan)), _to_permille_ref(sp_ref) if sp_ref is not None else np.nan))

        rows.append(
            {
                "variant": var,
                "max_rel_err_strain_mild": float(np.nanmax(rel_sm)) if len(rel_sm) else np.nan,
                "max_rel_err_strain_prestressed": float(np.nanmax(rel_sp)) if len(rel_sp) else np.nan,
                "max_rel_err_Mx": float(np.nanmax(rel_mx)) if len(rel_mx) else np.nan,
                "max_rel_err_My": float(np.nanmax(rel_my)) if len(rel_my) else np.nan,
                "max_rel_err_kappa": float(np.nanmax(rel_kappa)) if len(rel_kappa) else np.nan,
                "max_rel_err_compress_force": float(np.nanmax(rel_cf)) if len(rel_cf) else np.nan,
            }
        )

    out = pd.DataFrame(rows).sort_values("variant").reset_index(drop=True)
    base = out[out["variant"] == "baseline"].iloc[0]
    for c in [
        "max_rel_err_strain_mild",
        "max_rel_err_strain_prestressed",
        "max_rel_err_Mx",
        "max_rel_err_My",
        "max_rel_err_kappa",
        "max_rel_err_compress_force",
    ]:
        out[f"delta_vs_baseline_{c}"] = out[c] - float(base[c])
    return out



def run_tbeam_branch_audit() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Audit all admissible branches on the six T-beam benchmark rows."""
    rows = []
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)

    for lc, angle in DIAGNOSTIC_ROWS:
        a = float(angle)
        p_target = _case_target(int(lc))
        selected = solver.solve(a, p_target)
        candidates = solver._solve_candidates(a, p_target)
        ref_mm = MANUAL_ROWS[(int(lc), a)]
        ref_diag = MANUAL_ROW_DIAGNOSTICS[(int(lc), a)]

        for idx, cand in enumerate(candidates):
            moment_err = max(
                _safe_rel_err(float(cand.get("Mx", np.nan)), float(ref_mm["Mx"])),
                _safe_rel_err(float(cand.get("My", np.nan)), float(ref_mm["My"])),
            )
            state_err = np.nanmax(
                [
                    _safe_rel_err(float(cand.get("kappa", np.nan)), float(ref_diag["kappa"])),
                    _safe_rel_err(float(cand.get("compress_force", np.nan)), float(ref_diag["compress_force"])),
                    _safe_rel_err(float(cand.get("strain_mild", np.nan)), _to_permille_ref(ref_diag.get("strain_mild"))),
                    _safe_rel_err(float(cand.get("strain_prestressed", np.nan)), _to_permille_ref(ref_diag.get("strain_prestressed"))),
                ]
            )
            rows.append(
                {
                    "load_case": int(lc),
                    "V_deg": a,
                    "candidate_index": idx,
                    "is_selected": bool(cand.get("pivot") == selected.get("pivot")),
                    "pivot": cand.get("pivot"),
                    "y_na": float(cand.get("y_na", np.nan)),
                    "kappa": float(cand.get("kappa", np.nan)),
                    "Mx": float(cand.get("Mx", np.nan)),
                    "My": float(cand.get("My", np.nan)),
                    "compress_force": float(cand.get("compress_force", np.nan)),
                    "strain_concrete": float(cand.get("strain_concrete", np.nan)),
                    "strain_mild": float(cand.get("strain_mild", np.nan)),
                    "strain_prestressed": float(cand.get("strain_prestressed", np.nan)),
                    "candidate_count": int(selected.get("candidate_count", len(candidates))),
                    "selected_candidate_index": int(selected.get("selected_candidate_index", -1)),
                    "selection_source": selected.get("selection_source"),
                    "moment_fit_error": float(moment_err),
                    "state_fit_error": float(state_err),
                }
            )

    detail = pd.DataFrame(rows).sort_values(["load_case", "V_deg", "candidate_index"]).reset_index(drop=True)

    summary_rows = []
    for (lc, a), grp in detail.groupby(["load_case", "V_deg"]):
        best_m = grp.sort_values(["moment_fit_error", "state_fit_error"]).iloc[0]
        best_s = grp.sort_values(["state_fit_error", "moment_fit_error"]).iloc[0]
        summary_rows.append(
            {
                "load_case": int(lc),
                "V_deg": float(a),
                "selected_candidate_index": int(grp["selected_candidate_index"].iloc[0]),
                "best_moment_candidate_index": int(best_m["candidate_index"]),
                "best_state_candidate_index": int(best_s["candidate_index"]),
                "best_moment_error": float(best_m["moment_fit_error"]),
                "best_state_error": float(best_s["state_fit_error"]),
                "same_candidate_for_moment_and_state": bool(int(best_m["candidate_index"]) == int(best_s["candidate_index"])),
                "selected_equals_best_state": bool(int(grp["selected_candidate_index"].iloc[0]) == int(best_s["candidate_index"])),
            }
        )

    summary = pd.DataFrame(summary_rows).sort_values(["load_case", "V_deg"]).reset_index(drop=True)
    return detail, summary


def _type1_curve_sigma(ps, eps_total: np.ndarray) -> np.ndarray:
    eps_arr = np.asarray(eps_total, dtype=float)
    e_pct = 100.0 * eps_arr
    sigma = np.zeros_like(eps_arr, dtype=float)
    mask1 = (e_pct >= 0.0) & (e_pct < 0.6)
    sigma[mask1] = (2000.0 * e_pct[mask1]) / ps.gamma_y
    mask2 = (e_pct >= 0.6) & (e_pct < 1.0)
    e = e_pct[mask2]
    sigma[mask2] = (-2500.0 * e**2 + 5000.0 * e - 900.0) / ps.gamma_y
    mask3 = (e_pct >= 1.0) & (e_pct < 1.75)
    sigma[mask3] = (60.0 * e_pct[mask3] + 1540.0) / ps.gamma_y
    mask4 = (e_pct >= 1.75) & (e_pct <= ps.RES_PCT)
    sigma[mask4] = 1645.0 / ps.gamma_y
    return sigma


def run_tbeam_type1_interpretation_study() -> pd.DataFrame:
    """Benchmark-only PrestressedSteelType1 interpretation variants on T-beam rows."""
    variants = [
        "A_current_total_strain_on_curve",
        "B_initial_stress_offset_plus_incremental_E",
        "C_shifted_strain_origin_relative_curve",
        "D_hybrid_curve_plus_incremental_cap",
    ]

    rows = []
    for variant in variants:
        solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
        ps = solver.prestressed_steel
        eps0 = float(ps.initial_strain)
        sigma0 = float(_type1_curve_sigma(ps, np.asarray([eps0]))[0])
        sigma_cap = 1645.0 / ps.gamma_y

        if variant != "A_current_total_strain_on_curve":
            def stress_variant(total_eps):
                et = np.asarray(total_eps, dtype=float)
                inc = et - eps0
                if variant == "B_initial_stress_offset_plus_incremental_E":
                    sigma = sigma0 + ps.E_p * inc
                    return np.clip(sigma, 0.0, sigma_cap)
                if variant == "C_shifted_strain_origin_relative_curve":
                    sigma_rel = _type1_curve_sigma(ps, np.maximum(inc, 0.0))
                    return np.clip(sigma0 + sigma_rel, 0.0, sigma_cap)
                # D hybrid
                sigma_curve = _type1_curve_sigma(ps, et)
                sigma_inc = sigma0 + 0.5 * ps.E_p * inc
                return np.clip(0.5 * sigma_curve + 0.5 * sigma_inc, 0.0, sigma_cap)

            ps.stress = stress_variant

        rel_mx = []
        rel_my = []
        rel_kappa = []
        rel_cf = []
        rel_sm = []
        rel_sp = []
        for lc, ang in DIAGNOSTIC_ROWS:
            solved = solver.solve(float(ang), _case_target(int(lc)))
            ref_mm = MANUAL_ROWS[(int(lc), float(ang))]
            ref_diag = MANUAL_ROW_DIAGNOSTICS[(int(lc), float(ang))]
            rel_mx.append(_safe_rel_err(float(solved.get("Mx", np.nan)), float(ref_mm["Mx"])))
            rel_my.append(_safe_rel_err(float(solved.get("My", np.nan)), float(ref_mm["My"])))
            rel_kappa.append(_safe_rel_err(float(solved.get("kappa", np.nan)), float(ref_diag["kappa"])))
            rel_cf.append(_safe_rel_err(float(solved.get("compress_force", np.nan)), float(ref_diag["compress_force"])))
            rel_sm.append(_safe_rel_err(float(solved.get("strain_mild", np.nan)), _to_permille_ref(ref_diag.get("strain_mild"))))
            rel_sp.append(_safe_rel_err(float(solved.get("strain_prestressed", np.nan)), _to_permille_ref(ref_diag.get("strain_prestressed"))))

        rows.append(
            {
                "variant": variant,
                "max_rel_err_strain_mild": float(np.nanmax(rel_sm)),
                "max_rel_err_strain_prestressed": float(np.nanmax(rel_sp)),
                "max_rel_err_kappa": float(np.nanmax(rel_kappa)),
                "max_rel_err_compress_force": float(np.nanmax(rel_cf)),
                "max_rel_err_Mx": float(np.nanmax(rel_mx)),
                "max_rel_err_My": float(np.nanmax(rel_my)),
            }
        )

    out = pd.DataFrame(rows).sort_values("variant").reset_index(drop=True)
    base = out[out["variant"] == "A_current_total_strain_on_curve"].iloc[0]
    for c in ["max_rel_err_strain_mild","max_rel_err_strain_prestressed","max_rel_err_kappa","max_rel_err_compress_force","max_rel_err_Mx","max_rel_err_My"]:
        out[f"delta_vs_baseline_{c}"] = out[c] - float(base[c])
    return out


def run_tbeam_reported_strain_study() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Focused T-beam audit for reported strain output definitions."""
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    rows = []

    for load_case, load in [(3, LOAD_CASE_3), (4, LOAD_CASE_4)]:
        solved = solver.solve_angle_sweep(load.angles_deg, load.P_target)
        by_angle = {float(r["angle_v_deg"]): r for r in solved}

        for lc, angle in DIAGNOSTIC_ROWS:
            if int(lc) != int(load_case):
                continue
            a = float(angle)
            row = by_angle[a]
            ref = MANUAL_ROW_DIAGNOSTICS[(int(load_case), a)]
            ref_mild = _to_permille_ref(ref.get("strain_mild"))
            ref_pre = _to_permille_ref(ref.get("strain_prestressed"))
            dbg = row.get("debug_force_components") or {}
            mild_rows = list(dbg.get("mild_bar_details") or [])
            pre_rows = list(dbg.get("prestressed_bar_details") or [])

            if mild_rows:
                force_gov = max(mild_rows, key=lambda r: abs(float(r.get("force_kN", 0.0))))
                abs_gov = max(mild_rows, key=lambda r: abs(float(r.get("strain_total", 0.0))))
                comp_ext = min(mild_rows, key=lambda r: float(r.get("y", np.inf)))
                tens_ext = max(mild_rows, key=lambda r: float(r.get("y", -np.inf)))
                mild_candidates = {
                    "A_force_governing_bar_total_legacy": -1000.0 * float(force_gov.get("strain_total", np.nan)),
                    "B_abs_strain_governing_bar_total_legacy": -1000.0 * float(abs_gov.get("strain_total", np.nan)),
                    "C_extreme_compression_side_bar_total_legacy": -1000.0 * float(comp_ext.get("strain_total", np.nan)),
                    "D_extreme_tension_side_bar_total_legacy": -1000.0 * float(tens_ext.get("strain_total", np.nan)),
                    "E_max_algebraic_legacy_reported": float(max([-1000.0 * float(b.get("strain_total", np.nan)) for b in mild_rows])),
                    "F_min_algebraic_legacy_reported": float(min([-1000.0 * float(b.get("strain_total", np.nan)) for b in mild_rows])),
                    "G_current_solver_reported": float(row.get("strain_mild", np.nan)),
                }
            else:
                mild_candidates = {}

            if pre_rows:
                force_gov = max(pre_rows, key=lambda r: abs(float(r.get("force_kN", 0.0))))
                abs_gov = max(pre_rows, key=lambda r: abs(float(r.get("strain_total", 0.0))))
                comp_ext = min(pre_rows, key=lambda r: float(r.get("y", np.inf)))
                tens_ext = max(pre_rows, key=lambda r: float(r.get("y", -np.inf)))
                pre_candidates = {
                    "A_force_governing_bar_total_legacy": -1000.0 * float(force_gov.get("strain_total", np.nan)),
                    "B_abs_strain_governing_bar_total_legacy": -1000.0 * float(abs_gov.get("strain_total", np.nan)),
                    "C_extreme_compression_side_bar_total_legacy": -1000.0 * float(comp_ext.get("strain_total", np.nan)),
                    "D_extreme_tension_side_bar_total_legacy": -1000.0 * float(tens_ext.get("strain_total", np.nan)),
                    "E_max_algebraic_legacy_reported": float(max([-1000.0 * float(b.get("strain_total", np.nan)) for b in pre_rows])),
                    "F_min_algebraic_legacy_reported": float(min([-1000.0 * float(b.get("strain_total", np.nan)) for b in pre_rows])),
                    "G_current_solver_reported": float(row.get("strain_prestressed", np.nan)),
                    "G2_force_governing_incremental_internal": 1000.0 * float(force_gov.get("strain_incremental", np.nan)),
                }
            else:
                pre_candidates = {}

            mild_ids = [str(b.get("id")) for b in mild_rows]
            mild_force = [float(b.get("force_kN", np.nan)) for b in mild_rows]
            mild_total_internal = [1000.0 * float(b.get("strain_total", np.nan)) for b in mild_rows]
            mild_total_legacy = [-v for v in mild_total_internal]
            mild_zone = ["compression" if float(b.get("force_kN", 0.0)) < 0.0 else "tension" for b in mild_rows]

            pre_ids = [str(b.get("id")) for b in pre_rows]
            pre_force = [float(b.get("force_kN", np.nan)) for b in pre_rows]
            pre_total_internal = [1000.0 * float(b.get("strain_total", np.nan)) for b in pre_rows]
            pre_total_legacy = [-v for v in pre_total_internal]
            pre_inc_internal = [1000.0 * float(b.get("strain_incremental", np.nan)) for b in pre_rows]
            pre_inc_legacy = [-v for v in pre_inc_internal]
            pre_zone = ["compression" if float(b.get("force_kN", 0.0)) < 0.0 else "tension" for b in pre_rows]

            for cand, val in mild_candidates.items():
                rows.append({
                    "family": "tbeam",
                    "load_case": int(load_case),
                    "V_deg": a,
                    "output": "strain_mild",
                    "candidate": cand,
                    "ref": ref_mild,
                    "calc": float(val) if np.isfinite(val) else np.nan,
                    "rel_error": _safe_rel_err(float(val), ref_mild),
                    "signed_error": float(val) - float(ref_mild) if np.isfinite(val) and np.isfinite(ref_mild) else np.nan,
                    "sign_agreement": _sign_agreement(float(val), ref_mild),
                    "pivot": row.get("pivot"),
                    "candidate_count": row.get("candidate_count"),
                    "selected_candidate_index": row.get("selected_candidate_index"),
                    "bar_ids": "|".join(mild_ids),
                    "bar_force_kN": "|".join(f"{v:.6g}" for v in mild_force),
                    "bar_zone": "|".join(mild_zone),
                    "mild_total_internal_permille": "|".join(f"{v:.6g}" for v in mild_total_internal),
                    "mild_total_legacy_permille": "|".join(f"{v:.6g}" for v in mild_total_legacy),
                })

            for cand, val in pre_candidates.items():
                rows.append({
                    "family": "tbeam",
                    "load_case": int(load_case),
                    "V_deg": a,
                    "output": "strain_prestressed",
                    "candidate": cand,
                    "ref": ref_pre,
                    "calc": float(val) if np.isfinite(val) else np.nan,
                    "rel_error": _safe_rel_err(float(val), ref_pre),
                    "signed_error": float(val) - float(ref_pre) if np.isfinite(val) and np.isfinite(ref_pre) else np.nan,
                    "sign_agreement": _sign_agreement(float(val), ref_pre),
                    "pivot": row.get("pivot"),
                    "candidate_count": row.get("candidate_count"),
                    "selected_candidate_index": row.get("selected_candidate_index"),
                    "bar_ids": "|".join(pre_ids),
                    "bar_force_kN": "|".join(f"{v:.6g}" for v in pre_force),
                    "bar_zone": "|".join(pre_zone),
                    "prestress_total_internal_permille": "|".join(f"{v:.6g}" for v in pre_total_internal),
                    "prestress_total_legacy_permille": "|".join(f"{v:.6g}" for v in pre_total_legacy),
                    "prestress_incremental_internal_permille": "|".join(f"{v:.6g}" for v in pre_inc_internal),
                    "prestress_incremental_legacy_permille": "|".join(f"{v:.6g}" for v in pre_inc_legacy),
                })

    detail = pd.DataFrame(rows).sort_values(["output", "load_case", "V_deg", "candidate"]).reset_index(drop=True)
    summary = (
        detail.groupby(["output", "candidate"], dropna=False)
        .agg(
            count=("rel_error", "count"),
            max_rel_error=("rel_error", "max"),
            median_rel_error=("rel_error", "median"),
            sign_agreement_rate=("sign_agreement", "mean"),
        )
        .reset_index()
        .sort_values(["output", "max_rel_error", "median_rel_error"])
        .reset_index(drop=True)
    )
    return detail, summary


def run_annular_dxdy_definition_study() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Focused annular-only DX/DY output-definition candidate study."""
    rows = []
    pair_defs = [(0.0, 180.0), (90.0, 270.0), (45.0, 225.0)]

    for key in ["section0", "sectioniv"]:
        case = EMBEDDED_BENCHMARK_CASES[key]
        solver = case.solver_builder()
        solved = solver.solve_angle_sweep(case.load.angles_deg, case.load.P_target)
        by_angle = {float(r["angle_v_deg"]): r for r in solved}

        for angle in case.load.angles_deg:
            a = float(angle)
            row = by_angle[a]
            ref = case.reference_rows.get((case.load_case, a))
            if ref is None:
                continue
            ref_dx = float(ref.get("lever_DX", ref.get("DX", np.nan)))
            ref_dy = float(ref.get("lever_DY", ref.get("DY", np.nan)))
            if not (np.isfinite(ref_dx) and np.isfinite(ref_dy)):
                continue

            dz = row.get("debug_resultant_centroids") or {}
            xc = dz.get("compress_zone_centroid_x")
            yc = dz.get("compress_zone_centroid_y")
            xt = dz.get("tension_zone_centroid_x")
            yt = dz.get("tension_zone_centroid_y")
            if any(v is None or not np.isfinite(float(v)) for v in [xc, yc, xt, yt]):
                continue

            dx_local = float(xt) - float(xc)
            dy_local = float(yt) - float(yc)
            phi = float(solver.cs.local_rotation_deg(a))
            dx_g, dy_g = _rotate_to_global(dx_local, dy_local, phi)
            # rotate centroids first, then subtract in global frame
            xc_g, yc_g = _rotate_to_global(float(xc), float(yc), phi)
            xt_g, yt_g = _rotate_to_global(float(xt), float(yt), phi)
            dx_global_direct = xt_g - xc_g
            dy_global_direct = yt_g - yc_g

            candidates = {
                "A_current_branch_rule": (float(row.get("lever_DX", np.nan)), float(row.get("lever_DY", np.nan))),
                "B_without_post_transform_sign_override": (dx_g, dy_g),
                "C_flip_DX_only": (-dx_g, dy_g),
                "D_flip_DY_only": (dx_g, -dy_g),
                "E_local_to_global_centroid_vector": (dx_g, dy_g),
                "F_direct_global_centroid_vector": (dx_global_direct, dy_global_direct),
                "G_tension_to_compression_local_then_global": (-dx_g, -dy_g),
            }

            for cand, (dx, dy) in candidates.items():
                rows.append(
                    {
                        "fixture": key,
                        "load_case": int(case.load_case),
                        "V_deg": a,
                        "candidate": cand,
                        "DX_ref": ref_dx,
                        "DY_ref": ref_dy,
                        "DX_calc": float(dx),
                        "DY_calc": float(dy),
                        "DX_rel_error": _safe_rel_err(float(dx), ref_dx),
                        "DY_rel_error": _safe_rel_err(float(dy), ref_dy),
                        "DX_sign_agreement": _sign_agreement(float(dx), ref_dx),
                        "DY_sign_agreement": _sign_agreement(float(dy), ref_dy),
                    }
                )

    detail = pd.DataFrame(rows).sort_values(["candidate", "fixture", "V_deg"]).reset_index(drop=True)

    sym_rows = []
    for candidate, cdf in detail.groupby("candidate"):
        for fixture, fdf in cdf.groupby("fixture"):
            by_angle = {float(r["V_deg"]): r for _, r in fdf.iterrows()}
            for a, b in pair_defs:
                if a not in by_angle or b not in by_angle:
                    continue
                ra = by_angle[a]
                rb = by_angle[b]
                sym_rows.append(
                    {
                        "candidate": candidate,
                        "fixture": fixture,
                        "pair": f"{int(a)}_vs_{int(b)}",
                        "dx_pattern_ok": bool(np.sign(float(ra["DX_calc"])) == -np.sign(float(rb["DX_calc"]))),
                        "dy_pattern_ok": bool(np.sign(float(ra["DY_calc"])) == -np.sign(float(rb["DY_calc"]))),
                    }
                )
    sym = pd.DataFrame(sym_rows)

    summary = (
        detail.groupby("candidate", dropna=False)
        .agg(
            max_rel_error_DX=("DX_rel_error", "max"),
            max_rel_error_DY=("DY_rel_error", "max"),
            sign_agreement_rate_DX=("DX_sign_agreement", "mean"),
            sign_agreement_rate_DY=("DY_sign_agreement", "mean"),
        )
        .reset_index()
    )
    if not sym.empty:
        sym_agg = (
            sym.groupby("candidate", dropna=False)
            .agg(
                rotational_symmetry_dx_rate=("dx_pattern_ok", "mean"),
                rotational_symmetry_dy_rate=("dy_pattern_ok", "mean"),
            )
            .reset_index()
        )
        summary = summary.merge(sym_agg, on="candidate", how="left")
    else:
        summary["rotational_symmetry_dx_rate"] = np.nan
        summary["rotational_symmetry_dy_rate"] = np.nan

    summary = summary.sort_values(["max_rel_error_DX", "max_rel_error_DY", "sign_agreement_rate_DX", "sign_agreement_rate_DY"], ascending=[True, True, False, False]).reset_index(drop=True)
    return detail, summary


def run_unified_output_rule_study() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Cross-family selection study for unified PCROSS-facing output rules."""
    detail, _, _ = run_output_definition_study()
    targets = {"strain_mild", "strain_prestressed", "lever_DX", "lever_DY"}
    d = detail[detail["output"].isin(targets)].copy()

    family_stats = (
        d.groupby(["output", "candidate", "fixture_family"], dropna=False)
        .agg(
            count=("rel_error", "count"),
            max_rel_error=("rel_error", "max"),
            median_rel_error=("rel_error", "median"),
            sign_agreement_rate=("sign_agreement", "mean"),
        )
        .reset_index()
    )

    global_stats = (
        d.groupby(["output", "candidate"], dropna=False)
        .agg(
            count=("rel_error", "count"),
            family_coverage=("fixture_family", "nunique"),
            global_max_rel_error=("rel_error", "max"),
            global_median_rel_error=("rel_error", "median"),
            global_sign_agreement_rate=("sign_agreement", "mean"),
        )
        .reset_index()
    )

    per_family_worst = (
        family_stats.groupby(["output", "candidate"], dropna=False)
        .agg(
            worst_family_max_rel_error=("max_rel_error", "max"),
            worst_family_median_rel_error=("median_rel_error", "max"),
        )
        .reset_index()
    )
    summary = (
        global_stats.merge(per_family_worst, on=["output", "candidate"], how="left")
        .sort_values(["output", "worst_family_max_rel_error", "global_max_rel_error", "global_median_rel_error"]) 
        .reset_index(drop=True)
    )

    winner_rows = []
    for output in sorted(targets):
        sub = summary[summary["output"] == output]
        if sub.empty:
            continue
        best = sub.iloc[0]
        runner = sub.iloc[1] if len(sub) > 1 else None
        robust = False
        if runner is not None and np.isfinite(best["worst_family_max_rel_error"]) and np.isfinite(runner["worst_family_max_rel_error"]):
            robust = float(best["worst_family_max_rel_error"]) + 1e-12 < 0.90 * float(runner["worst_family_max_rel_error"])

        winner_rows.append(
            {
                "output": output,
                "best_candidate": best["candidate"],
                "best_worst_family_max_rel_error": best["worst_family_max_rel_error"],
                "best_global_max_rel_error": best["global_max_rel_error"],
                "best_global_median_rel_error": best["global_median_rel_error"],
                "best_family_coverage": int(best["family_coverage"]),
                "runner_up_candidate": None if runner is None else runner["candidate"],
                "runner_up_worst_family_max_rel_error": None if runner is None else runner["worst_family_max_rel_error"],
                "single_global_winner_exists": bool(robust),
                "remaining_gap_interpretation": (
                    "output-definition mismatch (global winner supported)"
                    if robust else
                    "likely constitutive/model-form mismatch or family-specific legacy behavior"
                ),
            }
        )

    winners = pd.DataFrame(winner_rows).sort_values("output").reset_index(drop=True)
    return family_stats, summary, winners


def run_methodology_alignment_audit() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Code-driven methodology alignment audit: RCSect plastic vs embedded PCROSS facts."""
    family_stats, unified_summary, unified_winners = run_unified_output_rule_study()

    # Runtime probes for evidence notes.
    tbeam_solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    tbeam_row = tbeam_solver.solve(5.0, LOAD_CASE_3.P_target)
    ann_case = EMBEDDED_BENCHMARK_CASES["section0"]
    ann_row = ann_case.solver_builder().solve(45.0, ann_case.load.P_target)

    rows = [
        # A) sign conventions
        {"category":"A_sign_conventions","item":"axial_load_sign","pcross_expectation":"Compression-positive P input/output","rcsect_observation":"P_target and N_calc are compression-positive; internal N_tot is tension-positive and converted before report","status":"aligned","evidence":"PlasticSolver.solve docstring and _to_compression_positive usage"},
        {"category":"A_sign_conventions","item":"concrete_strain_sign","pcross_expectation":"Printed strain positive in compression","rcsect_observation":"Internal/report concrete strain is compression-positive (kappa*(y_top-y_na))","status":"aligned","evidence":"strain_concrete uses internal_concrete_strain directly"},
        {"category":"A_sign_conventions","item":"mild_strain_sign","pcross_expectation":"Printed strain positive in compression","rcsect_observation":"Internal mild strain follows constitutive sign; reported mild strain uses legacy inversion (-internal)","status":"partially_aligned","evidence":"_reported_strain_outputs inverts internal mild strain"},
        {"category":"A_sign_conventions","item":"prestress_strain_sign","pcross_expectation":"Printed cable strain positive in compression","rcsect_observation":"Internal prestress total/incremental tracked with constitutive sign; reported prestress strain uses legacy inversion","status":"partially_aligned","evidence":"_reported_strain_outputs and debug prestress strain channels"},
        {"category":"A_sign_conventions","item":"moment_signs","pcross_expectation":"Mx/My signs match benchmark printed orientation","rcsect_observation":"Local->global transform includes benchmark-facing Mx sign anchoring and global rotation","status":"aligned","evidence":"_assemble_solution Mx/My transform logic"},
        {"category":"A_sign_conventions","item":"lever_signs","pcross_expectation":"Printed DX/DY follow PCROSS reported convention","rcsect_observation":"Centroid-based arm vector reported; DY uses unified global sign inversion winner, DX kept on existing unified reconstruction","status":"partially_aligned","evidence":"_reported_lever_outputs + unified study winner for DY"},

        # B) angle/orientation
        {"category":"B_angle_orientation","item":"V_definition","pcross_expectation":"V is NA angle to Y-axis","rcsect_observation":"Solver takes angle_v_deg and rotates section via get_rotated_system/local_rotation_deg, then solves NA depth","status":"partially_aligned","evidence":"Direct NA-to-Y axis statement not explicitly encoded as contract"},
        {"category":"B_angle_orientation","item":"rotation_direction","pcross_expectation":"Consistent section/NA orientation conventions","rcsect_observation":"Rotation handled through CrossSection local_rotation_deg + trig transforms for moments/levers","status":"partially_aligned","evidence":"Consistent implementation, but legacy orientation contract remains inferred from benchmarks"},
        {"category":"B_angle_orientation","item":"MxMy_local_to_global","pcross_expectation":"Printed Mx/My mapped from solved local frame","rcsect_observation":"Explicit trig transform with benchmark-facing sign anchoring","status":"aligned","evidence":"_assemble_solution Mx_global/My_global equations"},
        {"category":"B_angle_orientation","item":"DXDY_local_to_global","pcross_expectation":"Printed DX/DY mapped from centroid arm","rcsect_observation":"Arm built in rotated frame then mapped to global; DY convention overridden per global winner","status":"partially_aligned","evidence":"_reported_lever_outputs"},
        {"category":"B_angle_orientation","item":"NA_intersections","pcross_expectation":"Report NA intersections with X and Y axes","rcsect_observation":"na_intersect_x and na_intersect_y are explicitly reported from y_na and trig","status":"aligned","evidence":"_assemble_solution intersection_x/intersection_y"},

        # C) safety factors
        {"category":"C_safety_factors","item":"gamma_c_FC","pcross_expectation":"Concrete design strength reduced by FC","rcsect_observation":"ConcreteType1 uses gamma_c from benchmark mappings","status":"aligned","evidence":"build_pcross_tbeam_solver maps gamma_c to ConcreteType1"},
        {"category":"C_safety_factors","item":"gamma_y_FY","pcross_expectation":"Steel design strength reduced by FY","rcsect_observation":"Mild/prestress type1 and type6 builders pass gamma_y","status":"aligned","evidence":"fixture builders pass gamma_y to steel models"},
        {"category":"C_safety_factors","item":"gamma_u_FU","pcross_expectation":"Rupture stress/strain reduced by FU","rcsect_observation":"Type1/type6 builders pass gamma_u and diagnostics include FU-mapping studies","status":"partially_aligned","evidence":"FU influence validated in benchmark fixture studies, not fully proven across all families"},
        {"category":"C_safety_factors","item":"gamma_E_FE","pcross_expectation":"Steel modulus adjusted by FE","rcsect_observation":"Type1/type6 builders pass gamma_E and benchmark mappings include FE variants","status":"aligned","evidence":"build_pcross_tbeam_solver and strip builders map gamma_E"},

        # D) material families
        {"category":"D_material_families","item":"concrete_type1","pcross_expectation":"Explicit legacy type family","rcsect_observation":"ConcreteType1 used in benchmark fixtures","status":"aligned","evidence":"build_pcross_tbeam_solver/build_strip/build_annular use ConcreteType1"},
        {"category":"D_material_families","item":"mild_steel_type1","pcross_expectation":"Explicit legacy type family","rcsect_observation":"MildSteelType1 used for benchmark families","status":"aligned","evidence":"Fixture builders instantiate MildSteelType1"},
        {"category":"D_material_families","item":"prestressed_type1","pcross_expectation":"Explicit legacy type family","rcsect_observation":"PrestressedSteelType1 used in tbeam benchmark path","status":"aligned","evidence":"build_pcross_tbeam_solver"},
        {"category":"D_material_families","item":"prestressed_type6","pcross_expectation":"Explicit legacy type family","rcsect_observation":"PrestressedSteelType6 used in snit benchmark path","status":"aligned","evidence":"_build_strip_solver"},

        # E) reported outputs
        {"category":"E_reported_outputs","item":"strain_concrete","pcross_expectation":"Reported max concrete strain compression-positive","rcsect_observation":"Directly reported from solved kappa/y_na as compression-positive","status":"directly_aligned","evidence":"strain_concrete field"},
        {"category":"E_reported_outputs","item":"strain_mild","pcross_expectation":"Reported max mild strain compression-positive","rcsect_observation":"No robust global winner across families in unified study","status":"unresolved","evidence":"unified_winners strain_mild"},
        {"category":"E_reported_outputs","item":"strain_prestressed","pcross_expectation":"Reported max cable strain compression-positive","rcsect_observation":"No robust global winner across families in unified study","status":"unresolved","evidence":"unified_winners strain_prestressed"},
        {"category":"E_reported_outputs","item":"compress_force","pcross_expectation":"Compression-zone sum concrete+mild+prestress","rcsect_observation":"Reported as zone_compression_concrete+mild+prestress","status":"directly_aligned","evidence":"_reported_compression_and_warning_outputs"},
        {"category":"E_reported_outputs","item":"L","pcross_expectation":"Lever-arm magnitude","rcsect_observation":"Reported as hypot(DX,DY)","status":"approximately_aligned","evidence":"lever_L from reported DX/DY"},
        {"category":"E_reported_outputs","item":"DX","pcross_expectation":"Reported lever component DX","rcsect_observation":"No robust global winner in unified study","status":"unresolved","evidence":"unified_winners lever_DX"},
        {"category":"E_reported_outputs","item":"DY","pcross_expectation":"Reported lever component DY","rcsect_observation":"Global winner exists and production mapping follows reported DY sign inversion","status":"directly_aligned","evidence":"unified_winners lever_DY + _reported_lever_outputs"},
        {"category":"E_reported_outputs","item":"W1_W2","pcross_expectation":"Warnings based on compression reinforcement vs full concrete-compression design force","rcsect_observation":"Reported thresholds are 0.5*N_c_util and 1.0*N_c_util","status":"directly_aligned","evidence":"_reported_compression_and_warning_outputs"},
        {"category":"E_reported_outputs","item":"U_R","pcross_expectation":"U and R printed legacy outputs","rcsect_observation":"U/R are not explicitly reported by production solver outputs","status":"unresolved","evidence":"_assemble_solution output keys exclude U and R"},
        {"category":"E_reported_outputs","item":"NA_intersections","pcross_expectation":"NA intersections printed","rcsect_observation":"na_intersect_x and na_intersect_y are reported","status":"directly_aligned","evidence":"_assemble_solution"},

        # F) geometry/input semantics
        {"category":"F_geometry_input","item":"coords_in_m","pcross_expectation":"Coordinates in meters","rcsect_observation":"Fixtures and solver geometry values are in meter-scale coordinates","status":"aligned","evidence":"fixture coordinate magnitudes + force conversion conventions"},
        {"category":"F_geometry_input","item":"bar_area_mm2","pcross_expectation":"Bar areas in mm²","rcsect_observation":"Bar areas consumed as mm² and converted through MPa*mm² -> N -> kN","status":"aligned","evidence":"_bar_force_kN and fixture bar areas"},
        {"category":"F_geometry_input","item":"outer_clockwise","pcross_expectation":"Outer boundary clockwise","rcsect_observation":"No universal runtime enforcement in solver core; fixtures are authored to required orientation","status":"partially_aligned","evidence":"fixture conventions relied upon"},
        {"category":"F_geometry_input","item":"void_anticlockwise","pcross_expectation":"Void boundaries anti-clockwise","rcsect_observation":"No universal runtime enforcement in solver core; fixtures authored accordingly","status":"partially_aligned","evidence":"fixture conventions relied upon"},
        {"category":"F_geometry_input","item":"mild_before_prestress","pcross_expectation":"Mild bars listed before prestressed bars","rcsect_observation":"CrossSection API takes separate mild/prestress lists; ordering is structurally separated","status":"aligned","evidence":"CrossSection inputs split as rebar_mild/rebar_prestressed"},
    ]

    detail = pd.DataFrame(rows)

    # Remaining structural mismatch summary rows (for easy CSV filtering).
    mismatch_rows = [
        {
            "category": "Z_remaining_structural_mismatch",
            "item": "tbeam_strain_gap",
            "pcross_expectation": "T-beam reported strains should align under one global rule if output-only issue",
            "rcsect_observation": "Current studies show no robust global winner for strain_mild/strain_prestressed",
            "status": "likely_constitutive_or_family_methodology",
            "evidence": "plastic_tbeam_reported_strain_summary + unified_output_rule_summary",
        },
        {
            "category": "Z_remaining_structural_mismatch",
            "item": "lever_DX_ambiguity",
            "pcross_expectation": "DX should admit robust global convention if purely output semantic",
            "rcsect_observation": "Unified study does not identify robust global DX winner",
            "status": "still_unresolved",
            "evidence": "plastic_unified_output_rule_summary",
        },
        {
            "category": "Z_remaining_structural_mismatch",
            "item": "project_blocker_type",
            "pcross_expectation": "Output-definition tuning should close residuals if semantics-only",
            "rcsect_observation": "After DY adoption, remaining major residuals are mostly non-output-global (constitutive/family-methodology + missing U/R)",
            "status": "methodology_dominant",
            "evidence": "unified winners + reported output coverage",
        },
    ]

    detail = pd.concat([detail, pd.DataFrame(mismatch_rows)], ignore_index=True)

    status_summary = (
        detail.groupby(["category", "status"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["category", "status"])
        .reset_index(drop=True)
    )

    return detail, status_summary
